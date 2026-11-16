"""Tests for the publisher image pipeline (scripts/safe_fetch.py, scripts/sync_publisher_images.py).

Runs entirely offline against a local HTTP fixture server:
    python3 -m unittest discover -s tests -p 'test_*.py'
Requires Pillow (scripts/requirements.txt).
"""
import io
import json
import shutil
import sys
import tempfile
import threading
import unittest
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from types import SimpleNamespace
from zoneinfo import ZoneInfo

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import safe_fetch  # noqa: E402
import sync_publisher_images as sync  # noqa: E402


def make_image(fmt="JPEG", size=(2400, 1260), mode="RGB", color=(30, 120, 200), **save):
    im = Image.new(mode, size, color)
    if mode == "RGB":  # add detail so lossy encoding is exercised
        for x in range(0, size[0], 40):
            for y in range(0, size[1], 40):
                im.putpixel((x, y), ((x * 7) % 255, (y * 3) % 255, 90))
    buf = io.BytesIO()
    im.save(buf, fmt, **save)
    return buf.getvalue()


def animated_gif():
    frames = [Image.new("RGB", (400, 300), c) for c in ((255, 0, 0), (0, 255, 0), (0, 0, 255))]
    buf = io.BytesIO()
    frames[0].save(buf, "GIF", save_all=True, append_images=frames[1:], duration=100, loop=0)
    return buf.getvalue()


class Fixture(BaseHTTPRequestHandler):
    routes: dict = {}
    hits: dict = {}

    def do_GET(self):
        Fixture.hits[self.path] = Fixture.hits.get(self.path, 0) + 1
        route = Fixture.routes.get(self.path)
        if route is None:
            self.send_response(404)
            self.end_headers()
            return
        status, headers, body = route
        self.send_response(status)
        for key, value in headers.items():
            self.send_header(key, value)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


class ServerTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), Fixture)
        cls.base = f"http://127.0.0.1:{cls.server.server_port}"
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()

    def setUp(self):
        Fixture.routes, Fixture.hits = {}, {}
        # Allow only the loopback fixture server; everything else keeps production rules.
        def allowed(address):
            return address == "127.0.0.1"
        allowed.allow_any_port = True
        self._original_allowed = safe_fetch.address_allowed
        safe_fetch.address_allowed = allowed

    def tearDown(self):
        safe_fetch.address_allowed = self._original_allowed

    def route(self, path, body, content_type="image/jpeg", status=200, headers=None):
        Fixture.routes[path] = (status, {"Content-Type": content_type, **(headers or {})}, body)
        return self.base + path


class OptimizeTests(unittest.TestCase):
    def test_jpeg_resized_lossy_and_metadata_stripped(self):
        exif = Image.Exif()
        exif[0x010F] = "CameraMaker"
        result = sync.optimize(make_image("JPEG", (2400, 1260), exif=exif.tobytes()))
        self.assertEqual((result["width"], result["height"]), (600, 315))
        self.assertTrue(result["encoding"].startswith("q"))
        out = Image.open(io.BytesIO(result["bytes"]))
        self.assertEqual(out.format, "WEBP")
        self.assertIsNone(out.info.get("exif"))
        self.assertIsNone(out.info.get("icc_profile"))
        self.assertLessEqual(len(result["bytes"]), sync.OUTPUT_CAP)

    def test_never_upscales(self):
        result = sync.optimize(make_image("JPEG", (480, 270)))
        self.assertEqual((result["width"], result["height"]), (480, 270))

    def test_png_transparency_preserved_losslessly(self):
        im = Image.new("RGBA", (800, 400), (255, 0, 0, 0))
        for x in range(200, 600):
            for y in range(100, 300):
                im.putpixel((x, y), (0, 0, 0, 255))
        buf = io.BytesIO()
        im.save(buf, "PNG")
        result = sync.optimize(buf.getvalue())
        out = Image.open(io.BytesIO(result["bytes"]))
        self.assertEqual(out.mode, "RGBA")
        self.assertEqual(out.getchannel("A").getextrema(), (0, 255))
        self.assertEqual(result["encoding"], "lossless")

    def test_animated_gif_uses_first_frame(self):
        result = sync.optimize(animated_gif())
        self.assertEqual(result["frames"], 3)
        self.assertEqual(Image.open(io.BytesIO(result["bytes"])).n_frames, 1)

    def test_quality_chosen_per_image_keeps_it_visually_identical(self):
        from PIL import Image as PILImage
        result = sync.optimize(make_image("JPEG", (1600, 900)))
        quality = int(result["encoding"][1:])
        self.assertLessEqual(quality, sync.PHOTO_MAX_QUALITY)
        reference = PILImage.open(io.BytesIO(make_image("JPEG", (1600, 900)))).convert("RGB")
        reference.thumbnail((sync.MAX_SIDE, sync.MAX_SIDE), PILImage.Resampling.LANCZOS)
        mean, worst = sync.similarity(reference, PILImage.open(io.BytesIO(result["bytes"])))
        if quality < sync.PHOTO_MAX_QUALITY:
            self.assertGreaterEqual(mean, sync.SSIM_MEAN - 0.002)
        # A flat graphic needs nowhere near the ceiling.
        flat = sync.optimize(make_image("PNG", (800, 400), color=(250, 250, 250)))
        self.assertTrue(flat["encoding"] == "lossless" or int(flat["encoding"][1:]) < sync.GRAPHIC_MAX_QUALITY)

    def test_rejects_decompression_bomb(self):
        buf = io.BytesIO()
        Image.new("1", (7000, 7000)).save(buf, "PNG")  # tiny file, 49 MP
        with self.assertRaises(sync.ImageRejected):
            sync.optimize(buf.getvalue())

    def test_rejects_svg_and_garbage_and_tiny(self):
        for data in (b'<svg xmlns="http://www.w3.org/2000/svg"/>', b"not an image", make_image("PNG", (32, 32))):
            with self.assertRaises(sync.ImageRejected):
                sync.optimize(data)


