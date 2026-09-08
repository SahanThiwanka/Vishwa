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
  const adapter = new PrismaBetterSqlite3({
    url: process.env.DATABASE_URL ?? "file:./dev.db",
  });
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
