import React, { useEffect, useState } from "react";
import { getAllUsers, deleteUser, adminDeleteBook } from "../api/userAPI";
import { getAllBooks } from "../api/bookAPI";
import { UserResponse, Book } from "../api/interfaces";

const AdminPage: React.FC = () => {
  const [users, setUsers] = useState<UserResponse[]>([]);
  const [books, setBooks] = useState<Book[]>([]);
  const [error, setError] = useState<string | null>(null);

  // Fetch Users
  const fetchUsers = async () => {
    try {
      const data = await getAllUsers();
      setUsers(data);
    } catch (error) {
      setError("Failed to fetch users");
    }
  };

  // Fetch Books
  const fetchBooks = async () => {
    try {
      const data = await getAllBooks();
      setBooks(data.books);
    } catch (error) {
      setError("Failed to fetch books");
    }
  };

  const handleDeleteUser = async (userEmail: string) => {
    try {
      await deleteUser(userEmail);
      setUsers(users.filter((user) => user.email !== userEmail));
    } catch (error) {
      setError("Failed to delete user");
    }
  };

  const handleDeleteBook = async (bookId: number) => {
    try {
      await adminDeleteBook(bookId);
      setBooks(books.filter((book) => book.id !== bookId));
    } catch (error) {
      setError("Failed to delete book");
    }
  };

  useEffect(() => {
    fetchUsers();
    fetchBooks();
  }, []);

  return (
    <div className="p-6 bg-gray-100 min-h-screen">
      <h1 className="text-3xl font-bold mb-6 text-blue-900">Admin Dashboard</h1>
      {error && <div className="text-red-600 mb-6">{error}</div>}

      {/* Users Table */}
      <div className="mb-10">
        <h2 className="text-2xl font-semibold mb-4 text-blue-800">Users</h2>
        <div className="overflow-x-auto">
          <table className="min-w-full bg-white shadow-md rounded-lg">
            <thead className="bg-blue-800 text-white">
              <tr>
                <th className="px-6 py-3 text-left">Email</th>
                <th className="px-6 py-3 text-left">First Name</th>
                <th className="px-6 py-3 text-left">Last Name</th>
                <th className="px-6 py-3 text-left">Role</th>
                <th className="px-6 py-3 text-left">Actions</th>
              </tr>
            </thead>
            <tbody>
              {users.length > 0 ? (
                users.map((user) => (
                  <tr key={user.email} className="border-t">
                    <td className="px-6 py-4 text-left text-gray-700">{user.email}</td>
                    <td className="px-6 py-4 text-left text-gray-700">{user.fname}</td>
                    <td className="px-6 py-4 text-left text-gray-700">{user.lname}</td>
                    <td className="px-6 py-4 text-left text-gray-700">{user.role === 1 ? "Admin" : "User"}</td>
                    <td className="px-6 py-4 text-left">
                      <button
                        onClick={() => handleDeleteUser(user.email)}
                        className="bg-red-500 hover:bg-red-600 text-white font-semibold py-2 px-4 rounded"
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={5} className="px-6 py-4 text-center text-gray-600">No users found</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Books Table */}
      <div>
        <h2 className="text-2xl font-semibold mb-4 text-blue-800">Books</h2>
        <div className="overflow-x-auto">
          <table className="min-w-full bg-white shadow-md rounded-lg">
            <thead className="bg-blue-800 text-white">
              <tr>
                <th className="px-6 py-3 text-left">Title</th>
                <th className="px-6 py-3 text-left">Authors</th>
                <th className="px-6 py-3 text-left">Published Year</th>
                <th className="px-6 py-3 text-left">Genre</th>
                <th className="px-6 py-3 text-left">Actions</th>
              </tr>
            </thead>
            <tbody>
              {books.length > 0 ? (
                books.map((book) => (
                  <tr key={book.id} className="border-t">
                    <td className="px-6 py-4 text-left text-gray-700">{book.title}</td>
                    <td className="px-6 py-4 text-left text-gray-700">
                      {Array.isArray(book.authors) ? book.authors.join(", ") : "Unknown"}
                    </td>
                    <td className="px-6 py-4 text-left text-gray-700">{book.published_year}</td>
                    <td className="px-6 py-4 text-left text-gray-700">{book.genre}</td>
                    <td className="px-6 py-4 text-left">
                      <button
                        onClick={() => handleDeleteBook(book.id)}
                        className="bg-red-500 hover:bg-red-600 text-white font-semibold py-2 px-4 rounded"
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={5} className="px-6 py-4 text-center text-gray-600">No books found</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default AdminPage;
