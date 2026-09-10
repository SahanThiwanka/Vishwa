/**
 * Create or update a single user account, with a password you choose.
 *
 * Run:  npm run db:create-user
 *
 * This exists because `db:seed-users` must never run against a deployment.
 * Its three accounts carry passwords committed to the repository, which is
 * correct for a viva demonstration on a laptop and unacceptable on anything
 * reachable from the internet.
 *
 * The password is read from a prompt rather than an argument or an environment
 * variable, so it does not end up in shell history, in the process list, or in
 * a Vercel settings page.
 *
 * Works against whichever database DATABASE_URL points at, choosing the driver
 * adapter the same way src/lib/db.ts does.
 */

import { PrismaBetterSqlite3 } from "@prisma/adapter-better-sqlite3";
import { PrismaPg } from "@prisma/adapter-pg";
import { randomBytes, scryptSync } from "node:crypto";
import { createInterface } from "node:readline";

import { PrismaClient } from "../src/generated/prisma/client";

const ROLES = ["OFFICER", "RECOMMENDER", "HEAD_OFFICE", "ADMIN"];

// Short enough to be typed by a person, long enough that the scrypt cost
// actually matters. Sign-in is rate limited, but a four-character password on a
// public deployment is indefensible regardless.
const MIN_PASSWORD = 12;

function hashPassword(password: string): string {
  const salt = randomBytes(16);
  const derived = scryptSync(password, salt, 64);
  return `${salt.toString("hex")}:${derived.toString("hex")}`;
}

function ask(question: string, hidden = false): Promise<string> {
  const rl = createInterface({ input: process.stdin, output: process.stdout });
  return new Promise((resolve) => {
    if (hidden) {
      // Suppress echo so the password is not left on screen or in a screenshot.
      const stdout = process.stdout as NodeJS.WriteStream & {
        muted?: boolean;
      };
      const write = stdout.write.bind(stdout);
      stdout.muted = false;
      (rl as unknown as { _writeToOutput: (s: string) => void })._writeToOutput =
        (s: string) => {
          if (!stdout.muted) write(s);
        };
      rl.question(question, (answer) => {
        stdout.muted = false;
        write("\n");
        rl.close();
        resolve(answer.trim());
      });
      stdout.muted = true;
      write(question);
      return;
    }
    rl.question(question, (answer) => {
      rl.close();
      resolve(answer.trim());
    });
  });
}

function client(): PrismaClient {
  const url = process.env.DATABASE_URL ?? "file:./dev.db";
  const postgres =
    url.startsWith("postgres://") || url.startsWith("postgresql://");

  console.log(
    postgres
      ? "Target: PostgreSQL (the deployed database)"
      : "Target: local SQLite (web/dev.db)",
  );

  const adapter = postgres
    ? new PrismaPg({ connectionString: url })
    : new PrismaBetterSqlite3({ url });
  return new PrismaClient({ adapter });
}

async function main() {
  const prisma = client();

  const username = (await ask("Username: ")).toLowerCase();
  if (!username) {
    console.error("A username is required.");
    process.exit(1);
  }

  const displayName = await ask("Display name (as it should appear on sign-offs): ");
  const designation = await ask("Designation (optional): ");

  console.log(`\nRoles: ${ROLES.join(", ")}`);
  const role = (await ask("Role: ")).toUpperCase();
  if (!ROLES.includes(role)) {
    console.error(`Not a valid role. Choose one of: ${ROLES.join(", ")}`);
    process.exit(1);
  }

  const password = await ask(`Password (min ${MIN_PASSWORD} chars): `, true);
  if (password.length < MIN_PASSWORD) {
    console.error(`Too short - at least ${MIN_PASSWORD} characters.`);
    process.exit(1);
  }
  const again = await ask("Confirm password: ", true);
  if (password !== again) {
    console.error("Passwords do not match. Nothing was written.");
    process.exit(1);
  }

  const existing = await prisma.user.findUnique({ where: { username } });
  await prisma.user.upsert({
    where: { username },
    update: {
      displayName: displayName || username,
      designation: designation || null,
      role,
      passwordHash: hashPassword(password),
      active: true,
    },
    create: {
      username,
      displayName: displayName || username,
      designation: designation || null,
      role,
      passwordHash: hashPassword(password),
    },
  });

  console.log(
    `\n${existing ? "Updated" : "Created"} '${username}' with role ${role}.`,
  );
  console.log("The password was not written to any file or log.");
  await prisma.$disconnect();
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
