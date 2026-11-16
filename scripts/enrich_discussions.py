#!/usr/bin/env python3
"""Match existing daily stories to actual HN/Reddit discussion threads.

Run by GitHub Actions after the briefing is published. This is discussion
discovery only; it NEVER fabricates a 'discoveredVia' provenance record.

Inputs: data/daily/YYYY-MM-DD.json
Outputs: optional story.discussions entries with verified thread permalinks.
External sources: HN Algolia public search API, Reddit public RSS search.
Reddit RSS access can be blocked or restricted; failures are non-fatal.
"""
from __future__ import annotations
import argparse
import concurrent.futures
from datetime import date, datetime, timedelta, timezone
from difflib import SequenceMatcher
from functools import lru_cache
from html import unescape
import json
import re
import sys
from pathlib import Path
from urllib.parse import parse_qsl, quote, unquote, urlsplit, urlunsplit, urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from xml.etree import ElementTree as ET
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
FOLDER = ROOT / "data" / "daily"
HEADERS = {
    "User-Agent": "mawburn-tech-feed/1.1 (+https://mawburn.com; source-linked public news index)",
    "Accept": "application/json,application/atom+xml,application/rss+xml,text/xml;q=0.9,*/*;q=0.5",
}
HN_API = "https://hn.algolia.com/api/v1/search"
REDDIT_RSS = "https://www.reddit.com/search.rss"
REDDIT_ARCHIVE = "https://api.pullpush.io/reddit/search/submission/"
STOP = {
    "a","an","the","and","of","for","on","in","to","with","its",
    "from","into","out","as","at","is","are","was","were","by",
    "new","now","how","why","what","this","that","today",
    "company","announces","announced","launches","launched","introduces",
    "releases","released","report","reports","latest","more",
}
FAILED = {"hn": 0, "reddit": 0, "reddit_archive": 0}
SUCCESS = {"hn": 0, "reddit": 0, "reddit_archive": 0}

def normalize_url(value):
    try:
        url = urlsplit(str(value or "").strip())
        if url.scheme not in ("http","https") or not url.netloc:
            return ""
        host = (url.hostname or "").lower().removeprefix("www.").removeprefix("m.")
        path = re.sub(r"/+", "/", unquote(url.path)).rstrip("/").lower()
        return host + path
    except ValueError:
        return ""

def article_specific(url):
    """Exclude generic news indexes that are reused across unrelated stories."""
    try:
        parsed = urlsplit(url)
        path = unquote(parsed.path).strip("/").lower()
        parts = path.split("/") if path else []
        if not parts:
            return False
        if path in {"blog","news","newsroom","changelog","releases","models",
                    "products","announcements","ai","docs","press","research"}:
            return False
        if "month" in parts or "search" in parts or "tags" in parts:
            return False
        if len(parts) == 1 and not (len(parts[0]) >= 22 and "-" in parts[0]):
            return False
        if len(parts) == 2 and parts[-1] in {"blog","news","changelog","announcements"}:
            return False
        return True
    except (ValueError,TypeError):
        return False

def near_date(timestamp, issue_date):
    """Treat old community discussions as unrelated to this edition."""
    try:
        try:
            posted=datetime.fromtimestamp(int(timestamp),timezone.utc).date()
        except (ValueError,TypeError):
            posted=datetime.fromisoformat(str(timestamp).replace("Z","+00:00")).date()
        day=date.fromisoformat(issue_date)
        return day - timedelta(days=21) <= posted <= day + timedelta(days=3)
    except (ValueError,TypeError,OverflowError):
        return False

def tokens(value):
    words = re.findall(r"[a-z0-9]{2,}", unescape(str(value or "")).lower())
    return set(w for w in words if w not in STOP)

def overlap(a, b):
    x, y = tokens(a), tokens(b)
    if not x or not y:
        return 0.0
    intersection = len(x & y)
    if intersection < 3:
        return 0.0
    # Allow the original title to be shorter or longer than the brief title.
    return 0.7 * (intersection / min(len(x),len(y))) + 0.3 * (intersection / max(len(x),len(y)))

