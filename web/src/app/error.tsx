"use client";

/**
 * Application-level error boundary.
 *
 * Without this, an unhandled error shows the framework's default error screen.
 * That matters most on the elicitation instrument: a practitioner fifteen
 * minutes into the study who hits a raw stack trace abandons it, and the
 * response is lost. This gives them a way back instead.
 */

import Link from "next/link";
import { useEffect } from "react";

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error("Unhandled application error:", error);
  }, [error]);

  return (
    <div className="mx-auto max-w-lg py-16 text-center">
      <h1 className="text-lg font-semibold text-slate-900">Something went wrong</h1>
      <p className="mt-2 text-sm text-slate-600">
        The action could not be completed. Nothing was saved, so you can safely
        try again.
      </p>
      {error.digest && (
        <p className="mt-2 font-mono text-xs text-slate-400">
          reference: {error.digest}
        </p>
      )}
      <div className="mt-6 flex justify-center gap-2">
        <button
          type="button"
          onClick={reset}
          className="rounded-md bg-slate-900 px-4 py-2 text-sm text-white hover:bg-slate-800"
        >
          Try again
        </button>
        <Link
          href="/"
          className="rounded-md border border-slate-300 bg-white px-4 py-2 text-sm text-slate-700 hover:bg-slate-50"
        >
          Back to appraisals
        </Link>
      </div>
    </div>
  );
}
