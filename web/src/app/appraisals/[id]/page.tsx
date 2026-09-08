import Link from "next/link";
import { notFound } from "next/navigation";

import { prisma } from "@/lib/db";
import { criteriaTree } from "@/lib/scoring";
import type { AppraisalResult, ObjectiveResult } from "@/lib/scoring/types";

// Reads one appraisal at request time; must not be cached across requests.
export const dynamic = "force-dynamic";

const CURRENCY = new Intl.NumberFormat("en-LK", { maximumFractionDigits: 0 });

function bandClass(code?: string | null) {
  switch (code) {
    case "A": return "bg-emerald-50 text-emerald-800 border-emerald-300";
    case "B": return "bg-lime-50 text-lime-800 border-lime-300";
    case "C": return "bg-amber-50 text-amber-800 border-amber-300";
    case "D": return "bg-red-50 text-red-800 border-red-300";
    default: return "bg-slate-50 text-slate-600 border-slate-300";
  }
}

/** Bar colour by score, so the breakdown reads at a glance. */
function scoreBar(score: number) {
  if (score >= 75) return "bg-emerald-500";
  if (score >= 60) return "bg-lime-500";
  if (score >= 45) return "bg-amber-500";
  return "bg-red-500";
}

export default async function AppraisalDetail({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;

  const appraisal = await prisma.appraisal.findUnique({
    where: { id },
    include: { events: { orderBy: { createdAt: "asc" } } },
  });

  if (!appraisal || !appraisal.result) notFound();

  const result: AppraisalResult = JSON.parse(appraisal.result);
  const credit = result.objectives.find((o) => o.id === "credit_risk");
  const development = result.objectives.find((o) => o.id === "development_impact");

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between gap-4">
        <div>
          <div className="font-mono text-xs text-slate-500">{appraisal.reference}</div>
          <h1 className="mt-0.5 text-xl font-semibold text-slate-900">
            {appraisal.businessName}
          </h1>
          <p className="mt-0.5 text-sm text-slate-500">
            {appraisal.branch}
            {appraisal.district ? ` · ${appraisal.district}` : ""} ·{" "}
            {appraisal.facilityType} · Rs.{" "}
            {CURRENCY.format(appraisal.facilityAmount)}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <a
            href={`/appraisals/${appraisal.id}/report`}
            className="rounded-md border border-slate-300 bg-white px-3 py-2 text-sm text-slate-700 hover:bg-slate-50"
          >
            Export report (.docx)
          </a>
          <Link
            href="/"
            className="rounded-md border border-slate-300 bg-white px-3 py-2 text-sm text-slate-700 hover:bg-slate-50"
          >
            Back
          </Link>
        </div>
      </div>

      {result.criticalBreaches.length > 0 && (
        <div className="rounded-lg border border-red-300 bg-red-50 p-4">
          <h2 className="text-sm font-semibold text-red-900">
            Critical breach — cannot be offset by other criteria
          </h2>
          <ul className="mt-2 space-y-1.5">
            {result.criticalBreaches.map((b) => (
              <li key={b.id} className="text-sm text-red-800">
                <span className="font-medium">{b.name}</span> = {String(b.rawValue)}{" "}
                <span className="text-red-600">(clause {b.ref})</span>
                {b.criticalNote && (
                  <p className="mt-0.5 text-xs text-red-700/80">{b.criticalNote}</p>
                )}
              </li>
            ))}
          </ul>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {[credit, development].map((objective) =>
          objective ? (
            <ObjectiveCard key={objective.id} objective={objective} />
          ) : null,
        )}
      </div>

      {/* Explainability: how each dimension and criterion moved the score. */}
      {credit && <Breakdown objective={credit} />}
      {development && <Breakdown objective={development} />}

      <section className="rounded-lg border border-slate-200 bg-white p-5">
        <h2 className="text-sm font-semibold text-slate-900">Audit trail</h2>
        <p className="mt-0.5 text-xs text-slate-500">
          Mirrors the sign-off chain in clause 7 of the appraisal form.
        </p>
        <ol className="mt-4 space-y-3">
          {appraisal.events.map((e) => (
            <li key={e.id} className="flex gap-3 text-sm">
              <div className="w-32 shrink-0 text-xs text-slate-400">
                {new Date(e.createdAt).toLocaleString("en-GB")}
              </div>
              <div className="min-w-0">
                <span className="font-medium text-slate-900">{e.action}</span>
                <span className="text-slate-500">
                  {" "}
                  by {e.actor}
                  {e.role ? ` (${e.role})` : ""}
                </span>
                {e.note && <p className="text-xs text-slate-500">{e.note}</p>}
              </div>
            </li>
          ))}
        </ol>
      </section>

      <p className="text-xs text-slate-400">
        Scored against model {appraisal.modelVersion} on{" "}
        {new Date(result.computedAt).toLocaleString("en-GB")}. Weights:{" "}
        {result.weightStatus.state}.
      </p>
    </div>
  );
}

function ObjectiveCard({ objective }: { objective: ObjectiveResult }) {
  return (
    <div className="rounded-lg border border-slate-200 bg-white p-5">
      <div className="text-xs font-medium uppercase tracking-wide text-slate-500">
        {objective.name}
      </div>
      <div className="mt-1 flex items-baseline gap-2">
        <span className="text-4xl font-semibold tabular-nums text-slate-900">
          {objective.score?.toFixed(1) ?? "—"}
        </span>
        <span className="text-sm text-slate-400">/ 100</span>
        <span className="ml-auto text-xs text-slate-500">
          {Math.round(objective.completeness * 100)}% assessed
        </span>
      </div>

      {objective.sufficient && objective.band ? (
        <div
          className={`mt-3 rounded border px-3 py-2 text-sm font-medium ${bandClass(objective.band.code)}`}
        >
          Band {objective.band.code} — {objective.band.label}
          <div className="text-xs font-normal opacity-80">
            {objective.band.action}
          </div>
        </div>
      ) : (
        <div className="mt-3 rounded border border-slate-300 bg-slate-50 px-3 py-2 text-sm text-slate-700">
          Recommendation withheld
          <div className="text-xs text-slate-500">
            Only {Math.round(objective.completeness * 100)}% of criteria assessed;{" "}
            {Math.round(
              criteriaTree.completenessPolicy.minObjectiveCompleteness * 100,
            )}
            % is required before a band is issued.
            {objective.missingCriteria.length > 0 && (
              <> {objective.missingCriteria.length} criteria outstanding.</>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

function Breakdown({ objective }: { objective: ObjectiveResult }) {
  const assessed = objective.dimensions.filter((d) => d.score !== null);

  return (
    <section className="rounded-lg border border-slate-200 bg-white p-5">
      <h2 className="text-sm font-semibold text-slate-900">
        {objective.name} — contribution breakdown
      </h2>
      <p className="mt-0.5 text-xs text-slate-500">
        Contributions sum to the objective score. Every criterion cites the clause
        of the People&apos;s Bank form it came from.
      </p>

      <div className="mt-4 space-y-5">
        {assessed.map((dimension) => (
          <div key={dimension.id}>
            <div className="flex items-baseline justify-between gap-4">
              <h3 className="text-sm font-medium text-slate-800">
                {dimension.name}
                <span className="ml-2 text-xs font-normal text-slate-400">
                  clause {dimension.ref}
                </span>
              </h3>
              <div className="text-sm tabular-nums text-slate-600">
                {dimension.score?.toFixed(1)}
                <span className="ml-2 text-xs text-slate-400">
                  contributes {dimension.contribution.toFixed(1)} pts
                </span>
              </div>
            </div>

            <div className="mt-1.5 h-2 w-full rounded-full bg-slate-100">
              <div
                className={`h-2 rounded-full ${scoreBar(dimension.score ?? 0)}`}
                style={{ width: `${dimension.score ?? 0}%` }}
              />
            </div>

            <table className="mt-2 w-full text-xs">
              <tbody>
                {dimension.criteria
                  .filter((c) => c.assessed)
                  .sort((a, b) => b.contribution - a.contribution)
                  .map((c) => (
                    <tr key={c.id} className="text-slate-600">
                      <td className="py-0.5 pr-2">{c.name}</td>
                      <td className="w-20 py-0.5 text-right tabular-nums text-slate-400">
                        {String(c.rawValue)}
                      </td>
                      <td className="w-12 py-0.5 text-right tabular-nums text-slate-900">
                        {c.score?.toFixed(0)}
                      </td>
                      <td className="w-24 py-0.5 text-right tabular-nums text-slate-500">
                        {c.contribution.toFixed(1)} pts
                      </td>
                    </tr>
                  ))}
              </tbody>
            </table>
          </div>
        ))}
      </div>
    </section>
  );
}
