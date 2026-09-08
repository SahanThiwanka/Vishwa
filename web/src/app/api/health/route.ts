/**
 * Deployment health check.
 *
 * Confirms the app is up, which database backend it resolved, whether the
 * schema is reachable, and — importantly for this project — whether criterion
 * weights are still placeholders. A deployment collecting elicitation responses
 * should report `weights: "PLACEHOLDER"` until the study is complete; if it ever
 * reports ELICITED unexpectedly, something has written weights that should not
 * have.
 */

import { criteriaTree } from "@/lib/scoring";
import { databaseBackend, prisma } from "@/lib/db";

export const dynamic = "force-dynamic";

export async function GET() {
  const checks: Record<string, unknown> = {
    status: "ok",
    database: databaseBackend,
    modelVersion: criteriaTree.version,
    weights: criteriaTree.weightStatus.state,
    criteria: criteriaTree.objectives.reduce(
      (total, o) => total + o.dimensions.reduce((s, d) => s + d.criteria.length, 0),
      0,
    ),
  };

  try {
    checks.elicitationResponses = await prisma.elicitationResponse.count();
    checks.appraisals = await prisma.appraisal.count();
  } catch (error) {
    checks.status = "degraded";
    checks.databaseError =
      error instanceof Error ? error.message : "unknown database error";
    return Response.json(checks, { status: 503 });
  }

  return Response.json(checks);
}
