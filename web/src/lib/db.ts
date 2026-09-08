/**
 * Prisma client singleton.
 *
 * Prisma 7 requires a driver adapter rather than a connection string in the
 * schema, so the adapter is chosen here from the shape of DATABASE_URL:
 *
 *   file:./dev.db        -> SQLite  (local development, demonstrations)
 *   postgres://... | postgresql://...  -> PostgreSQL (deployment)
 *
 * SQLite is the committed default on purpose. The system must run for a
 * demonstration with no network and no external services; a deployment that
 * depends on a cloud database is a poor thing to rely on in a viva. Vercel's
 * filesystem is ephemeral, so production uses PostgreSQL.
 *
 * The globalThis cache prevents Next.js dev-mode hot reloading from opening a
 * new connection on every edit, which exhausts handles quickly.
 */

import { PrismaBetterSqlite3 } from "@prisma/adapter-better-sqlite3";
import { PrismaPg } from "@prisma/adapter-pg";

import { PrismaClient } from "@/generated/prisma/client";

const globalForPrisma = globalThis as unknown as {
  prisma: PrismaClient | undefined;
};

const DATABASE_URL = process.env.DATABASE_URL ?? "file:./dev.db";

function isPostgres(url: string): boolean {
  return url.startsWith("postgres://") || url.startsWith("postgresql://");
}

function createClient(): PrismaClient {
  if (isPostgres(DATABASE_URL)) {
    // Serverless: many short-lived invocations, so keep the pool small and let
    // connections retire quickly rather than exhausting the database's limit.
    const adapter = new PrismaPg({
      connectionString: DATABASE_URL,
      max: 5,
      idleTimeoutMillis: 10_000,
    });
    return new PrismaClient({ adapter });
  }

  const adapter = new PrismaBetterSqlite3({ url: DATABASE_URL });
  return new PrismaClient({ adapter });
}

export const prisma = globalForPrisma.prisma ?? createClient();

if (process.env.NODE_ENV !== "production") {
  globalForPrisma.prisma = prisma;
}

/** Which backend is in use — surfaced in the deployment health check. */
export const databaseBackend = isPostgres(DATABASE_URL) ? "postgresql" : "sqlite";
