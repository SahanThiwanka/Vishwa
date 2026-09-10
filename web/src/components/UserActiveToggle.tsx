"use client";

import { useActionState } from "react";

import { setUserActive, type AccountResult } from "@/lib/user-actions";

/**
 * Deactivate or reactivate one account.
 *
 * A client component rather than a bare `<form action={...}>` because the
 * action refuses some requests - deactivating the last active administrator,
 * for one - and those refusals have to reach the person who tried. A plain form
 * action must return void, so the message would be discarded and the button
 * would appear to do nothing.
 */
export function UserActiveToggle({
  username,
  active,
}: {
  username: string;
  active: boolean;
}) {
  const [state, action, pending] = useActionState(
    async (_prev: AccountResult | null, formData: FormData) =>
      setUserActive(formData),
    null,
  );

  return (
    <form action={action} className="flex flex-col items-end gap-1">
      <input type="hidden" name="username" value={username} />
      <input type="hidden" name="active" value={active ? "false" : "true"} />
      <button
        type="submit"
        disabled={pending}
        className="rounded-md border border-slate-300 px-2.5 py-1 text-xs text-slate-700 hover:bg-slate-50 disabled:opacity-50"
      >
        {pending ? "…" : active ? "Deactivate" : "Reactivate"}
      </button>
      {state?.error && (
        <span role="alert" className="max-w-xs text-right text-xs text-red-700">
          {state.error}
        </span>
      )}
    </form>
  );
}
