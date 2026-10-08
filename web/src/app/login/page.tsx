import { signIn } from "./actions";

export default async function LoginPage({ searchParams }: PageProps<"/login">) {
  const { error } = await searchParams;
  return (
    <main className="flex flex-1 items-center justify-center p-4">
      <form action={signIn} className="w-full max-w-sm space-y-3">
        <h1 className="text-xl font-semibold">epilogue</h1>
        <input
          name="email"
          type="email"
          required
          placeholder="you@umich.edu"
          className="w-full rounded border border-neutral-300 bg-transparent px-3 py-2 dark:border-neutral-700"
        />
        <input
          name="password"
          type="password"
          required
          placeholder="password"
          className="w-full rounded border border-neutral-300 bg-transparent px-3 py-2 dark:border-neutral-700"
        />
        <button className="w-full rounded bg-foreground px-3 py-2 text-background">Log in</button>
        {error && <p className="text-sm text-red-600">That didn&apos;t work: {error}</p>}
      </form>
    </main>
  );
}
