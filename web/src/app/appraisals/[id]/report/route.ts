/**
 * Export a completed appraisal as a Word document in the People's Bank format.
 *
 * This is the point where the system stops being a parallel tool and starts
 * being usable: the officer gets back the document the bank already works with,
 * with the sections it already expects, plus the scoring evidence appended. No
 * retyping, and nothing about the existing approval chain has to change.
 */

import {
  AlignmentType,
  BorderStyle,
  Document,
  HeadingLevel,
  Packer,
  Paragraph,
  Table,
  TableCell,
  TableRow,
  TextRun,
  WidthType,
} from "docx";

import { prisma } from "@/lib/db";
import { criteriaTree } from "@/lib/scoring";
import type { AppraisalResult, ObjectiveResult } from "@/lib/scoring/types";

const CURRENCY = new Intl.NumberFormat("en-LK", { maximumFractionDigits: 2 });

const NO_BORDER = {
  top: { style: BorderStyle.NONE, size: 0, color: "FFFFFF" },
  bottom: { style: BorderStyle.NONE, size: 0, color: "FFFFFF" },
  left: { style: BorderStyle.NONE, size: 0, color: "FFFFFF" },
  right: { style: BorderStyle.NONE, size: 0, color: "FFFFFF" },
};

function heading(text: string) {
  return new Paragraph({
    text,
    heading: HeadingLevel.HEADING_2,
    spacing: { before: 280, after: 140 },
  });
}

function labelled(label: string, value: string) {
  return new TableRow({
    children: [
      new TableCell({
        width: { size: 42, type: WidthType.PERCENTAGE },
        borders: NO_BORDER,
        children: [new Paragraph({ children: [new TextRun({ text: label, bold: true })] })],
      }),
      new TableCell({
        width: { size: 58, type: WidthType.PERCENTAGE },
        borders: NO_BORDER,
        children: [new Paragraph(value)],
      }),
    ],
  });
}

function cell(text: string, opts: { bold?: boolean; align?: (typeof AlignmentType)[keyof typeof AlignmentType] } = {}) {
  return new TableCell({
    children: [
      new Paragraph({
        alignment: opts.align,
        children: [new TextRun({ text, bold: opts.bold })],
      }),
    ],
  });
}

function objectiveSection(objective: ObjectiveResult): Paragraph[] | (Paragraph | Table)[] {
  const blocks: (Paragraph | Table)[] = [heading(objective.name)];

  blocks.push(
    new Paragraph({
      children: [
        new TextRun({ text: "Score: ", bold: true }),
        new TextRun({ text: `${objective.score?.toFixed(1) ?? "not assessed"} / 100` }),
        new TextRun({
          text: `    (${Math.round(objective.completeness * 100)}% of criteria assessed)`,
          italics: true,
        }),
      ],
    }),
  );

  if (objective.sufficient && objective.band) {
    blocks.push(
      new Paragraph({
        children: [
          new TextRun({ text: "Risk band: ", bold: true }),
          new TextRun({
            text: `${objective.band.code} — ${objective.band.label}. ${objective.band.action}.`,
          }),
        ],
      }),
    );
  } else {
    blocks.push(
      new Paragraph({
        children: [
          new TextRun({ text: "Recommendation withheld. ", bold: true }),
          new TextRun({
            text:
              `Only ${Math.round(objective.completeness * 100)}% of criteria were assessed, ` +
              `below the ${Math.round(criteriaTree.completenessPolicy.minObjectiveCompleteness * 100)}% ` +
              `required before this system issues a risk band. ` +
              `${objective.missingCriteria.length} criteria remain outstanding.`,
          }),
        ],
      }),
    );
  }

  const rows = [
    new TableRow({
      children: [
        cell("Dimension", { bold: true }),
        cell("Form clause", { bold: true }),
        cell("Score", { bold: true, align: AlignmentType.RIGHT }),
        cell("Contribution", { bold: true, align: AlignmentType.RIGHT }),
        cell("Assessed", { bold: true, align: AlignmentType.RIGHT }),
      ],
    }),
  ];

  for (const d of objective.dimensions) {
    rows.push(
      new TableRow({
        children: [
          cell(d.name),
          cell(d.ref),
          cell(d.score?.toFixed(1) ?? "—", { align: AlignmentType.RIGHT }),
          cell(d.score !== null ? `${d.contribution.toFixed(1)} pts` : "—", {
            align: AlignmentType.RIGHT,
          }),
          cell(`${Math.round(d.completeness * 100)}%`, { align: AlignmentType.RIGHT }),
        ],
      }),
    );
  }

  blocks.push(new Table({ width: { size: 100, type: WidthType.PERCENTAGE }, rows }));
  return blocks as (Paragraph | Table)[];
}

