import path from "node:path";
import { config as loadEnv } from "dotenv";
import { defineConfig } from "prisma/config";

// Prisma 7 no longer accepts `url` inside the schema's datasource block.
// Migration and introspection commands read the connection string from here;
// the runtime client gets a driver adapter instead (see src/lib/db.ts).
//
// .env IS LOADED EXPLICITLY, AND HAS TO BE. Prisma 7 stopped reading .env
// automatically, and this file falls back to the local SQLite database when
// DATABASE_URL is unset. Those two behaviours together are a trap: someone
// writes their PostgreSQL URL into .env exactly as every tutorial says, runs
// `db push`, and Prisma silently applies the PostgreSQL schema to dev.db
// instead. It reports success. The cloud database stays empty, and the reason
// is invisible.
//
// Shell variables still win, so `$env:DATABASE_URL="..."` overrides the file.
loadEnv({ path: path.join(__dirname, ".env"), quiet: true });

/**
 * Neon hands out a pooled connection string by default, and the schema tools
 * want a direct one.
 *
 * The pooled endpoint runs through PgBouncer in transaction mode, which does
 * not support everything `db push` needs; the failures it produces are obscure
 * and do not mention pooling. Neon's own direct endpoint is the same host with
 * the `-pooler` suffix removed, so the correct URL can be derived rather than
 * demanded from whoever is deploying.
 *
 * This rewrites the URL only for Prisma's CLI, only for Neon hosts, and prints
 * what it did. The application keeps using the pooled string at runtime, which
 * is what pooling is for.
 */
function directConnection(url: string | undefined): string | undefined {
  if (!url || !url.includes(".neon.tech") || !url.includes("-pooler")) {
    return url;
  }
  const direct = url.replace("-pooler.", ".");
  console.log(
    "prisma.config.ts: using Neon's direct endpoint for schema commands " +
      "(dropped '-pooler'). The app still uses the pooled URL at runtime.",
  );
  return direct;
}

// PRISMA_SCHEMA selects the PostgreSQL schema for deployment:
//   PRISMA_SCHEMA=prisma/schema.postgres.prisma npx prisma db push
export default defineConfig({
  schema: process.env.PRISMA_SCHEMA ?? path.join("prisma", "schema.prisma"),
  migrations: {
    path: path.join("prisma", "migrations"),
  },
  datasource: {
    url: directConnection(process.env.DATABASE_URL) ?? "file:./dev.db",
  },
});
