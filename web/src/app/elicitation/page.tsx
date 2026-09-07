import { ElicitationWizard } from "@/components/ElicitationWizard";

export const metadata = { title: "Criterion weighting study" };

export default function ElicitationPage() {
  return (
    <div className="space-y-6">
      <div className="mx-auto max-w-3xl">
        <h1 className="text-xl font-semibold text-slate-900">
          Criterion weighting study
        </h1>
        <p className="mt-0.5 text-sm text-slate-500">
          Best-Worst Method elicitation. Your judgements determine how the scoring
          model weights each part of an SME credit appraisal.
        </p>
      </div>
      <ElicitationWizard />
    </div>
  );
}
