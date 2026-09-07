"use client";

import { useMemo, useState, useTransition } from "react";

import { createAppraisal, type AppraisalHeader } from "@/lib/actions";
import { appraise, criteriaTree } from "@/lib/scoring";
import type { AppraisalInput, LinguisticCode } from "@/lib/scoring/types";

const LEVELS = criteriaTree.linguisticScale.levels;

const LEVEL_STYLES: Record<LinguisticCode, string> = {
  VP: "bg-red-600 text-white border-red-600",
  P: "bg-orange-500 text-white border-orange-500",
  F: "bg-amber-400 text-slate-900 border-amber-400",
  G: "bg-lime-600 text-white border-lime-600",
  E: "bg-emerald-600 text-white border-emerald-600",
};

function bandColour(code?: string) {
  switch (code) {
    case "A": return "text-emerald-700 bg-emerald-50 border-emerald-300";
    case "B": return "text-lime-700 bg-lime-50 border-lime-300";
    case "C": return "text-amber-700 bg-amber-50 border-amber-300";
    case "D": return "text-red-700 bg-red-50 border-red-300";
    default: return "text-slate-600 bg-slate-50 border-slate-300";
  }
}

export function AppraisalForm() {
  const [header, setHeader] = useState<AppraisalHeader>({
    businessName: "",
    branch: "",
    facilityAmount: 0,
    facilityType: "Term Loan",
    projectType: "New",
    appraisalOfficer: "",
    district: "",
    organisationType: "Proprietorship",
  });

  const [inputs, setInputs] = useState<AppraisalInput>({});
  const [pending, startTransition] = useTransition();

  // Live scoring. The engine is pure TypeScript with no I/O, so the officer sees
  // the score and its breakdown update as the file is filled in, rather than
  // discovering the outcome only on submission.
  const result = useMemo(() => appraise(inputs, criteriaTree), [inputs]);

  const credit = result.objectives.find((o) => o.id === "credit_risk");
  const development = result.objectives.find((o) => o.id === "development_impact");

  function setValue(id: string, value: number | LinguisticCode | null) {
    setInputs((prev) => {
      const next = { ...prev };
      if (value === null || (typeof value === "number" && Number.isNaN(value))) {
        delete next[id];
      }
      else next[id] = value;
      return next;
    });
  }

  const headerValid =
    header.businessName.trim() !== "" &&
    header.branch.trim() !== "" &&
    header.appraisalOfficer.trim() !== "" &&
    header.facilityAmount > 0;

  function submit() {
    startTransition(async () => {
      await createAppraisal(header, inputs);
    });
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-[1fr_360px] gap-6">
      <div className="space-y-6">
        {/* ---- General information: form clauses 1 and 2 ---- */}
        <section className="rounded-lg border border-slate-200 bg-white p-5">
          <h2 className="text-base font-semibold text-slate-900">
            General Information
          </h2>
          <p className="mt-0.5 text-xs text-slate-500">
            People&apos;s Bank appraisal form, clauses 1 &amp; 2
          </p>

          <div className="mt-4 grid grid-cols-1 sm:grid-cols-2 gap-4">
            <Field label="Business name" required>
              <input
                className="input"
                value={header.businessName}
                onChange={(e) => setHeader({ ...header, businessName: e.target.value })}
              />
            </Field>
            <Field label="Branch" required>
              <input
                className="input"
                value={header.branch}
                onChange={(e) => setHeader({ ...header, branch: e.target.value })}
              />
            </Field>
            <Field label="District">
              <input
                className="input"
                value={header.district}
                onChange={(e) => setHeader({ ...header, district: e.target.value })}
              />
            </Field>
            <Field label="Facility amount (Rs.)" required>
              <input
                type="number"
                className="input"
                value={header.facilityAmount || ""}
                onChange={(e) =>
                  setHeader({ ...header, facilityAmount: Number(e.target.value) })
                }
              />
            </Field>
            <Field label="Type of facility">
              <select
                className="input"
                value={header.facilityType}
                onChange={(e) => setHeader({ ...header, facilityType: e.target.value })}
              >
                <option>Term Loan</option>
                <option>Working Capital</option>
                <option>Overdraft</option>
                <option>Leasing</option>
              </select>
            </Field>
            <Field label="Project type">
              <select
                className="input"
                value={header.projectType}
                onChange={(e) => setHeader({ ...header, projectType: e.target.value })}
              >
                <option>New</option>
                <option>Expansion</option>
                <option>Cost Overrun</option>
                <option>Working Capital</option>
              </select>
            </Field>
            <Field label="Organisation">
              <select
                className="input"
                value={header.organisationType}
                onChange={(e) =>
                  setHeader({ ...header, organisationType: e.target.value })
                }
              >
                <option>Proprietorship</option>
                <option>Partnership</option>
                <option>Limited Company</option>
                <option>Co-operative</option>
              </select>
            </Field>
            <Field label="Appraisal officer" required>
              <input
                className="input"
                value={header.appraisalOfficer}
                onChange={(e) =>
                  setHeader({ ...header, appraisalOfficer: e.target.value })
                }
              />
            </Field>
          </div>
        </section>

        {/* ---- Criteria, grouped by objective and dimension ---- */}
        {criteriaTree.objectives.map((objective) => (
          <div key={objective.id} className="space-y-4">
            <div className="flex items-baseline gap-3 pt-2">
              <h2 className="text-lg font-semibold text-slate-900">
                {objective.name}
              </h2>
              {objective.id === "development_impact" && (
                <span className="rounded bg-indigo-50 px-2 py-0.5 text-xs font-medium text-indigo-700 border border-indigo-200">
                  scored separately
                </span>
              )}
            </div>

            {objective.dimensions.map((dimension) => {
              const dimResult = (objective.id === "credit_risk" ? credit : development)
                ?.dimensions.find((d) => d.id === dimension.id);

              return (
                <section
                  key={dimension.id}
                  className="rounded-lg border border-slate-200 bg-white p-5"
                >
                  <div className="flex items-start justify-between gap-4">
                    <div>
                      <h3 className="text-sm font-semibold text-slate-900">
                        {dimension.name}
                      </h3>
                      <p className="mt-0.5 text-xs text-slate-500">
                        form clause {dimension.ref}
                      </p>
                    </div>
                    <div className="text-right shrink-0">
                      <div className="text-lg font-semibold tabular-nums text-slate-900">
                        {dimResult?.score?.toFixed(1) ?? "—"}
                      </div>
                      <div className="text-xs text-slate-500">
                        {Math.round((dimResult?.completeness ?? 0) * 100)}% assessed
                      </div>
                    </div>
                  </div>

                  <div className="mt-4 space-y-3">
                    {dimension.criteria.map((criterion) => {
                      const critResult = dimResult?.criteria.find(
                        (c) => c.id === criterion.id,
                      );

                      return (
                        <div
                          key={criterion.id}
                          className="grid grid-cols-1 sm:grid-cols-[1fr_auto] gap-2 sm:gap-4 sm:items-center border-b border-slate-100 pb-3 last:border-0 last:pb-0"
                        >
                          <div className="min-w-0">
                            <label className="text-sm text-slate-800">
                              {criterion.name}
                              {criterion.critical && (
                                <span className="ml-2 rounded bg-red-50 px-1.5 py-0.5 text-[10px] font-medium text-red-700 border border-red-200">
                                  critical
                                </span>
                              )}
                            </label>
                            <div className="text-xs text-slate-400">
                              clause {criterion.ref}
                              {criterion.unit ? ` · ${criterion.unit}` : ""}
                            </div>
                          </div>

                          <div className="flex items-center gap-2 shrink-0">
                            {criterion.type === "quantitative" ? (
                              <input
                                type="number"
                                step="any"
                                placeholder="—"
                                className="input w-28 text-right tabular-nums"
                                value={
                                  typeof inputs[criterion.id] === "number"
                                    ? (inputs[criterion.id] as number)
                                    : ""
                                }
                                onChange={(e) =>
                                  setValue(
                                    criterion.id,
                                    e.target.value === "" ? null : Number(e.target.value),
                                  )
                                }
                              />
                            ) : (
                              <div className="flex gap-1">
                                {LEVELS.map((level) => {
                                  const active = inputs[criterion.id] === level.code;
                                  return (
                                    <button
                                      key={level.code}
                                      type="button"
                                      title={level.label}
                                      onClick={() =>
                                        setValue(
                                          criterion.id,
                                          active ? null : level.code,
                                        )
                                      }
                                      className={`h-8 w-9 rounded border text-xs font-semibold transition ${
                                        active
                                          ? LEVEL_STYLES[level.code]
                                          : "border-slate-200 bg-white text-slate-400 hover:border-slate-400"
                                      }`}
                                    >
                                      {level.code}
                                    </button>
                                  );
                                })}
                              </div>
                            )}

                            <div className="w-12 text-right text-sm tabular-nums text-slate-500">
                              {critResult?.assessed ? critResult.score?.toFixed(0) : "—"}
                            </div>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </section>
              );
            })}
          </div>
        ))}
      </div>

      {/* ---- Live score panel ---- */}
      <aside className="lg:sticky lg:top-6 h-fit space-y-4">
        <div className="rounded-lg border border-slate-200 bg-white p-5">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-semibold text-slate-900">Live assessment</h3>
            <span className="text-xs text-slate-500">
              {Math.round(result.overallCompleteness * 100)}% complete
            </span>
          </div>

          <div className="mt-2 h-1.5 w-full rounded-full bg-slate-100">
            <div
              className="h-1.5 rounded-full bg-slate-800 transition-all"
              style={{ width: `${result.overallCompleteness * 100}%` }}
            />
          </div>

          {[credit, development].map((objective) =>
            objective ? (
              <div key={objective.id} className="mt-5 first:mt-4">
                <div className="text-xs font-medium uppercase tracking-wide text-slate-500">
                  {objective.name}
                </div>
                <div className="mt-1 flex items-baseline gap-2">
                  <span className="text-3xl font-semibold tabular-nums text-slate-900">
                    {objective.score?.toFixed(1) ?? "—"}
                  </span>
                  <span className="text-sm text-slate-400">/ 100</span>
                </div>

                {objective.sufficient && objective.band ? (
                  <div
                    className={`mt-2 rounded border px-2.5 py-1.5 text-xs font-medium ${bandColour(objective.band.code)}`}
                  >
                    Band {objective.band.code} · {objective.band.action}
                  </div>
                ) : (
                  <div className="mt-2 rounded border border-slate-300 bg-slate-50 px-2.5 py-1.5 text-xs text-slate-600">
                    No recommendation —{" "}
                    {Math.round(objective.completeness * 100)}% assessed, below the{" "}
                    {Math.round(
                      criteriaTree.completenessPolicy.minObjectiveCompleteness * 100,
                    )}
                    % required
                  </div>
                )}
              </div>
            ) : null,
          )}
        </div>

        {result.criticalBreaches.length > 0 && (
          <div className="rounded-lg border border-red-300 bg-red-50 p-4">
            <h3 className="text-sm font-semibold text-red-900">Critical breach</h3>
            <ul className="mt-2 space-y-2">
              {result.criticalBreaches.map((breach) => (
                <li key={breach.id} className="text-xs text-red-800">
                  <span className="font-medium">{breach.name}</span> ={" "}
                  {String(breach.rawValue)}
                  {breach.criticalNote && (
                    <p className="mt-0.5 text-red-700/80">{breach.criticalNote}</p>
                  )}
                </li>
              ))}
            </ul>
          </div>
        )}

        <div className="rounded-lg border border-amber-300 bg-amber-50 p-4">
          <h3 className="text-xs font-semibold text-amber-900">
            Weights: {result.weightStatus.state}
          </h3>
          <p className="mt-1 text-xs text-amber-800/90">
            Criterion weights have not been elicited. Scores are structurally
            valid but must not be reported as research results.
          </p>
        </div>

        <button
          type="button"
          disabled={!headerValid || pending}
          onClick={submit}
          className="w-full rounded-md bg-slate-900 px-4 py-2.5 text-sm font-medium text-white hover:bg-slate-800 disabled:cursor-not-allowed disabled:bg-slate-300"
        >
          {pending ? "Saving…" : "Save appraisal"}
        </button>
        {!headerValid && (
          <p className="text-center text-xs text-slate-500">
            Business name, branch, officer and facility amount are required
          </p>
        )}
      </aside>
    </div>
  );
}

function Field({
  label,
  required,
  children,
}: {
  label: string;
  required?: boolean;
  children: React.ReactNode;
}) {
  return (
    <div>
      <label className="block text-xs font-medium text-slate-600">
        {label}
        {required && <span className="ml-0.5 text-red-500">*</span>}
      </label>
      <div className="mt-1">{children}</div>
    </div>
  );
}
