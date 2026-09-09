/**
 * Tests for sign-in rate limiting.
 *
 * The failure this guards against is silent: a limiter that is wired in but
 * never actually refuses looks exactly like a working one until someone runs a
 * password list against it. The boundary cases matter most — off-by-one at the
 * threshold is the difference between eight guesses and unlimited guesses.
 */

import { beforeEach, describe, expect, it, vi } from "vitest";

const count = vi.fn();

vi.mock("@/lib/db", () => ({
  prisma: {
    loginAttempt: {
      count: (...args: unknown[]) => count(...args),
      create: vi.fn(),
      deleteMany: vi.fn(),
    },
  },
}));

const {
  MAX_ATTEMPTS_PER_CLIENT,
  MAX_ATTEMPTS_PER_USER,
  WINDOW_MINUTES,
  checkSignInAllowed,
  clientAddress,
  hashClient,
} = await import("./rate-limit");

/** First call is the per-username count, second is the per-client count. */
function counts(user: number, client: number) {
  count.mockReset();
  count.mockResolvedValueOnce(user).mockResolvedValueOnce(client);
}

describe("client address extraction", () => {
  it("takes the original client from a forwarded chain", () => {
    const h = new Headers({ "x-forwarded-for": "203.0.113.7, 70.41.3.18" });
    expect(clientAddress(h)).toBe("203.0.113.7");
  });

  it("falls back to x-real-ip", () => {
    expect(clientAddress(new Headers({ "x-real-ip": "203.0.113.9" }))).toBe(
      "203.0.113.9",
    );
  });

  it("returns null when the address is unknown", () => {
    expect(clientAddress(new Headers())).toBeNull();
  });
});

describe("client hashing", () => {
  it("never returns the address itself", () => {
    const hashed = hashClient("203.0.113.7");
    expect(hashed).not.toBeNull();
    expect(hashed).not.toContain("203.0.113.7");
  });

  it("is stable for the same address and different across addresses", () => {
    expect(hashClient("203.0.113.7")).toBe(hashClient("203.0.113.7"));
    expect(hashClient("203.0.113.7")).not.toBe(hashClient("203.0.113.8"));
  });

  it("passes null through", () => {
    expect(hashClient(null)).toBeNull();
  });
});

describe("sign-in limiting", () => {
  beforeEach(() => count.mockReset());

  it("allows an attempt when nothing has failed", async () => {
    counts(0, 0);
    expect(await checkSignInAllowed("officer", "abc")).toEqual({
      allowed: true,
    });
  });

  it("still allows the attempt one below the username threshold", async () => {
    counts(MAX_ATTEMPTS_PER_USER - 1, 0);
    expect(await checkSignInAllowed("officer", "abc")).toEqual({
      allowed: true,
    });
  });

  it("refuses at the username threshold", async () => {
    counts(MAX_ATTEMPTS_PER_USER, 0);
    expect(await checkSignInAllowed("officer", "abc")).toEqual({
      allowed: false,
      retryAfterMinutes: WINDOW_MINUTES,
    });
  });

  it("refuses at the client threshold even when the username is clean", async () => {
    // The case the per-username limit alone would miss: one attacker spreading
    // a small number of guesses across many different usernames.
    counts(0, MAX_ATTEMPTS_PER_CLIENT);
    expect(await checkSignInAllowed("officer", "abc")).toEqual({
      allowed: false,
      retryAfterMinutes: WINDOW_MINUTES,
    });
  });

  it("does not consult the client counter when the address is unknown", async () => {
    count.mockReset();
    count.mockResolvedValueOnce(0);
    expect(await checkSignInAllowed("officer", null)).toEqual({ allowed: true });
    expect(count).toHaveBeenCalledTimes(1);
  });

  it("counts a username case-insensitively", async () => {
    counts(0, 0);
    await checkSignInAllowed("  Officer  ", "abc");
    expect(count.mock.calls[0][0]).toMatchObject({
      where: expect.objectContaining({ subject: "officer" }),
    });
  });

  it("counts only failures inside the window", async () => {
    counts(0, 0);
    const before = Date.now();
    await checkSignInAllowed("officer", "abc");
    const where = count.mock.calls[0][0].where as {
      createdAt: { gte: Date };
    };
    const elapsed = before - where.createdAt.gte.getTime();
    expect(elapsed).toBeGreaterThanOrEqual(WINDOW_MINUTES * 60_000 - 1_000);
    expect(elapsed).toBeLessThanOrEqual(WINDOW_MINUTES * 60_000 + 1_000);
  });
});
