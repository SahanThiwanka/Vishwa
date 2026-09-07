import path from "node:path";
import { defineConfig } from "prisma/config";

// Prisma 7 no longer accepts `url` inside the schema's datasource block.
// Migration and introspection commands read the connection string from here;
// the runtime client gets a driver adapter instead (see src/lib/db.ts).
//
// This file is NOT loaded through Next.js, so .env is not read automatically.
// process.env is used directly, with the local SQLite file as the default so a
// fresh clone can migrate and run without any environment setup.
export default defineConfig({
  schema: path.join("prisma", "schema.prisma"),
  migrations: {
    path: path.join("prisma", "migrations"),
  },
  datasource: {
    url: process.env.DATABASE_URL ?? "file:./dev.db",
  },
});
