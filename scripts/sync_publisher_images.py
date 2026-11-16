#!/usr/bin/env python3
"""Discover publisher Open Graph images and store optimized local WebP copies.

Runs in GitHub Actions on `main` only. The scheduler never touches images.

Stages, all idempotent:
1. Discovery (daily stories without an image): read og:image / twitter:image
   metadata from the story's first sources and attach
   image = {url, alt, credit, sourceUrl}, as before.
2. Localization (daily stories and weekly themes with image.url): download
   the image through scripts/safe_fetch.py, validate it, convert it to WebP
   (≤600×600, never upscaled, metadata stripped, quality chosen per image so it
   still looks the same as the original, ≤50 KB) and store it in
   assets/img/<sha256-of-source[:20]>.webp. SVGs are kept as sanitized .svg.
   The name is a content hash, so
   identical source bytes share one file.
3. Annotation: add image.local, image.width, image.height and image.sha256 to
   the JSON. Existing keys (url, alt, credit, sourceUrl) are never changed.

scripts/image_manifest.json records the outcome for every image URL and article
page (ok / failed / skipped). Stored images are never re-downloaded, failures
are retried after a back-off with an attempt limit, and files are kept even
when the source disappears.

Usage:
  sync_publisher_images.py                 recent files (last 7 Pacific days)
  sync_publisher_images.py --days 14       a wider recent window
  sync_publisher_images.py --backfill      every daily and weekly file (restartable;
                                           bounded by --max-images / --time-budget)
  sync_publisher_images.py --dry-run       report only; write nothing
"""
from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import io
import json
import os
import re
import sys
import tempfile
import time
import warnings
from datetime import datetime, timedelta, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlsplit
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).resolve().parent))
import safe_fetch  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
ASSETS = ROOT / "assets"
IMG_DIR = ASSETS / "img"           # optimized images only; nothing else lives here
MANIFEST = Path(__file__).resolve().parent / "image_manifest.json"
POLICY = Path(__file__).resolve().parent / "image_policy.json"
SECTIONS = ("topStories", "alsoWorthKnowing", "newTools")

MAX_HTML_BYTES = 650_000
MAX_IMAGE_BYTES = 8_000_000
MAX_PIXELS = 40_000_000           # decompression-bomb guard (checked before decoding)
MAX_SIDE = 600                    # stored master fits 600x600; Hugo builds smaller srcset sizes
MIN_WIDTH, MIN_HEIGHT = 200, 100  # smaller images are icons/tracking pixels
OUTPUT_CAP = 50_000               # bytes per stored file (raster or SVG)
MIN_QUALITY, QUALITY_STEP = 60, 5 # per-image WebP quality search range
CAP_MIN_QUALITY = 40              # floor when stepping down to fit OUTPUT_CAP
PHOTO_MAX_QUALITY = 80
GRAPHIC_MAX_QUALITY = 90
SSIM_MEAN, SSIM_WORST = 0.99, 0.95  # "looks the same": average and worst-1% block similarity
SVG_MAX_BYTES = 300_000           # input limit; the sanitized output must fit OUTPUT_CAP
RETRY_AFTER = timedelta(days=3)
MAX_ATTEMPTS = 3
WARN_TOTAL = 300 * 1024 * 1024
HARD_TOTAL = 750 * 1024 * 1024
ACCEPTED_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif", "image/avif", "image/svg+xml",
                  "application/octet-stream", "binary/octet-stream", ""}
ACCEPTED_FORMATS = {"JPEG", "MPO", "PNG", "WEBP", "GIF", "AVIF"}
GRAPHIC_FORMATS = {"PNG", "GIF"}
META_PRIORITY = ("og:image:secure_url", "og:image", "twitter:image", "twitter:image:src", "image_src")


# --------------------------------------------------------------------------- helpers

def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def iso(moment: datetime) -> str:
    return moment.strftime("%Y-%m-%dT%H:%M:%SZ")


def public_url(candidate) -> bool:
    try:
        url = urlsplit(str(candidate))
        return url.scheme in ("http", "https") and bool(url.hostname) and not (url.username or url.password)
    except (TypeError, ValueError):
        return False


def host_of(url) -> str:
    try:
        return (urlsplit(str(url)).hostname or "").lower()
    except ValueError:
        return ""


