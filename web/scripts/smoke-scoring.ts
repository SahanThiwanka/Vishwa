/**
 * Smoke test for the scoring engine.
 *
 * Run:  cd web && npx tsx scripts/smoke-scoring.ts
 *
 * This is a structural check, not a research result. It verifies that the engine
 * discriminates between cases, flags critical breaches, renormalises weights over
 * unassessed criteria, and produces contributions that sum back to the parent
 * score. It says nothing about whether the model is *accurate* - that requires the
 * empirical validation in research/ and real elicited weights.
 */

import { appraise, criteriaTree, creditRisk, developmentImpact } from "../src/lib/scoring";
import type { AppraisalInput } from "../src/lib/scoring/types";

// A sound manufacturing expansion: experienced sponsor, clean conduct,
// comfortable cover, meaningful local employment and import substitution.
const strongCase: AppraisalInput = {
  sponsor_experience: 14, sponsor_quals: "G", org_structure: "G",
  hr_adequacy: "G", statutory_compliance: "E", business_vintage: 11,
  repayment_performance: "E", arrears_ratio: 0, account_turnover: 0.85,
  cheque_returns: 0, external_exposure: "G",
  gross_profit_ratio: 32, net_profit_ratio: 13, current_ratio: 1.9,
  debt_equity_hist: 0.9, gearing_ratio: 38, asset_turnover: 2.1,
  stock_retention: 34, debtor_retention: 41, sales_trend: "G",
  dscr: 1.85, iscr: 3.4, roi: 27, projected_np: 14,
  project_gearing: 1.1, promoter_equity: 38, capacity_growth: 65, bep_headroom: 42,
  rivalry: "F", threat_entry: "G", buyer_power: "F", supplier_power: "G",
  substitutes: "G", raw_material: "G", distribution: "G",
  security_cover: 1.6, technological_risk: "G", environmental_risk: "G",
  govt_consent: "E", insurance_cover: "G", implementation: "G",
  employment_generation: 55, women_participation: 44, local_raw_material: 78,
  productive_capacity: 65, export_share: 28, import_substitution: "G",
  value_added: 46, fx_earnings: "G",
};

// A thin startup proposal: no track record, arrears, DSCR under 1.0.
const weakCase: AppraisalInput = {
  sponsor_experience: 1, sponsor_quals: "P", org_structure: "P",
  hr_adequacy: "P", statutory_compliance: "F", business_vintage: 1,
  repayment_performance: "P", arrears_ratio: 12, account_turnover: 0.2,
  cheque_returns: 5, external_exposure: "P",
  gross_profit_ratio: 9, net_profit_ratio: 2, current_ratio: 0.85,
  debt_equity_hist: 3.4, gearing_ratio: 78, asset_turnover: 0.4,
  stock_retention: 105, debtor_retention: 96, sales_trend: "P",
  dscr: 0.92, iscr: 1.3, roi: 6, projected_np: 3,
  project_gearing: 3.1, promoter_equity: 14, capacity_growth: 12, bep_headroom: 8,
  rivalry: "P", threat_entry: "P", buyer_power: "P", supplier_power: "P",
  substitutes: "F", raw_material: "P", distribution: "P",
  security_cover: 0.7, technological_risk: "P", environmental_risk: "F",
  govt_consent: "P", insurance_cover: "P", implementation: "P",
  employment_generation: 8, women_participation: 6, local_raw_material: 20,
  productive_capacity: 12, export_share: 0, import_substitution: "P",
  value_added: 11, fx_earnings: "VP",
};

// Deliberately incomplete: only the financial dimension assessed.
const partialCase: AppraisalInput = {
  dscr: 1.6, iscr: 2.8, roi: 22, projected_np: 11,
  gross_profit_ratio: 28, net_profit_ratio: 11, current_ratio: 1.7,
};

function report(label: string, input: AppraisalInput) {
  const result = appraise(input, criteriaTree);
  const cr = creditRisk(result);
  const di = developmentImpact(result);

  console.log(`\n${"=".repeat(66)}\n${label}\n${"=".repeat(66)}`);
  console.log(
    `Credit risk        : ${cr?.score ?? "n/a"}  ` +
      `[band ${cr?.band?.code ?? "-"} - ${cr?.band?.action ?? "insufficient data"}]`,
  );
  console.log(
    `Development impact : ${di?.score ?? "n/a"}  ` +
      `[band ${di?.band?.code ?? "-"}]`,
  );
  console.log(`Completeness       : ${(result.overallCompleteness * 100).toFixed(0)}%`);

  if (result.criticalBreaches.length) {
    console.log(`\n  CRITICAL BREACHES:`);
    for (const b of result.criticalBreaches) {
      console.log(`   - ${b.name} = ${b.rawValue} (clause ${b.ref})`);
    }
  }

  console.log(`\n  Credit-risk dimensions:`);
  for (const d of cr?.dimensions ?? []) {
    const score = d.score === null ? " n/a" : d.score.toFixed(1).padStart(5);
    console.log(
      `   ${score}  ${d.name.padEnd(38)} ` +
        `contributes ${d.contribution.toFixed(1).padStart(5)} pts  ` +
        `(${(d.completeness * 100).toFixed(0)}% assessed)`,
    );
  }

  // Invariant: dimension contributions must sum to the objective score.
  const summed = (cr?.dimensions ?? []).reduce((s, d) => s + d.contribution, 0);
  const drift = Math.abs(summed - (cr?.score ?? 0));
  console.log(
    `\n  Contribution sum check: ${summed.toFixed(1)} vs objective ${cr?.score ?? 0}` +
      `  ->  ${drift < 0.5 ? "OK" : `DRIFT ${drift.toFixed(2)}`}`,
  );

  return result;
}

const strong = report("STRONG CASE - established manufacturer, expansion", strongCase);
const weak = report("WEAK CASE - startup, arrears, DSCR below 1.0", weakCase);
report("PARTIAL CASE - only financial criteria entered", partialCase);

console.log(`\n${"=".repeat(66)}\nASSERTIONS\n${"=".repeat(66)}`);

const checks: Array<[string, boolean]> = [
  ["strong scores above weak on credit risk",
    (creditRisk(strong)?.score ?? 0) > (creditRisk(weak)?.score ?? 0)],
  ["strong scores above weak on development impact",
    (developmentImpact(strong)?.score ?? 0) > (developmentImpact(weak)?.score ?? 0)],
  ["weak case flags a critical breach (DSCR < 1.0)",
    weak.criticalBreaches.length > 0],
  ["strong case flags no critical breach",
    strong.criticalBreaches.length === 0],
  ["strong case reaches band A or B",
    ["A", "B"].includes(creditRisk(strong)?.band?.code ?? "")],
  ["weak case falls to band C or D",
    ["C", "D"].includes(creditRisk(weak)?.band?.code ?? "")],
  ["objectives are reported separately, not merged",
    strong.objectives.length === 2],
  ["weights still flagged PLACEHOLDER",
    strong.weightStatus.state === "PLACEHOLDER"],
];

let failed = 0;
for (const [label, ok] of checks) {
  console.log(`  ${ok ? "PASS" : "FAIL"}  ${label}`);
  if (!ok) failed++;
}

console.log(
  `\n${failed === 0 ? "All structural checks passed." : `${failed} check(s) FAILED.`}\n`,
);
process.exit(failed === 0 ? 0 : 1);
