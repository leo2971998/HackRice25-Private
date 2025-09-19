import { useEffect, useMemo, useState } from "react";
import { listUsers, updateUserRole, deleteUser } from "@/api/auth";
import { useAuth } from "@/context/Auth";
import toast from "react-hot-toast";

interface ManagedUser {
  id: number;
  email: string;
  first_name?: string;
  last_name?: string;
  role?: "user" | "admin";
  created_at?: number;
}

export default function AdminPortalPage() {
  const [users, setUsers] = useState<ManagedUser[]>([]);
  const [loading, setLoading] = useState(true);
  const [savingId, setSavingId] = useState<number | null>(null);
  const [removingId, setRemovingId] = useState<number | null>(null);
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

  const handleRoleChange = async (userId: number, role: "user" | "admin") => {
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

  const handleDelete = async (userId: number) => {
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
    <div className="min-h-screen bg-white text-black">
      <div className="max-w-5xl mx-auto px-4 py-12">
        <div className="mb-10">
          <h1 className="text-3xl font-bold text-black">Admin Portal</h1>
          <p className="text-black mt-2">
            Manage user accounts, promote trusted members, and keep your admin roster healthy.
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-6 mb-10">
          <div className="border border-gray-200 rounded-xl p-6 bg-white shadow-sm">
            <p className="text-sm uppercase tracking-wide text-black">Total Users</p>
            <p className="text-3xl font-semibold text-black mt-2">{users.length}</p>
          </div>
          <div className="border border-gray-200 rounded-xl p-6 bg-white shadow-sm">
            <p className="text-sm uppercase tracking-wide text-black">Administrators</p>
            <p className="text-3xl font-semibold text-black mt-2">{totalAdmins}</p>
          </div>
          <div className="border border-gray-200 rounded-xl p-6 bg-white shadow-sm">
            <p className="text-sm uppercase tracking-wide text-black">Active Session</p>
            <p className="text-3xl font-semibold text-black mt-2">{user?.email}</p>
          </div>
        </div>

        <div className="border border-gray-200 rounded-2xl bg-white shadow-sm overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-200 bg-gray-50 text-black">
            <h2 className="text-xl font-semibold">User Directory</h2>
          </div>

          {loading ? (
            <div className="p-6 text-center text-black">Loading users...</div>
          ) : users.length === 0 ? (
            <div className="p-6 text-center text-black">No users found.</div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200 text-left text-black">
                <thead className="bg-white">
                  <tr>
                    <th className="px-6 py-3 text-xs font-semibold uppercase tracking-wide">Name</th>
                    <th className="px-6 py-3 text-xs font-semibold uppercase tracking-wide">Email</th>
                    <th className="px-6 py-3 text-xs font-semibold uppercase tracking-wide">Role</th>
                    <th className="px-6 py-3 text-xs font-semibold uppercase tracking-wide">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {users.map(u => {
                    const fullName = [u.first_name, u.last_name].filter(Boolean).join(" ") || "—";
                    const isCurrentUser = u.id === user?.id;
                    const currentRole = (u.role || "user") as "user" | "admin";

                    return (
                      <tr key={u.id} className="bg-white">
                        <td className="px-6 py-4 text-sm font-medium text-black">{fullName}</td>
                        <td className="px-6 py-4 text-sm text-black">{u.email}</td>
                        <td className="px-6 py-4 text-sm text-black">
                          <select
                            value={currentRole}
                            onChange={event => handleRoleChange(u.id, event.target.value as "user" | "admin")}
                            disabled={savingId === u.id || (isCurrentUser && totalAdmins === 1)}
                            className="border border-gray-300 rounded-lg px-3 py-2 text-sm text-black bg-white"
                          >
                            <option value="user">User</option>
                            <option value="admin">Admin</option>
                          </select>
                        </td>
                        <td className="px-6 py-4 text-sm text-black">
                          <div className="flex items-center gap-3">
                            <button
                              type="button"
                              onClick={() => handleRoleChange(u.id, currentRole)}
                              disabled={savingId === u.id}
                              className="px-3 py-1 rounded-lg border border-gray-300 text-black hover:bg-gray-100 disabled:opacity-60"
                            >
                              {savingId === u.id ? "Saving..." : "Refresh"}
                            </button>
                            {!isCurrentUser && (
                              <button
                                type="button"
                                onClick={() => handleDelete(u.id)}
                                disabled={removingId === u.id}
                                className="px-3 py-1 rounded-lg border border-red-400 text-black hover:bg-red-50 disabled:opacity-60"
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
