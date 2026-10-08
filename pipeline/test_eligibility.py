"""Run: pipeline/.venv/Scripts/python pipeline/test_eligibility.py"""
from eligibility import classify

CASES = {
    "Open to freshmen and sophomores pursuing a CS degree.": "fits",
    "Software Engineering Intern/Freshman/Sophomore: $30 USD per hour": "fits",
    "Rising sophomores, juniors, and seniors are encouraged to apply.": "fits",
    "Expected graduation date of 2029 or 2030.": "fits",
    "Candidates must be graduating between December 2027 and June 2028.": "no",
    "Expected graduation between December 2027 and June 2029, with sophomore standing or higher.": "no",
    "Must have an expected graduation date no later than June 2029.": "no",
    "Completion of sophomore year of study by the summer of 2027.": "no",
    "This program is for rising juniors and seniors.": "no",
    "Currently pursuing a PhD in Computer Science.": "no",
    "Must be a Sophomore, Junior, or Senior in college.": "unclear",  # hinges on sophomore standing
    "Forbes named us a best employer for the second-year in a row.": "unclear",
    "Second-year MBA students preferred.": "unclear",
    "We are hiring interns for Summer 2027. Python required.": "unclear",
    "": "unclear",
}

failures = [(text, want, classify(text)[0]) for text, want in CASES.items() if classify(text)[0] != want]
for text, want, got in failures:
    print(f"FAIL want={want} got={got}: {text!r}")
print(f"{len(CASES) - len(failures)}/{len(CASES)} passed")
raise SystemExit(1 if failures else 0)
