/**
 * Create the demonstration user accounts.
 *
 * Run:  npm run db:seed-users
 *
 * These are DEMONSTRATION credentials for a research prototype. They are
 * intentionally printed on creation so they can be used in a viva, and they
 * must not be used on any deployment reachable from the internet — change the
 * passwords, or create accounts individually, before deploying.
 */

import { PrismaBetterSqlite3 } from "@prisma/adapter-better-sqlite3";
import { randomBytes, scryptSync } from "node:crypto";

import { PrismaClient } from "../src/generated/prisma/client";

function hashPassword(password: string): string {
  const salt = randomBytes(16);
  const derived = scryptSync(password, salt, 64);
  return `${salt.toString("hex")}:${derived.toString("hex")}`;
}

const USERS = [
  {
    username: "officer",
    password: "officer-demo",
    displayName: "A. Athukorala",
    designation: "Appraisal Officer",
    role: "OFFICER",
  },
  {
    username: "recommender",
    password: "recommender-demo",
    displayName: "K. Perera",
    designation: "Branch Manager",
    role: "RECOMMENDER",
  },
  {
    username: "headoffice",
    password: "headoffice-demo",
    displayName: "S. Fernando",
    designation: "Head Office Credit",
    role: "HEAD_OFFICE",
  },
];

async function main() {
  const url = process.env.DATABASE_URL ?? "file:./dev.db";

  // Refuse to run against anything but the local file.
  //
  // The passwords below are committed to the repository, deliberately, so a
  // viva demonstration needs no secret handling. That makes running this
  // against a deployment equivalent to publishing an admin login. The comment
  // above used to be the only thing preventing it, and a comment is not a
  // control.
  if (url.startsWith("postgres://") || url.startsWith("postgresql://")) {
    console.error(
      "Refusing to run: DATABASE_URL points at PostgreSQL.\n\n" +
        "These are demonstration accounts whose passwords are published in\n" +
        "this repository. Creating them on a deployment would publish a\n" +
        "working login for it.\n\n" +
        "To create a real account with a password you choose:\n" +
        "    npm run db:create-user\n\n" +
        "To seed the demo accounts locally, comment DATABASE_URL out of\n" +
        "web/.env first.",
    );
    process.exit(1);
  }

  const adapter = new PrismaBetterSqlite3({ url });
  const prisma = new PrismaClient({ adapter });

  console.log("Demonstration accounts:\n");
  for (const user of USERS) {
    const { password, ...rest } = user;
    await prisma.user.upsert({
      where: { username: user.username },
      update: { ...rest, passwordHash: hashPassword(password) },
      create: { ...rest, passwordHash: hashPassword(password) },
    });
    console.log(`  ${user.username.padEnd(14)} ${password.padEnd(20)} ${user.role}`);
  }

  console.log("\nDemonstration accounts only. Do not deploy these publicly.");
  await prisma.$disconnect();
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
