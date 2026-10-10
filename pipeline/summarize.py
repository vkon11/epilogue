"""Write a one-to-two sentence "what you'd actually do" summary for each posting, via Claude Code
on VK's Pro plan (`claude -p`, no API key). Only postings with a description and no summary yet."""
import json
import shutil
import subprocess

from db import client, retry

BATCH = 20
MAX_CHARS = 6000  # role details sit near the top; the tail is mostly legal boilerplate
PROMPT = """For each internship posting below, write what the intern would actually do: the team,
the kind of work, and the main tools or skills. One or two sentences, at most 40 words. Skip company
boilerplate, perks, pay, and eligibility. Reply with only a JSON object mapping each id to its summary.

"""


def pending(db):
    rows, start = [], 0
    while True:
        page = (
            db.table("postings").select("id,company,title,description").not_.is_("description", "null")
            .is_("summary", "null").neq("status", "closed").range(start, start + 999).execute().data
        )
        rows += page
        if len(page) < 1000:
            return rows
        start += 1000


def summarize(batch):
    postings = "\n\n".join(
        f"### id {r['id']}: {r['company']} — {r['title']}\n{r['description'][:MAX_CHARS]}" for r in batch
    )
    out = subprocess.run([shutil.which("claude"), "-p", "--model", "haiku"], input=PROMPT + postings,
                         capture_output=True, text=True, encoding="utf-8", timeout=600)
    text = out.stdout
    return json.loads(text[text.index("{"):text.rindex("}") + 1])


def run(limit=None):
    db = client()
    rows = pending(db)[:limit]
    done = 0
    for i in range(0, len(rows), BATCH):
        try:
            summaries = summarize(rows[i:i + BATCH])
        except Exception as e:  # bad JSON or a timeout: skip, the next run retries these
            print(f"summarize: batch {i // BATCH} failed ({e})")
            continue
        for id_, summary in summaries.items():
            retry(db.table("postings").update({"summary": summary}).eq("id", int(id_)).execute)
            done += 1
    print(f"summarize: {done}/{len(rows)} summarized")


if __name__ == "__main__":
    run()
