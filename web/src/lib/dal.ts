import "server-only";

/**
 * Data Access Layer — the authorisation boundary.
 *
 * Next.js documentation is explicit that Proxy should perform optimistic checks
 * only and must not be the sole line of defence. Every real check lives here,
 * as close to the data as possible, and every page or action that touches
 * appraisal data calls one of these functions first.
 *
 * `cache` memoises verification for the duration of a single render pass, so a
 * page with several protected components verifies once rather than per
 * component.
 */

import { cache } from "react";
import { cookies } from "next/headers";
import { redirect } from "next/navigation";

import { sessionCookieName, verifySessionToken, type SessionPayload } from "@/lib/session";

export type Role = "OFFICER" | "RECOMMENDER" | "HEAD_OFFICE" | "ADMIN";

/** Who may take each step of the clause 7 sign-off chain. */
const DECISION_PERMISSIONS: Record<string, Role[]> = {
  RECOMMENDED: ["RECOMMENDER", "HEAD_OFFICE", "ADMIN"],
  APPROVED: ["HEAD_OFFICE", "ADMIN"],
  DECLINED: ["HEAD_OFFICE", "ADMIN"],
};

/** The current session, or null. Does not redirect. */
export const getSession = cache(async (): Promise<SessionPayload | null> => {
  const token = (await cookies()).get(sessionCookieName)?.value;
  return verifySessionToken(token);
});

/** The current session, or redirect to login. Use in protected pages. */
export const requireSession = cache(async (): Promise<SessionPayload> => {
  const session = await getSession();
  if (!session) redirect("/login");
  return session;
});

/**
 * Require a session holding one of `roles`.
 *
 * Throws rather than redirecting, because this guards actions rather than
 * navigation: a user who is signed in but lacks the role has not taken a wrong
 * turn, they have attempted something they may not do, and that should surface
 * as an error rather than a silent bounce to the login page.
 */
export async function requireRole(roles: Role[]): Promise<SessionPayload> {
  const session = await requireSession();
  if (!roles.includes(session.role as Role)) {
    throw new Error(
      `This action requires the role ${roles.join(" or ")}. You are signed in as ${session.role}.`,
    );
  }
  return session;
}

/** Whether a role may record a given sign-off decision. */
export function canDecide(role: string, action: string): boolean {
  return (DECISION_PERMISSIONS[action] ?? []).includes(role as Role);
}

/** Roles permitted to take a given decision — for guarding the UI. */
export function rolesFor(action: string): Role[] {
  return DECISION_PERMISSIONS[action] ?? [];
}
