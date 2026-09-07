import { criteriaTree } from "@/lib/scoring";

export const metadata = { title: "Scoring model" };

export default function ModelPage() {
  const total = criteriaTree.objectives.reduce(
    (sum, o) => sum + o.dimensions.reduce((s, d) => s + d.criteria.length, 0),
    0,
  );

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold text-slate-900">{criteriaTree.title}</h1>
        <p className="mt-1 text-sm text-slate-500">
          {total} criteria derived from the {criteriaTree.sourceInstrument.issuer}{" "}
          <em>{criteriaTree.sourceInstrument.name}</em> ({criteriaTree.sourceInstrument.annexure}).
          Model version {criteriaTree.version}.
        </p>
      </div>

      <div className="rounded-lg border border-amber-300 bg-amber-50 p-4">
        <h2 className="text-sm font-semibold text-amber-900">
          Weight status: {criteriaTree.weightStatus.state}
        </h2>
        <p className="mt-1 text-sm text-amber-800/90">{criteriaTree.weightStatus.detail}</p>
        {criteriaTree.weightStatus.plannedMethod && (
          <p className="mt-1 text-xs text-amber-800/80">
            Planned method: {criteriaTree.weightStatus.plannedMethod}
          </p>
        )}
      </div>

      {criteriaTree.objectives.map((objective) => (
        <section key={objective.id} className="space-y-3">
          <div>
            <h2 className="text-lg font-semibold text-slate-900">{objective.name}</h2>
            {objective.note && (
              <p className="mt-1 max-w-3xl text-sm text-slate-600">{objective.note}</p>
            )}
          </div>

          {objective.dimensions.map((dimension) => (
            <div key={dimension.id} className="rounded-lg border border-slate-200 bg-white p-5">
              <h3 className="text-sm font-semibold text-slate-900">
                {dimension.name}
                <span className="ml-2 text-xs font-normal text-slate-400">
                  clause {dimension.ref}
                </span>
              </h3>
              {dimension.note && (
                <p className="mt-1 text-xs text-slate-500">{dimension.note}</p>
              )}
              <table className="mt-3 w-full text-xs">
                <thead className="text-left text-slate-500">
                  <tr>
                    <th className="pb-1 font-medium">Criterion</th>
                    <th className="pb-1 font-medium">Clause</th>
                    <th className="pb-1 font-medium">Type</th>
                    <th className="pb-1 font-medium">Unit</th>
                  </tr>
                </thead>
                <tbody className="text-slate-700">
                  {dimension.criteria.map((c) => (
                    <tr key={c.id} className="border-t border-slate-100">
                      <td className="py-1 pr-2">
                        {c.name}
                        {c.critical && (
                          <span className="ml-2 rounded bg-red-50 px-1.5 py-0.5 text-[10px] text-red-700 border border-red-200">
                            critical
                          </span>
                        )}
                      </td>
                      <td className="py-1 pr-2 text-slate-400">{c.ref}</td>
                      <td className="py-1 pr-2 text-slate-500">{c.type}</td>
                      <td className="py-1 text-slate-500">{c.unit ?? "5-point scale"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ))}
        </section>
      ))}
    </div>
  );
}
