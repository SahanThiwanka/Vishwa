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
    allowed: ["RECOMMENDER", "HEAD_OFFICE", "ADMIN"],
    tone: "border-slate-300 bg-white text-slate-800 hover:bg-slate-50",
  },
  {
    action: "APPROVED" as const,
    label: "Approve",
    allowed: ["HEAD_OFFICE", "ADMIN"],
    tone: "border-emerald-600 bg-emerald-600 text-white hover:bg-emerald-700",
  },
  {
    action: "DECLINED" as const,
    label: "Decline",
    allowed: ["HEAD_OFFICE", "ADMIN"],
    tone: "border-red-600 bg-red-600 text-white hover:bg-red-700",
  },
];

export function DecisionPanel({
  appraisalId,
  status,
  user,
}: {
  appraisalId: string;
  status: string;
  user: { displayName: string; role: string };
}) {
  const [note, setNote] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [pending, startTransition] = useTransition();

  const settled = status === "APPROVED" || status === "DECLINED";

  function submit(action: (typeof STEPS)[number]["action"]) {
    setError(null);
    startTransition(async () => {
      try {
        await recordDecision(appraisalId, action, note || undefined);
        setNote("");
      } catch (e) {
        setError(e instanceof Error ? e.message : "Could not record the decision");
      }
    });
  }

  const permitted = STEPS.filter((s) => s.allowed.includes(user.role));

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

      <div className="mt-4">
        <p className="text-xs text-slate-500">
          Signing as{" "}
          <span className="font-medium text-slate-800">{user.displayName}</span>{" "}
          ({user.role})
        </p>
        <label
          htmlFor="decision-note"
          className="mt-3 block text-xs font-medium text-slate-600"
        >
          Note (optional)
        </label>
        <input
          id="decision-note"
          className="input mt-1"
          value={note}
          onChange={(e) => setNote(e.target.value)}
          placeholder="Conditions, observations"
        />
      </div>

      {error && (
        <p className="mt-3 rounded border border-red-300 bg-red-50 px-3 py-2 text-xs text-red-800">
          {error}
        </p>
      )}

      <div className="mt-4 flex flex-wrap gap-2">
        {permitted.map((step) => (
          <button
            key={step.action}
            type="button"
            disabled={pending}
            onClick={() => submit(step.action)}
            className={`rounded-md border px-4 py-2 text-sm font-medium transition disabled:cursor-not-allowed disabled:border-slate-200 disabled:bg-slate-100 disabled:text-slate-400 ${step.tone}`}
          >
            {pending ? "Recording…" : step.label}
          </button>
        ))}
      </div>

      {permitted.length === 0 && (
        <p className="mt-2 text-xs text-slate-500">
          Your role ({user.role}) cannot sign off on appraisals. A recommending
          officer or Head Office must act on this file.
        </p>
      )}
    </section>
  );
}
