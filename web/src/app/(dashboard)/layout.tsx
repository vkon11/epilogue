import Link from "next/link";

const TABS = [
  { label: "Professional", href: "/professional" },
  { label: "Calendar" },
  { label: "Projects" },
  { label: "75 Hard" },
];

export default function DashboardLayout({ children }: LayoutProps<"/">) {
  return (
    <div className="flex flex-1 flex-col sm:flex-row">
      <nav className="flex gap-4 border-b border-neutral-200 p-4 sm:w-48 sm:flex-col sm:gap-2 sm:border-b-0 sm:border-r dark:border-neutral-800">
        <span className="hidden font-semibold sm:block">epilogue</span>
        {TABS.map((tab) =>
          tab.href ? (
            <Link key={tab.label} href={tab.href} className="font-medium">
              {tab.label}
            </Link>
          ) : (
            <span key={tab.label} className="opacity-40" title="Coming later">
              {tab.label}
            </span>
          ),
        )}
      </nav>
      <main className="min-w-0 flex-1 p-4">{children}</main>
    </div>
  );
}
