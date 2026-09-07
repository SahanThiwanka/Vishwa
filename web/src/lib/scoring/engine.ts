/**
 * The scoring engine: walks the criteria tree, scores an appraisal, and reports
 * both objectives separately with a full per-criterion contribution breakdown.
 *
 * Design commitments worth defending in a viva:
 *
 *  1. Credit risk and development impact are NEVER merged into one number. A
 *     project can be bankable but developmentally thin, or vice versa, and that
 *     trade-off is the point of the study.
 *  2. Unassessed criteria are excluded and weights renormalised - never treated
 *     as zero, which would score an incomplete file as a bad one.
 *  3. Critical criteria (DSCR < 1.0) surface as explicit breaches rather than
 *     being smoothed away by a weighted average.
 *  4. Every score carries its contribution decomposition, so the recommendation
 *     is explainable clause by clause back to the bank's own form.
 */

import {
  crisp,
  defuzzify,
  round1,
  scoreFromBands,
  weightedAverage,
} from "./fuzzy";
import type {
  AppraisalInput,
  AppraisalResult,
  CriteriaTree,
  Criterion,
  CriterionResult,
  Dimension,
  DimensionResult,
  LinguisticCode,
  Objective,
  ObjectiveResult,
  RiskBand,
  TFN,
} from "./types";

/** Equal weight fallback while `weightStatus.state === "PLACEHOLDER"`. */
function effectiveWeight(weight: number | null | undefined, siblings: number): number {
  if (typeof weight === "number" && weight > 0) return weight;
  return 1 / siblings;
}

function scoreCriterion(
  criterion: Criterion,
  input: AppraisalInput,
  tree: CriteriaTree,
  siblings: number,
): CriterionResult {
  const raw = input[criterion.id] ?? null;
  const weight = effectiveWeight(criterion.weight, siblings);

  const base: CriterionResult = {
    id: criterion.id,
    name: criterion.name,
    ref: criterion.ref,
    type: criterion.type,
    rawValue: raw,
    score: null,
    tfn: null,
    weight,
    contribution: 0,
    assessed: false,
    criticalBreach: false,
    criticalNote: criterion.criticalNote,
  };

  if (raw === null || raw === undefined) return base;

  let tfn: TFN;

  if (criterion.type === "quantitative") {
    if (typeof raw !== "number" || Number.isNaN(raw)) return base;
    if (!criterion.bands) return base;
    tfn = crisp(scoreFromBands(raw, criterion.bands));
  } else {
    const level = tree.linguisticScale.levels.find((l) => l.code === raw);
    if (!level) return base;
    tfn = level.tfn;
  }

  const score = defuzzify(tfn);

  // A critical breach is judged on the RAW value against the criterion's own
  // knock-out threshold, not on the derived score, so it cannot be diluted.
  const criticalBreach =
    criterion.critical === true &&
    typeof raw === "number" &&
    criterion.bands !== undefined &&
    raw < knockoutThreshold(criterion);

  return {
    ...base,
    score: round1(score),
    tfn,
    assessed: true,
    criticalBreach,
  };
}

/**
 * The raw value below which a critical criterion is treated as a breach.
 * Taken as the anchor scoring 25 - the boundary between "Poor" and worse on the
 * linguistic scale. For DSCR this evaluates to 1.0, matching standard credit policy.
 */
function knockoutThreshold(criterion: Criterion): number {
  const anchor = criterion.bands?.find((b) => b[1] >= 25);
  return anchor ? anchor[0] : 0;
}

