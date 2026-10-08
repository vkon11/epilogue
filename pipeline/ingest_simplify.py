"""Pull Summer 2027 internships from SimplifyJobs into the postings table."""
from datetime import datetime, timezone

import requests

from db import client, retry
from regions import regions

URL = "https://raw.githubusercontent.com/SimplifyJobs/Summer2027-Internships/dev/.github/scripts/listings.json"
TRACKS = {
    "Quant": "quant",
    "Software": "swe",
    "Software Engineering": "swe",
    "Hardware": "ce",
    "Hardware Engineering": "ce",
}
CHUNK = 500


def keep(x):
    return (
        x.get("active")
        and x.get("is_visible", True)
        and "Summer 2027" in (x.get("terms") or [])
        and x.get("category") in TRACKS
        and (not x.get("degrees") or "Bachelor's" in x["degrees"])
    )


def existing(db):
    """source_id -> status for every Simplify posting already stored."""
    rows, start = {}, 0
    while True:
        page = (
            db.table("postings").select("source_id,status").eq("source", "simplify")
            .range(start, start + 999).execute().data
        )
        rows.update({r["source_id"]: r["status"] for r in page})
        if len(page) < 1000:
            return rows
        start += 1000


def run():
    listings = [x for x in retry(lambda: requests.get(URL, timeout=120).json()) if keep(x)]
    now = datetime.now(timezone.utc)
    rows = [
        {
            "source": "simplify",
            "source_id": x["id"],
            "company": x["company_name"].strip(),
            "title": x["title"].strip(),
            "url": x["url"],
            "category": x["category"],
            "track": TRACKS[x["category"]],
            "locations": x.get("locations") or [],
            "regions": regions(x.get("locations") or []),
            "status": "open",
            "date_posted": datetime.fromtimestamp(x["date_posted"], timezone.utc).date().isoformat()
            if x.get("date_posted") else None,
            "last_seen": now.isoformat(),
        }
        for x in listings
    ]
    rows = [r for r in rows if r["regions"]]  # US and remote only

    db = client()
    before = existing(db)

    companies = sorted({r["company"] for r in rows})
    for i in range(0, len(companies), CHUNK):
        db.table("companies").upsert(
            [{"name": n} for n in companies[i:i + CHUNK]], on_conflict="name", ignore_duplicates=True
        ).execute()
    for i in range(0, len(rows), CHUNK):
        db.table("postings").upsert(rows[i:i + CHUNK], on_conflict="source,source_id").execute()

    feed = {r["source_id"] for r in rows}
    gone = [sid for sid, status in before.items() if status != "closed" and sid not in feed]
    for i in range(0, len(gone), CHUNK):
        db.table("postings").update({"status": "closed"}).in_("source_id", gone[i:i + CHUNK]).execute()

    new = len(feed - before.keys())
    print(f"simplify: {len(rows)} in feed, {new} new, {len(gone)} closed")
