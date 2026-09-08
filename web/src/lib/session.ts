import "server-only";

/**
 * Password hashing and signed session cookies.
 *
 * Deliberately dependency-free, using node:crypto. Next.js 16 runs Proxy on the
 * Node runtime, so the same code verifies sessions in Proxy and in Server
 * Components without pulling in an auth library. For a research prototype that
 * has to run offline for a demonstration, fewer moving parts is the right trade.
 *
 * What this is NOT: a general-purpose auth system. There is no password reset,
 * no rate limiting, no MFA, no account lockout. Those are required for a real
 * banking deployment and are recorded as such in the thesis limitations.
 */

import {
  createHmac,
  randomBytes,
  scryptSync,
  timingSafeEqual,
} from "node:crypto";

const SESSION_COOKIE = "appraisal_session";
const SESSION_TTL_SECONDS = 60 * 60 * 8; // one working day

/**
 * Secret for signing session cookies.
 *
 * In production this MUST be set. Locally it falls back to a fixed development
 * value so the system runs with no configuration — acceptable because the local
 * database holds only demonstration data, and the fallback is refused when
 * NODE_ENV is production.
 */
function sessionSecret(): string {
  const secret = process.env.SESSION_SECRET;
  if (secret && secret.length >= 16) return secret;

  if (process.env.NODE_ENV === "production") {
    throw new Error(
      "SESSION_SECRET must be set to at least 16 characters in production",
    );
  }
  return "dev-only-insecure-session-secret";
}

// ---------------------------------------------------------------------------
// Passwords
// ---------------------------------------------------------------------------

/** Hash a password with scrypt. Returns "salt:derivedKey", both hex. */
export function hashPassword(password: string): string {
  const salt = randomBytes(16);
  const derived = scryptSync(password, salt, 64);
  return `${salt.toString("hex")}:${derived.toString("hex")}`;
}

/** Verify a password in constant time. Never throws on malformed input. */
export function verifyPassword(password: string, stored: string): boolean {
  try {
    const [saltHex, keyHex] = stored.split(":");
    if (!saltHex || !keyHex) return false;

    const salt = Buffer.from(saltHex, "hex");
    const expected = Buffer.from(keyHex, "hex");
    const actual = scryptSync(password, salt, expected.length);

    return timingSafeEqual(expected, actual);
  } catch {
    return false;
  }
}

// ---------------------------------------------------------------------------
// Sessions
// ---------------------------------------------------------------------------

export interface SessionPayload {
  userId: string;
  username: string;
  displayName: string;
  role: string;
  /** Unix seconds. */
  exp: number;
}

function base64url(input: Buffer | string): string {
  return Buffer.from(input)
    .toString("base64")
    .replace(/\+/g, "-")
    .replace(/\//g, "_")
    .replace(/=+$/, "");
}

function sign(data: string): string {
  return base64url(createHmac("sha256", sessionSecret()).update(data).digest());
}

/** Encode a session as a signed, tamper-evident token. */
export function createSessionToken(
  payload: Omit<SessionPayload, "exp">,
): string {
  const full: SessionPayload = {
    ...payload,
    exp: Math.floor(Date.now() / 1000) + SESSION_TTL_SECONDS,
  };
  const body = base64url(JSON.stringify(full));
  return `${body}.${sign(body)}`;
}

/**
 * Verify and decode a session token.
 *
 * Returns null for anything not provably ours and unexpired. The signature is
 * compared in constant time so the check cannot be probed by timing.
 */
export function verifySessionToken(token: string | undefined): SessionPayload | null {
  if (!token) return null;

  const [body, signature] = token.split(".");
  if (!body || !signature) return null;

  const expected = sign(body);
  if (expected.length !== signature.length) return null;
  if (!timingSafeEqual(Buffer.from(expected), Buffer.from(signature))) return null;

  try {
    const payload = JSON.parse(
      Buffer.from(body.replace(/-/g, "+").replace(/_/g, "/"), "base64").toString(),
    ) as SessionPayload;

    if (typeof payload.exp !== "number") return null;
    if (payload.exp < Math.floor(Date.now() / 1000)) return null;

    return payload;
  } catch {
    return null;
  }
}

export const sessionCookieName = SESSION_COOKIE;
export const sessionMaxAge = SESSION_TTL_SECONDS;
