"use client";

import { useMemo, useState, useTransition } from "react";

import {
  saveElicitation,
  type ElicitationLevelResponse,
  type Respondent,
} from "@/lib/actions";
import { criteriaTree } from "@/lib/scoring";

/** One comparison level: a set of sibling items judged against each other. */
interface Level {
  key: string;
  title: string;
  context: string;
  items: { id: string; name: string; ref?: string }[];
}

/** Saaty's 1-9 scale, worded for practitioners rather than for a textbook. */
const SCALE: { value: number; label: string }[] = [
  { value: 1, label: "1 — equally important" },
  { value: 2, label: "2" },
  { value: 3, label: "3 — moderately more important" },
  { value: 4, label: "4" },
  { value: 5, label: "5 — strongly more important" },
  { value: 6, label: "6" },
  { value: 7, label: "7 — very strongly more important" },
  { value: 8, label: "8" },
  { value: 9, label: "9 — extremely more important" },
];

function buildLevels(): Level[] {
  const levels: Level[] = [];

  for (const objective of criteriaTree.objectives) {
    // Comparing dimensions only makes sense when there is more than one.
    if (objective.dimensions.length > 1) {
      levels.push({
        key: `objective:${objective.id}`,
        title: `${objective.name} — which areas matter most?`,
        context:
          "Compare the broad areas of the appraisal against each other, as they " +
          "bear on this objective.",
        items: objective.dimensions.map((d) => ({
          id: d.id,
          name: d.name,
          ref: d.ref,
        })),
      });
    }

    for (const dimension of objective.dimensions) {
      levels.push({
        key: `dimension:${dimension.id}`,
        title: dimension.name,
        context: `Within this area only (form clause ${dimension.ref}), compare the individual criteria.`,
        items: dimension.criteria.map((c) => ({
          id: c.id,
          name: c.name,
          ref: c.ref,
        })),
      });
    }
  }

  return levels;
}

interface LevelAnswer {
  best?: string;
  worst?: string;
  bestToOthers: Record<string, number>;
  othersToWorst: Record<string, number>;
}