def best_query(title):
    words = [word for word in re.findall(r"[A-Za-z0-9]+", title) if len(word) >= 3 and word.lower() not in STOP]
    return " ".join(words[:7])

def get_bytes(url, kind, max_size=250_000):
    # Respect provider rate limits even after some earlier successful calls.
    if FAILED[kind] >= 6:
        return b""
    try:
        req = Request(url, headers=HEADERS)
        with urlopen(req, timeout=7) as response:
            if response.status != 200:
                return b""
            result = response.read(max_size)
        SUCCESS[kind] += 1
        return result
    except (HTTPError, URLError, TimeoutError, OSError) as exc:
        FAILED[kind] += 1
        if FAILED[kind] <= 3:
            print(f"{kind.upper()} endpoint unavailable ({type(exc).__name__}): {str(exc)[:100]}", file=sys.stderr)
        return b""

@lru_cache(maxsize=300)
def hn_search(query, restrict_url=False):
    if not query:
        return []
    options={"query":query,"tags":"story","hitsPerPage":"20"}
    if restrict_url:
        options["restrictSearchableAttributes"]="url"
    raw=get_bytes(HN_API+"?"+urlencode(options), "hn")
    if not raw:
        return []
    try:
        hits=json.loads(raw).get("hits", [])
        return hits if isinstance(hits,list) else []
    except (ValueError,TypeError):
        return []

def source_urls(story):
    return [s.get("url") for s in story.get("sources", []) if isinstance(s,dict) and normalize_url(s.get("url"))][:3]

def story_score(story, candidate_title, external_url):
    wanted=set(normalize_url(u) for u in source_urls(story) if article_specific(u))
    incoming=normalize_url(external_url)
    if incoming and incoming in wanted:
        return 1.0
    title_match=overlap(story.get("title",""),candidate_title)
    if title_match < .69:
        return 0.0
    # Title similarity alone needs a particularly strong match; otherwise
    # same-word stories (e.g. Nvidia earnings) link to unrelated events.
    return .80 * title_match if title_match >= .78 else 0.0

@lru_cache(maxsize=300)
def hn_item(item_id):
    raw=get_bytes("https://hn.algolia.com/api/v1/items/"+item_id,"hn")
    try:
        return json.loads(raw) if raw else None
    except (ValueError,TypeError):
        return None

def hn_eligible(story, hit, issue_date):
    if not near_date(hit.get("created_at_i") or hit.get("created_at"),issue_date):
        return 0
    if int(hit.get("num_comments") or 0) < 1 and not hit.get("children"):
        return 0
    return story_score(story,hit.get("title") or "",hit.get("url"))

def hn_match(story, issue_date):
    hits=[]
    for url in source_urls(story)[:2]:
        if article_specific(url):
            hits+=hn_search(url,True)
    hits+=hn_search(best_query(story.get("title","")))
    options=[]
    seen=set()
    for hit in hits:
        key=str(hit.get("objectID",""))
        if not key.isdecimal() or key in seen:
            continue
        seen.add(key)
        rating=hn_eligible(story,hit,issue_date)
        if rating:
            options.append((rating, min(int(hit.get("num_comments") or 0),300), key))
    if not options:
        return None
    options.sort(reverse=True)
    _, count, key=options[0]
    return {"platform":"Hacker News","url":"https://news.ycombinator.com/item?id="+key,"label":"HN discussion"}

def valid_prior_hn(story, link, issue_date):
    match=re.fullmatch(r"https://news\.ycombinator\.com/item\?id=(\d+)",str(link.get("url","")))
    if not match:
        return False
    hit=hn_item(match.group(1))
    if hit is None:
        return True  # Do not remove published data on an API outage.
    return bool(hn_eligible(story,hit,issue_date))

