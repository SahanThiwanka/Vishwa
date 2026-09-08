/**
 * Generate the PostgreSQL schema from the SQLite one.
 *
 * `prisma/schema.prisma` (SQLite) is the source of truth. SQLite is kept as the
 * committed default deliberately: the system must run for a demonstration with
 * no network and no external services. Production on Vercel needs PostgreSQL,
 * because Vercel's filesystem is ephemeral and a SQLite file written there is
 * lost on every deployment and not shared between serverless invocations.
 *
 * Rather than maintain two schemas by hand and let them drift, this derives the
 * PostgreSQL variant mechanically. Prisma does not accept an env var for the
 * datasource provider, so the two files must exist separately.
 *
 * Run:  npm run db:gen-postgres
 */

import { readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const source = join(here, "..", "prisma", "schema.prisma");
const target = join(here, "..", "prisma", "schema.postgres.prisma");

let schema = readFileSync(source, "utf8");

if (!schema.includes('provider = "sqlite"')) {
  console.error(
    "Expected the source schema to declare sqlite. Refusing to guess - check " +
      "prisma/schema.prisma.",
  );
  process.exit(1);
}

schema = schema.replace('provider = "sqlite"', 'provider = "postgresql"');

const banner = `// GENERATED FILE - DO NOT EDIT.
//
// Derived from prisma/schema.prisma by scripts/gen-postgres-schema.mjs.
// Edit the SQLite schema and re-run \`npm run db:gen-postgres\`.
//
// Used for production deployment only. Local development uses SQLite so the
// system runs with no external services.

`;

writeFileSync(target, banner + schema, "utf8");

const models = [...schema.matchAll(/^model\s+(\w+)/gm)].map((m) => m[1]);
console.log(
  `[gen-postgres-schema] wrote prisma/schema.postgres.prisma ` +
    `(${models.length} models: ${models.join(", ")})`,
);