export function ElicitationWizard() {
  const levels = useMemo(() => buildLevels(), []);

  const [respondent, setRespondent] = useState<Respondent>({
    respondentCode: "",
    yearsExperience: undefined,
    institution: "",
    role: "",
  });

  const [step, setStep] = useState(-1); // -1 is the participant-details step
  const [answers, setAnswers] = useState<Record<string, LevelAnswer>>({});
  const [pending, startTransition] = useTransition();
  const [done, setDone] = useState(false);

  const totalComparisons = levels.reduce((s, l) => s + 2 * l.items.length - 3, 0);

  function answerFor(key: string): LevelAnswer {
    return answers[key] ?? { bestToOthers: {}, othersToWorst: {} };
  }

  function update(key: string, patch: Partial<LevelAnswer>) {
    setAnswers((prev) => ({
      ...prev,
      [key]: { ...answerFor(key), ...patch },
    }));
  }

  const level = step >= 0 ? levels[step] : null;
  const answer = level ? answerFor(level.key) : null;

  const levelComplete =
    level && answer && answer.best && answer.worst && answer.best !== answer.worst
      ? level.items.every(
          (i) =>
            i.id === answer.best ||
            typeof answer.bestToOthers[i.id] === "number",
        ) &&
        level.items.every(
          (i) =>
            i.id === answer.worst ||
            typeof answer.othersToWorst[i.id] === "number",
        )
      : false;

  function submit() {
    startTransition(async () => {
      const payload: ElicitationLevelResponse[] = levels.map((l) => {
        const a = answerFor(l.key);
        return {
          level: l.key,
          best: a.best!,
          worst: a.worst!,
          // The best-vs-itself and worst-vs-itself entries are 1 by definition.
          bestToOthers: { ...a.bestToOthers, [a.best!]: 1 },
          othersToWorst: { ...a.othersToWorst, [a.worst!]: 1 },
        };
      });
      await saveElicitation(respondent, payload);
      setDone(true);
    });
  }

  if (done) {
    return (
      <div className="rounded-lg border border-emerald-300 bg-emerald-50 p-8 text-center">
        <h2 className="text-lg font-semibold text-emerald-900">Thank you</h2>
        <p className="mt-2 text-sm text-emerald-800">
          Your responses have been recorded under code{" "}
          <span className="font-mono">{respondent.respondentCode}</span>.
        </p>
      </div>
    );
  }

  // ---- participant details ----
  if (step === -1) {
    const canStart = respondent.respondentCode.trim().length > 0;
    return (
      <div className="mx-auto max-w-2xl space-y-6">
        <div className="rounded-lg border border-slate-200 bg-white p-6">
          <h2 className="text-base font-semibold text-slate-900">
            Criterion weighting study
          </h2>
          <div className="mt-3 space-y-3 text-sm text-slate-600">
            <p>
              This exercise asks how much weight the different parts of an SME
              credit appraisal should carry. It takes about 15 minutes and
              involves {totalComparisons} quick comparisons.
            </p>
            <p>
              There are no right answers — the study is measuring experienced
              judgement, including where practitioners disagree.
            </p>
            <p className="rounded border border-slate-200 bg-slate-50 p-3 text-xs">
              <strong>Participation and confidentiality.</strong> Participation is
              voluntary and you may stop at any point. Do not enter your name or
              any customer information. Responses are identified only by the code
              you choose below, are used solely for academic research, and are
              reported only in aggregate.
            </p>
          </div>

          <div className="mt-5 grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-medium text-slate-600">
                Participant code <span className="text-red-500">*</span>
              </label>
              <input
                className="input mt-1"
                placeholder="e.g. R01"
                value={respondent.respondentCode}
                onChange={(e) =>
                  setRespondent({ ...respondent, respondentCode: e.target.value })
                }
              />
              <p className="mt-1 text-xs text-slate-400">
                Any code you will remember. Not your name.
              </p>
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-600">
                Years in credit / appraisal work
              </label>
              <input
                type="number"
                className="input mt-1"
                value={respondent.yearsExperience ?? ""}
                onChange={(e) =>
                  setRespondent({
                    ...respondent,
                    yearsExperience: e.target.value ? Number(e.target.value) : undefined,
                  })
                }
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-600">
                Institution type
              </label>
              <select
                className="input mt-1"
                value={respondent.institution}
                onChange={(e) =>
                  setRespondent({ ...respondent, institution: e.target.value })
                }
              >
                <option value="">—</option>
                <option>State commercial bank</option>
                <option>Private commercial bank</option>
                <option>Licensed finance company</option>
                <option>Development bank</option>
                <option>Other</option>
              </select>
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-600">Role</label>
              <select
                className="input mt-1"
                value={respondent.role}
                onChange={(e) => setRespondent({ ...respondent, role: e.target.value })}
              >
                <option value="">—</option>
                <option>Credit / appraisal officer</option>
                <option>Branch manager</option>
                <option>Credit committee member</option>
                <option>Regional / head office credit</option>
                <option>Other</option>
              </select>
            </div>
          </div>

          <button
            type="button"
            disabled={!canStart}
            onClick={() => setStep(0)}
            className="mt-6 w-full rounded-md bg-slate-900 px-4 py-2.5 text-sm font-medium text-white hover:bg-slate-800 disabled:bg-slate-300"
          >
            Begin
          </button>
        </div>
      </div>
    );
  }

  if (!level || !answer) return null;

  const others = level.items.filter((i) => i.id !== answer.best);
  const toWorst = level.items.filter((i) => i.id !== answer.worst);

  return (
    <div className="mx-auto max-w-3xl space-y-4">
      <div>
        <div className="flex items-center justify-between text-xs text-slate-500">
          <span>
            Section {step + 1} of {levels.length}
          </span>
          <span>{Math.round(((step + 1) / levels.length) * 100)}%</span>
        </div>
        <div className="mt-1 h-1.5 w-full rounded-full bg-slate-200">
          <div
            className="h-1.5 rounded-full bg-slate-800 transition-all"
            style={{ width: `${((step + 1) / levels.length) * 100}%` }}
          />
        </div>
      </div>

      <div className="rounded-lg border border-slate-200 bg-white p-6">
        <h2 className="text-base font-semibold text-slate-900">{level.title}</h2>
        <p className="mt-1 text-sm text-slate-500">{level.context}</p>

        {/* Step 1 - pick best */}
        <div className="mt-5">
          <h3 className="text-sm font-medium text-slate-800">
            1. Which is the <span className="text-emerald-700">most</span> important?
          </h3>
          <div className="mt-2 flex flex-wrap gap-2">
            {level.items.map((item) => (
              <button
                key={item.id}
                type="button"
                onClick={() => update(level.key, { best: item.id })}
                className={`rounded border px-3 py-1.5 text-xs transition ${
                  answer.best === item.id
                    ? "border-emerald-600 bg-emerald-600 text-white"
                    : "border-slate-300 bg-white text-slate-700 hover:border-slate-500"
                }`}
              >
                {item.name}
              </button>
            ))}
          </div>
        </div>

        {/* Step 2 - pick worst */}
        {answer.best && (
          <div className="mt-5">
            <h3 className="text-sm font-medium text-slate-800">
              2. Which is the <span className="text-red-700">least</span> important?
            </h3>
            <div className="mt-2 flex flex-wrap gap-2">
              {level.items
                .filter((i) => i.id !== answer.best)
                .map((item) => (
                  <button
                    key={item.id}
                    type="button"
                    onClick={() => update(level.key, { worst: item.id })}
                    className={`rounded border px-3 py-1.5 text-xs transition ${
                      answer.worst === item.id
                        ? "border-red-600 bg-red-600 text-white"
                        : "border-slate-300 bg-white text-slate-700 hover:border-slate-500"
                    }`}
                  >
                    {item.name}
                  </button>
                ))}
            </div>
          </div>
        )}

        {/* Step 3 - best vs others */}
        {answer.best && answer.worst && (
          <div className="mt-6 border-t border-slate-100 pt-5">
            <h3 className="text-sm font-medium text-slate-800">
              3. How much more important is{" "}
              <span className="text-emerald-700">
                {level.items.find((i) => i.id === answer.best)?.name}
              </span>{" "}
              than each of these?
            </h3>
            <div className="mt-3 space-y-2">
              {others.map((item) => (
                <div key={item.id} className="grid grid-cols-[1fr_auto] items-center gap-3">
                  <span className="text-sm text-slate-700">{item.name}</span>
                  <select
                    className="input w-64"
                    value={answer.bestToOthers[item.id] ?? ""}
                    onChange={(e) =>
                      update(level.key, {
                        bestToOthers: {
                          ...answer.bestToOthers,
                          [item.id]: Number(e.target.value),
                        },
                      })
                    }
                  >
                    <option value="">Choose…</option>
                    {SCALE.map((s) => (
                      <option key={s.value} value={s.value}>
                        {s.label}
                      </option>
                    ))}
                  </select>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Step 4 - others vs worst */}
        {answer.best && answer.worst && (
          <div className="mt-6 border-t border-slate-100 pt-5">
            <h3 className="text-sm font-medium text-slate-800">
              4. How much more important is each of these than{" "}
              <span className="text-red-700">
                {level.items.find((i) => i.id === answer.worst)?.name}
              </span>
              ?
            </h3>
            <div className="mt-3 space-y-2">
              {toWorst.map((item) => (
                <div key={item.id} className="grid grid-cols-[1fr_auto] items-center gap-3">
                  <span className="text-sm text-slate-700">{item.name}</span>
                  <select
                    className="input w-64"
                    value={answer.othersToWorst[item.id] ?? ""}
                    onChange={(e) =>
                      update(level.key, {
                        othersToWorst: {
                          ...answer.othersToWorst,
                          [item.id]: Number(e.target.value),
                        },
                      })
                    }
                  >
                    <option value="">Choose…</option>
                    {SCALE.map((s) => (
                      <option key={s.value} value={s.value}>
                        {s.label}
                      </option>
                    ))}
                  </select>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      <div className="flex items-center justify-between">
        <button
          type="button"
          onClick={() => setStep((s) => s - 1)}
          className="rounded-md border border-slate-300 bg-white px-4 py-2 text-sm text-slate-700 hover:bg-slate-50"
        >
          Back
        </button>

        {step < levels.length - 1 ? (
          <button
            type="button"
            disabled={!levelComplete}
            onClick={() => setStep((s) => s + 1)}
            className="rounded-md bg-slate-900 px-5 py-2 text-sm font-medium text-white hover:bg-slate-800 disabled:bg-slate-300"
          >
            Next
          </button>
        ) : (
          <button
            type="button"
            disabled={!levelComplete || pending}
            onClick={submit}
            className="rounded-md bg-emerald-700 px-5 py-2 text-sm font-medium text-white hover:bg-emerald-800 disabled:bg-slate-300"
          >
            {pending ? "Saving…" : "Submit responses"}
          </button>
        )}
      </div>
    </div>
  );
}
