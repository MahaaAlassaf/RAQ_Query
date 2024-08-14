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
    <div className="p-6 bg-primary min-h-screen">
      <h1 className="text-3xl font-bold mb-6 text-white">Admin Dashboard</h1>
      {error && <div className="text-red-600 mb-6">{error}</div>}

      {/* Users Table */}
      <div className="mb-10">
        <h2 className="text-2xl font-semibold mb-4 text-slate">Users</h2>
        <div className="overflow-x-auto">
          <table className="min-w-full bg-secondary shadow-md rounded-lg">
            <thead className="bg-slate text-white">
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
                    <td className="px-6 py-4 text-left text-gray-100">{user.email}</td>
                    <td className="px-6 py-4 text-left text-gray-100">{user.fname}</td>
                    <td className="px-6 py-4 text-left text-gray-100">{user.lname}</td>
                    <td className="px-6 py-4 text-left text-gray-100">{user.role === 1 ? "Admin" : "User"}</td>
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
        <h2 className="text-2xl font-semibold mb-4 text-slate">Books</h2>
        <div className="overflow-x-auto">
          <table className="min-w-full bg-secondary shadow-md rounded-lg">
            <thead className="bg-slate text-white">
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
                    <td className="px-6 py-4 text-left text-gray-100">{book.title}</td>
                    <td className="px-6 py-4 text-left text-gray-100">
                      {Array.isArray(book.authors) ? book.authors.join(", ") : "Unknown"}
                    </td>
                    <td className="px-6 py-4 text-left text-gray-100">{book.published_year}</td>
                    <td className="px-6 py-4 text-left text-gray-100">{book.genre}</td>
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