import { AccountForm } from "@/components/AccountForm";
import { UserActiveToggle } from "@/components/UserActiveToggle";
import { requireRole } from "@/lib/dal";
import { prisma } from "@/lib/db";
import { createUser } from "@/lib/user-actions";

export const dynamic = "force-dynamic";

const ROLE_LABEL: Record<string, string> = {
  OFFICER: "Officer",
  RECOMMENDER: "Recommender",
  HEAD_OFFICE: "Head Office",
  ADMIN: "Administrator",
};

export default async function UsersPage() {
  const session = await requireRole(["ADMIN"]);

  const users = await prisma.user.findMany({
    orderBy: [{ active: "desc" }, { username: "asc" }],
  });

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-xl font-semibold text-slate-900">Accounts</h1>
        <p className="mt-0.5 text-sm text-slate-500">
          Roles map to the sign-off chain in clause 7 of the appraisal form. An
          officer prepares, a recommender endorses, Head Office approves.
        </p>
      </div>

      <section>
        <h2 className="text-sm font-semibold text-slate-900">Existing accounts</h2>
        <div className="mt-2 overflow-x-auto rounded-lg border border-slate-200 bg-white">
          <table className="w-full text-sm">
            <caption className="sr-only">
              All accounts, active ones first.
            </caption>
            <thead className="border-b border-slate-200 bg-slate-50 text-left">
              <tr className="text-xs uppercase tracking-wide text-slate-500">
                <th scope="col" className="px-4 py-2.5 font-medium">Username</th>
                <th scope="col" className="px-4 py-2.5 font-medium">Name</th>
                <th scope="col" className="px-4 py-2.5 font-medium">Role</th>
                <th scope="col" className="px-4 py-2.5 font-medium">Status</th>
                <th scope="col" className="px-4 py-2.5 font-medium">
                  <span className="sr-only">Action</span>
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {users.map((u) => (
                <tr key={u.id} className={u.active ? "" : "bg-slate-50"}>
                  <td className="px-4 py-2.5 font-mono text-xs text-slate-900">
                    {u.username}
                    {u.username === session.username && (
                      <span className="ml-2 text-slate-400">(you)</span>
                    )}
                  </td>
                  <td className="px-4 py-2.5 text-slate-800">
                    {u.displayName}
                    {u.designation && (
                      <span className="block text-xs text-slate-500">
                        {u.designation}
                      </span>
                    )}
                  </td>
                  <td className="px-4 py-2.5 text-slate-700">
                    {ROLE_LABEL[u.role] ?? u.role}
                  </td>
                  <td className="px-4 py-2.5">
                    <span
                      className={
                        u.active
                          ? "text-emerald-700"
                          : "text-slate-500"
                      }
                    >
                      {u.active ? "Active" : "Deactivated"}
                    </span>
                  </td>
                  <td className="px-4 py-2.5 text-right">
                    {u.username !== session.username && (
                      <UserActiveToggle
                        username={u.username}
                        active={u.active}
                      />
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="mt-2 text-xs text-slate-500">
          Accounts are deactivated, never deleted. A sign-off whose signatory had
          been removed would leave an audit trail naming someone the system can
          no longer describe.
        </p>
      </section>

      <section>
        <h2 className="text-sm font-semibold text-slate-900">Add an account</h2>
        <div className="mt-2 rounded-lg border border-slate-200 bg-white p-6">
          <AccountForm action={createUser} />
        </div>
      </section>
    </div>
  );
}
