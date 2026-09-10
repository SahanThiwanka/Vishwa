/**
 * Tests for account creation, and above all for the first-run setup guard.
 *
 * `/setup` is necessarily public: a fresh deployment has no accounts, so
 * requiring a session would deadlock. The only thing standing between that page
 * and an anonymous stranger taking the first ADMIN account on a live system is
 * the user-count check, and a Server Action is reachable by direct POST whatever
 * the page decides to render. So the check has to live in the action, and it has
 * to stay there.
 */

import { beforeEach, describe, expect, it, vi } from "vitest";

const count = vi.fn();
const findUnique = vi.fn();
const create = vi.fn();
const update = vi.fn();
const requireRole = vi.fn();

vi.mock("@/lib/db", () => ({
  prisma: {
    user: {
      count: (...a: unknown[]) => count(...a),
      findUnique: (...a: unknown[]) => findUnique(...a),
      create: (...a: unknown[]) => create(...a),
      update: (...a: unknown[]) => update(...a),
    },
  },
}));

vi.mock("@/lib/dal", () => ({
  requireRole: (...a: unknown[]) => requireRole(...a),
}));

vi.mock("next/cache", () => ({ revalidatePath: vi.fn() }));

const { createFirstAdmin, createUser, setUserActive } = await import(
  "./user-actions"
);

function form(fields: Record<string, string>): FormData {
  const fd = new FormData();
  for (const [k, v] of Object.entries(fields)) fd.set(k, v);
  return fd;
}

const GOOD = {
  username: "a.athukorala",
  displayName: "A. Athukorala",
  designation: "Appraisal Officer",
  password: "correct-horse-battery",
  confirm: "correct-horse-battery",
};

beforeEach(() => {
  count.mockReset();
  findUnique.mockReset().mockResolvedValue(null);
  create.mockReset().mockResolvedValue({});
  update.mockReset().mockResolvedValue({});
  requireRole.mockReset().mockResolvedValue({
    username: "admin",
    role: "ADMIN",
  });
});

describe("first-run setup", () => {
  it("creates the first account as ADMIN when the database is empty", async () => {
    count.mockResolvedValue(0);
    const result = await createFirstAdmin(null, form(GOOD));
    expect(result.ok).toContain("ADMIN");
    expect(create).toHaveBeenCalledOnce();
    expect(create.mock.calls[0][0].data.role).toBe("ADMIN");
  });

  it("REFUSES once any account exists", async () => {
    count.mockResolvedValue(1);
    const result = await createFirstAdmin(null, form(GOOD));
    expect(result.error).toMatch(/closed/i);
    expect(create).not.toHaveBeenCalled();
  });

  it("ignores a role submitted in the form and forces ADMIN", async () => {
    // Direct POST could set anything; the first account must be an admin or the
    // deployment is unmanageable.
    count.mockResolvedValue(0);
    await createFirstAdmin(null, form({ ...GOOD, role: "OFFICER" }));
    expect(create.mock.calls[0][0].data.role).toBe("ADMIN");
  });

  it("rejects a password under 12 characters", async () => {
    count.mockResolvedValue(0);
    const result = await createFirstAdmin(
      null,
      form({ ...GOOD, password: "short", confirm: "short" }),
    );
    expect(result.error).toMatch(/12 characters/);
    expect(create).not.toHaveBeenCalled();
  });

  it("rejects mismatched confirmation", async () => {
    count.mockResolvedValue(0);
    const result = await createFirstAdmin(
      null,
      form({ ...GOOD, confirm: "something-else-entirely" }),
    );
    expect(result.error).toMatch(/do not match/i);
    expect(create).not.toHaveBeenCalled();
  });

  it("never stores the password itself", async () => {
    count.mockResolvedValue(0);
    await createFirstAdmin(null, form(GOOD));
    const written = JSON.stringify(create.mock.calls[0][0].data);
    expect(written).not.toContain(GOOD.password);
    expect(create.mock.calls[0][0].data.passwordHash).toMatch(/^[0-9a-f]+:[0-9a-f]+$/);
  });
});

describe("creating further accounts", () => {
  it("requires an administrator", async () => {
    requireRole.mockRejectedValue(new Error("This action requires the role ADMIN."));
    const result = await createUser(null, form({ ...GOOD, role: "OFFICER" }));
    expect(result.error).toMatch(/requires the role ADMIN/);
    expect(create).not.toHaveBeenCalled();
  });

  it("rejects a duplicate username", async () => {
    findUnique.mockResolvedValue({ username: "a.athukorala" });
    const result = await createUser(null, form({ ...GOOD, role: "OFFICER" }));
    expect(result.error).toMatch(/already exists/);
    expect(create).not.toHaveBeenCalled();
  });

  it("rejects a role outside the sign-off chain", async () => {
    const result = await createUser(null, form({ ...GOOD, role: "SUPERUSER" }));
    expect(result.error).toBeTruthy();
    expect(create).not.toHaveBeenCalled();
  });

  it.each([["Bad Name"], ["has spaces"], ["sym$bol"], ["ab"]])(
    "rejects the username %p",
    async (username) => {
      const result = await createUser(
        null,
        form({ ...GOOD, username, role: "OFFICER" }),
      );
      expect(result.error).toBeTruthy();
      expect(create).not.toHaveBeenCalled();
    },
  );
});

describe("deactivation", () => {
  it("refuses to deactivate the last active administrator", async () => {
    count.mockResolvedValue(1);
    findUnique.mockResolvedValue({ username: "other", role: "ADMIN" });
    const result = await setUserActive(
      form({ username: "other", active: "false" }),
    );
    expect(result.error).toMatch(/only active administrator/i);
    expect(update).not.toHaveBeenCalled();
  });

  it("refuses to deactivate yourself", async () => {
    const result = await setUserActive(
      form({ username: "admin", active: "false" }),
    );
    expect(result.error).toMatch(/signed in as/i);
    expect(update).not.toHaveBeenCalled();
  });

  it("allows deactivation when another administrator remains", async () => {
    count.mockResolvedValue(2);
    findUnique.mockResolvedValue({ username: "other", role: "ADMIN" });
    const result = await setUserActive(
      form({ username: "other", active: "false" }),
    );
    expect(result.ok).toMatch(/Deactivated/);
    expect(update).toHaveBeenCalledOnce();
  });
});
