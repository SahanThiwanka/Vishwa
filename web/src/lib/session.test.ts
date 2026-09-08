/**
 * Tests for password hashing, session tokens, and the sign-off role matrix.
 *
 * These guard the authorisation boundary. A regression here does not produce a
 * visibly broken page — it produces a system that quietly lets the wrong person
 * sign off a credit facility, which is exactly the failure the audit trail
 * exists to prevent.
 */

import { describe, expect, it, vi } from "vitest";

import { canDecide } from "./dal";
import {
  createSessionToken,
  hashPassword,
  verifyPassword,
  verifySessionToken,
} from "./session";

describe("password hashing", () => {
  it("verifies a correct password", () => {
    const hash = hashPassword("correct horse battery staple");
    expect(verifyPassword("correct horse battery staple", hash)).toBe(true);
  });

  it("rejects an incorrect password", () => {
    const hash = hashPassword("correct horse battery staple");
    expect(verifyPassword("Correct horse battery staple", hash)).toBe(false);
    expect(verifyPassword("", hash)).toBe(false);
  });

  it("never stores the password in the hash", () => {
    const hash = hashPassword("hunter2");
    expect(hash).not.toContain("hunter2");
  });

  it("salts, so identical passwords hash differently", () => {
    expect(hashPassword("same")).not.toBe(hashPassword("same"));
  });

  it("returns false rather than throwing on a malformed stored hash", () => {
    for (const bad of ["", "nonsense", "no-colon-here", ":", "abc:"]) {
      expect(verifyPassword("anything", bad)).toBe(false);
    }
  });
});

describe("session tokens", () => {
  const payload = {
    userId: "u1",
    username: "headoffice",
    displayName: "S. Fernando",
    role: "HEAD_OFFICE",
  };

  it("round-trips a valid session", () => {
    const decoded = verifySessionToken(createSessionToken(payload));
    expect(decoded).not.toBeNull();
    expect(decoded!.username).toBe("headoffice");
    expect(decoded!.role).toBe("HEAD_OFFICE");
  });

  it("rejects a tampered payload", () => {
    const token = createSessionToken(payload);
    const [body, signature] = token.split(".");

    // Re-encode the payload with an escalated role, keeping the old signature.
    const decoded = JSON.parse(
      Buffer.from(body.replace(/-/g, "+").replace(/_/g, "/"), "base64").toString(),
    );
    decoded.role = "ADMIN";
    const forged = Buffer.from(JSON.stringify(decoded))
      .toString("base64")
      .replace(/\+/g, "-")
      .replace(/\//g, "_")
      .replace(/=+$/, "");

    expect(verifySessionToken(`${forged}.${signature}`)).toBeNull();
  });

  it("rejects a tampered signature", () => {
    const token = createSessionToken(payload);
    const [body] = token.split(".");
    expect(verifySessionToken(`${body}.notavalidsignature`)).toBeNull();
  });

  it("rejects malformed and absent tokens", () => {
    for (const bad of [undefined, "", "no-dot", "a.b.c.d"]) {
      expect(verifySessionToken(bad as string | undefined)).toBeNull();
    }
  });

  it("rejects an expired session", () => {
    const token = createSessionToken(payload);
    // Nine hours on; the TTL is eight.
    vi.useFakeTimers();
    vi.setSystemTime(Date.now() + 9 * 60 * 60 * 1000);
    expect(verifySessionToken(token)).toBeNull();
    vi.useRealTimers();
  });
});

describe("sign-off permissions", () => {
  it("lets only the recommending chain recommend", () => {
    expect(canDecide("RECOMMENDER", "RECOMMENDED")).toBe(true);
    expect(canDecide("HEAD_OFFICE", "RECOMMENDED")).toBe(true);
    expect(canDecide("ADMIN", "RECOMMENDED")).toBe(true);
    expect(canDecide("OFFICER", "RECOMMENDED")).toBe(false);
  });

  it("restricts approval and decline to Head Office", () => {
    for (const action of ["APPROVED", "DECLINED"]) {
      expect(canDecide("HEAD_OFFICE", action)).toBe(true);
      expect(canDecide("ADMIN", action)).toBe(true);
      expect(canDecide("RECOMMENDER", action)).toBe(false);
      expect(canDecide("OFFICER", action)).toBe(false);
    }
  });

  it("refuses an unknown role or action", () => {
    expect(canDecide("INTERN", "APPROVED")).toBe(false);
    expect(canDecide("HEAD_OFFICE", "DELETED")).toBe(false);
    expect(canDecide("", "")).toBe(false);
  });
});
