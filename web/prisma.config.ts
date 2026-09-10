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
/**
 * Pick the schema that matches the database being used.
 *
 * `src/lib/db.ts` chooses its driver adapter from the shape of DATABASE_URL, so
 * the generated client has to be built from the schema for the same provider.
 * Defaulting to the SQLite schema regardless meant the Vercel build generated a
 * sqlite client, the runtime then loaded the PostgreSQL adapter, and the build
 * died with "The Driver Adapter `@prisma/adapter-pg` ... is not compatible with
 * the provider `sqlite`". The two decisions were made in different files from
 * different inputs, so they could disagree; now they read the same one.
 *
 * PRISMA_SCHEMA still overrides, for the rare case of pointing the CLI at a
 * schema that does not match the current URL.
 */
function schemaPath(): string {
  if (process.env.PRISMA_SCHEMA) return process.env.PRISMA_SCHEMA;
  const url = process.env.DATABASE_URL ?? "";
  const postgres = url.startsWith("postgres://") ||
    url.startsWith("postgresql://");
  return path.join("prisma", postgres ? "schema.postgres.prisma"
                                      : "schema.prisma");
}

export default defineConfig({
  schema: schemaPath(),
  migrations: {
    path: path.join("prisma", "migrations"),
  },
  datasource: {
    url: directConnection(process.env.DATABASE_URL) ?? "file:./dev.db",
  },
});