class SvgTests(unittest.TestCase):
    EVIL = b"""<?xml version="1.0"?>
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"
     xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape" viewBox="0 0 400 200" onload="alert(1)">
  <script>alert(2)</script>
  <metadata><rdf>x</rdf></metadata>
  <style>@import url(https://evil.example/x.css); .a{fill:red}</style>
  <defs><linearGradient id="g"><stop offset="0" stop-color="#fff"/></linearGradient></defs>
  <rect width="400" height="200" fill="url(#g)" inkscape:label="bg"/>
  <a href="javascript:alert(3)"><text x="10" y="20">link</text></a>
  <foreignObject><div xmlns="http://www.w3.org/1999/xhtml">html</div></foreignObject>
  <image href="https://tracker.example/p.png" width="1" height="1"/>
  <use xlink:href="https://evil.example/s.svg#x"/>
  <use xlink:href="#g"/>
  <circle r="5" style="fill:url(https://evil.example/f)" onclick="x()"/>
  <text x="10" y="40">Kept</text>
</svg>"""

    def test_sanitizer_keeps_drawing_and_strips_active_content(self):
        result = sync.sanitize_svg(self.EVIL)
        out = result["bytes"].decode()
        for bad in ("script", "alert", "onload", "onclick", "evil.example", "tracker.example",
                    "foreignObject", "javascript", "inkscape", "metadata", "@import", "<a"):
            self.assertNotIn(bad, out)
        for good in ("<rect", 'fill="url(#g)"', 'href="#g"', "Kept", "linearGradient"):
            self.assertIn(good, out)
        self.assertEqual((result["width"], result["height"]), (400, 200))

    def test_rejects_entities_and_non_svg(self):
        bomb = b'<?xml version="1.0"?><!DOCTYPE svg [<!ENTITY a "aaaa">]><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1 1">&a;</svg>'
        for data in (bomb, b"<html></html>", b"<svg>no namespace</svg>",
                     b'<svg xmlns="http://www.w3.org/2000/svg"><rect/></svg>'):
            with self.assertRaises(sync.ImageRejected):
                sync.sanitize_svg(data)


