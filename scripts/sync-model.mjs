/**
 * Copy the criteria tree from shared/model into the Next.js app.
 *
 * `shared/model/criteria-tree.json` is the single source of truth for the whole
 * project - the Python research pipeline and the web app both read that file.
 * Next.js cannot reliably import JSON from outside its own root, so this script
 * mirrors it in before dev/build. Edit the shared copy, never the mirror.
 */

import { copyFileSync, mkdirSync, readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");

const source = join(root, "shared", "model", "criteria-tree.json");
const target = join(root, "web", "src", "lib", "scoring", "criteria-tree.json");

const tree = JSON.parse(readFileSync(source, "utf8"));

const criteriaCount = tree.objectives.reduce(
  (total, objective) =>
    total +
    objective.dimensions.reduce((sum, dim) => sum + dim.criteria.length, 0),
  0,
);

mkdirSync(dirname(target), { recursive: true });
copyFileSync(source, target);

console.log(
  `[sync-model] v${tree.version} - ${criteriaCount} criteria, ` +
    `weights: ${tree.weightStatus.state}`,
);

if (tree.weightStatus.state === "PLACEHOLDER") {
  console.warn(
    "[sync-model] WARNING: weights are PLACEHOLDER. " +
      "Scores computed now are structurally valid but MUST NOT be reported as results.",
  );
}
