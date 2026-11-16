#!/usr/bin/env python3
"""Attach remote publisher-provided og:image / twitter:image URLs to feed stories.

No stock art, generated art, or copied/rehosted images. Publisher pages are
queried only for metadata; a missing or blocked image leaves the story text-only.
"""
import concurrent.futures
import json
import re
import urllib.error
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DAILY_DIR = ROOT / "data" / "daily"
MAX_HTML = 650_000
TIMEOUT = 9
HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; mawburn-feed/1.0; +https://mawburn.github.io/tech-feed/)",
    "Accept": "text/html,application/xhtml+xml",
    "Accept-Language": "en-US,en;q=0.8",
}

def public_url(candidate):
    try:
        url = urllib.parse.urlsplit(candidate)
        return url.scheme in ("http", "https") and bool(url.netloc) and not (url.username or url.password) and url.hostname not in ("localhost", "127.0.0.1", "::1")
    except (TypeError, ValueError):
        return False

class ImageMetadata(HTMLParser):
    def __init__(self):
        super().__init__()
        self.candidates = []
    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if tag == "meta":
            key = (d.get("property") or d.get("name") or "").lower()
            if key in ("og:image:secure_url", "og:image", "twitter:image", "twitter:image:src"):
                if d.get("content"): self.candidates.append((key, d["content"]))
        elif tag == "link" and "image_src" in (d.get("rel") or ""):
            if d.get("href"): self.candidates.append(("image_src", d["href"]))

def image_for_source(url):
    if not public_url(url) or urllib.parse.urlsplit(url).path.lower().endswith((".pdf", ".zip", ".json", ".md")):
        return None
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            if "html" not in (resp.headers.get("Content-Type") or "").lower():
                return None
            body = resp.read(MAX_HTML)
            charset = resp.headers.get_content_charset() or "utf-8"
            html = body.decode(charset, "replace")
        parser = ImageMetadata()
        parser.feed(html)
        for _, candidate in sorted(parser.candidates, key=lambda t: ("og:image:secure_url", "og:image", "twitter:image", "twitter:image:src", "image_src").index(t[0])):
            image = urllib.parse.urljoin(url, candidate.strip())
            if not public_url(image): continue
            path = urllib.parse.urlsplit(image).path.lower()
            if path.endswith((".svg", ".ico", ".pdf", ".gif")): continue
            if re.search(r"(?i)(favicon|(?:^|[-_/])logo(?:[-_.0-9]|$)|avatar|pixel|tracking)", path): continue
            return image
    except (urllib.error.URLError, TimeoutError, OSError, ValueError, UnicodeError):
        pass
    return None

def run():
    today = datetime.now(ZoneInfo("America/Los_Angeles")).date()
    oldest = (today - timedelta(days=6)).isoformat()
    latest = today.isoformat()
    files = sorted(p for p in DAILY_DIR.glob("*.json") if oldest <= p.stem <= latest)
    documents = [(path, json.loads(path.read_text(encoding="utf8"))) for path in files]

    # Only enrich the active seven-day archive; don't revisit years of history.
    stories = []
    story_file = {}
    for path, issue in documents:
        for key in ("topStories", "alsoWorthKnowing", "newTools"):
            for story in issue.get(key, []):
                stories.append(story)
                story_file[id(story)] = path

    candidates = {}
    for story in stories:
        if isinstance(story.get("image"), dict) and public_url(story["image"].get("url")):
            continue
        urls = [s.get("url") for s in story.get("sources", []) if public_url(s.get("url"))]
        if urls:
            candidates[id(story)] = urls[:2]

    distinct = sorted(set(url for urls in candidates.values() for url in urls))
    print(f"Checking publisher metadata for {len(candidates)} stories, {len(distinct)} distinct source URLs")
    with concurrent.futures.ThreadPoolExecutor(max_workers=7) as pool:
        answers = dict(zip(distinct, pool.map(image_for_source, distinct)))

    changed_paths = set()
    count = 0
    for story in stories:
        for url in candidates.get(id(story), []):
            if answers.get(url):
                domain = urllib.parse.urlsplit(url).hostname or "publisher"
                story["image"] = {
                    "url": answers[url],
                    "alt": "Publisher-provided image for " + story.get("title", "article"),
                    "credit": domain.removeprefix("www."),
                    "sourceUrl": url,
                }
                changed_paths.add(story_file[id(story)])
                count += 1
                break
    for path, data in documents:
        if path in changed_paths:
            path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf8")
    print(f"Added {count} publisher OG images to {len(changed_paths)} dated JSON files")
 
if __name__ == "__main__":
    run()
