import React, { useEffect, useState } from "react";
import { useSelector, useDispatch } from "react-redux";
import { fetchBooks, setOffset } from "../store/bookSlice";
import { RootState, AppDispatch } from "../store";
import { Loading as Spinner } from "../components/Loading";
import Search from "../components/Search";
import Chatbot from "../components/chatBot";
import Book from "../components/book";
import Error from "../components/Error";
import Pagination from "../components/Pagination";
import LogInSignUp from "../components/DropdownWithIcon";

const Home: React.FC = () => {
  const dispatch = useDispatch<AppDispatch>();
  const [title, setTitle] = useState("");
  const { books, loading, error, limit, offset } = useSelector(
    (state: RootState) => state.books
  );

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (token) {
      console.log("Token: ", token);
    }
  }, []);

  useEffect(() => {
    dispatch(fetchBooks({ title, limit, offset }));
  }, [dispatch, title, limit, offset]);  // Included `title`  

  const handleNextPage = () => dispatch(setOffset(offset + limit));
  const handlePreviousPage = () =>
    dispatch(setOffset(Math.max(offset - limit, 0)));

  if (loading) return <Spinner />;
  if (error) return <Error error={error} />;

  return (
    <div className="h-screen flex flex-col bg-primary px-6 pt-6">
      <Chatbot />
      <div className="flex justify-between items-center mb-4 border-b border-opacity-15 border-slate pb-4">
        <Search title={title} setTitle={setTitle} />
        <LogInSignUp />
      </div>
      <div className="flex flex-col overflow-y-auto pb-6">
        <div className="grid sm:grid-cols-2  md:grid-cols-4 xl:grid-cols-5 lg:grid-cols-5 gap-8">
          {books.map((book) => (
            <Book key={book.id} book={book} />
          ))}
        </div>
        <Chatbot></Chatbot>
        <Pagination
          offset={offset}
          limit={limit}
          booksLength={books.length}
          handleNextPage={handleNextPage}
          handlePreviousPage={handlePreviousPage}
        />
      </div>
    </div>
  );
};

export default Home;
