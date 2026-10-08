"""Rule-based screen: can VK apply? Rising sophomore in summer 2027, graduating 2030. Free — no AI.

fits    — open to freshmen / first-years / rising sophomores, or graduation range reaches 2030
no      — graduation range ends before 2030, sophomore year must be finished, or juniors/seniors/grad only
unclear — says nothing either way, or hinges on sophomore standing (see SOPHOMORE_STANDING)
"""
import re

from db import client, retry

GRAD_YEAR = 2030
# "Sophomore standing" is about credits, not years — AP credit can get a first-year there early.
# Set True once VK confirms his standing in Wolverine Access; until then those postings stay "unclear".
SOPHOMORE_STANDING = False

STUDENT = r"(students?|undergrad\w*)"
STRONG = re.compile(rf"\b(freshm[ae]n|first[- ]year {STUDENT}|rising sophomores?|underclass\w*)\b")
SOPH = re.compile(rf"\b(sophomores?|second[- ]year {STUDENT})\b")
SOPH_DONE = re.compile(r"\b(complet(ed|ion of)|finished) (the |their |your )?sophomore year")
NO = re.compile(
    r"\b(rising (junior|senior)s?|juniors? (or|and) seniors?|penultimate[- ]year|final[- ]year"
    r"|(currently )?(pursuing|enrolled in) an? (ph\.?d|master))"
)
GRAD = re.compile(r"graduat|class of|degree (completion|conferral)|expected to complete")
YEAR = re.compile(r"\b(20(?:2[6-9]|3[0-2]))\b")


def sentences(text):
    text = text.replace("&nbsp;", " ").replace(" ", " ")
    return [re.sub(r"\s+", " ", s).strip() for s in re.split(r"(?<=[.!?\n])\s+", text) if s.strip()]


def first(pattern, sents):
    return next((s for s in sents if pattern.search(s.lower())), None)


def classify(text):
    if not text:
        return "unclear", "No description available"
    sents = sentences(text)

    if s := first(STRONG, sents):
        return "fits", s[:240]

    years = [(int(y), s) for s in sents if GRAD.search(s.lower()) for y in YEAR.findall(s)]
    if years:
        top_year, s = max(years)
        return ("fits" if top_year >= GRAD_YEAR else "no"), s[:240]

    if s := first(SOPH_DONE, sents):
        return "no", s[:240]
    if s := first(SOPH, sents):
        return ("fits", s[:240]) if SOPHOMORE_STANDING else ("unclear", f"Needs sophomore standing: {s}"[:240])
    if s := first(NO, sents):
        return "no", s[:240]
    return "unclear", "Description doesn't mention class year"


def run(rescreen=False):
    db = client()
    rows, start = [], 0
    while True:
        query = db.table("postings").select("id,description").not_.is_("described_at", "null")
        if not rescreen:
            query = query.is_("eligibility", "null")
        page = query.range(start, start + 999).execute().data
        rows += page
        if len(page) < 1000:
            break
        start += 1000

    counts = {"fits": 0, "no": 0, "unclear": 0}
    for row in rows:
        label, reason = classify(row["description"])
        counts[label] += 1
        retry(db.table("postings").update({"eligibility": label, "eligibility_reason": reason}).eq("id", row["id"]).execute)
    print(f"eligibility: {len(rows)} screened, {counts}")


if __name__ == "__main__":
    run(rescreen=True)  # python pipeline/eligibility.py re-screens everything after a rule change