def load_policy() -> list[str]:
    try:
        return [h.lower().lstrip(".") for h in json.loads(POLICY.read_text("utf8")).get("blockedHosts", [])]
    except (OSError, ValueError):
        return []


def blocked_by_policy(urls, blocked) -> str | None:
    for url in urls:
        host = host_of(url)
        for suffix in blocked:
            if host == suffix or host.endswith("." + suffix):
                return f"publisher policy ({suffix})"
    return None


def noimageindex(value: str | None) -> bool:
    tokens = {t.strip().lower() for t in re.split(r"[,\s]+", value or "")}
    return bool(tokens & {"noimageindex", "none"})


# --------------------------------------------------------------------------- discovery

class PageMetadata(HTMLParser):
    def __init__(self):
        super().__init__()
        self.candidates: list[tuple[str, str]] = []
        self.noimageindex = False

    def handle_starttag(self, tag, attrs):
        d = {k.lower(): (v or "") for k, v in attrs}
        if tag == "meta":
            key = (d.get("property") or d.get("name") or "").lower()
            if key in META_PRIORITY and d.get("content"):
                self.candidates.append((key, d["content"]))
            if key in ("robots", "googlebot") and noimageindex(d.get("content")):
                self.noimageindex = True
        elif tag == "link" and "image_src" in d.get("rel", "").lower().split() and d.get("href"):
            self.candidates.append(("image_src", d["href"]))


def best_candidate(page_url: str, candidates) -> str | None:
    for _, raw in sorted(candidates, key=lambda c: META_PRIORITY.index(c[0])):
        raw = raw.strip()
        if not raw or re.search(r"[\s<>\"']", raw):
            continue  # unfilled template placeholders such as "<link or path of image>"
        image = urljoin(page_url, raw)
        if not public_url(image):
            continue
        path = urlsplit(image).path.lower()
        if path.endswith((".ico", ".pdf", ".gif")):
            continue
        if re.search(r"(?i)(favicon|(?:^|[-_/])logo(?:[-_.0-9]|$)|avatar|pixel|tracking)", path):
            continue
        return image
    return None


def inspect_page(url: str) -> dict:
    """Fetch an article page and report its preferred OG image and image-indexing policy."""
    if not public_url(url) or urlsplit(url).path.lower().endswith((".pdf", ".zip", ".json", ".md")):
        return {"status": "skipped", "reason": "not an HTML article URL"}
    try:
        resp = safe_fetch.fetch(url, max_bytes=MAX_HTML_BYTES, accept="text/html,application/xhtml+xml",
                                headers={"Accept-Language": "en-US,en;q=0.8"}, truncate=True)
    except safe_fetch.FetchError as exc:
        return {"status": "failed", "reason": str(exc)[:200]}
    if "html" not in resp.content_type:
        return {"status": "skipped", "reason": f"not HTML ({resp.content_type or 'unknown'})"}
    parser = PageMetadata()
    try:
        parser.feed(resp.body.decode(resp.charset(), "replace"))
    except (LookupError, AssertionError):
        parser.feed(resp.body.decode("utf-8", "replace"))
    blocked = parser.noimageindex or noimageindex(resp.headers.get("x-robots-tag"))
    return {"status": "ok", "image": None if blocked else best_candidate(resp.url, parser.candidates),
            "noimageindex": blocked}


# --------------------------------------------------------------------------- processing

class ImageRejected(Exception):
    pass


def _to_srgb(im):
    from PIL import ImageCms
    icc = im.info.get("icc_profile")
    if not icc:
        return im
    try:
        src = ImageCms.ImageCmsProfile(io.BytesIO(icc))
        dst = ImageCms.createProfile("sRGB")
        mode = "RGBA" if "A" in im.mode else "RGB"
        if im.mode not in ("RGB", "RGBA", "CMYK"):
            im = im.convert(mode)
        return ImageCms.profileToProfile(im, src, dst, outputMode=mode)
    except (ImageCms.PyCMSError, OSError, ValueError):
        return im


