/**
 * Proxy — optimistic route protection.
 *
 * Next.js 16 renamed Middleware to Proxy; the file must be `proxy.ts` beside the
 * app directory. Per the framework's own guidance this performs an OPTIMISTIC
 * check only: it reads the session cookie and redirects, without touching the
 * database. Real authorisation lives in the Data Access Layer (src/lib/dal.ts),
 * as close to the data as possible.
 *
 * The elicitation instrument is deliberately PUBLIC. Practitioners complete it
 * from a shared link and must not need an account; requiring one would collapse
 * the response rate and defeat the purpose of deploying it.
 */

import { NextResponse, type NextRequest } from "next/server";

import { sessionCookieName, verifySessionToken } from "@/lib/session";

/** Reachable without signing in. */
const PUBLIC_PATHS = [
  "/login",
  "/elicitation", // the research instrument — public by design
  "/api/health",
];

function isPublic(pathname: string): boolean {
  return PUBLIC_PATHS.some(
    (p) => pathname === p || pathname.startsWith(`${p}/`),
  );
}

export function proxy(request: NextRequest) {
  const { pathname } = request.nextUrl;

  if (isPublic(pathname)) return NextResponse.next();

  const session = verifySessionToken(
    request.cookies.get(sessionCookieName)?.value,
  );

  if (!session) {
    const url = new URL("/login", request.url);
    // Preserve where they were headed so login can return them there.
    url.searchParams.set("from", pathname);
    return NextResponse.redirect(url);
  }

  return NextResponse.next();
}

export const config = {
  // Everything except Next internals and static assets.
  matcher: ["/((?!_next/static|_next/image|favicon.ico|.*\.(?:png|jpg|svg|ico)$).*)"],
};
