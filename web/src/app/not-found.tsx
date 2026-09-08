import Link from "next/link";

export default function NotFound() {
  return (
    <div className="mx-auto max-w-lg py-16 text-center">
      <h1 className="text-lg font-semibold text-slate-900">Not found</h1>
      <p className="mt-2 text-sm text-slate-600">
        That appraisal does not exist, or its reference has changed.
      </p>
      <Link
        href="/"
        className="mt-6 inline-block rounded-md bg-slate-900 px-4 py-2 text-sm text-white hover:bg-slate-800"
      >
        Back to appraisals
      </Link>
    </div>
  );
}