def similarity(reference, candidate) -> tuple[float, float]:
    """Structural similarity (SSIM) of luminance over 8x8 blocks.

    Returns (mean, 1st percentile). The percentile catches local damage, such as
    smeared text, that a good average would hide.
    """
    import numpy as np

    def luma(im):
        return np.asarray(im.convert("L"), dtype=np.float64)

    a, b = luma(reference), luma(candidate)
    k = 8
    h, w = (a.shape[0] // k) * k, (a.shape[1] // k) * k
    a = a[:h, :w].reshape(h // k, k, w // k, k)
    b = b[:h, :w].reshape(h // k, k, w // k, k)
    ma, mb = a.mean((1, 3)), b.mean((1, 3))
    va, vb = a.var((1, 3)), b.var((1, 3))
    cov = ((a - ma[:, None, :, None]) * (b - mb[:, None, :, None])).mean((1, 3))
    c1, c2 = (0.01 * 255) ** 2, (0.03 * 255) ** 2
    ssim = ((2 * ma * mb + c1) * (2 * cov + c2)) / ((ma ** 2 + mb ** 2 + c1) * (va + vb + c2))
    return float(ssim.mean()), float(np.percentile(ssim, 1))


def optimize(data: bytes) -> dict:
    """Validate and convert raster image bytes to optimized WebP. Raises ImageRejected."""
    from PIL import Image, ImageOps, UnidentifiedImageError

    Image.MAX_IMAGE_PIXELS = MAX_PIXELS
    with warnings.catch_warnings():
        warnings.simplefilter("error", Image.DecompressionBombWarning)
        try:
            im = Image.open(io.BytesIO(data))
            fmt = im.format
            width, height = im.size
            if fmt not in ACCEPTED_FORMATS:
                raise ImageRejected(f"unsupported format {fmt}")
            if width * height > MAX_PIXELS:
                raise ImageRejected(f"too many pixels ({width}x{height})")
            if width < MIN_WIDTH or height < MIN_HEIGHT:
                raise ImageRejected(f"too small ({width}x{height})")
            frames = getattr(im, "n_frames", 1)
            im.seek(0)
            im.load()
        except ImageRejected:
            raise
        except (UnidentifiedImageError, Image.DecompressionBombError, Image.DecompressionBombWarning,
                OSError, ValueError, SyntaxError, EOFError) as exc:
            raise ImageRejected(f"undecodable image ({type(exc).__name__})") from None

    im = ImageOps.exif_transpose(im)
    im = _to_srgb(im)
    has_alpha = im.mode in ("RGBA", "LA", "PA") or (im.mode == "P" and "transparency" in im.info)
    im = im.convert("RGBA" if has_alpha else "RGB")
    if has_alpha and im.getchannel("A").getextrema() == (255, 255):
        im = im.convert("RGB")  # fully opaque: drop the useless alpha channel
        has_alpha = False
    im.info = {}  # never carry EXIF/ICC/XMP into the output
    im.thumbnail((MAX_SIDE, MAX_SIDE), Image.Resampling.LANCZOS)  # never upscales

    def encode(method=6, **options) -> bytes:
        buf = io.BytesIO()
        im.save(buf, "WEBP", method=method, **options)
        return buf.getvalue()

    # Graphics (screenshots, diagrams, text) get a higher quality ceiling than photos.
    graphic = fmt in GRAPHIC_FORMATS or im.getcolors(maxcolors=256) is not None
    ceiling = GRAPHIC_MAX_QUALITY if graphic else PHOTO_MAX_QUALITY

    # Per-image quality: the lowest quality that still looks the same as the resized
    # original. Busy images need more; flat ones compress far below the ceiling.
    # The search uses the faster encoder effort; the final file uses the slowest/best.
    quality = ceiling
    for candidate in range(MIN_QUALITY, ceiling + 1, QUALITY_STEP):
        trial = Image.open(io.BytesIO(encode(method=4, quality=candidate, exact=has_alpha)))
        mean, worst = similarity(im, trial)
        if mean >= SSIM_MEAN and worst >= SSIM_WORST:
            quality = candidate
            break
    chosen = (encode(quality=quality, exact=has_alpha), f"q{quality}")
    if graphic:
        lossless = encode(lossless=True, quality=100)
        if len(lossless) <= 1.1 * len(chosen[0]):
            chosen = (lossless, "lossless")  # exact pixels for about the same size
    if len(chosen[0]) > OUTPUT_CAP:
        start = min(ceiling, int(chosen[1][1:]) if chosen[1].startswith("q") else ceiling) - QUALITY_STEP
        for quality in range(start, CAP_MIN_QUALITY - 1, -QUALITY_STEP):
            out = encode(quality=quality, exact=has_alpha)
            if len(out) <= OUTPUT_CAP:
                chosen = (out, f"q{quality}")
                break
        else:
            raise ImageRejected(f"still over {OUTPUT_CAP} bytes after compression")
    return {"bytes": chosen[0], "width": im.width, "height": im.height, "format": fmt,
            "frames": frames, "encoding": chosen[1], "alpha": has_alpha, "ext": "webp"}


# SVG is kept as vector art, but only a sanitized subset: an SVG opened directly runs
# scripts in this site's origin (shared by every mawburn.github.io project).
SVG_NS = "http://www.w3.org/2000/svg"
XLINK_NS = "http://www.w3.org/1999/xlink"
SVG_ELEMENTS = {
    "svg", "g", "defs", "symbol", "use", "title", "desc", "path", "rect", "circle", "ellipse",
    "line", "polyline", "polygon", "text", "tspan", "textPath", "linearGradient", "radialGradient",
    "stop", "clipPath", "mask", "pattern", "marker", "style", "filter", "feGaussianBlur", "feOffset",
    "feBlend", "feColorMatrix", "feComposite", "feFlood", "feMerge", "feMergeNode", "feMorphology",
}
UNSAFE_CSS = re.compile(r"(?i)@import|expression\s*\(|javascript:|url\(\s*['\"]?(?!#)")


def _svg_length(value) -> float | None:
    match = re.fullmatch(r"\s*([0-9]*\.?[0-9]+)\s*(px)?\s*", value or "")
    return float(match.group(1)) if match else None


def sanitize_svg(data: bytes) -> dict:
    """Return {bytes, width, height} for a safe copy of an SVG. Raises ImageRejected."""
    import xml.etree.ElementTree as ET

    if len(data) > SVG_MAX_BYTES:
        raise ImageRejected(f"SVG larger than {SVG_MAX_BYTES} bytes")
    if re.search(rb"(?i)<!(DOCTYPE|ENTITY)", data):
        raise ImageRejected("SVG with DOCTYPE/ENTITY declarations")
    try:
        root = ET.fromstring(data)
    except ET.ParseError as exc:
        raise ImageRejected(f"malformed SVG ({exc})") from None
    if root.tag != f"{{{SVG_NS}}}svg":
        raise ImageRejected("not an SVG document")

    def local(name):
        ns, _, tag = name.rpartition("}")
        return ns.lstrip("{"), tag

    def clean(element):
        for child in list(element):
            ns, tag = local(child.tag) if isinstance(child.tag, str) else ("", "")
            if ns != SVG_NS or tag not in SVG_ELEMENTS:
                element.remove(child)  # scripts, foreignObject, images, metadata, editor data
                continue
            if tag == "style" and UNSAFE_CSS.search(child.text or ""):
                element.remove(child)
                continue
            clean(child)
        for name in list(element.attrib):
            ns, attr = local(name)
            value = element.attrib[name]
            href = attr == "href" and ns in ("", XLINK_NS)
            if (ns not in ("", XLINK_NS) or attr.lower().startswith("on")
                    or (href and not value.startswith("#"))
                    or (not href and ns == XLINK_NS)
                    or UNSAFE_CSS.search(value)):
                del element.attrib[name]

    clean(root)
    width, height = _svg_length(root.get("width")), _svg_length(root.get("height"))
    box = [float(n) for n in re.findall(r"-?[0-9]*\.?[0-9]+", root.get("viewBox", ""))]
    if not (width and height) and len(box) == 4:
        width, height = box[2], box[3]
    if not (width and height) or width <= 0 or height <= 0:
        raise ImageRejected("SVG without usable width/height or viewBox")
    if not root.get("viewBox"):
        root.set("viewBox", f"0 0 {width:g} {height:g}")  # lets the image scale cleanly
    ET.register_namespace("", SVG_NS)
    ET.register_namespace("xlink", XLINK_NS)
    out = ET.tostring(root, encoding="utf-8", xml_declaration=False)
    if len(out) > OUTPUT_CAP:
        raise ImageRejected(f"sanitized SVG larger than {OUTPUT_CAP} bytes")
    return {"bytes": out, "width": round(width), "height": round(height), "format": "SVG",
            "frames": 1, "encoding": "svg-sanitized", "alpha": True, "ext": "svg"}


def looks_like_svg(resp_type: str, data: bytes) -> bool:
    head = data[:1024].lstrip().lower()
    return resp_type == "image/svg+xml" or (head.startswith((b"<?xml", b"<svg")) and b"<svg" in data[:4096].lower())


def store(data: bytes, result: dict) -> dict:
    digest = hashlib.sha256(data).hexdigest()
    rel = f"img/{digest[:20]}.{result['ext']}"
    path = ASSETS / rel
    if not path.exists():  # dedupe: identical source bytes share one file
        path.parent.mkdir(parents=True, exist_ok=True)
        # Unique temp name: parallel downloads of identical bytes may store the same file.
        fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=".", suffix=".tmp")
        with os.fdopen(fd, "wb") as fh:
            fh.write(result["bytes"])
        os.replace(tmp, path)
    return {"file": rel, "sha256": digest, "width": result["width"], "height": result["height"],
            "bytes": path.stat().st_size, "sourceBytes": len(data), "sourceFormat": result["format"],
            "encoding": result["encoding"], **({"frames": result["frames"]} if result["frames"] > 1 else {})}


def download_and_store(url: str) -> dict:
    """Returns a manifest entry (status ok/failed/skipped) for one image URL."""
    try:
        resp = safe_fetch.fetch(url, max_bytes=MAX_IMAGE_BYTES,
                                accept="image/avif,image/webp,image/png,image/jpeg,image/gif,image/svg+xml;q=0.9,*/*;q=0.1")
    except safe_fetch.FetchError as exc:
        return {"status": "failed", "reason": str(exc)[:200]}
    if noimageindex(resp.headers.get("x-robots-tag")):
        return {"status": "skipped", "reason": "X-Robots-Tag noimageindex"}
    if resp.content_type not in ACCEPTED_TYPES:
        return {"status": "skipped", "reason": f"unsupported content type {resp.content_type}"}
    try:
        result = sanitize_svg(resp.body) if looks_like_svg(resp.content_type, resp.body) else optimize(resp.body)
    except ImageRejected as exc:
        return {"status": "skipped", "reason": str(exc)}
    return {"status": "ok", **store(resp.body, result)}


# --------------------------------------------------------------------------- manifest

class Manifest:
    def __init__(self, path: Path):
        self.path = path
        try:
            raw = json.loads(path.read_text("utf8"))
        except (OSError, ValueError):
            raw = {}
        self.images: dict = raw.get("images", {})
        self.pages: dict = raw.get("pages", {})
        self._original = self.dump()

    def dump(self) -> str:
        return json.dumps({"version": 1, "images": self.images, "pages": self.pages},
                          indent=2, sort_keys=True, ensure_ascii=False) + "\n"

    def save(self) -> bool:
        text = self.dump()
        if text == self._original:
            return False
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(text, "utf8")
        self._original = text
        return True

    @staticmethod
    def due(entry: dict | None, moment: datetime) -> bool:
        """Whether a URL should be (re)tried now."""
        if not entry:
            return True
        status = entry.get("status")
        if status == "ok":
            return entry.get("file") is not None and not (ASSETS / entry["file"]).exists()
        if status == "skipped":
            return False
        if int(entry.get("attempts", 0)) >= MAX_ATTEMPTS:
            return False
        try:
            last = datetime.strptime(entry.get("lastAttempt", ""), "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        except ValueError:
            return True
        return moment - last >= RETRY_AFTER

    @staticmethod
    def record(table: dict, key: str, outcome: dict, moment: datetime) -> None:
        previous = table.get(key) or {}
        entry = dict(outcome)
        entry["attempts"] = int(previous.get("attempts", 0)) + 1 if outcome["status"] == "failed" else 1
        entry["lastAttempt"] = iso(moment)
        table[key] = entry


# --------------------------------------------------------------------------- documents

def pacific_today():
    return datetime.now(ZoneInfo("America/Los_Angeles")).date()


def load_documents(days: int | None) -> list[tuple[Path, dict, str]]:
    """Dated publication files in scope, newest first. Unparseable files are skipped, never rewritten."""
    today = pacific_today()
    oldest = (today - timedelta(days=days - 1)).isoformat() if days else "0000-00-00"
    docs = []
    for kind in ("daily", "weekly"):
        for path in sorted((DATA / kind).glob("*.json"), reverse=True):
            if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", path.stem) or not oldest <= path.stem <= today.isoformat():
                continue
            try:
                doc = json.loads(path.read_text("utf8"))
            except (OSError, ValueError) as exc:
                shown = path.relative_to(ROOT) if path.is_relative_to(ROOT) else path
                print(f"::warning file={shown}::skipped unparseable file ({exc})")
                continue
            if isinstance(doc, dict):
                docs.append((path, doc, kind))
    docs.sort(key=lambda d: d[0].stem, reverse=True)
    return docs


def holders(doc: dict, kind: str):
    """Story (daily) or theme (weekly) dicts that may carry an image."""
    lists = [doc.get(k) for k in SECTIONS] if kind == "daily" else [doc.get("themes")]
    for items in lists:
        for item in items if isinstance(items, list) else []:
            if isinstance(item, dict):
                yield item


def stored_files() -> list[Path]:
    return [p for p in IMG_DIR.glob("*") if p.suffix in (".webp", ".svg")] if IMG_DIR.exists() else []


def stored_bytes() -> int:
    return sum(p.stat().st_size for p in stored_files())


def has_image_url(item: dict) -> bool:
    return isinstance(item.get("image"), dict) and public_url(item["image"].get("url"))


# --------------------------------------------------------------------------- run

def run(args) -> dict:
    moment = now_utc()
    deadline = time.monotonic() + args.time_budget
    manifest = Manifest(MANIFEST)
    blocked_hosts = load_policy()
    docs = load_documents(None if args.backfill else args.days)
    original = {path: json.dumps(doc, ensure_ascii=False, indent=2) + "\n" for path, doc, _ in docs}
    stats = {"files": len(docs), "discovered": 0, "downloaded": 0, "reused": 0, "failed": 0,
             "skipped": 0, "annotated": 0, "deferred": 0, "budget_exhausted": False}

    # 1. Discovery for daily stories without an image.
    wanted: dict[int, tuple[dict, list[str]]] = {}
    for _, doc, kind in docs:
        if kind != "daily":
            continue
        for story in holders(doc, kind):
            if has_image_url(story):
                continue
            urls = [s.get("url") for s in story.get("sources", []) if isinstance(s, dict) and public_url(s.get("url"))][:2]
            if urls:
                wanted[id(story)] = (story, urls)
    pages_to_fetch = sorted({u for _, urls in wanted.values() for u in urls if Manifest.due(manifest.pages.get(u), moment)})
    if args.max_pages is not None:
        pages_to_fetch = pages_to_fetch[: args.max_pages]
    print(f"Discovery: {len(wanted)} stories without images, fetching {len(pages_to_fetch)} article pages")
    if pages_to_fetch and not args.dry_run:
        with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
            for url, outcome in zip(pages_to_fetch, pool.map(inspect_page, pages_to_fetch)):
                Manifest.record(manifest.pages, url, outcome, moment)
    for story, urls in wanted.values():
        for url in urls:
            page = manifest.pages.get(url) or {}
            if page.get("status") == "ok" and page.get("image"):
                credit = host_of(url).removeprefix("www.") or "publisher"
                story["image"] = {"url": page["image"], "alt": "Publisher-provided image for " + str(story.get("title", "article")),
                                  "credit": credit, "sourceUrl": url}
                stats["discovered"] += 1
                break

    # 2. Localization.
    total = stored_bytes()
    items = [item for _, doc, kind in docs for item in holders(doc, kind) if has_image_url(item)]
    queue: list[str] = []
    for item in items:
        image = item["image"]
        url = image["url"]
        entry = manifest.images.get(url)
        if entry and (entry.get("status") == "skipped"
                      or (entry.get("status") == "ok" and (ASSETS / entry["file"]).exists())):
            continue
        reason = blocked_by_policy([url, image.get("sourceUrl")], blocked_hosts)
        if url.startswith("data:"):
            reason = "inline data URI"
        source = image.get("sourceUrl")
        if not reason and public_url(source):
            page = manifest.pages.get(source)
            if Manifest.due(page, moment) and not args.dry_run and source not in pages_to_fetch:
                page = inspect_page(source)
                Manifest.record(manifest.pages, source, page, moment)
            if (page or {}).get("noimageindex"):
                reason = "article marked noimageindex"
        if reason:
            if not args.dry_run and (entry or {}).get("reason") != reason:
                Manifest.record(manifest.images, url, {"status": "skipped", "reason": reason}, moment)
            continue
        if Manifest.due(entry, moment) and url not in queue:
            queue.append(url)

    if total >= HARD_TOTAL:
        print(f"::warning::assets/img is {total / 2**20:.0f} MB (hard cap {HARD_TOTAL / 2**20:.0f} MB); not adding images")
        stats["deferred"] = len(queue)
        queue = []
    if len(queue) > args.max_images:
        stats["deferred"] += len(queue) - args.max_images
        stats["budget_exhausted"] = True
        queue = queue[: args.max_images]
    print(f"Localization: {len(items)} images in scope, {len(queue)} to download")

    def task(url):
        if time.monotonic() > deadline:
            return url, None
        return url, download_and_store(url)

    if queue and not args.dry_run:
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
            for url, outcome in pool.map(task, queue):
                if outcome is None:
                    stats["deferred"] += 1
                    stats["budget_exhausted"] = True
                    continue
                Manifest.record(manifest.images, url, outcome, moment)
                stats[{"ok": "downloaded", "failed": "failed", "skipped": "skipped"}[outcome["status"]]] += 1
                if outcome["status"] != "ok":
                    print(f"  {outcome['status']}: {url[:120]} — {outcome.get('reason')}")

    # 3. Annotate JSON with local references (also re-applies them if the scheduler rewrote a file).
    for item in items:
        image = item["image"]
        entry = manifest.images.get(image["url"]) or {}
        if entry.get("status") != "ok" or not (ASSETS / entry["file"]).exists():
            if image.get("local") and not (ASSETS / image["local"]).exists():
                for key in ("local", "width", "height", "sha256"):  # stale reference: keep JSON valid
                    image.pop(key, None)
                stats["annotated"] += 1
            continue
        update = {"local": entry["file"], "width": entry["width"], "height": entry["height"], "sha256": entry["sha256"]}
        if any(image.get(k) != v for k, v in update.items()):
            image.update(update)
            stats["annotated"] += 1

    changed = []
    if not args.dry_run:
        for path, doc, _ in docs:
            text = json.dumps(doc, ensure_ascii=False, indent=2) + "\n"
            if text != original[path]:
                path.write_text(text, "utf8")
                changed.append(path)
        manifest_changed = manifest.save()
    else:
        manifest_changed = False

    total = stored_bytes()
    files = len(stored_files())
    stats.update(changed_files=len(changed), manifest_changed=manifest_changed, stored_files=files, stored_mb=round(total / 2**20, 1))
    report(stats, total)
    return stats


def report(stats: dict, total: int) -> None:
    line = ("Images: {discovered} discovered, {downloaded} downloaded, {skipped} skipped, {failed} failed, "
            "{deferred} deferred, {annotated} JSON references updated in {changed_files} files; "
            "assets/img holds {stored_files} files ({stored_mb} MB)").format(**stats)
    print(line)
    if total >= WARN_TOTAL:
        print(f"::warning::assets/img is {total / 2**20:.0f} MB; review image retention before it reaches {HARD_TOTAL / 2**20:.0f} MB")
    if stats["budget_exhausted"]:
        print("Budget reached; run again to continue (already stored images are not fetched again).")
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf8") as fh:
            fh.write("### Publisher images\n\n" + line + "\n\n")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--days", type=int, default=7, help="recent Pacific days to process (default 7)")
    parser.add_argument("--backfill", action="store_true", help="process every daily and weekly file")
    parser.add_argument("--max-images", type=int, default=None, help="maximum image downloads this run")
    parser.add_argument("--max-pages", type=int, default=None, help="maximum article pages fetched for discovery")
    parser.add_argument("--time-budget", type=float, default=None, help="seconds before deferring remaining downloads")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    if args.max_images is None:
        args.max_images = 150 if args.backfill else 60
    if args.time_budget is None:
        args.time_budget = 1200 if args.backfill else 420
    run(args)


if __name__ == "__main__":
    main()
