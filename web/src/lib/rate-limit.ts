import "server-only";

import { createHash } from "node:crypto";

import { prisma } from "@/lib/db";

/**
 * Sign-in rate limiting.
 *
 * Without this, the sign-in action will verify a password as often as it is
 * asked to. scrypt makes each attempt expensive enough to rule out a fast
 * offline-style attack, but not expensive enough to make an online guessing
 * attack against a weak password impractical, and the appraisal records behind
 * this login are commercially sensitive.
 *
 * Two independent windows are enforced:
 *
 *   per username   stops an attacker working through a password list against
 *                  one known account
 *   per client     stops the same attacker spreading attempts thinly across
 *                  many usernames to stay under the per-username limit
 *
 * State lives in the database rather than in process memory. An in-memory
 * counter resets on restart and is not shared between instances, so on the
 * intended serverless deployment it would be defeated by attempts landing on
 * different cold starts.
 *
 * WHAT THIS DOES NOT DO. It does not defend against a distributed attack from
 * many addresses against many accounts, and the per-client window is only as
 * good as the forwarded address, which a proxy can set. It raises the cost of
 * the ordinary case; it is not a substitute for a WAF in front of a real
 * deployment.
 */

/** Failures allowed against one username before it is locked out. */
export const MAX_ATTEMPTS_PER_USER = 8;

/** Failures allowed from one client address, across all usernames. */
export const MAX_ATTEMPTS_PER_CLIENT = 30;

/** Sliding window, in minutes, over which failures are counted. */
export const WINDOW_MINUTES = 15;

/**
 * Salt for the client-address hash.
 *
 * The point of hashing is that the table should not become a record of which
 * address tried to sign in as which user. A bare hash of an IPv4 address is
 * reversible by enumeration in seconds, so a salt is required for the hash to
 * mean anything. It is read from the environment where one is configured, and
 * otherwise derived per deployment - a fixed literal default would be no salt
 * at all.
 */
const CLIENT_SALT =
  process.env.RATE_LIMIT_SALT ??
  process.env.SESSION_SECRET ??
  "dev-only-rate-limit-salt";

export function hashClient(address: string | null): string | null {
  if (!address) return null;
  return createHash("sha256")
    .update(`${CLIENT_SALT}:${address}`)
    .digest("hex")
    .slice(0, 32);
}

/**
 * Client address from the proxy headers.
 *
 * `x-forwarded-for` is a comma-separated chain; the first entry is the original
 * client. It is trivially spoofable when the app is exposed directly, which is
 * why the per-username limit above does not depend on it.
 */
export function clientAddress(headers: Headers): string | null {
  const forwarded = headers.get("x-forwarded-for");
  if (forwarded) {
    const first = forwarded.split(",")[0]?.trim();
    if (first) return first;
  }
  return headers.get("x-real-ip");
}

export type RateLimitResult =
  | { allowed: true }
  | { allowed: false; retryAfterMinutes: number };

function windowStart(): Date {
  return new Date(Date.now() - WINDOW_MINUTES * 60_000);
}

/**
 * Is this attempt allowed? Call BEFORE verifying the password.
 *
 * Returns the same shape whether the username exists or not — checking the
 * limit before looking the user up keeps the rate limiter from becoming a way
 * to enumerate accounts.
 */
export async function checkSignInAllowed(
  username: string,
  clientHash: string | null,
): Promise<RateLimitResult> {
  const since = windowStart();
  const subject = username.trim().toLowerCase();

  const [userFailures, clientFailures] = await Promise.all([
    prisma.loginAttempt.count({
      where: { subject, createdAt: { gte: since } },
    }),
    clientHash
      ? prisma.loginAttempt.count({
          where: { clientHash, createdAt: { gte: since } },
        })
      : Promise.resolve(0),
  ]);

  if (
    userFailures >= MAX_ATTEMPTS_PER_USER ||
    clientFailures >= MAX_ATTEMPTS_PER_CLIENT
  ) {
    // Report the full window rather than the true remaining time. The exact
    // remainder would tell an attacker when their earliest attempt landed.
    return { allowed: false, retryAfterMinutes: WINDOW_MINUTES };
  }

  return { allowed: true };
}

/** Record a failure. Only failures are stored; successes are not interesting. */
export async function recordFailedSignIn(
  username: string,
  clientHash: string | null,
): Promise<void> {
  await prisma.loginAttempt.create({
    data: { subject: username.trim().toLowerCase(), clientHash },
  });
}

/**
 * Clear a username's failures after a successful sign-in, so a user who
 * mistyped several times is not locked out by their own success.
 */
export async function clearFailedSignIns(username: string): Promise<void> {
  await prisma.loginAttempt.deleteMany({
    where: { subject: username.trim().toLowerCase() },
  });
}

/**
 * Drop rows that have fallen out of the window.
 *
 * Called opportunistically from the sign-in path rather than on a schedule,
 * because the deployment target has no cron. The table is only ever read with a
 * `createdAt >= window` filter, so stale rows affect storage rather than
 * correctness, and a failure to prune must never block a sign-in.
 */
export async function pruneOldAttempts(): Promise<void> {
  try {
    await prisma.loginAttempt.deleteMany({
      where: { createdAt: { lt: windowStart() } },
    });
  } catch {
    // Pruning is housekeeping. Never let it fail a sign-in.
  }
}
