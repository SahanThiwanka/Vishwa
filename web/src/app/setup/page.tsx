import Link from "next/link";

import { AccountForm } from "@/components/AccountForm";
import { createFirstAdmin, userCount } from "@/lib/user-actions";

// Must reflect the database on every request: the whole point is that this page
// stops working the moment an account exists.
export const dynamic = "force-dynamic";

export default async function SetupPage() {
  const count = await userCount();

  if (count > 0) {
    return (
      <div className="mx-auto max-w-lg">
        <h1 className="text-xl font-semibold text-slate-900">Setup is closed</h1>
        <p className="mt-2 text-sm text-slate-600">
          This deployment already has {count} account{count === 1 ? "" : "s"}.
          First-run setup is available only while there are none, so that it
          cannot be used to take over a running system.
        </p>
        <p className="mt-4 text-sm text-slate-600">
          To add further accounts, sign in as an administrator and use{" "}
          <Link href="/admin/users" className="underline">
            account management
          </Link>
          .
        </p>
        <Link
          href="/login"
          className="mt-6 inline-block rounded-md bg-slate-900 px-4 py-2 text-sm text-white hover:bg-slate-800"
        >
          Sign in
        </Link>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-3xl">
      <h1 className="text-xl font-semibold text-slate-900">
        Create the first administrator
      </h1>
      <p className="mt-1 text-sm text-slate-600">
        This deployment has no accounts yet. Create one now.
      </p>

      <div className="mt-4 rounded-md border border-amber-300 bg-amber-50 px-4 py-3 text-sm text-amber-900">
        <p className="font-medium">Do this immediately, and only once.</p>
        <p className="mt-1">
          While no accounts exist, anyone who reaches this page can create the
          first administrator. It closes permanently as soon as you submit this
          form, so the exposure is the gap between deploying and finishing
          setup. Do not leave a deployment sitting at this screen.
        </p>
      </div>

      <div className="mt-6 rounded-lg border border-slate-200 bg-white p-6">
        <AccountForm
          action={createFirstAdmin}
          fixedRole="ADMIN"
          submitLabel="Create administrator"
        />
      </div>

      <p className="mt-4 text-xs text-slate-500">
        The criterion weighting study at <code>/elicitation</code> is public and
        needs no account. If this deployment exists only to collect weights, you
        do not need to create one at all.
      </p>
    </div>
  );
}
