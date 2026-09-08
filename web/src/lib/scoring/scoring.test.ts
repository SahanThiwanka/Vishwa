/**
 * Tests for the scoring engine.
 *
 * The engine is the research artefact, not just application code: every number
 * reported in the thesis passes through it. These tests pin the behaviour the
 * thesis describes, so a later change that quietly alters scoring fails here
 * rather than silently invalidating published results.
 */

import { describe, expect, it } from "vitest";

import { appraise, criteriaTree } from "./index";
import { crisp, defuzzify, scoreFromBands, weightedAverage } from "./fuzzy";
import type { AppraisalInput, TFN } from "./types";

describe("triangular fuzzy numbers", () => {
  it("defuzzifies by centroid", () => {
    expect(defuzzify([0, 25, 50])).toBe(25);
    expect(defuzzify([75, 100, 100])).toBeCloseTo(91.667, 3);
  });

  it("treats a crisp value as a degenerate TFN", () => {
    expect(defuzzify(crisp(42))).toBe(42);
  });

  it("renormalises a weighted average over the entries given", () => {
    const result = weightedAverage([
      { tfn: crisp(100), weight: 1 },
      { tfn: crisp(0), weight: 1 },
    ]);
    expect(defuzzify(result as TFN)).toBe(50);
  });

  it("respects unequal weights", () => {
    const result = weightedAverage([
      { tfn: crisp(100), weight: 3 },
      { tfn: crisp(0), weight: 1 },
    ]);
    expect(defuzzify(result as TFN)).toBe(75);
  });

  it("returns null when there is nothing to average", () => {
    expect(weightedAverage([])).toBeNull();
  });
});

describe("band mapping", () => {
  const bands: [number, number][] = [[0, 0], [10, 50], [20, 100]];

  it("interpolates linearly between anchors", () => {
    expect(scoreFromBands(5, bands)).toBe(25);
    expect(scoreFromBands(15, bands)).toBe(75);
  });

  it("hits anchors exactly", () => {
    expect(scoreFromBands(10, bands)).toBe(50);
  });

  it("clamps outside the anchor range", () => {
    expect(scoreFromBands(-100, bands)).toBe(0);
    expect(scoreFromBands(1000, bands)).toBe(100);
  });

  it("handles descending (lower-is-better) anchors", () => {
    const descending: [number, number][] = [[0, 100], [10, 0]];
    expect(scoreFromBands(0, descending)).toBe(100);
    expect(scoreFromBands(5, descending)).toBe(50);
    expect(scoreFromBands(10, descending)).toBe(0);
  });

  it("handles band-optimal anchors that peak in the middle", () => {
    // Mirrors current ratio: too low is bad, too high signals idle assets.
    const optimal: [number, number][] = [[0.5, 0], [2.0, 100], [3.5, 70]];
    expect(scoreFromBands(2.0, optimal)).toBe(100);
    expect(scoreFromBands(0.5, optimal)).toBe(0);
    expect(scoreFromBands(3.5, optimal)).toBe(70);
    expect(scoreFromBands(2.75, optimal)).toBe(85);
  });
});

/** A complete, sound application. */
function completeCase(): AppraisalInput {
  const input: AppraisalInput = {};
  for (const objective of criteriaTree.objectives) {
    for (const dimension of objective.dimensions) {
      for (const criterion of dimension.criteria) {
        if (criterion.type === "qualitative") {
          input[criterion.id] = "G";
        } else {
          // Take the anchor scoring highest, so the case is unambiguously strong.
          const best = [...criterion.bands!].sort((a, b) => b[1] - a[1])[0];
          input[criterion.id] = best[0];
        }
      }
    }
  }
  return input;
}

