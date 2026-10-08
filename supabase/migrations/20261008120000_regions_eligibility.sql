-- Postings can sit in several regions at once (e.g. NYC + Chicago), and get screened for class-year eligibility.
alter table postings drop column region;
alter table postings add column regions text[] not null default '{}';  -- remote, midwest, nyc, bay_area, texas, us

alter table postings add column description text;
alter table postings add column described_at timestamptz;
alter table postings add column eligibility text check (eligibility in ('fits', 'no', 'unclear'));
alter table postings add column eligibility_reason text;
