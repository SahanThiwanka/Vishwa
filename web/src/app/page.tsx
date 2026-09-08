import Link from "next/link";

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

export default async function Home() {
  const appraisals = await prisma.appraisal.findMany({
    orderBy: { createdAt: "desc" },
    take: 50,
  });

  const banded = appraisals.filter((a) => a.riskBand);
  const withheld = appraisals.filter((a) => !a.riskBand).length;

  const avgCredit = banded.length
    ? banded.reduce((s, a) => s + (a.creditRiskScore ?? 0), 0) / banded.length
    : null;
  const avgDevelopment = banded.length
    ? banded.reduce((s, a) => s + (a.developmentScore ?? 0), 0) / banded.length
    : null;

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
        <Stat label="Total appraisals" value={String(appraisals.length)} />
        <Stat
          label="Mean credit risk"
          value={avgCredit !== null ? avgCredit.toFixed(1) : "—"}
        />
        <Stat
          label="Mean development impact"
          value={avgDevelopment !== null ? avgDevelopment.toFixed(1) : "—"}
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
        <div className="overflow-hidden rounded-lg border border-slate-200 bg-white">
          <table className="w-full text-sm">
            <thead className="border-b border-slate-200 bg-slate-50 text-left">
              <tr className="text-xs uppercase tracking-wide text-slate-500">
                <th className="px-4 py-2.5 font-medium">Reference</th>
                <th className="px-4 py-2.5 font-medium">Business</th>
                <th className="px-4 py-2.5 font-medium text-right">Facility (Rs.)</th>
                <th className="px-4 py-2.5 font-medium text-right">Credit</th>
                <th className="px-4 py-2.5 font-medium text-right">Development</th>
                <th className="px-4 py-2.5 font-medium">Band</th>
                <th className="px-4 py-2.5 font-medium">Status</th>
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
    </div>
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