class SafeFetchTests(ServerTestCase):
    def test_production_rules_block_private_addresses(self):
        safe_fetch.address_allowed = safe_fetch._address_allowed
        for url in ("http://127.0.0.1/", "http://10.0.0.5/", "http://[::1]/", "http://169.254.169.254/latest"):
            with self.assertRaises(safe_fetch.FetchError):
                safe_fetch.fetch(url, max_bytes=1000)
        with self.assertRaises(safe_fetch.FetchError):
            safe_fetch.fetch("http://example.com:8080/", max_bytes=1000)
        with self.assertRaises(safe_fetch.FetchError):
            safe_fetch.fetch("ftp://example.com/x", max_bytes=1000)
        with self.assertRaises(safe_fetch.FetchError):
            safe_fetch.fetch("https://user:pw@example.com/", max_bytes=1000)

    def test_redirect_to_private_address_is_rejected(self):
        self.route("/hop", b"", status=302, headers={"Location": "http://10.1.2.3/secret"})
        with self.assertRaises(safe_fetch.FetchError):
            safe_fetch.fetch(self.base + "/hop", max_bytes=1000)

    def test_redirect_followed_and_oversized_rejected(self):
        url = self.route("/img", b"x" * 5000, "image/png")
        self.route("/go", b"", status=301, headers={"Location": "/img"})
        resp = safe_fetch.fetch(self.base + "/go", max_bytes=10_000)
        self.assertEqual(resp.url, url)
        with self.assertRaises(safe_fetch.FetchError):
            safe_fetch.fetch(url, max_bytes=1000)

    def test_wrong_mime_type_skipped(self):
        url = self.route("/page", b"<html></html>", "text/html")
        self.assertEqual(sync.download_and_store(url)["status"], "skipped")


