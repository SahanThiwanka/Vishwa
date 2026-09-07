import { AppraisalForm } from "@/components/AppraisalForm";

export const metadata = { title: "New appraisal" };

export default function NewAppraisalPage() {
  return (
    <div className="space-y-5">
      <div>
        <h1 className="text-xl font-semibold text-slate-900">New appraisal</h1>
        <p className="mt-0.5 text-sm text-slate-500">
          Sections follow the People&apos;s Bank appraisal form. Scores update as
          you fill the file; leave a criterion blank if it has not been assessed
          and its weight is redistributed rather than counted as zero.
        </p>
      </div>
      <AppraisalForm />
    </div>
  );
}