def parse_reddit_feed(raw):
    if not raw:
        return []
    try:
        root=ET.fromstring(raw)
    except ET.ParseError:
        return []
    entries=[]
    ns={"a":"http://www.w3.org/2005/Atom"}
    for entry in root.findall("a:entry",ns):
        title=entry.findtext("a:title","",ns)
        link=entry.find("a:link",ns)
        comments=link.attrib.get("href","") if link is not None else ""
        content=entry.findtext("a:content","",ns)
        if not content:
            content=entry.findtext("a:summary","",ns)
        # RSS may place an external article's URL in the escaped HTML content.
        external=[unescape(h) for h in re.findall(r'href=["\']([^"\']+)["\']',unescape(content),re.I)]
        published=entry.findtext("a:published","",ns) or entry.findtext("a:updated","",ns)
        entries.append((title,comments,external,published))
    return entries

@lru_cache(maxsize=300)
def reddit_search(query):
    if not query:
        return []
    args=urlencode({"q":query,"sort":"relevance","t":"month","limit":25})
    return parse_reddit_feed(get_bytes(REDDIT_RSS+"?"+args, "reddit",400_000))

@lru_cache(maxsize=300)
def reddit_archive_search(query):
    # Public archive index fallback when Reddit blocks RSS (403/429).
    # It may lag and can contain deleted posts, so only include strong matches.
    if not query:
        return []
    url=REDDIT_ARCHIVE+"?"+urlencode({"q":query,"size":30,"sort":"desc"})
    raw=get_bytes(url,"reddit_archive",550_000)
    if not raw:
        return []
    try:
        data=json.loads(raw).get("data",[])
        return data if isinstance(data,list) else []
    except (ValueError,TypeError):
        return []

def permalink_candidate(url):
    try:
        parsed=urlsplit(url)
        if parsed.netloc.lower() not in ("www.reddit.com","reddit.com","old.reddit.com"):
            return None
        match=re.search(r"^/r/([A-Za-z0-9_]+)/comments/([A-Za-z0-9]+)/",parsed.path,re.I)
        if not match:
            return None
        return "https://www.reddit.com"+parsed.path,match.group(1)
    except (ValueError,TypeError):
        return None

def reddit_match(story, issue_date):
    best=None
    query=best_query(story.get("title",""))
    for title,url,external,published in reddit_search(query):
        if not near_date(published,issue_date):
            continue
        match=permalink_candidate(url)
        if not match:
            continue
        score=max([story_score(story,title,target) for target in external] + [story_score(story,title,None)])
        if score < .65:
            continue
        permalink,subreddit=match
        candidate=(score,permalink,subreddit)
        if best is None or candidate[0] > best[0]:
            best=candidate
    if best is None:
        for post in reddit_archive_search(query):
            if not isinstance(post,dict) or not near_date(post.get("created_utc"),issue_date):
                continue
            external=post.get("url")
            title=post.get("title","")
            score=story_score(story,title,external)
            if score < .65:
                continue
            raw=post.get("permalink","")
            if raw.startswith("/"):
                raw="https://www.reddit.com"+raw
            match=permalink_candidate(raw)
            if not match:
                continue
            permalink,subreddit=match
            candidate=(score,permalink,subreddit)
            if best is None or candidate[0] > best[0]:
                best=candidate
    if not best:
        return None
    _,permalink,subreddit=best
    return {"platform":"Reddit","url":permalink,"label":"r/"+subreddit}

def safe_platforms(existing):
    return {str(item.get("platform","")).strip().lower() for item in existing if isinstance(item,dict)}

def enrich_story(issue_date, story):
    before=list(story.get("discussions") or [])
    kept=[]
    removed=0
    for link in before:
        # Re-check only links automatically added by this script. Explicit
        # editorial links are left intact.
        if (isinstance(link,dict) and link.get("platform")=="Hacker News"
                and link.get("label")=="HN discussion"
                and not valid_prior_hn(story,link,issue_date)):
            removed+=1
            continue
        kept.append(link)
    existing=safe_platforms(kept)
    changes=[]
    if "hacker news" not in existing:
        matched=hn_match(story,issue_date)
        if matched:
            changes.append(matched)
    if "reddit" not in existing:
        matched=reddit_match(story,issue_date)
        if matched:
            changes.append(matched)
    if changes or removed:
        if kept or changes:
            story["discussions"]=kept+changes
        else:
            story.pop("discussions",None)
    return {"added":changes,"removed":removed}

