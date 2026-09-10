"use server";

/**
 * Account management.
 *
 * Two entry points, deliberately separated:
 *
 *   createFirstAdmin  works ONLY while the database holds no users at all
 *   createUser        requires an existing ADMIN session
 *
 * The first exists to solve the bootstrap problem. A deployment starts with no
 * accounts, so there is nobody who can create one, and the alternative -
 * seeding accounts whose passwords live in the repository - would publish a
 * working login for the deployment. It closes permanently the moment the first
 * account exists, so the window is the interval between deploying and setting
 * up, which should be minutes.
 */

import { revalidatePath } from "next/cache";
import { z } from "zod";

import { requireRole } from "@/lib/dal";
import { prisma } from "@/lib/db";
import { hashPassword } from "@/lib/session";
import { validate } from "@/lib/validation";

const ROLES = ["OFFICER", "RECOMMENDER", "HEAD_OFFICE", "ADMIN"] as const;

/**
 * Twelve characters, not eight.
 *
 * Sign-in is rate limited and passwords are scrypt-hashed, so this is not the
 * only defence. But these accounts sign off credit facilities and the audit
 * trail's entire value rests on a signature being attributable to a person, so
 * a guessable password undermines the property the system exists to provide.
 */
const MIN_PASSWORD = 12;

const accountSchema = z.object({
  username: z
    .string()
    .trim()
    .toLowerCase()
    .min(3, "Username must be at least 3 characters")
    .max(40)
    .regex(/^[a-z0-9._-]+$/,
      "Username may contain only letters, numbers, dot, dash and underscore"),
  displayName: z
    .string()
    .trim()
    .min(1, "Display name is required")
    .max(120),
  designation: z.string().trim().max(120).optional(),
  role: z.enum(ROLES),
  password: z
    .string()
    .min(MIN_PASSWORD, `Password must be at least ${MIN_PASSWORD} characters`)
    .max(200),
});

export type AccountResult = { error?: string; ok?: string };

function readForm(formData: FormData) {
  return {
    username: formData.get("username"),
    displayName: formData.get("displayName"),
    designation: formData.get("designation") || undefined,
    role: formData.get("role"),
    password: formData.get("password"),
  };
}

/** How many accounts exist. Used to decide whether setup is still open. */
export async function userCount(): Promise<number> {
  return prisma.user.count();
}

async function create(input: unknown, confirm: unknown): Promise<AccountResult> {
  let data;
  try {
    data = validate(accountSchema, input, "account");
  } catch (error) {
    if (error instanceof Error && error.message.startsWith("Invalid ")) {
      return { error: error.message };
    }
    throw error;
  }

  if (data.password !== confirm) {
    return { error: "The two passwords do not match." };
  }

  const existing = await prisma.user.findUnique({
    where: { username: data.username },
  });
  if (existing) {
    return { error: `An account named '${data.username}' already exists.` };
  }

  await prisma.user.create({
    data: {
      username: data.username,
      displayName: data.displayName,
      designation: data.designation ?? null,
      role: data.role,
      passwordHash: hashPassword(data.password),
    },
  });

  return { ok: `Created '${data.username}' with role ${data.role}.` };
}

/**
 * Create the very first account, as ADMIN.
 *
 * Guarded by the user count being zero, checked here rather than only in the
 * page. A Server Action is reachable by direct POST, so a check that lives only
 * in the rendering path is not a check.
 */
export async function createFirstAdmin(
  _prev: AccountResult | null,
  formData: FormData,
): Promise<AccountResult> {
  if ((await prisma.user.count()) > 0) {
    return {
      error:
        "Setup is closed: this deployment already has accounts. " +
        "Sign in as an administrator to add more.",
    };
  }

  const result = await create(
    { ...readForm(formData), role: "ADMIN" },
    formData.get("confirm"),
  );
  if (result.ok) revalidatePath("/admin/users");
  return result;
}

/** Create a further account. Administrators only. */
export async function createUser(
  _prev: AccountResult | null,
  formData: FormData,
): Promise<AccountResult> {
  try {
    await requireRole(["ADMIN"]);
  } catch (error) {
    return { error: error instanceof Error ? error.message : "Not permitted." };
  }

  const result = await create(readForm(formData), formData.get("confirm"));
  if (result.ok) revalidatePath("/admin/users");
  return result;
}

/**
 * Deactivate or reactivate an account.
 *
 * Accounts are never deleted. A sign-off recorded by someone whose account
 * later vanished would leave an audit trail referring to a person the system
 * cannot describe, which defeats the purpose of keeping one.
 */
export async function setUserActive(
  formData: FormData,
): Promise<AccountResult> {
  let session;
  try {
    session = await requireRole(["ADMIN"]);
  } catch (error) {
    return { error: error instanceof Error ? error.message : "Not permitted." };
  }

  const username = String(formData.get("username") ?? "").trim().toLowerCase();
  const active = formData.get("active") === "true";

  if (username === session.username && !active) {
    return { error: "You cannot deactivate the account you are signed in as." };
  }

  const admins = await prisma.user.count({
    where: { role: "ADMIN", active: true },
  });
  const target = await prisma.user.findUnique({ where: { username } });
  if (!target) return { error: "No such account." };

  if (!active && target.role === "ADMIN" && admins <= 1) {
    return {
      error:
        "This is the only active administrator. Create another before " +
        "deactivating this one, or the deployment becomes unmanageable.",
    };
  }

  await prisma.user.update({ where: { username }, data: { active } });
  revalidatePath("/admin/users");
  return { ok: `${active ? "Reactivated" : "Deactivated"} '${username}'.` };
}