export async function GET(
  _request: Request,
  { params }: { params: Promise<{ id: string }> },
) {
  const { id } = await params;

  const appraisal = await prisma.appraisal.findUnique({ where: { id } });
  if (!appraisal || !appraisal.result) {
    return new Response("Appraisal not found", { status: 404 });
  }

  const result: AppraisalResult = JSON.parse(appraisal.result);
  const credit = result.objectives.find((o) => o.id === "credit_risk");
  const development = result.objectives.find((o) => o.id === "development_impact");

  const children: (Paragraph | Table)[] = [
    new Paragraph({
      alignment: AlignmentType.RIGHT,
      children: [new TextRun({ text: "Annexure I", italics: true })],
    }),
    new Paragraph({
      alignment: AlignmentType.CENTER,
      children: [new TextRun({ text: "People's Bank", bold: true, size: 32 })],
    }),
    new Paragraph({
      alignment: AlignmentType.CENTER,
      spacing: { after: 240 },
      children: [
        new TextRun({
          text: "Project / Business Appraisal Report for SME Credit Facility",
          bold: true,
          size: 26,
        }),
      ],
    }),

    heading("1.  General Information"),
    new Table({
      width: { size: 100, type: WidthType.PERCENTAGE },
      borders: NO_BORDER,
      rows: [
        labelled("Reference", appraisal.reference),
        labelled("Branch", appraisal.branch),
        labelled("District", appraisal.district ?? "—"),
        labelled("Facility Amount (Rs.)", CURRENCY.format(appraisal.facilityAmount)),
        labelled("Type of Facility", appraisal.facilityType),
        labelled("Project Type", appraisal.projectType ?? "—"),
        labelled("Appraisal Officer", appraisal.appraisalOfficer),
      ],
    }),

    heading("2.  Borrower"),
    new Table({
      width: { size: 100, type: WidthType.PERCENTAGE },
      borders: NO_BORDER,
      rows: [
        labelled("2.1  Business Name", appraisal.businessName),
        labelled("2.7  Organization", appraisal.organisationType ?? "—"),
      ],
    }),
  ];

  if (result.criticalBreaches.length > 0) {
    children.push(heading("Critical Findings"));
    children.push(
      new Paragraph({
        children: [
          new TextRun({
            text:
              "The following criteria breached thresholds that cannot be offset by " +
              "strength elsewhere in the appraisal:",
            italics: true,
          }),
        ],
      }),
    );
    for (const b of result.criticalBreaches) {
      children.push(
        new Paragraph({
          bullet: { level: 0 },
          children: [
            new TextRun({ text: `${b.name} = ${String(b.rawValue)}`, bold: true }),
            new TextRun({ text: `  (clause ${b.ref})` }),
          ],
        }),
      );
    }
  }

  if (credit) children.push(...objectiveSection(credit));
  if (development) children.push(...objectiveSection(development));

  children.push(
    new Paragraph({
      spacing: { before: 200 },
      children: [
        new TextRun({
          text:
            "Note: credit risk and development impact are assessed as separate " +
            "objectives and are deliberately not combined into a single score. A " +
            "facility may be sound on credit grounds while contributing little " +
            "developmentally, or the reverse; that trade-off is a matter for the " +
            "approving authority, not for the scoring model to resolve.",
          italics: true,
          size: 18,
        }),
      ],
    }),
  );

  children.push(
    heading("7.  Recommendation / Approval"),
    new Paragraph({
      spacing: { after: 200 },
      children: [
        new TextRun(
          `This is to certify that we have appraised the application made by ` +
            `${appraisal.businessName} for a loan of Rs. ` +
            `${CURRENCY.format(appraisal.facilityAmount)} and record the assessment above.`,
        ),
      ],
    }),
    new Table({
      width: { size: 100, type: WidthType.PERCENTAGE },
      borders: NO_BORDER,
      rows: [
        new TableRow({
          children: [
            new TableCell({
              borders: NO_BORDER,
              children: [
                new Paragraph({ spacing: { before: 400 }, text: "............................." }),
                new Paragraph("Prepared by (Name & Designation)"),
                new Paragraph(appraisal.appraisalOfficer),
                new Paragraph("Date: ........................"),
              ],
            }),
            new TableCell({
              borders: NO_BORDER,
              children: [
                new Paragraph({ spacing: { before: 400 }, text: "............................." }),
                new Paragraph("Recommended (Name & Designation)"),
                new Paragraph(""),
                new Paragraph("Date: ........................"),
              ],
            }),
          ],
        }),
      ],
    }),
    new Paragraph({
      spacing: { before: 500 },
      children: [
        new TextRun({
          text:
            `Generated by the SME Credit Appraisal decision-support system, model ` +
            `${appraisal.modelVersion}, on ${new Date().toLocaleString("en-GB")}. ` +
            `Criterion weights: ${result.weightStatus.state}. ` +
            `This is a research prototype; the assessment above supports the ` +
            `officer's judgement and does not replace it.`,
          italics: true,
          size: 16,
          color: "666666",
        }),
      ],
    }),
  );

  const doc = new Document({ sections: [{ children }] });
  const buffer = await Packer.toBuffer(doc);

  await prisma.auditEvent.create({
    data: {
      appraisalId: appraisal.id,
      action: "EXPORTED",
      actor: appraisal.appraisalOfficer,
      note: "Appraisal report exported to .docx",
      scoreSnapshot: appraisal.creditRiskScore,
    },
  });

  const filename = `${appraisal.reference.replace(/\//g, "-")}.docx`;

  return new Response(new Uint8Array(buffer), {
    headers: {
      "Content-Type":
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
      "Content-Disposition": `attachment; filename="${filename}"`,
    },
  });
}
