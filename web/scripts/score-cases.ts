/**
 * Score a batch of appraisal inputs with the TypeScript engine and emit JSON.
 *
 * Used by research/src/test_parity.py to check that the TypeScript engine (which
 * the deployed system runs) and the Python implementation (which the thesis
 * analysis runs) agree. Two implementations of one method is a real risk: without
 * this check, the thesis could report numbers from one while demonstrating a
 * system running the other.
 *
 * Usage:  npx tsx scripts/score-cases.ts <input.json> <output.json>
 */

import { readFileSync, writeFileSync } from "node:fs";

import { appraise, criteriaTree } from "../src/lib/scoring";
import type { AppraisalInput } from "../src/lib/scoring/types";

const [, , inputPath, outputPath] = process.argv;

if (!inputPath || !outputPath) {
  console.error("usage: tsx scripts/score-cases.ts <input.json> <output.json>");
  process.exit(1);
}

const cases: AppraisalInput[] = JSON.parse(readFileSync(inputPath, "utf8"));

const results = cases.map((input) => {
  const result = appraise(input, criteriaTree);
  return {
    objectives: result.objectives.map((o) => ({
      id: o.id,
      score: o.score,
      completeness: o.completeness,
      sufficient: o.sufficient,
      dimensions: o.dimensions.map((d) => ({
        id: d.id,
        score: d.score,
        completeness: d.completeness,
      })),
    })),
    overallCompleteness: result.overallCompleteness,
    criticalBreaches: result.criticalBreaches.map((c) => c.id),
  };
});

writeFileSync(outputPath, JSON.stringify(results, null, 2), "utf8");
console.log(`scored ${results.length} cases -> ${outputPath}`);
