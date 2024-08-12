import React, { useEffect, useState } from "react";
import { getAllUsers, deleteUser } from "../api/userAPI";
import { UserResponse } from "../api/interfaces";

const AdminPage: React.FC = () => {
  const [users, setUsers] = useState<UserResponse[]>([]);
  const [error, setError] = useState<string | null>(null);

  const fetchUsers = async () => {
    try {
      const data = await getAllUsers();
      if (Array.isArray(data)) {
        setUsers(data);
      } else {
        setError("Unexpected data format");
        setUsers([]); // Ensure users is an empty array to avoid map error
      }
    } catch (error) {
      setError("Failed to fetch users");
    }
  };

  const handleDelete = async (userEmail: string) => {
    try {
      await deleteUser(userEmail);
      setUsers(users.filter((user) => user.email !== userEmail));
    } catch (error) {
      setError("Failed to delete user");
      console.error("Error deleting user:", error);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, []);

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-4">Admin Page</h1>
      {error && <div className="text-red-500 mb-4">{error}</div>}
      <table className="min-w-full bg-white">
        <thead>
          <tr>
            <th className="px-4 py-2">Email</th>
            <th className="px-4 py-2">First Name</th>
            <th className="px-4 py-2">Last Name</th>
            <th className="px-4 py-2">Role</th>
            <th className="px-4 py-2">Actions</th>
          </tr>
        </thead>
        <tbody>
          {users.length > 0 ? (
            users.map((user) => (
              <tr key={user.email} className="border-t">
                <td className="px-4 py-2">{user.email}</td>
                <td className="px-4 py-2">{user.fname}</td>
                <td className="px-4 py-2">{user.lname}</td>
                <td className="px-4 py-2">{user.role === 1 ? "Admin" : "User"}</td>
                <td className="px-4 py-2">
                  <button
                    onClick={() => handleDelete(user.email)}
                    className="bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-4 rounded"
                  >
                    Delete
                  </button>
                </td>
              </tr>
            ))
          ) : (
            <tr>
              <td colSpan={5} className="text-center py-4">No users available.</td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
};

export default AdminPage;
