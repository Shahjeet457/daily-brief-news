#!/usr/bin/env python3
"""Fetch free RSS feeds and write news.json (headline aggregator, stdlib only)."""
import json, re, html, urllib.request, xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

FEEDS = {
  "Top Stories": [("BBC News","https://feeds.bbci.co.uk/news/rss.xml"),("NPR","https://feeds.npr.org/1001/rss.xml"),("Al Jazeera","https://www.aljazeera.com/xml/rss/all.xml")],
  "World": [("BBC News","https://feeds.bbci.co.uk/news/world/rss.xml"),("The Guardian","https://www.theguardian.com/world/rss"),("NPR","https://feeds.npr.org/1004/rss.xml")],
  "Business": [("BBC News","https://feeds.bbci.co.uk/news/business/rss.xml"),("The Guardian","https://www.theguardian.com/business/rss"),("NPR","https://feeds.npr.org/1006/rss.xml")],
  "Technology": [("BBC News","https://feeds.bbci.co.uk/news/technology/rss.xml"),("The Guardian","https://www.theguardian.com/technology/rss"),("NPR","https://feeds.npr.org/1019/rss.xml")],
  "Science": [("BBC News","https://feeds.bbci.co.uk/news/science_and_environment/rss.xml"),("The Guardian","https://www.theguardian.com/science/rss"),("NPR","https://feeds.npr.org/1007/rss.xml")],
  "Sports": [("BBC Sport","https://feeds.bbci.co.uk/sport/rss.xml"),("The Guardian","https://www.theguardian.com/sport/rss")],
  "Health": [("BBC News","https://feeds.bbci.co.uk/news/health/rss.xml"),("The Guardian","https://www.theguardian.com/society/health/rss"),("NPR","https://feeds.npr.org/1128/rss.xml")],
}
PER_SECTION = 24

def clean(t, n=260):
    t = html.unescape(re.sub(r"<[^>]+>", " ", t or ""))
    t = re.sub(r"\s+", " ", t).strip()
    return t if len(t) <= n else t[:n].rsplit(" ",1)[0] + "…"

def parse_date(s):
    try:
        d = parsedate_to_datetime(s)
        if d.tzinfo is None: d = d.replace(tzinfo=timezone.utc)
        return d.astimezone(timezone.utc).isoformat()
    except Exception:
        return None

def fetch(source, url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 DailyNewsAggregator"})
    root = ET.fromstring(urllib.request.urlopen(req, timeout=20).read())
    out = []
    for it in root.iter("item"):
        title, link = clean(it.findtext("title"), 300), (it.findtext("link") or "").strip()
        if not title or not link.startswith("http"): continue
        out.append({"title": title, "link": link, "source": source,
                    "summary": clean(it.findtext("description")),
                    "published": parse_date(it.findtext("pubDate") or "")})
    return out

def main():
    seen_links, seen_titles, sections, ok = set(), set(), {}, []
    for sec, feeds in FEEDS.items():
        items = []
        for source, url in feeds:
            try:
                got = fetch(source, url); ok.append(url); items += got
                print(f"  {sec:12} {source:13} {len(got):3} items")
            except Exception as e:
                print(f"  WARN {url}: {e}")
        items.sort(key=lambda x: x["published"] or "", reverse=True)
        kept = []
        for s in items:
            key = re.sub(r"\W+", "", s["title"].lower())
            lk = s["link"].split("?")[0]
            if lk in seen_links or key in seen_titles: continue
            seen_links.add(lk); seen_titles.add(key); kept.append(s)
            if len(kept) >= PER_SECTION: break
        sections[sec] = kept
    data = {"generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "feeds": sorted(set(ok)), "sections": sections}
    if not any(sections.values()): raise SystemExit("No stories fetched; news.json not written")
    with open("news.json", "w", encoding="utf-8") as f: json.dump(data, f, ensure_ascii=False, indent=1)
    print("Wrote news.json:", {k: len(v) for k, v in sections.items()})

if __name__ == "__main__": main()
