import { LoginForm } from "@/components/LoginForm";

export const metadata = { title: "Sign in" };
export const dynamic = "force-dynamic";

export default async function LoginPage({
  searchParams,
}: {
  searchParams: Promise<{ from?: string }>;
}) {
  const { from } = await searchParams;

  return (
    <div className="mx-auto max-w-sm py-12">
      <h1 className="text-xl font-semibold text-slate-900">Sign in</h1>
      <p className="mt-1 text-sm text-slate-500">
        Appraisal records are restricted. The criterion weighting study does not
        require an account.
      </p>
      <LoginForm from={from} />
    </div>
  );
}
