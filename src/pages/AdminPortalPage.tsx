import { useEffect, useMemo, useState } from "react";
import { listUsers, updateUserRole, deleteUser } from "@/api/auth";
import { useAuth } from "@/context/Auth";
import toast from "react-hot-toast";
import { SkeletonGroup } from "@/components/Skeleton";

interface ManagedUser {
  id: string;
  email: string;
  first_name?: string;
  last_name?: string;
  role?: "user" | "admin";
  created_at?: number;
}

export default function AdminPortalPage() {
  const [users, setUsers] = useState<ManagedUser[]>([]);
  const [loading, setLoading] = useState(true);
  const [savingId, setSavingId] = useState<string | null>(null);
  const [removingId, setRemovingId] = useState<string | null>(null);
  const { user } = useAuth();

  const loadUsers = async () => {
    try {
      setLoading(true);
      const data: ManagedUser[] = await listUsers();
      setUsers(Array.isArray(data) ? data : []);
    } catch (error: any) {
      toast.error(error?.response?.data?.error || "Failed to load users");
      setUsers([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadUsers();
  }, []);

  const handleRoleChange = async (userId: string, role: "user" | "admin") => {
    try {
      setSavingId(userId);
      await updateUserRole(userId, role);
      toast.success("User role updated");
      await loadUsers();
    } catch (error: any) {
      toast.error(error?.response?.data?.error || "Unable to update role");
    } finally {
      setSavingId(null);
    }
  };
  const handleDelete = async (userId: string) => {
    try {
      setRemovingId(userId);
      await deleteUser(userId);
      toast.success("User removed");
      await loadUsers();
    } catch (error: any) {
      toast.error(error?.response?.data?.error || "Unable to remove user");
    } finally {
      setRemovingId(null);
    }
  };

  const totalAdmins = useMemo(() => users.filter(u => (u.role || "user") === "admin").length, [users]);

  return (
    <div className="min-h-screen bg-dark-100 text-white">
      <div className="max-w-5xl mx-auto px-4 py-12 space-y-10">
        <div>
          <h1 className="text-3xl font-bold">Admin Portal</h1>
          <p className="text-white mt-2">
            Manage user accounts, promote trusted members, and keep your admin roster healthy.
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-6">
          <div className="border border-dark-400 rounded-xl p-6 bg-dark-200 shadow-lg">
            <p className="text-sm uppercase tracking-wide text-white">Total Users</p>
            <p className="text-3xl font-semibold text-white mt-2">{users.length}</p>
          </div>
          <div className="border border-dark-400 rounded-xl p-6 bg-dark-200 shadow-lg">
            <p className="text-sm uppercase tracking-wide text-white">Administrators</p>
            <p className="text-3xl font-semibold text-white mt-2">{totalAdmins}</p>
          </div>
          <div className="border border-dark-400 rounded-xl p-6 bg-dark-200 shadow-lg">
            <p className="text-sm uppercase tracking-wide text-white">Active Session</p>
            <p className="text-3xl font-semibold text-white mt-2 truncate">{user?.email}</p>
          </div>
        </div>

        <div className="border border-dark-400 rounded-2xl bg-dark-200 shadow-lg overflow-hidden">
          <div className="px-6 py-4 border-b border-dark-400 bg-dark-300 text-white">
            <h2 className="text-xl font-semibold">User Directory</h2>
          </div>

          {loading ? (
            <div className="p-6">
              <SkeletonGroup count={4} itemClassName="h-12 w-full bg-dark-300/70" />
            </div>
          ) : users.length === 0 ? (
            <div className="p-6 text-center text-white">No users found.</div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-dark-400 text-left">
                <thead className="bg-dark-300">
                  <tr>
                    <th className="px-6 py-3 text-xs font-semibold uppercase tracking-wide text-white">Name</th>
                    <th className="px-6 py-3 text-xs font-semibold uppercase tracking-wide text-white">Email</th>
                    <th className="px-6 py-3 text-xs font-semibold uppercase tracking-wide text-white">Role</th>
                    <th className="px-6 py-3 text-xs font-semibold uppercase tracking-wide text-white">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-dark-400">
                  {users.map(u => {
                    const fullName = [u.first_name, u.last_name].filter(Boolean).join(" ") || "—";
                    const isCurrentUser = u.id === user?.id;
                    const currentRole = (u.role || "user") as "user" | "admin";

                    return (
                      <tr key={u.id} className="bg-dark-200">
                        <td className="px-6 py-4 text-sm font-medium text-white">{fullName}</td>
                        <td className="px-6 py-4 text-sm text-white">{u.email}</td>
                        <td className="px-6 py-4 text-sm text-white">
                          <select
                            value={currentRole}
                            onChange={event => handleRoleChange(u.id, event.target.value as "user" | "admin")}
                            disabled={savingId === u.id || (isCurrentUser && totalAdmins === 1)}
                            className="border border-dark-500 rounded-lg px-3 py-2 text-sm bg-dark-300 text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
                          >
                            <option value="user">User</option>
                            <option value="admin">Admin</option>
                          </select>
                        </td>
                        <td className="px-6 py-4 text-sm text-white">
                          <div className="flex items-center gap-3">
                            <button
                              type="button"
                              onClick={() => handleRoleChange(u.id, currentRole)}
                              disabled={savingId === u.id}
                              className="px-3 py-1 rounded-lg border border-dark-500 text-white hover:bg-dark-300 disabled:opacity-60"
                            >
                              {savingId === u.id ? "Saving..." : "Refresh"}
                            </button>
                            {!isCurrentUser && (
                              <button
                                type="button"
                                onClick={() => handleDelete(u.id)}
                                disabled={removingId === u.id}
                                className="px-3 py-1 rounded-lg border border-red-400 text-red-300 hover:bg-red-500/10 disabled:opacity-60"
                              >
                                {removingId === u.id ? "Removing..." : "Remove"}
                              </button>
                            )}
                          </div>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
