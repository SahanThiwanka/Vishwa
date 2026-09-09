/**
 * Page arithmetic for list views.
 *
 * Pulled out of the page component so the edge cases can be tested. They are
 * where the bugs are: a page number that came from the query string is
 * attacker-controlled text, and `?page=0`, `?page=-3`, `?page=abc` and
 * `?page=99999` must each resolve to something sensible rather than producing a
 * negative OFFSET or an empty table with no way back.
 */

export type Pagination = {
  /** The page actually being shown, clamped into range. */
  page: number;
  /** Total pages; at least 1 even when there are no rows. */
  pageCount: number;
  /** Rows to skip in the query. Never negative. */
  skip: number;
  /** Rows to take in the query. */
  take: number;
  /** 1-based index of the first row shown; 0 when there are none. */
  firstRow: number;
  /** 1-based index of the last row shown; 0 when there are none. */
  lastRow: number;
};

export function paginate(
  total: number,
  requested: string | number | undefined | null,
  pageSize: number,
): Pagination {
  const parsed =
    typeof requested === "number"
      ? requested
      : Number.parseInt(requested ?? "1", 10);

  // Anything that is not a usable page number falls back to the first page.
  const asked = Number.isFinite(parsed) && parsed > 0 ? Math.floor(parsed) : 1;

  const pageCount = Math.max(1, Math.ceil(Math.max(0, total) / pageSize));
  const page = Math.min(asked, pageCount);

  const skip = (page - 1) * pageSize;
  const firstRow = total === 0 ? 0 : skip + 1;
  const lastRow = Math.min(page * pageSize, total);

  return { page, pageCount, skip, take: pageSize, firstRow, lastRow };
}