def run():
    parser=argparse.ArgumentParser()
    parser.add_argument("--self-test",action="store_true")
    parser.add_argument("--days",type=int,default=7)
    args=parser.parse_args()
    if args.self_test:
        assert normalize_url("https://www.example.com/Blog/Article/?utm_source=reddit") == "example.com/blog/article"
        assert overlap("LangChain raises $300m valuation", "LangChain raises funding at new valuation") > .5
        assert story_score({"title":"LangChain funding","sources":[{"url":"https://example.com/news/2026/langchain-raises-funds"}]},"LangChain","https://www.example.com/news/2026/langchain-raises-funds/") == 1.
        assert not article_specific("https://example.com/news")
        assert near_date("2026-11-12T08:00:00Z","2026-11-15")
        assert not near_date("2024-01-01T08:00:00Z","2026-11-15")
        assert permalink_candidate("https://www.reddit.com/r/programming/comments/abc123/thread/")
        assert story_score({"title":"Nvidia CEO transition","sources":[]},"Nvidia earnings beat estimates",None) == 0.
        doc=b'<feed xmlns="http://www.w3.org/2005/Atom"><entry><title>LangChain funding</title><link href="https://www.reddit.com/r/programming/comments/abc123/news/"/></entry></feed>'
        assert len(parse_reddit_feed(doc))==1
        print("Discussion matcher self-tests passed")
        return
    current=datetime.now(ZoneInfo("America/Los_Angeles")).date()
    start=(current-timedelta(days=max(1,args.days)-1)).isoformat()
    files=sorted(p for p in FOLDER.glob("*.json") if start<=p.stem<=current.isoformat())
    changed=0
    counts={"Hacker News":0,"Reddit":0}
    docs=[(file,json.loads(file.read_text(encoding="utf8"))) for file in files]
    stories=[(issue["date"],story) for _,issue in docs for section in ("topStories","alsoWorthKnowing","newTools") for story in issue.get(section,[])]
    # Bounded parallelism, with in-memory URL caches and endpoint circuit breakers.
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        matches=list(pool.map(lambda task: enrich_story(*task),stories))
    by_id={id(story):matches[i] for i,(_,story) in enumerate(stories)}
    removed_total=0
    for file,data in docs:
        outcome=[by_id[id(story)] for section in ("topStories","alsoWorthKnowing","newTools") for story in data.get(section,[]) if id(story) in by_id]
        found=[link for item in outcome for link in item["added"]]
        removed=sum(item["removed"] for item in outcome)
        removed_total+=removed
        if found or removed:
            file.write_text(json.dumps(data,indent=2,ensure_ascii=False)+"\n",encoding="utf8")
            changed+=1
        for item in found:
            counts[item["platform"]]+=1
        print(f"{file.name}: added {len(found)} and removed {removed} discussion links")
    print(f"Done. Updated {changed} edition files; added HN={counts['Hacker News']}, Reddit={counts['Reddit']}; removed stale HN={removed_total}; HTTP successes HN={SUCCESS['hn']}, Reddit RSS={SUCCESS['reddit']}, Reddit archive={SUCCESS['reddit_archive']}; failures HN={FAILED['hn']}, Reddit RSS={FAILED['reddit']}, Reddit archive={FAILED['reddit_archive']}")
    if not SUCCESS["hn"] and not SUCCESS["reddit"] and not SUCCESS["reddit_archive"]:
        print("WARNING: No community search endpoint responded; no links were fabricated.",file=sys.stderr)

if __name__ == "__main__":
    run()
