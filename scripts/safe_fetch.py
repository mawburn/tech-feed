"""Small, dependency-free HTTP(S) client for fetching untrusted publisher URLs.

Protections:
- only http/https on the default ports, no credentials in URLs;
- every hostname is resolved once and every resolved address must be globally
  routable (no loopback, private, link-local, CGNAT, multicast or reserved ranges);
- the socket connects to the address that was checked (TLS still verifies the
  original hostname via SNI), so DNS rebinding cannot swap in a private address;
- redirects are followed manually (max 5) and every hop is re-validated;
- response bodies are streamed with a hard byte cap and a total timeout.
"""
from __future__ import annotations

import http.client
import ipaddress
import socket
import ssl
import time
from dataclasses import dataclass, field
from urllib.parse import urljoin, urlsplit

USER_AGENT = "mawburn-tech-feed/2.0 (+https://mawburn.github.io/tech-feed/; publisher metadata fetcher)"
ALLOWED_PORTS = {"http": 80, "https": 443}
MAX_REDIRECTS = 5


class FetchError(Exception):
    """A URL was unsafe, unreachable, too large or otherwise unusable."""


@dataclass
class Response:
    url: str
    status: int
    headers: dict[str, str]
    body: bytes
    redirects: list[str] = field(default_factory=list)

    @property
    def content_type(self) -> str:
        return self.headers.get("content-type", "").split(";")[0].strip().lower()

    def charset(self, default="utf-8") -> str:
        for part in self.headers.get("content-type", "").split(";")[1:]:
            key, _, value = part.partition("=")
            if key.strip().lower() == "charset" and value.strip():
                return value.strip().strip('"')
        return default


def _address_allowed(address: str) -> bool:
    try:
        ip = ipaddress.ip_address(address)
    except ValueError:
        return False
    if isinstance(ip, ipaddress.IPv6Address) and ip.ipv4_mapped:
        ip = ip.ipv4_mapped
    return ip.is_global and not ip.is_multicast


# Tests replace this to reach a local fixture server.
address_allowed = _address_allowed


def check_url(url: str) -> tuple[str, str, int]:
    """Validate a URL's shape. Returns (scheme, host, port)."""
    try:
        parts = urlsplit(url)
        port = parts.port
    except (TypeError, ValueError) as exc:
        raise FetchError(f"malformed URL: {exc}") from None
    if parts.scheme not in ALLOWED_PORTS:
        raise FetchError(f"unsupported scheme {parts.scheme!r}")
    if not parts.hostname or parts.username or parts.password:
        raise FetchError("URL must have a host and no credentials")
    default = ALLOWED_PORTS[parts.scheme]
    if port not in (None, default) and not getattr(address_allowed, "allow_any_port", False):
        raise FetchError(f"port {port} not allowed")
    return parts.scheme, parts.hostname, port or default


def resolve_public(host: str, port: int) -> str:
    """Resolve a hostname and return one address, refusing if ANY address is non-public."""
    try:
        infos = socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)
    except socket.gaierror as exc:
        raise FetchError(f"DNS lookup failed for {host}: {exc}") from None
    addresses = [info[4][0] for info in infos]
    if not addresses:
        raise FetchError(f"no addresses for {host}")
    for address in addresses:
        if not address_allowed(address):
            raise FetchError(f"{host} resolves to non-public address {address}")
    return addresses[0]


class _PinnedHTTPConnection(http.client.HTTPConnection):
    def __init__(self, host, port, address, timeout):
        super().__init__(host, port, timeout=timeout)
        self._address = address

    def connect(self):
        self.sock = socket.create_connection((self._address, self.port), self.timeout)


class _PinnedHTTPSConnection(http.client.HTTPSConnection):
    def __init__(self, host, port, address, timeout, context):
        super().__init__(host, port, timeout=timeout, context=context)
        self._address = address

    def connect(self):
        sock = socket.create_connection((self._address, self.port), self.timeout)
        self.sock = self._context.wrap_socket(sock, server_hostname=self.host)


_TLS = ssl.create_default_context()


def fetch(url: str, *, max_bytes: int, accept: str = "*/*", timeout: float = 10.0,
          total_timeout: float = 25.0, headers: dict | None = None, truncate: bool = False) -> Response:
    """GET a URL safely. Raises FetchError for anything unsafe or unusable.

    Non-2xx final responses raise FetchError too (with the status in the message).
    With truncate=True, bodies longer than max_bytes are cut off instead of rejected
    (useful for HTML, where the metadata is in <head>).
    """
    deadline = time.monotonic() + total_timeout
    redirects: list[str] = []
    current = url
    for _ in range(MAX_REDIRECTS + 1):
        scheme, host, port = check_url(current)
        address = resolve_public(host, port)
        parts = urlsplit(current)
        path = (parts.path or "/") + (f"?{parts.query}" if parts.query else "")
        if scheme == "https":
            conn = _PinnedHTTPSConnection(host, port, address, timeout, _TLS)
        else:
            conn = _PinnedHTTPConnection(host, port, address, timeout)
        request_headers = {"User-Agent": USER_AGENT, "Accept": accept,
                           "Accept-Encoding": "identity", "Connection": "close"}
        request_headers.update(headers or {})
        try:
            conn.request("GET", path, headers=request_headers)
            resp = conn.getresponse()
            status = resp.status
            response_headers = {k.lower(): v for k, v in resp.getheaders()}
            if status in (301, 302, 303, 307, 308):
                location = response_headers.get("location")
                resp.close()
                if not location:
                    raise FetchError(f"redirect without Location from {current}")
                current = urljoin(current, location)
                redirects.append(current)
                continue
            if not 200 <= status < 300:
                raise FetchError(f"HTTP {status} from {current}")
            declared = response_headers.get("content-length")
            if not truncate and declared and declared.isdigit() and int(declared) > max_bytes:
                raise FetchError(f"response too large ({declared} bytes > {max_bytes})")
            chunks, size = [], 0
            while True:
                if time.monotonic() > deadline:
                    raise FetchError("download timed out")
                chunk = resp.read(min(65536, max_bytes + 1 - size))
                if not chunk:
                    break
                chunks.append(chunk)
                size += len(chunk)
                if size > max_bytes:
                    if truncate:
                        chunks[-1] = chunk[: len(chunk) - (size - max_bytes)]
                        break
                    raise FetchError(f"response exceeds {max_bytes} bytes")
            return Response(current, status, response_headers, b"".join(chunks), redirects)
        except FetchError:
            raise
        except (OSError, http.client.HTTPException, ssl.SSLError, ValueError) as exc:
            raise FetchError(f"{type(exc).__name__}: {str(exc)[:160]}") from None
        finally:
            conn.close()
    raise FetchError(f"too many redirects from {url}")
