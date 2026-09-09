import Link from "next/link";

import { requireSession } from "@/lib/dal";
import { paginate } from "@/lib/pagination";
import { prisma } from "@/lib/db";

// The dashboard reads appraisals at request time. Without this it is
// prerendered at build, and a deployment would serve the list as it stood when
// the build ran - never showing anything created afterwards.
export const dynamic = "force-dynamic";

function bandClass(code: string | null) {
  switch (code) {
    case "A": return "bg-emerald-50 text-emerald-700 border-emerald-300";
    case "B": return "bg-lime-50 text-lime-700 border-lime-300";
    case "C": return "bg-amber-50 text-amber-700 border-amber-300";
    case "D": return "bg-red-50 text-red-700 border-red-300";
    default: return "bg-slate-50 text-slate-500 border-slate-300";
  }
}

const CURRENCY = new Intl.NumberFormat("en-LK", { maximumFractionDigits: 0 });

const PAGE_SIZE = 25;

export default async function Home({
  searchParams,
}: {
  searchParams: Promise<{ page?: string }>;
}) {
  await requireSession();

  const requestedPage = (await searchParams).page;

  // The summary figures are computed by the database over EVERY appraisal, not
  // over the rows on this page. They previously reduced over the same truncated
  // `take: 50` array the table rendered, so "Total appraisals" stopped counting
  // at 50 and the two means silently became means of the fifty most recent -
  // presented, in both cases, as portfolio statistics.
  const [total, withheld, averages] = await Promise.all([
    prisma.appraisal.count(),
    prisma.appraisal.count({ where: { riskBand: null } }),
    prisma.appraisal.aggregate({
      where: { riskBand: { not: null } },
      _avg: { creditRiskScore: true, developmentScore: true },
    }),
  ]);

  const {
    page: current,
    pageCount,
    skip,
    take,
    firstRow,
    lastRow,
  } = paginate(total, requestedPage, PAGE_SIZE);

  const appraisals = await prisma.appraisal.findMany({
    orderBy: { createdAt: "desc" },
    skip,
    take,
  });

  const avgCredit = averages._avg.creditRiskScore;
  const avgDevelopment = averages._avg.developmentScore;

  return (
    <div className="space-y-6">
      <div className="flex items-end justify-between">
        <div>
          <h1 className="text-xl font-semibold text-slate-900">Appraisals</h1>
          <p className="mt-0.5 text-sm text-slate-500">
            Credit risk and development impact are scored separately and never
            combined into a single number.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <Stat label="Total appraisals" value={String(total)} />
        <Stat
          label="Mean credit risk"
          value={avgCredit != null ? avgCredit.toFixed(1) : "—"}
          hint="banded appraisals only"
        />
        <Stat
          label="Mean development impact"
          value={avgDevelopment != null ? avgDevelopment.toFixed(1) : "—"}
          hint="banded appraisals only"
        />
        <Stat
          label="Withheld (incomplete)"
          value={String(withheld)}
          hint={withheld > 0 ? "no recommendation issued" : undefined}
        />
      </div>

      {appraisals.length === 0 ? (
        <div className="rounded-lg border border-dashed border-slate-300 bg-white p-12 text-center">
          <p className="text-sm text-slate-600">No appraisals yet.</p>
          <Link
            href="/appraisals/new"
            className="mt-3 inline-block rounded-md bg-slate-900 px-4 py-2 text-sm text-white hover:bg-slate-800"
          >
            Create the first appraisal
          </Link>
        </div>
      ) : (
        <div className="overflow-x-auto rounded-lg border border-slate-200 bg-white">
          <table className="w-full text-sm">
            <caption className="sr-only">
              Appraisals, most recent first. Showing {firstRow} to {lastRow} of{" "}
              {total}.
            </caption>
            <thead className="border-b border-slate-200 bg-slate-50 text-left">
              <tr className="text-xs uppercase tracking-wide text-slate-500">
                <th scope="col" className="px-4 py-2.5 font-medium">Reference</th>
                <th scope="col" className="px-4 py-2.5 font-medium">Business</th>
                <th scope="col" className="px-4 py-2.5 font-medium text-right">Facility (Rs.)</th>
                <th scope="col" className="px-4 py-2.5 font-medium text-right">Credit</th>
                <th scope="col" className="px-4 py-2.5 font-medium text-right">Development</th>
                <th scope="col" className="px-4 py-2.5 font-medium">Band</th>
                <th scope="col" className="px-4 py-2.5 font-medium">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {appraisals.map((a) => (
                <tr key={a.id} className="hover:bg-slate-50">
                  <td className="px-4 py-2.5">
                    <Link
                      href={`/appraisals/${a.id}`}
                      className="font-mono text-xs text-slate-900 hover:underline"
                    >
                      {a.reference}
                    </Link>
                  </td>
                  <td className="px-4 py-2.5 text-slate-800">{a.businessName}</td>
                  <td className="px-4 py-2.5 text-right tabular-nums text-slate-700">
                    {CURRENCY.format(a.facilityAmount)}
                  </td>
                  <td className="px-4 py-2.5 text-right tabular-nums text-slate-900">
                    {a.creditRiskScore?.toFixed(1) ?? "—"}
                  </td>
                  <td className="px-4 py-2.5 text-right tabular-nums text-slate-900">
                    {a.developmentScore?.toFixed(1) ?? "—"}
                  </td>
                  <td className="px-4 py-2.5">
                    <span
                      className={`inline-block rounded border px-2 py-0.5 text-xs font-medium ${bandClass(a.riskBand)}`}
                    >
                      {a.riskBand ?? "withheld"}
                    </span>
                  </td>
                  <td className="px-4 py-2.5 text-xs text-slate-500">{a.status}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {pageCount > 1 && (
        <nav
          aria-label="Appraisal pages"
          className="flex items-center justify-between"
        >
          <p className="text-xs text-slate-500" aria-live="polite">
            Showing {firstRow}–{lastRow} of {total}
          </p>
          <div className="flex items-center gap-2">
            <PageLink
              page={current - 1}
              disabled={current === 1}
              label="Previous page"
            >
              Previous
            </PageLink>
            <span className="text-xs text-slate-500">
              Page {current} of {pageCount}
            </span>
            <PageLink
              page={current + 1}
              disabled={current === pageCount}
              label="Next page"
            >
              Next
            </PageLink>
          </div>
        </nav>
      )}
    </div>
  );
}

/**
 * A pagination control.
 *
 * The disabled state renders a span rather than a link, because a link that
 * goes nowhere is still focusable and still announced as a link. Screen-reader
 * users would tab to "Previous" on the first page and find it does nothing.
 */
function PageLink({
  page,
  disabled,
  label,
  children,
}: {
  page: number;
  disabled: boolean;
  label: string;
  children: React.ReactNode;
}) {
  const shared = "rounded-md border px-3 py-1.5 text-sm";

  if (disabled) {
    return (
      <span
        aria-disabled="true"
        className={`${shared} border-slate-200 text-slate-400`}
      >
        {children}
      </span>
    );
  }

  return (
    <Link
      href={`/?page=${page}`}
      aria-label={label}
      className={`${shared} border-slate-300 text-slate-700 hover:bg-slate-50`}
    >
      {children}
    </Link>
  );
}

function Stat({
  label,
  value,
  hint,
}: {
  label: string;
  value: string;
  hint?: string;
}) {
  return (
    <div className="rounded-lg border border-slate-200 bg-white p-4">
      <div className="text-xs font-medium uppercase tracking-wide text-slate-500">
        {label}
      </div>
      <div className="mt-1 text-2xl font-semibold tabular-nums text-slate-900">
        {value}
      </div>
      {hint && <div className="mt-0.5 text-xs text-slate-400">{hint}</div>}
    </div>
  );
}
