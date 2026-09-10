"use client";

import { useActionState } from "react";

import type { AccountResult } from "@/lib/user-actions";

type Action = (
  prev: AccountResult | null,
  formData: FormData,
) => Promise<AccountResult>;

const ROLES: { value: string; label: string; note: string }[] = [
  { value: "OFFICER", label: "Officer", note: "Prepares appraisals" },
  { value: "RECOMMENDER", label: "Recommender", note: "Endorses them (clause 7)" },
  { value: "HEAD_OFFICE", label: "Head Office", note: "Approves or declines" },
  { value: "ADMIN", label: "Administrator", note: "Manages accounts and the model" },
];

/**
 * Create an account.
 *
 * `fixedRole` is used by the first-run setup page, where the role is not a
 * choice: the first account has to be an administrator or nobody can create
 * the second.
 */
export function AccountForm({
  action,
  fixedRole,
  submitLabel = "Create account",
}: {
  action: Action;
  fixedRole?: string;
  submitLabel?: string;
}) {
  const [state, formAction, pending] = useActionState(action, null);

  return (
    <form action={formAction} className="space-y-4">
      <div className="grid gap-4 sm:grid-cols-2">
        <div>
          <label htmlFor="username" className="block text-xs font-medium text-slate-600">
            Username <span className="text-red-600">*</span>
          </label>
          <input
            id="username"
            name="username"
            required
            autoComplete="off"
            placeholder="a.athukorala"
            className="input mt-1"
          />
          <p className="mt-1 text-xs text-slate-500">
            Letters, numbers, dot, dash, underscore. Used to sign in.
          </p>
        </div>

        <div>
          <label htmlFor="displayName" className="block text-xs font-medium text-slate-600">
            Display name <span className="text-red-600">*</span>
          </label>
          <input
            id="displayName"
            name="displayName"
            required
            autoComplete="off"
            placeholder="A. Athukorala"
            className="input mt-1"
          />
          <p className="mt-1 text-xs text-slate-500">
            Appears on sign-offs and in the audit trail.
          </p>
        </div>

        <div>
          <label htmlFor="designation" className="block text-xs font-medium text-slate-600">
            Designation
          </label>
          <input
            id="designation"
            name="designation"
            autoComplete="off"
            placeholder="Appraisal Officer"
            className="input mt-1"
          />
        </div>

        {fixedRole ? (
          <div>
            <span className="block text-xs font-medium text-slate-600">Role</span>
            <p className="input mt-1 bg-slate-50 text-slate-700">
              Administrator
            </p>
            <p className="mt-1 text-xs text-slate-500">
              The first account must be an administrator.
            </p>
          </div>
        ) : (
          <div>
            <label htmlFor="role" className="block text-xs font-medium text-slate-600">
              Role <span className="text-red-600">*</span>
            </label>
            <select id="role" name="role" required defaultValue="OFFICER" className="input mt-1">
              {ROLES.map((r) => (
                <option key={r.value} value={r.value}>
                  {r.label} — {r.note}
                </option>
              ))}
            </select>
          </div>
        )}
      </div>

      <div className="grid gap-4 sm:grid-cols-2">
        <div>
          <label htmlFor="password" className="block text-xs font-medium text-slate-600">
            Password <span className="text-red-600">*</span>
          </label>
          <input
            id="password"
            name="password"
            type="password"
            required
            minLength={12}
            autoComplete="new-password"
            className="input mt-1"
          />
          <p className="mt-1 text-xs text-slate-500">At least 12 characters.</p>
        </div>

        <div>
          <label htmlFor="confirm" className="block text-xs font-medium text-slate-600">
            Confirm password <span className="text-red-600">*</span>
          </label>
          <input
            id="confirm"
            name="confirm"
            type="password"
            required
            minLength={12}
            autoComplete="new-password"
            className="input mt-1"
          />
        </div>
      </div>

      {state?.error && (
        <p role="alert" className="rounded-md border border-red-300 bg-red-50 px-3 py-2 text-sm text-red-800">
          {state.error}
        </p>
      )}
      {state?.ok && (
        <p role="status" className="rounded-md border border-emerald-300 bg-emerald-50 px-3 py-2 text-sm text-emerald-800">
          {state.ok}
        </p>
      )}

      <button
        type="submit"
        disabled={pending}
        className="rounded-md bg-slate-900 px-4 py-2 text-sm text-white hover:bg-slate-800 disabled:opacity-50"
      >
        {pending ? "Creating…" : submitLabel}
      </button>
    </form>
  );
}
