create table if not exists candidate_analysis_history (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz default now(),
  filename text,
  job_description text,
  match_score integer,
  result jsonb not null
);

alter table candidate_analysis_history enable row level security;

create policy "service role can manage history"
on candidate_analysis_history
for all
using (true)
with check (true);
