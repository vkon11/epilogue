"""Fetch job descriptions for focus-region postings that don't have one yet.

Free APIs first (Workday, Greenhouse, Lever, Ashby), then a plain page fetch, then Firecrawl
(1 credit per page) only when the page needs a browser to render.
"""
import html
import re
import shutil
import subprocess
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from urllib.parse import urlparse

import requests

from db import client, retry
from regions import FOCUS

MIN_CHARS = 1500  # shorter than this means the page didn't render its content
HEADERS = {"User-Agent": "Mozilla/5.0", "Accept": "application/json, text/html"}


def strip_html(text):
    text = re.sub(r"(?s)<(script|style)\b.*?</\1>", " ", html.unescape(text))
    text = re.sub(r"<(br|/p|/li|/h\d|/div)[^>]*>", "\n", text)
    return re.sub(r"[ \t]+", " ", re.sub(r"<[^>]+>", " ", text)).strip()


def workday(url):
    p = urlparse(url)
    parts = p.path.strip("/").split("/")
    if re.fullmatch(r"[a-z]{2}-[A-Z]{2}", parts[0]):  # optional locale prefix
        parts = parts[1:]
    r = requests.get(f"https://{p.netloc}/wday/cxs/{p.netloc.split('.')[0]}/{'/'.join(parts)}", headers=HEADERS, timeout=30)
    return r.json()["jobPostingInfo"]["jobDescription"]


def greenhouse(url):
    m = re.search(r"greenhouse\.io/([^/]+)/jobs/(\d+)", url)
    return requests.get(f"https://boards-api.greenhouse.io/v1/boards/{m[1]}/jobs/{m[2]}", timeout=30).json()["content"]


def lever(url):
    m = re.search(r"lever\.co/([^/]+)/([0-9a-f-]{36})", url)
    j = requests.get(f"https://api.lever.co/v0/postings/{m[1]}/{m[2]}", timeout=30).json()
    lists = "\n".join(f"{x['text']}\n{x['content']}" for x in j.get("lists", []))
    return f"{j.get('descriptionPlain', '')}\n{lists}\n{j.get('additionalPlain', '')}"


def ashby(url):
    m = re.search(r"ashbyhq\.com/([^/]+)/([0-9a-f-]{36})", url)
    jobs = requests.get(f"https://api.ashbyhq.com/posting-api/job-board/{m[1]}", timeout=30).json()["jobs"]
    return next(j["descriptionPlain"] for j in jobs if j["id"] == m[2])


def plain(url):
    return requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=30).text


def firecrawl(url):
    exe = shutil.which("firecrawl")
    if not exe:
        return ""
    out = subprocess.run([exe, "scrape", url, "--only-main-content", "-f", "markdown"],
                         capture_output=True, text=True, encoding="utf-8", timeout=120)
    return out.stdout if out.returncode == 0 else ""


def fetch_free(url):
    for host, fn in (("myworkdayjobs", workday), ("greenhouse.io", greenhouse), ("lever.co", lever),
                     ("ashbyhq", ashby), ("", plain)):
        if host in url:
            try:
                text = strip_html(fn(url))
                if len(text) >= MIN_CHARS or host:
                    return text
            except Exception:
                pass
    return ""


def pending(db):
    rows, start = [], 0
    while True:
        page = (
            db.table("postings").select("id,url").is_("described_at", "null").neq("status", "closed")
            .overlaps("regions", FOCUS).range(start, start + 999).execute().data
        )
        rows += page
        if len(page) < 1000:
            return rows
        start += 1000


def run():
    db = client()
    rows = pending(db)
    with ThreadPoolExecutor(8) as pool:
        texts = list(pool.map(lambda r: fetch_free(r["url"]), rows))

    credits = 0
    for row, text in zip(rows, texts):
        if len(text) < MIN_CHARS:  # Firecrawl allows 2 concurrent jobs, so these go one at a time
            rendered = firecrawl(row["url"])
            if rendered:
                credits += 1
                text = rendered
        retry(db.table("postings").update({
            "description": text or None,
            "described_at": datetime.now(timezone.utc).isoformat(),
        }).eq("id", row["id"]).execute)

    got = sum(1 for t in texts if t)
    print(f"describe: {len(rows)} fetched, {got} via free sources, {credits} Firecrawl credits")