describe("appraisal scoring", () => {
  it("scores a complete strong case into band A", () => {
    const result = appraise(completeCase(), criteriaTree);
    const credit = result.objectives.find((o) => o.id === "credit_risk")!;

    expect(result.overallCompleteness).toBe(1);
    expect(credit.sufficient).toBe(true);
    expect(credit.band?.code).toBe("A");
  });

  it("never merges the two objectives into one score", () => {
    const result = appraise(completeCase(), criteriaTree);
    expect(result.objectives).toHaveLength(2);
    expect(result).not.toHaveProperty("overallScore");
    expect(result).not.toHaveProperty("score");
  });

  it("excludes unassessed criteria instead of scoring them as zero", () => {
    // One criterion, at its best value. If missing criteria counted as zero the
    // dimension would score near zero; renormalisation should give full marks.
    const result = appraise({ dscr: 2.0 }, criteriaTree);
    const credit = result.objectives.find((o) => o.id === "credit_risk")!;
    const viability = credit.dimensions.find((d) => d.id === "project_viability")!;

    expect(viability.score).toBe(100);
    expect(viability.completeness).toBeLessThan(1);
  });

  it("withholds a recommendation below the completeness threshold", () => {
    const result = appraise({ dscr: 2.0, iscr: 4.0, roi: 35 }, criteriaTree);
    const credit = result.objectives.find((o) => o.id === "credit_risk")!;

    expect(credit.score).not.toBeNull();
    expect(credit.sufficient).toBe(false);
    expect(credit.band).toBeNull();
    expect(credit.missingCriteria.length).toBeGreaterThan(0);
  });

  it("flags a DSCR below 1.0 as a critical breach", () => {
    const result = appraise({ ...completeCase(), dscr: 0.9 }, criteriaTree);
    expect(result.criticalBreaches.map((b) => b.id)).toContain("dscr");
  });

  it("does not flag a healthy DSCR", () => {
    const result = appraise(completeCase(), criteriaTree);
    expect(result.criticalBreaches).toHaveLength(0);
  });

  it("surfaces a critical breach even when everything else is excellent", () => {
    // The whole point of the critical rule: a knock-out cannot be averaged away.
    const result = appraise({ ...completeCase(), dscr: 0.5 }, criteriaTree);
    const credit = result.objectives.find((o) => o.id === "credit_risk")!;

    expect(credit.score).toBeGreaterThan(80);
    expect(result.criticalBreaches).toHaveLength(1);
  });

  it("makes contributions sum to the parent score", () => {
    const result = appraise(completeCase(), criteriaTree);

    for (const objective of result.objectives) {
      const summed = objective.dimensions
        .filter((d) => d.score !== null)
        .reduce((s, d) => s + d.contribution, 0);
      expect(summed).toBeCloseTo(objective.score!, 0);

      for (const dimension of objective.dimensions) {
        if (dimension.score === null) continue;
        const inner = dimension.criteria
          .filter((c) => c.assessed)
          .reduce((s, c) => s + c.contribution, 0);
        expect(inner).toBeCloseTo(dimension.score, 0);
      }
    }
  });

  it("returns null scores for an empty appraisal rather than zero", () => {
    const result = appraise({}, criteriaTree);
    expect(result.overallCompleteness).toBe(0);
    for (const objective of result.objectives) {
      expect(objective.score).toBeNull();
      expect(objective.band).toBeNull();
    }
  });

  it("ignores an unknown criterion id", () => {
    const result = appraise({ not_a_real_criterion: 50 }, criteriaTree);
    expect(result.overallCompleteness).toBe(0);
  });

  it("orders a weak case below a strong one on both objectives", () => {
    const weak: AppraisalInput = {};
    for (const objective of criteriaTree.objectives) {
      for (const dimension of objective.dimensions) {
        for (const criterion of dimension.criteria) {
          if (criterion.type === "qualitative") weak[criterion.id] = "VP";
          else {
            const worst = [...criterion.bands!].sort((a, b) => a[1] - b[1])[0];
            weak[criterion.id] = worst[0];
          }
        }
      }
    }

    const strong = appraise(completeCase(), criteriaTree);
    const poor = appraise(weak, criteriaTree);

    for (const id of ["credit_risk", "development_impact"]) {
      const s = strong.objectives.find((o) => o.id === id)!;
      const p = poor.objectives.find((o) => o.id === id)!;
      expect(s.score!).toBeGreaterThan(p.score!);
    }
  });
});

describe("model integrity", () => {
  it("gives every criterion a source clause", () => {
    for (const objective of criteriaTree.objectives) {
      for (const dimension of objective.dimensions) {
        for (const criterion of dimension.criteria) {
          expect(criterion.ref, `${criterion.id} has no clause reference`).toBeTruthy();
        }
      }
    }
  });

  it("gives every quantitative criterion usable bands", () => {
    for (const objective of criteriaTree.objectives) {
      for (const dimension of objective.dimensions) {
        for (const criterion of dimension.criteria) {
          if (criterion.type !== "quantitative") continue;
          expect(criterion.bands, `${criterion.id} has no bands`).toBeDefined();
          expect(criterion.bands!.length).toBeGreaterThanOrEqual(2);
          for (const [, score] of criterion.bands!) {
            expect(score).toBeGreaterThanOrEqual(0);
            expect(score).toBeLessThanOrEqual(100);
          }
        }
      }
    }
  });

  it("uses unique criterion ids across the whole tree", () => {
    const ids = criteriaTree.objectives.flatMap((o) =>
      o.dimensions.flatMap((d) => d.criteria.map((c) => c.id)),
    );
    expect(new Set(ids).size).toBe(ids.length);
  });

  it("covers 0-100 with contiguous, non-overlapping risk bands", () => {
    const sorted = [...criteriaTree.riskBands].sort((a, b) => a.min - b.min);
    expect(sorted[0].min).toBe(0);
    expect(sorted[sorted.length - 1].max).toBe(100);
    for (let i = 0; i < sorted.length - 1; i++) {
      expect(sorted[i].max).toBe(sorted[i + 1].min);
    }
  });
});
