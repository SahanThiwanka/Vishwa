# Deploying the elicitation instrument

The point of deploying is one thing: **let practitioners complete the criterion
weighting study from wherever they are.** Until responses exist, RQ2 is
unanswered and the criteria model stays on placeholder weights.

Budget about 20 minutes.

---

## Why the database changes for deployment

Locally the system uses SQLite — a single file, no services, works offline. That
is deliberate: **the viva demonstration must not depend on an internet connection
or a cloud provider staying up.**

Vercel cannot use SQLite. Its filesystem is ephemeral, so a database file written
there is lost on the next deployment and is not shared between serverless
invocations. Responses would silently vanish.

So production uses PostgreSQL. The schema is identical; only the datasource
provider differs, and the PostgreSQL variant is generated mechanically from the
SQLite one so the two cannot drift:

```bash
cd web && npm run db:gen-postgres
```

`src/lib/db.ts` picks the adapter from the shape of `DATABASE_URL` — no code
change is needed to switch.

---

## Step 1 — Create a PostgreSQL database

Any hosted Postgres works. **Neon** has a free tier and integrates with Vercel:

1. Sign up at `neon.tech` (or use Vercel's Storage tab → Postgres)
2. Create a project
3. Copy the connection string — it looks like
   `postgresql://user:password@host.neon.tech/dbname?sslmode=require`

Keep it. It is a credential: do not commit it, and do not paste it into the
thesis or any shared document.

---

## Step 2 — Create the tables

From the `web/` directory, with the connection string in your environment:

```bash
cd web
npm run db:gen-postgres
```

```bash
DATABASE_URL="postgresql://..." npm run db:migrate:postgres
```

On Windows PowerShell, set it first:

```bash
$env:DATABASE_URL="postgresql://..."; npm run db:migrate:postgres
```

This applies the existing migrations to the new database. It does **not** copy
your local SQLite data, which is what you want — the local database contains test
appraisals, not research data.

---

## Step 3 — Push to GitHub

Vercel deploys from a repository.

```bash
git remote add origin https://github.com/<you>/<repo>.git
git push -u origin master
```

`.gitignore` already excludes `dev.db`, `.env`, `node_modules/` and the raw
dataset. **Check `git status` before pushing** and confirm no connection string
or database file is staged.

---

## Step 4 — Deploy on Vercel

1. `vercel.com` → **Add New → Project** → import the repository
2. Set **Root Directory** to `web` — this matters, the repo root is not the app
3. Add an environment variable:

   | Name | Value |
   |---|---|
   | `DATABASE_URL` | your PostgreSQL connection string |
   | `SESSION_SECRET` | a random string, 32+ characters |

   Generate the secret with:

   ```bash
   node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"
   ```

   The application **refuses to start in production without it** — sessions
   signed with a guessable key can be forged, and a forged session is a
   Head Office sign-off.

4. Deploy

The build runs `prisma generate` and the model sync automatically
(`prebuild`).

---

## Step 5 — Verify before sending the link to anyone

Open `https://<your-app>.vercel.app/api/health`. Expect:

```json
{
  "status": "ok",
  "database": "postgresql",
  "modelVersion": "0.1.0-draft",
  "weights": "PLACEHOLDER",
  "criteria": 49,
  "elicitationResponses": 0,
  "appraisals": 0
}
```

Check all four:

- `"database": "postgresql"` — if it says `sqlite`, `DATABASE_URL` is not set and
  **responses will be lost**
- `"criteria": 49` — the model synced
- `"weights": "PLACEHOLDER"` — correct until elicitation completes
- `"elicitationResponses": 0` — the table exists and is queryable

### Create user accounts

Appraisal records require an account; the elicitation instrument does not.
`npm run db:seed-users` creates three **demonstration** accounts with published
passwords — these are for the viva only and **must not exist on a public
deployment**. Either change their passwords immediately or create real accounts
and delete the demo ones.

Then complete one full run of `/elicitation` yourself under a code like
`TEST-DELETE`, confirm the count increments, and **delete that row before
analysis** — `derive_weights.py` excludes codes listed in `EXCLUDED_CODES`, so
add it there if you keep it.

---

## Step 6 — Send it out

Send practitioners: `https://<your-app>.vercel.app/elicitation`

What to say, roughly:

> I'm doing an MSc research study on how SME credit appraisals are weighted.
> It takes about 15 minutes and asks you to compare parts of the appraisal
> against each other. No names, no customer information — just your professional
> judgement. Responses are anonymous and reported only in aggregate.

Ask them to use a code you can track (R01, R02, …) so you can chase incomplete
responses without needing their names.

---

## Step 7 — Retrieve the responses

`derive_weights.py` reads the local SQLite file by default. To analyse
production responses, point it at PostgreSQL — either export the table to the
local database, or adjust `load_responses()` to read from `DATABASE_URL`.

```bash
python research/src/derive_weights.py            # dry run: consistency + weights
python research/src/derive_weights.py --apply    # write into the criteria tree
cd web && npm run sync-model
```

`--apply` flips `weightStatus` to `ELICITED` and records the respondent count,
how many responses were dropped for inconsistency, and the date. **It refuses to
run without usable responses**, which is intentional — do not work around it.

After applying, re-run the analyses that depend on weights, and update
Chapter 6.

---

## Things that will go wrong

**Health check says `"database": "sqlite"`** — `DATABASE_URL` is missing in
Vercel's environment settings. Responses are going nowhere. Fix before sending
the link.

**Build fails on `@prisma/client` not found** — the `prebuild` script runs
`prisma generate`; confirm Root Directory is `web`.

**Table does not exist** — Step 2 was skipped or ran against a different
database.

**Responses submit but the count stays at zero** — you are looking at a different
deployment than the one people used, or at a preview rather than production URL.

---

## A caution

Once this is public, anyone with the link can submit. For a small study that is
acceptable, but it means:

- **Check the respondent codes** in the data before analysis; discard anything you
  cannot attribute to someone you actually invited.
- Do not treat the response count as a sample size without checking who they are.
- If you need stronger control, gate the page behind a shared passphrase before
  circulating the link widely.

The instrument collects no names, so an unattributable response cannot be traced
after the fact. Track who you invited separately, offline.
