export default function Loading() {
  return (
    <div className="space-y-4" aria-busy="true" aria-live="polite">
      <div className="h-6 w-48 animate-pulse rounded bg-slate-200" />
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <div key={i} className="h-20 animate-pulse rounded-lg bg-slate-200" />
        ))}
      </div>
      <div className="h-64 animate-pulse rounded-lg bg-slate-200" />
      <span className="sr-only">Loading</span>
    </div>
  );
}
