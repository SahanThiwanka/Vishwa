"use client";

import { useActionState } from "react";

import { signIn } from "@/lib/auth-actions";

export function LoginForm({ from }: { from?: string }) {
  const [state, action, pending] = useActionState(signIn, null);

  return (
    <form action={action} className="mt-6 space-y-4">
      {from && <input type="hidden" name="from" value={from} />}

      <div>
        <label htmlFor="username" className="block text-xs font-medium text-slate-600">
          Username
        </label>
        <input
          id="username"
          name="username"
          autoComplete="username"
          required
          className="input mt-1"
        />
      </div>

      <div>
        <label htmlFor="password" className="block text-xs font-medium text-slate-600">
          Password
        </label>
        <input
          id="password"
          name="password"
          type="password"
          autoComplete="current-password"
          required
          className="input mt-1"
        />
      </div>

      {state?.error && (
        <p
          role="alert"
          className="rounded border border-red-300 bg-red-50 px-3 py-2 text-xs text-red-800"
        >
          {state.error}
        </p>
      )}

      <button
        type="submit"
        disabled={pending}
        className="w-full rounded-md bg-slate-900 px-4 py-2.5 text-sm font-medium text-white hover:bg-slate-800 disabled:bg-slate-300"
      >
        {pending ? "Signing in…" : "Sign in"}
      </button>

      <p className="text-center text-xs text-slate-400">
        Research prototype. Accounts are created by the administrator.
      </p>
    </form>
  );
}
