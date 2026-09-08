/**
 * Input validation for everything that crosses a trust boundary.
 *
 * Server Actions are reachable by direct POST, not only through this
 * application's own forms. Anything arriving in one is untrusted input, and
 * before this module existed it went to the database unvalidated. That matters
 * more once the elicitation instrument is deployed publicly: the link is
 * shareable, so submissions can come from anyone.
 *
 * Validation failures throw with a message safe to show a user - they must never
 * echo back the offending value, which could carry injected content.
 */

import { z } from "zod";

import { criteriaTree } from "@/lib/scoring";

/** Criterion ids that actually exist in the model. */
const CRITERION_IDS = new Set(
  criteriaTree.objectives.flatMap((o) =>
    o.dimensions.flatMap((d) => d.criteria.map((c) => c.id)),
  ),
);

const LINGUISTIC_CODES = criteriaTree.linguisticScale.levels.map((l) => l.code);

/** Trimmed, bounded free text. Rejects control characters. */
const text = (max: number) =>
  z
    .string()
    .trim()
    .max(max)
    .refine((v) => !/[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]/.test(v), {
      message: "contains control characters",
    });

export const appraisalHeaderSchema = z.object({
  businessName: text(200).min(1, "Business name is required"),
  branch: text(100).min(1, "Branch is required"),
  facilityAmount: z
    .number()
    .finite()
    .positive("Facility amount must be greater than zero")
    // A Sri Lankan SME facility above Rs. 1bn is not an SME facility; a value
    // that large is a data-entry error, not a real application.
    .max(1_000_000_000, "Facility amount is implausibly large"),
  facilityType: text(60).min(1),
  projectType: text(60).optional(),
  appraisalOfficer: text(120).min(1, "Appraisal officer is required"),
  district: text(100).optional(),
  organisationType: text(60).optional(),
});

/**
 * Criterion inputs. Keys are checked against the model, so an unknown criterion
 * id is rejected rather than silently stored and later ignored.
 */
export const appraisalInputSchema = z
  .record(
    z.string(),
    z.union([z.number().finite(), z.enum(LINGUISTIC_CODES as [string, ...string[]]), z.null()]),
  )
  .refine(
    (input) => Object.keys(input).every((k) => CRITERION_IDS.has(k)),
    { message: "Input contains a criterion id that is not in the model" },
  );

const RATING = z.number().int().min(1).max(9);

export const elicitationResponseSchema = z.object({
  level: text(120).min(1),
  best: text(80).min(1),
  worst: text(80).min(1),
  bestToOthers: z.record(z.string(), RATING),
  othersToWorst: z.record(z.string(), RATING),
}).refine((r) => r.best !== r.worst, {
  message: "The most and least important item cannot be the same",
});

export const respondentSchema = z.object({
  // Participant codes are identifiers, not free text - constraining the
  // character set keeps them safe to use in filenames and CSV exports.
  respondentCode: z
    .string()
    .trim()
    .min(1, "A participant code is required")
    .max(40)
    .regex(/^[A-Za-z0-9_-]+$/, "Use only letters, numbers, hyphens and underscores"),
  yearsExperience: z.number().int().min(0).max(70).optional(),
  institution: text(80).optional(),
  role: text(80).optional(),
});

export const decisionSchema = z.object({
  id: z.string().trim().min(1).max(60),
  action: z.enum(["RECOMMENDED", "APPROVED", "DECLINED"]),
  actor: text(120).min(1, "A name or designation is required"),
  role: text(80).min(1),
  note: text(1000).optional(),
});

/**
 * Validate, or throw an error whose message is safe to display.
 *
 * Zod's own message can quote the offending input; this reports only which
 * fields failed and why, never the values themselves.
 */
export function validate<T>(schema: z.ZodType<T>, value: unknown, what: string): T {
  const result = schema.safeParse(value);
  if (result.success) return result.data;

  const issues = result.error.issues
    .map((i) => {
      const path = i.path.join(".");
      return path ? `${path}: ${i.message}` : i.message;
    })
    .slice(0, 5)
    .join("; ");

  throw new Error(`Invalid ${what} — ${issues}`);
}
