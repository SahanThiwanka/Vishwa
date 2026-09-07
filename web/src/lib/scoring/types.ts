/**
 * Type definitions for the dual-objective SME appraisal scoring model.
 *
 * These mirror the structure of `shared/model/criteria-tree.json`, which is the
 * single source of truth for the model. Do not redefine criteria here.
 */

/** Triangular fuzzy number: [lower, modal, upper]. */
export type TFN = [number, number, number];

export type LinguisticCode = "VP" | "P" | "F" | "G" | "E";

export type CriterionType = "quantitative" | "qualitative";

/**
 * How a raw value maps onto the 0-100 scale.
 * `band_optimal` means the score peaks at some middle value and falls away on
 * both sides (a current ratio of 8.0 signals idle assets, not strength).
 */
export type Direction = "higher_better" | "lower_better" | "band_optimal";

/** A [rawValue, score] anchor point. Interpolation runs between consecutive anchors. */
export type Band = [number, number];

export interface Criterion {
  id: string;
  name: string;
  /** Clause of the People's Bank form this criterion derives from. */
  ref: string;
  type: CriterionType;
  unit?: string;
  direction?: Direction;
  bands?: Band[];
  weight?: number | null;
  /** Criteria whose breach cannot be averaged away (e.g. DSCR < 1.0). */
  critical?: boolean;
  criticalNote?: string;
}

export interface Dimension {
  id: string;
  name: string;
  ref: string;
  note?: string;
  weight?: number | null;
  criteria: Criterion[];
}

export interface Objective {
  id: string;
  name: string;
  note?: string;
  weight?: number | null;
  dimensions: Dimension[];
}

export interface RiskBand {
  code: "A" | "B" | "C" | "D";
  label: string;
  min: number;
  max: number;
  action: string;
}

export interface LinguisticLevel {
  code: LinguisticCode;
  label: string;
  tfn: TFN;
}

export interface WeightStatus {
  state: "PLACEHOLDER" | "ELICITED";
  detail: string;
  plannedMethod?: string;
  elicitation?: {
    method: string;
    respondents: number;
    date: string;
    meanConsistencyRatio: number;
  };
}

export interface CriteriaTree {
  version: string;
  title: string;
  sourceInstrument: Record<string, string>;
  weightStatus: WeightStatus;
  linguisticScale: {
    type: string;
    levels: LinguisticLevel[];
    defuzzification: string;
  };
  riskBands: RiskBand[];
  objectives: Objective[];
}

// ---------------------------------------------------------------------------
// Inputs and results
// ---------------------------------------------------------------------------

/**
 * One appraisal's raw inputs, keyed by criterion id.
 *
 * `null` means "not assessed" - the criterion is excluded and the remaining
 * weights are renormalised. This is deliberate: a half-complete appraisal must
 * not silently score as though the missing parts were zero.
 */
export type AppraisalInput = Record<string, number | LinguisticCode | null>;

export interface CriterionResult {
  id: string;
  name: string;
  ref: string;
  type: CriterionType;
  rawValue: number | LinguisticCode | null;
  /** Defuzzified 0-100 score, or null when not assessed. */
  score: number | null;
  tfn: TFN | null;
  weight: number;
  /** Share of the parent dimension's score attributable to this criterion. */
  contribution: number;
  assessed: boolean;
  criticalBreach: boolean;
  criticalNote?: string;
}

export interface DimensionResult {
  id: string;
  name: string;
  ref: string;
  score: number | null;
  tfn: TFN | null;
  weight: number;
  contribution: number;
  completeness: number;
  criteria: CriterionResult[];
}

export interface ObjectiveResult {
  id: string;
  name: string;
  score: number | null;
  tfn: TFN | null;
  completeness: number;
  band: RiskBand | null;
  dimensions: DimensionResult[];
}

export interface AppraisalResult {
  /**
   * Objectives are reported side by side and never merged into one number.
   * Collapsing credit risk and development impact into a single score would
   * hide exactly the trade-off this research exists to surface.
   */
  objectives: ObjectiveResult[];
  criticalBreaches: CriterionResult[];
  overallCompleteness: number;
  weightStatus: WeightStatus;
  modelVersion: string;
  computedAt: string;
}
