/**
 * Public entry point for the scoring model.
 *
 * The criteria tree is mirrored in from `shared/model/criteria-tree.json` by
 * `scripts/sync-model.mjs`, which runs automatically before `npm run dev` and
 * `npm run build`. Edit the shared file, not the mirror.
 */

import treeJson from "./criteria-tree.json";
import type { CriteriaTree } from "./types";

export const criteriaTree = treeJson as unknown as CriteriaTree;

/** Flat list of every criterion in the tree, with its parents attached. */
export function allCriteria() {
  return criteriaTree.objectives.flatMap((objective) =>
    objective.dimensions.flatMap((dimension) =>
      dimension.criteria.map((criterion) => ({
        criterion,
        dimension,
        objective,
      })),
    ),
  );
}

/** Look up a single criterion by id. */
export function findCriterion(id: string) {
  return allCriteria().find((entry) => entry.criterion.id === id);
}

export { appraise, creditRisk, developmentImpact } from "./engine";
export {
  crisp,
  defuzzify,
  round1,
  scoreFromBands,
  weightedAverage,
} from "./fuzzy";
export type * from "./types";
