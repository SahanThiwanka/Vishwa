/**
 * Prisma client singleton.
 *
 * Prisma 7 requires a driver adapter rather than a connection string in the
 * schema, so the SQLite adapter is constructed here. Swapping to PostgreSQL for
 * a production deployment means changing this adapter and the schema's
 * `provider` line - no model or query changes.
 *
 * The globalThis cache prevents Next.js dev-mode hot reloading from opening a
 * new database connection on every edit, which exhausts handles quickly.
 */

import { PrismaBetterSqlite3 } from "@prisma/adapter-better-sqlite3";

import { PrismaClient } from "@/generated/prisma/client";

const globalForPrisma = globalThis as unknown as {
  prisma: PrismaClient | undefined;
};

function createClient() {
  const adapter = new PrismaBetterSqlite3({
    url: process.env.DATABASE_URL ?? "file:./dev.db",
  });
  return new PrismaClient({ adapter });
}

export const prisma = globalForPrisma.prisma ?? createClient();

if (process.env.NODE_ENV !== "production") {
  globalForPrisma.prisma = prisma;
}
