#!/usr/bin/env python3
"""Match existing daily stories to actual HN/Reddit discussion threads.

Run by GitHub Actions after the briefing is published. This is discussion
discovery only; it NEVER fabricates a 'discoveredVia' provenance record.

Inputs: data/daily/YYYY-MM-DD.json
Outputs: optional story.discussions entries with verified thread permalinks.
External sources: HN Algolia public search API, approved Reddit OAuth Data API.
No unauthenticated Reddit RSS or unofficial archive fallback.
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
import os
import base64
import threading
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
REDDIT_OAUTH_TOKEN = None
REDDIT_SEARCH_COUNT = 0
REDDIT_SEARCH_LIMIT = 24
REDDIT_LOCK = threading.Lock()
STOP = {
    "a","an","the","and","of","for","on","in","to","with","its",
    "from","into","out","as","at","is","are","was","were","by",
    "new","now","how","why","what","this","that","today",
    "company","announces","announced","launches","launched","introduces",
    "releases","released","report","reports","latest","more",
}
FAILED = {"hn": 0, "reddit_oauth": 0}
SUCCESS = {"hn": 0, "reddit_oauth": 0}

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

def reddit_token():
    """Use only approved Reddit Data API credentials; never bypass rate limits."""
    client_id=os.environ.get("REDDIT_CLIENT_ID","").strip()
    secret=os.environ.get("REDDIT_CLIENT_SECRET","").strip()
    agent=os.environ.get("REDDIT_USER_AGENT","").strip()
    if not client_id or not secret or not agent:
        print("Reddit API disabled: approved OAuth credentials and user agent not configured.")
        return None
    auth=base64.b64encode((client_id+":"+secret).encode()).decode()
    req=Request(
        "https://www.reddit.com/api/v1/access_token",
        data=urlencode({"grant_type":"client_credentials"}).encode(),
        headers={"Authorization":"Basic "+auth,"User-Agent":agent,
                 "Content-Type":"application/x-www-form-urlencoded"},
        method="POST")
    try:
        with urlopen(req,timeout=10) as response:
            data=json.loads(response.read(200_000))
        if data.get("token_type","").lower()=="bearer" and data.get("access_token"):
            print("Reddit OAuth token acquired for authorized discussion search.")
            return data["access_token"]
    except (HTTPError,URLError,TimeoutError,OSError,ValueError) as exc:
        print("Reddit OAuth unavailable ("+type(exc).__name__+"); skipping Reddit.",file=sys.stderr)
    return None

@lru_cache(maxsize=80)
def reddit_search(query):
    global REDDIT_SEARCH_COUNT
    if not query or not REDDIT_OAUTH_TOKEN:
        return []
    with REDDIT_LOCK:
        if REDDIT_SEARCH_COUNT >= REDDIT_SEARCH_LIMIT:
            return []
        REDDIT_SEARCH_COUNT+=1
    params=urlencode({"q":query,"sort":"relevance","t":"month","limit":25,"type":"link"})
    req=Request("https://oauth.reddit.com/search?"+params,
                headers={"User-Agent":os.environ["REDDIT_USER_AGENT"],
                         "Authorization":"bearer "+REDDIT_OAUTH_TOKEN,
                         "Accept":"application/json"})
    try:
        with urlopen(req,timeout=9) as response:
            data=json.loads(response.read(300_000))
        SUCCESS["reddit_oauth"]+=1
        return [c["data"] for c in data.get("data",{}).get("children",[])
                if isinstance(c,dict) and isinstance(c.get("data"),dict)]
    except (HTTPError,URLError,TimeoutError,OSError,ValueError,KeyError) as exc:
        FAILED["reddit_oauth"]+=1
        if FAILED["reddit_oauth"] <= 3:
            print("Reddit OAuth search failed ("+type(exc).__name__+").",file=sys.stderr)
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

def reddit_match(story,issue_date):
    if not REDDIT_OAUTH_TOKEN:
        return None
    best=None
    query=" ".join(best_query(story.get("title","")).split()[:5])
    for post in reddit_search(query):
        if not near_date(post.get("created_utc"),issue_date):
            continue
        if int(post.get("num_comments") or 0) < 1:
            continue
        score=story_score(story,post.get("title",""),post.get("url",""))
        if score < .68:
            continue
        raw=str(post.get("permalink",""))
        if raw.startswith("/"):
            raw="https://www.reddit.com"+raw
        match=permalink_candidate(raw)
        if not match:
            continue
        permalink,subreddit=match
        candidate=(score,int(post.get("num_comments") or 0),permalink,subreddit)
        if best is None or candidate > best:
            best=candidate
    if not best:
        return None
    return {"platform":"Reddit","url":best[2],"label":"r/"+best[3]}

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
    parser.add_argument("--days",type=int,default=2)
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
        print("Discussion matcher self-tests passed")
        return
    global REDDIT_OAUTH_TOKEN
    REDDIT_OAUTH_TOKEN=reddit_token()
    current=datetime.now(ZoneInfo("America/Los_Angeles")).date()
    start=(current-timedelta(days=max(1,args.days)-1)).isoformat()
    files=sorted(p for p in FOLDER.glob("*.json") if start<=p.stem<=current.isoformat())
    changed=0
    counts={"Hacker News":0,"Reddit":0}
    docs=[]
    for file in files:
        # A malformed publication is reported by the validator; never rewrite it here.
        try:
            issue=json.loads(file.read_text(encoding="utf8"))
        except (OSError,ValueError) as exc:
            print(f"Skipping unparseable {file.name}: {exc}",file=sys.stderr)
            continue
        if isinstance(issue,dict) and issue.get("date")==file.stem:
            docs.append((file,issue))
    stories=[(issue["date"],story) for _,issue in docs for section in ("topStories","alsoWorthKnowing","newTools")
             for story in (issue.get(section) if isinstance(issue.get(section),list) else []) if isinstance(story,dict)]
    # Bounded parallelism, with in-memory URL caches and endpoint circuit breakers.
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        matches=list(pool.map(lambda task: enrich_story(*task),stories))
    by_id={id(story):matches[i] for i,(_,story) in enumerate(stories)}
    removed_total=0
    for file,data in docs:
        outcome=[by_id[id(story)] for section in ("topStories","alsoWorthKnowing","newTools") for story in (data.get(section) or []) if id(story) in by_id]
        found=[link for item in outcome for link in item["added"]]
        removed=sum(item["removed"] for item in outcome)
        removed_total+=removed
        if found or removed:
            file.write_text(json.dumps(data,indent=2,ensure_ascii=False)+"\n",encoding="utf8")
            changed+=1
        for item in found:
            counts[item["platform"]]+=1
        print(f"{file.name}: added {len(found)} and removed {removed} discussion links")
    print(f"Done. Updated {changed} edition files; added HN={counts['Hacker News']}, Reddit={counts['Reddit']}; removed stale HN={removed_total}; HTTP HN={SUCCESS['hn']}, Reddit OAuth={SUCCESS['reddit_oauth']}; failures HN={FAILED['hn']}, Reddit OAuth={FAILED['reddit_oauth']}")
    if not SUCCESS["hn"] and not SUCCESS["reddit_oauth"]:
        print("WARNING: No community search endpoint responded; no links were fabricated.",file=sys.stderr)

if __name__ == "__main__":
    run()