function scoreDimension(
  dimension: Dimension,
  input: AppraisalInput,
  tree: CriteriaTree,
  siblings: number,
): DimensionResult {
  const criteria = dimension.criteria.map((c) =>
    scoreCriterion(c, input, tree, dimension.criteria.length),
  );

  const assessed = criteria.filter((c) => c.assessed && c.tfn);
  const tfn = weightedAverage(
    assessed.map((c) => ({ tfn: c.tfn as TFN, weight: c.weight })),
  );

  // Contribution: each criterion's share of this dimension's score, in points.
  // These sum to the dimension score, which is what makes the waterfall read.
  const totalWeight = assessed.reduce((s, c) => s + c.weight, 0);
  for (const c of assessed) {
    c.contribution = round1(((c.weight / totalWeight) * (c.score ?? 0)));
  }

  return {
    id: dimension.id,
    name: dimension.name,
    ref: dimension.ref,
    score: tfn ? round1(defuzzify(tfn)) : null,
    tfn,
    weight: effectiveWeight(dimension.weight, siblings),
    contribution: 0,
    completeness: dimension.criteria.length
      ? assessed.length / dimension.criteria.length
      : 0,
    criteria,
  };
}

function bandFor(score: number | null, bands: RiskBand[]): RiskBand | null {
  if (score === null) return null;
  return (
    bands.find((b) => score >= b.min && score <= b.max) ??
    bands.find((b) => score >= b.min) ??
    null
  );
}

function scoreObjective(
  objective: Objective,
  input: AppraisalInput,
  tree: CriteriaTree,
): ObjectiveResult {
  const dimensions = objective.dimensions.map((d) =>
    scoreDimension(d, input, tree, objective.dimensions.length),
  );

  const scored = dimensions.filter((d) => d.tfn);
  const tfn = weightedAverage(
    scored.map((d) => ({ tfn: d.tfn as TFN, weight: d.weight })),
  );

  const totalWeight = scored.reduce((s, d) => s + d.weight, 0);
  for (const d of scored) {
    d.contribution = round1((d.weight / totalWeight) * (d.score ?? 0));
  }

  const totalCriteria = objective.dimensions.reduce(
    (s, d) => s + d.criteria.length,
    0,
  );
  const assessedCriteria = dimensions.reduce(
    (s, d) => s + d.criteria.filter((c) => c.assessed).length,
    0,
  );

  const score = tfn ? round1(defuzzify(tfn)) : null;
  const completeness = totalCriteria ? assessedCriteria / totalCriteria : 0;

  // Completeness gate. A score computed from a handful of criteria is not wrong
  // arithmetically - weight renormalisation keeps it plausible - but it has no
  // evidential basis, so it gets no band and no recommendation.
  const sufficient =
    completeness >= tree.completenessPolicy.minObjectiveCompleteness;

  const missingCriteria = dimensions.flatMap((d) =>
    d.criteria
      .filter((c) => !c.assessed)
      .map((c) => ({
        id: c.id,
        name: c.name,
        ref: c.ref,
        dimension: d.name,
      })),
  );

  return {
    id: objective.id,
    name: objective.name,
    score,
    tfn,
    completeness,
    sufficient,
    band: sufficient ? bandFor(score, tree.riskBands) : null,
    missingCriteria,
    dimensions,
  };
}

/** Score a full appraisal against the criteria tree. */
export function appraise(
  input: AppraisalInput,
  tree: CriteriaTree,
): AppraisalResult {
  const objectives = tree.objectives.map((o) => scoreObjective(o, input, tree));

  const criticalBreaches = objectives
    .flatMap((o) => o.dimensions)
    .flatMap((d) => d.criteria)
    .filter((c) => c.criticalBreach);

  const allCriteria = objectives
    .flatMap((o) => o.dimensions)
    .flatMap((d) => d.criteria);

  return {
    objectives,
    criticalBreaches,
    overallCompleteness: allCriteria.length
      ? allCriteria.filter((c) => c.assessed).length / allCriteria.length
      : 0,
    weightStatus: tree.weightStatus,
    modelVersion: tree.version,
    computedAt: new Date().toISOString(),
  };
}

/** Convenience accessor: the credit-risk objective result. */
export function creditRisk(result: AppraisalResult): ObjectiveResult | undefined {
  return result.objectives.find((o) => o.id === "credit_risk");
}

/** Convenience accessor: the development-impact objective result. */
export function developmentImpact(
  result: AppraisalResult,
): ObjectiveResult | undefined {
  return result.objectives.find((o) => o.id === "development_impact");
}

export type { LinguisticCode };