class PipelineTests(ServerTestCase):
    def setUp(self):
        super().setUp()
        self.tmp = Path(tempfile.mkdtemp())
        self.saved = {k: getattr(sync, k) for k in ("DATA", "ASSETS", "IMG_DIR", "MANIFEST", "POLICY")}
        sync.DATA = self.tmp / "data"
        sync.ASSETS = self.tmp / "assets"
        sync.IMG_DIR = sync.ASSETS / "img"
        sync.MANIFEST = self.tmp / "image_manifest.json"
        sync.POLICY = self.tmp / "policy.json"
        sync.POLICY.write_text(json.dumps({"blockedHosts": ["blocked.example"]}))
        (sync.DATA / "daily").mkdir(parents=True)
        (sync.DATA / "weekly").mkdir(parents=True)
        self.today = datetime.now(ZoneInfo("America/Los_Angeles")).date().isoformat()

    def tearDown(self):
        for k, v in self.saved.items():
            setattr(sync, k, v)
        shutil.rmtree(self.tmp)
        super().tearDown()

    def args(self, **kw):
        base = dict(days=7, backfill=False, max_images=50, max_pages=None, time_budget=60, dry_run=False)
        base.update(kw)
        return SimpleNamespace(**base)

    def story(self, title, image=None, source="/article"):
        s = {"title": title, "category": "Security", "summary": "Summary.",
             "sources": [{"label": "Publisher", "url": self.base + source}]}
        if image:
            s["image"] = image
        return s

    def write_daily(self, stories):
        doc = {"date": self.today, "label": "Test", "overview": "Overview.", "marketPulse": "",
               "topStories": stories, "alsoWorthKnowing": [], "newTools": []}
        path = sync.DATA / "daily" / f"{self.today}.json"
        path.write_text(json.dumps(doc, indent=2) + "\n")
        return path

    def test_end_to_end_dedupe_idempotency_and_failures(self):
        photo = make_image("JPEG", (1600, 900))
        a = self.route("/a.jpg", photo)
        b = self.route("/b.jpg", photo)  # identical bytes, different URL
        missing = self.base + "/gone.jpg"
        self.route("/article", b'<html><head><meta property="og:image" content="/og.jpg"></head></html>', "text/html")
        self.route("/og.jpg", make_image("JPEG", (1200, 630), color=(200, 40, 40)))
        original_image = {"url": a, "alt": "Alt text", "credit": "example.org", "sourceUrl": self.base + "/article"}
        path = self.write_daily([
            self.story("One", dict(original_image)),
            self.story("Two", {"url": b, "alt": "B", "credit": "c", "sourceUrl": self.base + "/article"}),
            self.story("Three", {"url": missing, "alt": "Gone"}),
            self.story("Four (discovered)"),
            self.story("Blocked", {"url": "https://blocked.example/x.jpg"}),
        ])

        stats = sync.run(self.args())
        doc = json.loads(path.read_text())
        one, two, three, four, blocked = doc["topStories"]
        for key, value in original_image.items():
            self.assertEqual(one["image"][key], value)  # scheduler keys untouched
        self.assertEqual(one["image"]["local"], two["image"]["local"])  # deduplicated
        self.assertTrue((sync.ASSETS / one["image"]["local"]).exists())
        self.assertEqual((one["image"]["width"], one["image"]["height"]), (600, 338))
        self.assertNotIn("local", three["image"])
        self.assertIn("local", four["image"])
        self.assertEqual(four["image"]["sourceUrl"], self.base + "/article")
        self.assertNotIn("local", blocked["image"])
        self.assertEqual(len(list(sync.IMG_DIR.glob("*.webp"))), 2)
        manifest = json.loads(sync.MANIFEST.read_text())
        self.assertEqual(manifest["images"][missing]["status"], "failed")
        self.assertEqual(manifest["images"][missing]["attempts"], 1)
        self.assertEqual(manifest["images"]["https://blocked.example/x.jpg"]["status"], "skipped")
        self.assertEqual(stats["downloaded"], 3)

        # Second run: nothing fetched, nothing rewritten; the failure is inside its back-off.
        hits_before = dict(Fixture.hits)
        before = {p: p.read_bytes() for p in self.tmp.rglob("*") if p.is_file()}
        stats = sync.run(self.args())
        self.assertEqual(Fixture.hits, hits_before)
        self.assertEqual({p: p.read_bytes() for p in self.tmp.rglob("*") if p.is_file()}, before)
        self.assertEqual(stats["changed_files"], 0)
        self.assertFalse(stats["manifest_changed"])

    def test_reapplies_local_reference_after_scheduler_rewrite(self):
        url = self.route("/p.jpg", make_image("JPEG", (900, 500)))
        image = {"url": url, "alt": "x"}
        path = self.write_daily([self.story("Story", dict(image))])
        sync.run(self.args())
        self.write_daily([self.story("Story", dict(image))])  # scheduler rewrites without local fields
        hits = dict(Fixture.hits)
        sync.run(self.args())
        self.assertIn("local", json.loads(path.read_text())["topStories"][0]["image"])
        self.assertEqual(Fixture.hits, hits)

    def test_svg_stored_as_sanitized_vector(self):
        url = self.route("/logo.svg", SvgTests.EVIL, "image/svg+xml")
        path = self.write_daily([self.story("Vector", {"url": url})])
        sync.run(self.args())
        image = json.loads(path.read_text())["topStories"][0]["image"]
        self.assertTrue(image["local"].endswith(".svg"))
        self.assertEqual((image["width"], image["height"]), (400, 200))
        self.assertNotIn(b"script", (sync.ASSETS / image["local"]).read_bytes())

    def test_stale_local_reference_removed(self):
        image = {"url": self.base + "/gone.jpg", "local": "img/0123456789abcdef0123.webp",
                 "width": 1, "height": 1, "sha256": "a" * 64}
        path = self.write_daily([self.story("Stale", image)])
        sync.run(self.args())
        image = json.loads(path.read_text())["topStories"][0]["image"]
        self.assertEqual(image, {"url": self.base + "/gone.jpg"})

    def test_noimageindex_respected_and_weekly_themes_processed(self):
        self.route("/private-article", b'<meta name="robots" content="noimageindex">', "text/html")
        hidden = self.route("/hidden.jpg", make_image("JPEG", (800, 450)))
        shown = self.route("/shown.jpg", make_image("JPEG", (800, 450), color=(1, 2, 3)))
        week = {"weekEnding": self.today, "title": "T", "themes": [
            {"title": "A", "summary": "s", "image": {"url": hidden, "sourceUrl": self.base + "/private-article"}},
            {"title": "B", "summary": "s", "image": {"url": shown}}],
            "toolsToWatch": [], "sourceDays": []}
        path = sync.DATA / "weekly" / f"{self.today}.json"
        path.write_text(json.dumps(week))
        sync.run(self.args())
        themes = json.loads(path.read_text())["themes"]
        self.assertNotIn("local", themes[0]["image"])
        self.assertIn("local", themes[1]["image"])
        self.assertNotIn("/hidden.jpg", Fixture.hits)

    def test_unparseable_file_left_alone_and_budget_defers(self):
        bad = sync.DATA / "daily" / "2020-01-01.json"
        bad.write_text("{not json")
        urls = [self.route(f"/{i}.jpg", make_image("JPEG", (400, 300), color=(i, i, i))) for i in range(3)]
        self.write_daily([self.story(str(i), {"url": u}) for i, u in enumerate(urls)])
        stats = sync.run(self.args(backfill=True, max_images=2))
        self.assertEqual(stats["downloaded"], 2)
        self.assertTrue(stats["budget_exhausted"])
        stats = sync.run(self.args(backfill=True, max_images=2))  # restartable: picks up the rest
        self.assertEqual(stats["downloaded"], 1)
        self.assertEqual(bad.read_text(), "{not json")


if __name__ == "__main__":
    unittest.main()
