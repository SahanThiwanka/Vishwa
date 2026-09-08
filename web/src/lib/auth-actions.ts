"use server";

import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import { z } from "zod";

import { getSession } from "@/lib/dal";
import { prisma } from "@/lib/db";
import {
  createSessionToken,
  sessionCookieName,
  sessionMaxAge,
  verifyPassword,
} from "@/lib/session";
import { validate } from "@/lib/validation";

const credentialsSchema = z.object({
  username: z.string().trim().min(1, "Username is required").max(60),
  password: z.string().min(1, "Password is required").max(200),
});

/**
 * Sign in.
 *
 * Failures return one message regardless of cause. Distinguishing "no such
 * user" from "wrong password" tells an attacker which usernames exist, and the
 * dummy verification keeps the timing of both paths comparable so the same
 * information cannot be recovered from response time.
 */
export async function signIn(
  _prev: { error?: string } | null,
  formData: FormData,
): Promise<{ error?: string }> {
  let target = "/";

  try {
    const { username, password } = validate(
      credentialsSchema,
      {
        username: formData.get("username"),
        password: formData.get("password"),
      },
      "credentials",
    );

    const user = await prisma.user.findUnique({ where: { username } });

    if (!user || !user.active) {
      // Verify against a throwaway hash so a missing user costs the same time
      // as a wrong password.
      verifyPassword(
        password,
        "00000000000000000000000000000000:" + "0".repeat(128),
      );
      return { error: "Incorrect username or password" };
    }

    if (!verifyPassword(password, user.passwordHash)) {
      return { error: "Incorrect username or password" };
    }

    const token = createSessionToken({
      userId: user.id,
      username: user.username,
      displayName: user.displayName,
      role: user.role,
    });

    (await cookies()).set(sessionCookieName, token, {
      httpOnly: true,
      sameSite: "lax",
      secure: process.env.NODE_ENV === "production",
      path: "/",
      maxAge: sessionMaxAge,
    });

    const from = formData.get("from");
    if (typeof from === "string" && from.startsWith("/") && !from.startsWith("//")) {
      target = from;
    }
  } catch (error) {
    // Validation failures are written for users and are safe to show. Anything
    // else is an internal fault: log it server-side and return a generic
    // message, so database or framework internals never reach the login screen.
    if (error instanceof Error && error.message.startsWith("Invalid ")) {
      return { error: error.message };
    }
    console.error("Sign-in failed:", error);
    return { error: "Sign-in is temporarily unavailable. Please try again." };
  }

  // redirect() throws, so it must sit outside the try block.
  redirect(target);
}

export async function signOut() {
  (await cookies()).delete(sessionCookieName);
  redirect("/login");
}

/** The signed-in user, for rendering. Null when signed out. */
export async function currentUser() {
  const session = await getSession();
  if (!session) return null;
  return {
    username: session.username,
    displayName: session.displayName,
    role: session.role,
  };
}
