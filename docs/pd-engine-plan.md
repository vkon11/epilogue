# PD Engine — Plan (v1)

Tab 1 of the epilogue dashboard: find Summer 2027 internships, summarize and categorize them against
VK's profile, and keep a list of people worth contacting. No application tracker, no message drafting,
no resume editor in v1.

## Success criteria for v1

- A deployed dashboard (Vercel) behind a login only VK can pass.
- **Postings view:** every active Summer 2027 quant / SWE / computer-engineering internship from the
  sources below, each with track, firm type, status, a 2–3 sentence summary, and a 1–5 fit score with
  a one-line reason. Filterable and sortable.
- **Contacts view:** UM faculty in relevant research areas (name, role, org, primary research
  interest, source link), plus a form to add alumni/engineers by hand.
- One local command refreshes everything; re-running it never creates duplicates.
- Cost: $0/month.

## Data sources (verified 2026-10-07)

| Source | What it gives | Access | Volume |
|---|---|---|---|
| SimplifyJobs `Summer2027-Internships` repo | Internship postings with category, company, title, locations, degrees, date posted, active flag | Free JSON file (`.github/scripts/listings.json`) | 1,219 active Summer 2027 postings in our tracks (725 Software, 346 Hardware, 146 Quant) |
| Greenhouse public job boards | Postings straight from firms | Free JSON API | Live for Jane Street, HRT, IMC, Optiver, DRW, Jump, Tower, Akuna, Virtu |
| Watchlist pages (Firecrawl) | Freshman programs not on any feed: Citadel Launch, NVIDIA Ignite, Two Sigma, UberSTAR, Capital One TEIP/AEIP, Amazon Future Engineer, bank insight programs | Firecrawl scrape, weekly, cached | ~15 pages ≈ 60 credits/month of 1,000 |
| UM CSE faculty pages + Math FAM group | Faculty names, titles, research areas | Plain HTTP fetch, Firecrawl as fallback | Public pages, both return 200 |

Not used: MCommunity (login-gated, bulk collection likely against UM policy), LinkedIn (scraping
prohibited). Alumni and industry engineers are added one at a time by hand.

Known gap: Simplify has no deadlines. Status is `open` / `closed` from the active flag; `closing soon`
only exists for watchlist programs with known windows.

## Architecture

```
epilogue/
├── web/                  Next.js 16 + TypeScript + Tailwind 4 → Vercel
├── pipeline/             Python 3.12 scripts, run locally
│   ├── profile.md        VK's profile for fit scoring (git-ignored — personal)
│   ├── companies.yaml    company → firm type map (hand-curated)
│   └── watchlist.yaml    freshman program pages to check
├── supabase/migrations/  SQL schema + row-level security
└── docs/
```

- **Database:** Supabase Postgres. Row-level security on every table; only VK's account can read or
  write. The pipeline uses the secret key locally; the browser only ever sees the publishable key.
- **Auth:** Supabase magic-link login, restricted to one allowlisted email.
- **AI work:** done by Claude Code in headless mode (`claude -p`) on VK's Pro plan, called from the
  pipeline in batches. No Anthropic API key, no per-call cost. The dashboard never calls an AI itself.

## Pipeline steps (`python pipeline/run.py`)

1. **Ingest Simplify** — download the JSON, keep: active, Summer 2027, category in
   {Quant, Software, Hardware}, degrees include Bachelor's (or unspecified). Upsert by Simplify id;
   mark postings closed when they drop out.
2. **Ingest Greenhouse** — pull each quant firm's board, keep titles containing "intern". Dedupe
   against Simplify by URL.
3. **Check watchlist** — Firecrawl-scrape each program page at most once a week; record open/closed
   and the window.
4. **Tag (rules, no AI)** — track from Simplify category + title keywords (Quant split into
   research / trading / dev; Hardware → computer engineering); firm type from `companies.yaml`.
5. **Enrich (Claude Code)** — only postings that are new or changed, and only the priority set (all
   Quant, all watchlist programs, Software/Hardware at target companies or with early-career signals in
   the title). Batches of ~25 → JSON: summary, relevance to profile, fit 1–5, reason.
6. **Faculty** — fetch CSE faculty in hardware/architecture/systems areas and the Math FAM group; a
   Claude Code pass condenses each into one "primary research interest" line. Monthly refresh.

## Database tables

- `companies` — name, firm_type, website
- `postings` — source, source_id (unique), company, title, url, locations, track, status, date_posted,
  first_seen, summary, relevance, fit_score, fit_reason, enriched_at
- `contacts` — kind (faculty / industry), name, role, org, research_interest, source_url, notes

## Dashboard (web)

- Sidebar with four tabs; only Professional is live, the other three are placeholders.
- **Postings:** cards or table with filters (track, firm type, fit, status), sorted by fit then date.
  Each item shows the summary and fit reason and links straight to the application.
- **Contacts:** table plus an "add contact" form.

## Milestones

| # | Build | Verify |
|---|---|---|
| M0 | Scaffold `web/`, link Supabase, apply schema migration | Tables exist; querying with the publishable key and no login returns 0 rows |
| M1 | Simplify ingest | ~1,200 rows; second run adds 0 duplicates |
| M2 | Postings view + login, deployed to Vercel | VK can log in and see postings; an incognito window sees nothing |
| M3 | Tagging, Greenhouse ingest, watchlist | Every posting has a track and firm type; watchlist programs show status |
| M4 | Claude Code enrichment | Hand-check 20 summaries and fit scores against the profile |
| M5 | Faculty ingest + contacts view and form | Faculty list populated; hand-added contact appears |

Each milestone ends with a short walkthrough of what was built and why.
