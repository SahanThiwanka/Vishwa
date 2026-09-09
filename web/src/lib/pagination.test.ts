/**
 * Tests for list pagination.
 *
 * The page number arrives from the query string, so it is untrusted input. A
 * negative or non-numeric value reaching the query as an OFFSET is the failure
 * these guard against — Prisma rejects a negative skip at runtime, which would
 * turn `?page=-1` into a 500 on the dashboard.
 */

import { describe, expect, it } from "vitest";

import { paginate } from "./pagination";

const SIZE = 25;

describe("paginate", () => {
  it("describes the first page of a full list", () => {
    expect(paginate(100, "1", SIZE)).toEqual({
      page: 1,
      pageCount: 4,
      skip: 0,
      take: 25,
      firstRow: 1,
      lastRow: 25,
    });
  });

  it("describes a middle page", () => {
    const p = paginate(100, "3", SIZE);
    expect(p).toMatchObject({ page: 3, skip: 50, firstRow: 51, lastRow: 75 });
  });

  it("reports a short final page correctly", () => {
    // 63 rows: the last page holds 13, not 25.
    const p = paginate(63, "3", SIZE);
    expect(p).toMatchObject({ page: 3, pageCount: 3, firstRow: 51, lastRow: 63 });
  });

  it("clamps a page beyond the end to the last page", () => {
    const p = paginate(60, "9999", SIZE);
    expect(p).toMatchObject({ page: 3, pageCount: 3, skip: 50, lastRow: 60 });
  });

  it.each([["0"], ["-3"], ["abc"], [""], [undefined], [null]])(
    "falls back to page 1 for %p",
    (input) => {
      const p = paginate(100, input as string | undefined | null, SIZE);
      expect(p.page).toBe(1);
      expect(p.skip).toBe(0);
    },
  );

  it("never produces a negative skip", () => {
    for (const bad of ["-1", "-100", "0", "NaN", "1e-9"]) {
      expect(paginate(10, bad, SIZE).skip).toBeGreaterThanOrEqual(0);
    }
  });

  it("handles an empty list without claiming to show a row", () => {
    expect(paginate(0, "1", SIZE)).toEqual({
      page: 1,
      pageCount: 1,
      skip: 0,
      take: 25,
      firstRow: 0,
      lastRow: 0,
    });
  });

  it("gives an exact multiple the right number of pages", () => {
    // 50 rows over a page size of 25 is two pages, not three.
    expect(paginate(50, "1", SIZE).pageCount).toBe(2);
    expect(paginate(75, "1", SIZE).pageCount).toBe(3);
  });

  it("truncates a fractional page number rather than rejecting it", () => {
    expect(paginate(100, "2.7", SIZE).page).toBe(2);
  });
});
