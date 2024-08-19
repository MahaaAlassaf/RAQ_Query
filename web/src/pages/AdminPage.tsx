import React, { useEffect, useState } from "react";
import { getAllUsers, deleteUser, adminDeleteBook } from "../api/userAPI";
import { fetchBooks, setOffset, setLimit } from "../store/bookSlice";
import { useSelector, useDispatch } from "react-redux";
import { RootState, AppDispatch } from "../store";
import { UserResponse } from "../api/interfaces";
import Pagination from "../components/Pagination";
import LogInSignUp from "../components/DropdownWithIcon";
import NewBookForm from "../components/AddBook";

const AdminPage: React.FC = () => {
  const [users, setUsers] = useState<UserResponse[]>([]);
  // const [books, setBooks] = useState<Book[]>([]);
  const [error, setError] = useState<string | null>(null);
  const { books, limit, offset } = useSelector(
    (state: RootState) => state.books
  );
  const dispatch = useDispatch<AppDispatch>();
  const [title, setTitle] = useState("");

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
  useEffect(() => {
    dispatch(fetchBooks({ title, limit: 10, offset }));
  }, [dispatch, limit, offset]);

  const handleNextPage = () => dispatch(setOffset(offset + limit));
  const handlePreviousPage = () =>
    dispatch(setOffset(Math.max(offset - limit, 0)));

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
      dispatch(fetchBooks({ title, limit, offset }));
    } catch (error) {
      setError("Failed to delete book");
    }
  };

  useEffect(() => {
    fetchUsers();
  }, []);

  const [showModal, setShowModal] = useState(false);

  const closeModal = () => {
    setShowModal(false);
  };

  const handleSubmit = (event: React.FormEvent) => {
    event.preventDefault();
    dispatch(fetchBooks({ title, limit, offset: 0 }));
  };

  const handlePerPageChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    const newLimit = Number(event.target.value);
    dispatch(setLimit(newLimit));
    dispatch(fetchBooks({ title, limit: newLimit, offset: 0 }));
  };

  return (
    <div className="p-6 bg-primary min-h-screen">
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50 ">
          <div className="bg-[#101936] p-8 rounded-lg w-full max-w-4xl mx-4 overflow-auto max-h-screen">
            <button onClick={closeModal} className="text-red-500 mb-4">
              Close
            </button>
            <NewBookForm callback={closeModal} />
          </div>
        </div>
      )}
      <div className="flex justify-between items-center mb-4 border-b border-opacity-15 border-slate pb-4">
        <h1 className="text-3xl font-bold text-white">Admin Dashboard</h1>

        <LogInSignUp />
      </div>
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
                    <td className="px-6 py-4 text-left text-gray-100">
                      {user.email}
                    </td>
                    <td className="px-6 py-4 text-left text-gray-100">
                      {user.fname}
                    </td>
                    <td className="px-6 py-4 text-left text-gray-100">
                      {user.lname}
                    </td>
                    <td className="px-6 py-4 text-left text-gray-100">
                      {user.role === 1 ? "Admin" : "User"}
                    </td>
                    <td className="px-6 py-4 text-left">
                      <button
                        onClick={() => handleDeleteUser(user.email)}
                        className="bg-red-500 hover:bg-red-600 text-white font-semibold py-2 px-4 rounded">
                        Delete
                      </button>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td
                    colSpan={5}
                    className="px-6 py-4 text-center text-gray-600">
                    No users found
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Books Table */}
      <div>
        <h2 className="text-2xl font-semibold mb-4 text-slate">Books</h2>
        <div className="flex flex-row justify-between items-center mb-4">
          <form
            className="flex justify-start items-center w-2/6"
            onSubmit={handleSubmit}>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Search by title"
              className="px-4 py-2 bg-[#445A9A] text-white rounded mr-2 w-full"
            />
            <button
              onClick={() => dispatch(fetchBooks({ title, limit, offset: 0 }))}
              className="bg-blue-500 hover:bg-blue-600 text-white font-semibold py-2 px-4 rounded">
              Search
            </button>
          </form>
          <button
            onClick={() => setShowModal(true)}
            className="bg-green-600 hover:bg-green-700 text-white font-semibold py-2 px-4 rounded">
            Add Book
          </button>
        </div>
        <label htmlFor="perPage" className="text-white mr-2">
          Results Per Page:
        </label>
        <select
          id="perPage"
          onChange={handlePerPageChange}
          value={limit}
          className="px-2 py-1 bg-blue-900 text-white rounded">
          {[10, 20, 30, 40, 50].map((value) => (
            <option key={value} value={value}>
              {value}
            </option>
          ))}
        </select>
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
                    <td className="px-6 py-4 text-left text-gray-100">
                      {book.title}
                    </td>
                    <td className="px-6 py-4 text-left text-gray-100">
                      {Array.isArray(book.authors)
                        ? book.authors.join(", ")
                        : "Unknown"}
                    </td>
                    <td className="px-6 py-4 text-left text-gray-100">
                      {book.published_year}
                    </td>
                    <td className="px-6 py-4 text-left text-gray-100">
                      {book.genre}
                    </td>
                    <td className="px-6 py-4 text-left">
                      <button
                        onClick={() => handleDeleteBook(book.id)}
                        className="bg-red-500 hover:bg-red-600 text-white font-semibold py-2 px-4 rounded">
                        Delete
                      </button>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td
                    colSpan={5}
                    className="px-6 py-4 text-center text-gray-600">
                    No books found
                  </td>
                </tr>
              )}
            </tbody>
            <Pagination
              offset={offset}
              limit={limit}
              booksLength={books.length}
              handleNextPage={handleNextPage}
              handlePreviousPage={handlePreviousPage}
            />
          </table>
        </div>
      </div>
    </div>
  );
};

export default AdminPage;
