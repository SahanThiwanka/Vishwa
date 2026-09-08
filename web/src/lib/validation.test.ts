/**
 * Tests for input validation.
 *
 * Server Actions accept direct POSTs, so these schemas are the trust boundary
 * between the public internet and the database. Once the elicitation instrument
 * is deployed the link is shareable, so submissions can come from anyone.
 */

import { describe, expect, it } from "vitest";

import {
  appraisalHeaderSchema,
  appraisalInputSchema,
  decisionSchema,
  elicitationResponseSchema,
  respondentSchema,
  validate,
} from "./validation";

const goodHeader = {
  businessName: "Lanka Spice Processors (Pvt) Ltd",
  branch: "Kurunegala",
  facilityAmount: 12_500_000,
  facilityType: "Term Loan",
  appraisalOfficer: "A. Athukorala",
};

describe("appraisal header", () => {
  it("accepts a well-formed header", () => {
    expect(() => validate(appraisalHeaderSchema, goodHeader, "header")).not.toThrow();
  });

  it("rejects a missing business name", () => {
    expect(() =>
      validate(appraisalHeaderSchema, { ...goodHeader, businessName: "" }, "header"),
    ).toThrow(/business/i);
  });

  it("rejects a zero or negative facility amount", () => {
    for (const amount of [0, -1]) {
      expect(() =>
        validate(appraisalHeaderSchema, { ...goodHeader, facilityAmount: amount }, "header"),
      ).toThrow();
    }
  });

  it("rejects an implausibly large facility", () => {
    expect(() =>
      validate(appraisalHeaderSchema, { ...goodHeader, facilityAmount: 5e9 }, "header"),
    ).toThrow(/implausibly/i);
  });

  it("rejects NaN and Infinity", () => {
    for (const amount of [NaN, Infinity]) {
      expect(() =>
        validate(appraisalHeaderSchema, { ...goodHeader, facilityAmount: amount }, "header"),
      ).toThrow();
    }
  });

  it("rejects control characters in free text", () => {
    expect(() =>
      validate(
        appraisalHeaderSchema,
        { ...goodHeader, businessName: "Acme\u0007Ltd" },
        "header",
      ),
    ).toThrow(/control/i);
  });

  it("trims surrounding whitespace", () => {
    const parsed = validate(
      appraisalHeaderSchema,
      { ...goodHeader, branch: "  Kurunegala  " },
      "header",
    );
    expect(parsed.branch).toBe("Kurunegala");
  });

  it("rejects an over-long business name", () => {
    expect(() =>
      validate(appraisalHeaderSchema, { ...goodHeader, businessName: "x".repeat(500) }, "header"),
    ).toThrow();
  });
});

describe("criterion inputs", () => {
  it("accepts known criteria with valid values", () => {
    expect(() =>
      validate(appraisalInputSchema, { dscr: 1.8, org_structure: "G" }, "inputs"),
    ).not.toThrow();
  });

  it("rejects a criterion id that is not in the model", () => {
    expect(() =>
      validate(appraisalInputSchema, { made_up_criterion: 5 }, "inputs"),
    ).toThrow(/not in the model/i);
  });

  it("rejects a linguistic code outside the scale", () => {
    expect(() =>
      validate(appraisalInputSchema, { org_structure: "AMAZING" }, "inputs"),
    ).toThrow();
  });

  it("accepts an empty appraisal", () => {
    expect(() => validate(appraisalInputSchema, {}, "inputs")).not.toThrow();
  });
});

describe("elicitation responses", () => {
  const good = {
    level: "dimension:credit_conduct",
    best: "repayment_performance",
    worst: "external_exposure",
    bestToOthers: { repayment_performance: 1, arrears_ratio: 3 },
    othersToWorst: { external_exposure: 1, arrears_ratio: 2 },
  };

  it("accepts a well-formed response", () => {
    expect(() => validate(elicitationResponseSchema, good, "response")).not.toThrow();
  });

  it("rejects the same item as both best and worst", () => {
    expect(() =>
      validate(elicitationResponseSchema, { ...good, worst: good.best }, "response"),
    ).toThrow(/cannot be the same/i);
  });

  it("rejects ratings outside the 1-9 scale", () => {
    for (const bad of [0, 10, -3]) {
      expect(() =>
        validate(
          elicitationResponseSchema,
          { ...good, bestToOthers: { arrears_ratio: bad } },
          "response",
        ),
      ).toThrow();
    }
  });

  it("rejects non-integer ratings", () => {
    expect(() =>
      validate(
        elicitationResponseSchema,
        { ...good, bestToOthers: { arrears_ratio: 2.5 } },
        "response",
      ),
    ).toThrow();
  });
});

describe("respondent", () => {
  it("accepts a simple participant code", () => {
    expect(() => validate(respondentSchema, { respondentCode: "R01" }, "respondent")).not.toThrow();
  });

  it("rejects codes with characters unsafe for filenames and exports", () => {
    for (const code of ["R 01", "R/01", "../etc", "R;DROP"]) {
      expect(() =>
        validate(respondentSchema, { respondentCode: code }, "respondent"),
      ).toThrow();
    }
  });

  it("rejects an empty code", () => {
    expect(() => validate(respondentSchema, { respondentCode: "" }, "respondent")).toThrow();
  });

  it("rejects implausible years of experience", () => {
    expect(() =>
      validate(respondentSchema, { respondentCode: "R01", yearsExperience: 120 }, "respondent"),
    ).toThrow();
  });
});

describe("decisions", () => {
  const good = {
    id: "abc123",
    action: "APPROVED" as const,
    actor: "K. Perera, Branch Manager",
    role: "Head Office",
  };

  it("accepts a valid decision", () => {
    expect(() => validate(decisionSchema, good, "decision")).not.toThrow();
  });

  it("rejects an action outside the sign-off chain", () => {
    expect(() =>
      validate(decisionSchema, { ...good, action: "DELETED" }, "decision"),
    ).toThrow();
  });

  it("rejects an unnamed signatory", () => {
    expect(() => validate(decisionSchema, { ...good, actor: "" }, "decision")).toThrow();
  });
});

describe("error messages", () => {
  it("names the failing field without echoing the value back", () => {
    let message = "";
    try {
      validate(
        appraisalHeaderSchema,
        { ...goodHeader, businessName: "SECRET-INJECTED-VALUE" + "\u0007" },
        "appraisal details",
      );
    } catch (e) {
      message = e instanceof Error ? e.message : String(e);
    }
    expect(message).toContain("businessName");
    expect(message).not.toContain("SECRET-INJECTED-VALUE");
  });
});
