"use server";

import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";

import { prisma } from "@/lib/db";
import { appraise, criteriaTree, creditRisk, developmentImpact } from "@/lib/scoring";
import type { AppraisalInput } from "@/lib/scoring/types";
import {
  appraisalHeaderSchema,
  appraisalInputSchema,
  decisionSchema,
  elicitationResponseSchema,
  respondentSchema,
  validate,
} from "@/lib/validation";

export interface AppraisalHeader {
  businessName: string;
  branch: string;
  facilityAmount: number;
  facilityType: string;
  projectType?: string;
  appraisalOfficer: string;
  district?: string;
  organisationType?: string;
}

/** Reference format mirrors the bank's own file numbering: SME/<branch>/<year>/<seq>. */
async function nextReference(branch: string): Promise<string> {
  const year = new Date().getFullYear();
  const prefix = `SME/${branch.toUpperCase().slice(0, 4)}/${year}/`;

  const last = await prisma.appraisal.findFirst({
    where: { reference: { startsWith: prefix } },
    orderBy: { reference: "desc" },
    select: { reference: true },
  });

  const seq = last ? Number(last.reference.slice(prefix.length)) + 1 : 1;
  return prefix + String(seq).padStart(4, "0");
}

export async function createAppraisal(
  rawHeader: AppraisalHeader,
  rawInputs: AppraisalInput,
) {
  // Server Actions accept direct POSTs, so this input is untrusted regardless
  // of what the form component sends.
  const header = validate(appraisalHeaderSchema, rawHeader, "appraisal details");
  const inputs = validate(
    appraisalInputSchema, rawInputs, "criterion inputs",
  ) as AppraisalInput;

  const result = appraise(inputs, criteriaTree);
  const credit = creditRisk(result);
  const development = developmentImpact(result);

  const reference = await nextReference(header.branch);

  const appraisal = await prisma.appraisal.create({
    data: {
      reference,
      branch: header.branch,
      district: header.district,
      facilityAmount: header.facilityAmount,
      facilityType: header.facilityType,
      projectType: header.projectType,
      businessName: header.businessName,
      organisationType: header.organisationType,
      appraisalOfficer: header.appraisalOfficer,

      inputs: JSON.stringify(inputs),
      result: JSON.stringify(result),
      modelVersion: result.modelVersion,

      // Denormalised for list views. A band is stored only when the
      // completeness gate allowed one - an under-assessed file has no band.
      creditRiskScore: credit?.score ?? null,
      developmentScore: development?.score ?? null,
      riskBand: credit?.band?.code ?? null,
      completeness: result.overallCompleteness,

      status: "SUBMITTED",

      events: {
        create: [
          {
            action: "CREATED",
            actor: header.appraisalOfficer,
            role: "Appraisal Officer",
            note: `Appraisal created against model ${result.modelVersion}`,
          },
          {
            action: "SCORED",
            actor: "system",
            note: credit?.sufficient
              ? `Credit risk ${credit.score} (band ${credit.band?.code}), development impact ${development?.score ?? "n/a"}`
              : `Scored but withheld: only ${Math.round(result.overallCompleteness * 100)}% of criteria assessed`,
            scoreSnapshot: credit?.score ?? null,
          },
        ],
      },
    },
  });

  revalidatePath("/");
  redirect(`/appraisals/${appraisal.id}`);
}

export async function recordDecision(
  rawId: string,
  rawAction: "RECOMMENDED" | "APPROVED" | "DECLINED",
  rawActor: string,
  rawRole: string,
  rawNote?: string,
) {
  const { id, action, actor, role, note } = validate(
    decisionSchema,
    { id: rawId, action: rawAction, actor: rawActor, role: rawRole, note: rawNote },
    "decision",
  );

  const appraisal = await prisma.appraisal.findUnique({ where: { id } });
  if (!appraisal) throw new Error("Appraisal not found");

  await prisma.appraisal.update({
    where: { id },
    data: {
      status: action,
      events: {
        create: {
          action,
          actor,
          role,
          note,
          scoreSnapshot: appraisal.creditRiskScore,
        },
      },
    },
  });

  revalidatePath(`/appraisals/${id}`);
  revalidatePath("/");
}

// ---------------------------------------------------------------------------
// Best-Worst Method elicitation
// ---------------------------------------------------------------------------

export interface ElicitationLevelResponse {
  level: string;
  best: string;
  worst: string;
  bestToOthers: Record<string, number>;
  othersToWorst: Record<string, number>;
}

export interface Respondent {
  respondentCode: string;
  yearsExperience?: number;
  institution?: string;
  role?: string;
}

export async function saveElicitation(
  rawRespondent: Respondent,
  rawLevels: ElicitationLevelResponse[],
) {
  const respondent = validate(respondentSchema, rawRespondent, "participant details");

  if (!Array.isArray(rawLevels) || rawLevels.length === 0) {
    throw new Error("Invalid submission — no responses were included");
  }
  const levels = rawLevels.map((l, i) =>
    validate(elicitationResponseSchema, l, `response for section ${i + 1}`),
  );

  // Upserted per (respondent, level) so a respondent who resumes or corrects a
  // level overwrites their earlier answer rather than creating a duplicate that
  // would silently double their influence on the aggregated weights.
  for (const level of levels) {
    const data = {
      respondentCode: respondent.respondentCode,
      yearsExperience: respondent.yearsExperience ?? null,
      institution: respondent.institution ?? null,
      role: respondent.role ?? null,
      level: level.level,
      best: level.best,
      worst: level.worst,
      bestToOthers: JSON.stringify(level.bestToOthers),
      othersToWorst: JSON.stringify(level.othersToWorst),
    };

    await prisma.elicitationResponse.upsert({
      where: {
        respondentCode_level: {
          respondentCode: respondent.respondentCode,
          level: level.level,
        },
      },
      create: data,
      update: data,
    });
  }

  return { saved: levels.length };
}

export async function elicitationProgress() {
  const rows = await prisma.elicitationResponse.groupBy({
    by: ["respondentCode"],
    _count: { level: true },
  });
  return rows.map((r) => ({
    respondentCode: r.respondentCode,
    levelsCompleted: r._count.level,
  }));
}
