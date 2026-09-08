"use client";

import { useState, useTransition } from "react";

import { recordDecision } from "@/lib/actions";

/**
 * Records a step in the sign-off chain from clause 7 of the People's Bank form:
 * the appraisal officer prepares, a recommending officer endorses, and Head
 * Office approves or declines.
 *
 * Every transition is written to the audit trail with the score as it stood at
 * the time, so the record shows not just who signed but what they were signing
 * against. Nothing is ever deleted.
 */

const STEPS = [
  {
    action: "RECOMMENDED" as const,
    label: "Recommend",
    role: "Recommending Officer",
    tone: "border-slate-300 bg-white text-slate-800 hover:bg-slate-50",
  },
  {
    action: "APPROVED" as const,
    label: "Approve",
    role: "Head Office",
    tone: "border-emerald-600 bg-emerald-600 text-white hover:bg-emerald-700",
  },
  {
    action: "DECLINED" as const,
    label: "Decline",
    role: "Head Office",
    tone: "border-red-600 bg-red-600 text-white hover:bg-red-700",
  },
];

export function DecisionPanel({
  appraisalId,
  status,
}: {
  appraisalId: string;
  status: string;
}) {
  const [actor, setActor] = useState("");
  const [note, setNote] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [pending, startTransition] = useTransition();

  const settled = status === "APPROVED" || status === "DECLINED";

  function submit(action: (typeof STEPS)[number]["action"], role: string) {
    setError(null);
    startTransition(async () => {
      try {
        await recordDecision(appraisalId, action, actor, role, note || undefined);
        setNote("");
      } catch (e) {
        setError(e instanceof Error ? e.message : "Could not record the decision");
      }
    });
  }

  if (settled) {
    return (
      <section className="rounded-lg border border-slate-200 bg-white p-5">
        <h2 className="text-sm font-semibold text-slate-900">Sign-off</h2>
        <p className="mt-1 text-sm text-slate-600">
          This appraisal is {status.toLowerCase()}. The decision is recorded in the
          audit trail and cannot be altered — a correction is made by raising a new
          appraisal, not by rewriting this one.
        </p>
      </section>
    );
  }

  return (
    <section className="rounded-lg border border-slate-200 bg-white p-5">
      <h2 className="text-sm font-semibold text-slate-900">Sign-off</h2>
      <p className="mt-0.5 text-xs text-slate-500">
        Clause 7 of the appraisal form. Current status:{" "}
        <span className="font-medium text-slate-700">{status}</span>
      </p>

      <div className="mt-4 grid grid-cols-1 sm:grid-cols-2 gap-3">
        <div>
          <label className="block text-xs font-medium text-slate-600">
            Name &amp; designation <span className="text-red-500">*</span>
          </label>
          <input
            className="input mt-1"
            value={actor}
            onChange={(e) => setActor(e.target.value)}
            placeholder="e.g. K. Perera, Branch Manager"
          />
        </div>
        <div>
          <label className="block text-xs font-medium text-slate-600">
            Note (optional)
          </label>
          <input
            className="input mt-1"
            value={note}
            onChange={(e) => setNote(e.target.value)}
            placeholder="Conditions, observations"
          />
        </div>
      </div>

      {error && (
        <p className="mt-3 rounded border border-red-300 bg-red-50 px-3 py-2 text-xs text-red-800">
          {error}
        </p>
      )}

      <div className="mt-4 flex flex-wrap gap-2">
        {STEPS.map((step) => (
          <button
            key={step.action}
            type="button"
            disabled={!actor.trim() || pending}
            onClick={() => submit(step.action, step.role)}
            className={`rounded-md border px-4 py-2 text-sm font-medium transition disabled:cursor-not-allowed disabled:border-slate-200 disabled:bg-slate-100 disabled:text-slate-400 ${step.tone}`}
          >
            {pending ? "Recording…" : step.label}
          </button>
        ))}
      </div>

      {!actor.trim() && (
        <p className="mt-2 text-xs text-slate-500">
          Enter a name and designation before signing off.
        </p>
      )}
    </section>
  );
}
