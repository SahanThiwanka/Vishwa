/**
 * Triangular fuzzy number arithmetic and the raw-value to score mapping.
 *
 * Method note for the thesis (Chapter 3):
 * Qualitative criteria are captured on a 5-point linguistic scale and represented
 * as triangular fuzzy numbers, following the standard fuzzy-MCDM treatment of
 * subjective assessment. Quantitative criteria are crisp and enter as degenerate
 * TFNs [x, x, x], so a single aggregation path handles both. Aggregation is the
 * fuzzy weighted average; defuzzification is by centroid, which for a TFN
 * reduces to (l + m + u) / 3.
 */

import type { Band, TFN } from "./types";

/** A crisp value expressed as a degenerate triangular fuzzy number. */
export function crisp(x: number): TFN {
  return [x, x, x];
}

/** Centroid defuzzification. For a TFN this is the arithmetic mean of its three points. */
export function defuzzify(t: TFN): number {
  return (t[0] + t[1] + t[2]) / 3;
}

/** Scalar multiplication of a TFN. */
export function scale(t: TFN, k: number): TFN {
  return [t[0] * k, t[1] * k, t[2] * k];
}

/** Element-wise addition of TFNs. */
export function add(a: TFN, b: TFN): TFN {
  return [a[0] + b[0], a[1] + b[1], a[2] + b[2]];
}

/**
 * Fuzzy weighted average.
 *
 * Weights are renormalised over whatever entries are supplied, so callers can
 * simply omit unassessed criteria rather than passing zeros. Passing zeros would
 * drag the result toward 0 and misrepresent an incomplete appraisal as a bad one.
 */
export function weightedAverage(
  entries: Array<{ tfn: TFN; weight: number }>,
): TFN | null {
  if (entries.length === 0) return null;

  const totalWeight = entries.reduce((sum, e) => sum + e.weight, 0);
  if (totalWeight <= 0) return null;

  return entries.reduce<TFN>(
    (acc, e) => add(acc, scale(e.tfn, e.weight / totalWeight)),
    [0, 0, 0],
  );
}

/**
 * Map a raw quantitative value onto 0-100 by piecewise-linear interpolation
 * across the criterion's band anchors.
 *
 * The anchors are [rawValue, score] pairs held in the criteria tree. Because
 * interpolation simply follows the anchor sequence, one implementation serves
 * higher-is-better, lower-is-better and band-optimal criteria alike - the
 * `direction` field is documentation, not control flow.
 *
 * Values outside the anchor range clamp to the nearest endpoint score. For
 * band-optimal criteria this means an extreme value holds the last anchor's
 * score rather than continuing to fall; note this as a modelling simplification.
 */
export function scoreFromBands(value: number, bands: Band[]): number {
  if (bands.length === 0) return 0;

  const sorted = [...bands].sort((a, b) => a[0] - b[0]);

  const first = sorted[0];
  const last = sorted[sorted.length - 1];
  if (value <= first[0]) return clamp(first[1]);
  if (value >= last[0]) return clamp(last[1]);

  for (let i = 0; i < sorted.length - 1; i++) {
    const [x0, y0] = sorted[i];
    const [x1, y1] = sorted[i + 1];

    if (value >= x0 && value <= x1) {
      if (x1 === x0) return clamp(y1);
      const t = (value - x0) / (x1 - x0);
      return clamp(y0 + t * (y1 - y0));
    }
  }

  return clamp(last[1]);
}

function clamp(x: number): number {
  return Math.max(0, Math.min(100, x));
}

/** Round for display without implying precision the model does not have. */
export function round1(x: number): number {
  return Math.round(x * 10) / 10;
}
