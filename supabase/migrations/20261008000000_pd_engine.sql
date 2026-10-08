-- PD engine: companies, internship postings, contacts.
-- Only the owner's account can read or write. The pipeline uses the secret key, which bypasses RLS.

create table companies (
  name       text primary key,
  firm_type  text,  -- prop/hft, hedge fund, bank, big tech, semis/hardware, startup
  website    text,
  created_at timestamptz not null default now()
);

create table postings (
  id          bigint generated always as identity primary key,
  source      text not null,  -- simplify, greenhouse, watchlist
  source_id   text not null,
  company     text not null references companies (name) on update cascade,
  title       text not null,
  url         text not null,
  category    text,           -- raw category from the source
  track       text,           -- quant, swe, ce (quant split in M3)
  locations   text[] not null default '{}',
  region      text check (region in ('remote', 'midwest', 'other')),
  status      text not null default 'open' check (status in ('open', 'closing_soon', 'rolling', 'closed')),
  date_posted date,
  first_seen  timestamptz not null default now(),
  last_seen   timestamptz not null default now(),
  summary     text,
  relevance   text,
  fit_score   smallint check (fit_score between 1 and 5),
  fit_reason  text,
  enriched_at timestamptz,
  unique (source, source_id)
);

create table contacts (
  id                bigint generated always as identity primary key,
  kind              text not null check (kind in ('faculty', 'industry')),
  name              text not null,
  role              text,
  org               text,
  research_interest text,
  source_url        text,
  notes             text,
  created_at        timestamptz not null default now(),
  unique (name, org)
);

alter table companies enable row level security;
alter table postings  enable row level security;
alter table contacts  enable row level security;

create policy owner_only on companies for all to authenticated
  using ((auth.jwt() ->> 'email') = 'vskondur@umich.edu')
  with check ((auth.jwt() ->> 'email') = 'vskondur@umich.edu');
create policy owner_only on postings for all to authenticated
  using ((auth.jwt() ->> 'email') = 'vskondur@umich.edu')
  with check ((auth.jwt() ->> 'email') = 'vskondur@umich.edu');
create policy owner_only on contacts for all to authenticated
  using ((auth.jwt() ->> 'email') = 'vskondur@umich.edu')
  with check ((auth.jwt() ->> 'email') = 'vskondur@umich.edu');

revoke all on companies, postings, contacts from anon;
grant select, insert, update, delete on companies, postings, contacts to authenticated, service_role;
