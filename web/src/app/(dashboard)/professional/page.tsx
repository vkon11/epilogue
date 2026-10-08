import Link from "next/link";
import { createClient } from "@/lib/supabase/server";

const TRACKS: Record<string, string> = { quant: "Quant", swe: "SWE", ce: "Computer Eng." };

type Filters = { track?: string; where?: string; closed?: string };

function href(filters: Filters) {
  const query = new URLSearchParams(
    Object.entries(filters).filter((entry): entry is [string, string] => Boolean(entry[1])),
  );
  return `/professional?${query}`;
}

function Chip({ active, to, children }: { active: boolean; to: string; children: React.ReactNode }) {
  return (
    <Link
      href={to}
      className={`rounded-full border px-3 py-1 text-sm ${
        active ? "border-foreground bg-foreground text-background" : "border-neutral-300 dark:border-neutral-700"
      }`}
    >
      {children}
    </Link>
  );
}

export default async function ProfessionalPage({ searchParams }: PageProps<"/professional">) {
  const params = await searchParams;
  const one = (v: string | string[] | undefined) => (Array.isArray(v) ? v[0] : v);
  const filters: Filters = { track: one(params.track), where: one(params.where), closed: one(params.closed) };

  const supabase = await createClient();
  let query = supabase
    .from("postings")
    .select("id, company, title, url, track, locations, status, date_posted")
    .order("date_posted", { ascending: false, nullsFirst: false })
    .limit(500);
  if (filters.track && filters.track in TRACKS) query = query.eq("track", filters.track);
  if (filters.where !== "all") query = query.in("region", ["remote", "midwest"]);
  if (!filters.closed) query = query.neq("status", "closed");
  const { data: postings, error } = await query;

  return (
    <div className="space-y-4">
      <h1 className="text-xl font-semibold">Internships · Summer 2027</h1>

      <div className="flex flex-wrap gap-2">
        <Chip active={!filters.track} to={href({ ...filters, track: undefined })}>All tracks</Chip>
        {Object.entries(TRACKS).map(([key, label]) => (
          <Chip key={key} active={filters.track === key} to={href({ ...filters, track: key })}>{label}</Chip>
        ))}
      </div>
      <div className="flex flex-wrap gap-2">
        <Chip active={filters.where !== "all"} to={href({ ...filters, where: undefined })}>Remote + Midwest</Chip>
        <Chip active={filters.where === "all"} to={href({ ...filters, where: "all" })}>All locations</Chip>
        <Chip active={Boolean(filters.closed)} to={href({ ...filters, closed: filters.closed ? undefined : "1" })}>
          Show closed
        </Chip>
      </div>

      {error ? (
        <p className="text-red-600">Couldn&apos;t load postings: {error.message}</p>
      ) : (
        <>
          <p className="text-sm opacity-70">{postings.length} postings</p>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="border-b border-neutral-200 dark:border-neutral-800">
                <tr>
                  <th className="py-2 pr-4">Company</th>
                  <th className="py-2 pr-4">Role</th>
                  <th className="py-2 pr-4">Track</th>
                  <th className="py-2 pr-4">Location</th>
                  <th className="py-2">Posted</th>
                </tr>
              </thead>
              <tbody>
                {postings.map((p) => (
                  <tr key={p.id} className="border-b border-neutral-100 dark:border-neutral-900">
                    <td className="py-2 pr-4 font-medium">{p.company}</td>
                    <td className="py-2 pr-4">
                      <a href={p.url} target="_blank" rel="noreferrer" className="underline">{p.title}</a>
                      {p.status === "closed" && <span className="ml-2 text-xs opacity-60">closed</span>}
                    </td>
                    <td className="py-2 pr-4">{TRACKS[p.track] ?? p.track}</td>
                    <td className="py-2 pr-4">{p.locations.join(" · ")}</td>
                    <td className="whitespace-nowrap py-2">{p.date_posted}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </div>
  );
}
