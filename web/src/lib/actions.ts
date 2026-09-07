"use server";

import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";

import { prisma } from "@/lib/db";
import { appraise, criteriaTree, creditRisk, developmentImpact } from "@/lib/scoring";
import type { AppraisalInput } from "@/lib/scoring/types";

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
  header: AppraisalHeader,
  inputs: AppraisalInput,
) {
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
  id: string,
  action: "RECOMMENDED" | "APPROVED" | "DECLINED",
  actor: string,
  role: string,
  note?: string,
) {
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
