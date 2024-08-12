// src/components/BookDetails.tsx
import React, { useEffect } from "react";
import { useParams } from "react-router-dom";
import { UnknownAction } from "@reduxjs/toolkit";
import { fetchBookById } from "../store/bookSlice";
import { useDispatch, useSelector } from "react-redux";
import { RootState } from "../store";
import { TailSpin as Spinner } from "react-loader-spinner";

const BookDetails: React.FC = () => {
  const { id = "" } = useParams<{ id: string }>();
  const dispatch = useDispatch();
  const { selectedBook, loading, error } = useSelector(
    (state: RootState) => state.books
  );

  useEffect(() => {
    dispatch(fetchBookById(id) as unknown as UnknownAction);
  }, [dispatch, id]);  // Corrected dependencies

  if (loading)
    return (
      <div className="p-6 bg-primary h-screen flex justify-center items-center">
        <Spinner
          visible={true}
          height="80"
          width="80"
          color="bg-white"
          ariaLabel="tail-spin-loading"
          radius="1"
          wrapperStyle={{}}
          wrapperClass=""
        />
      </div>
    );

  if (error) {
    return (
      <div className="h-screen flex justify-center items-center bg-red-500">
        <p className="text-white text-2xl">Error: {error}</p>
      </div>
    );
  }

  return (
    selectedBook && (
      <div className="p-6 bg-primary text-white h-screen flex flex-col px-10">
        <div className="flex flex-row">
          <img
            className="md:w-auto md:h-72 rounded-lg"
            src={selectedBook.thumbnail}
            alt={`${selectedBook.title} cover`}
          />
          <div className="md:ml-6 mt-4 md:mt-0">
            <h1 className="text-4xl font-bold">{selectedBook.title}</h1>
            <h2 className="text-2xl font-semibold text-gray-300 mt-2">
              {selectedBook.subtitle}
            </h2>
            <p className="text-gray-400 mt-2">
              by {selectedBook.authors.join(", ")}
            </p>
            <p className="text-gray-400 mt-2">Genre: {selectedBook.genre}</p>
            <p className="text-gray-400 mt-2">
              Published Year: {selectedBook.published_year}
            </p>
            <p className="text-gray-400 mt-2">
              Pages: {selectedBook.num_pages}
            </p>
            <p className="text-gray-400 mt-2">
              Average Rating: {selectedBook.average_rating}
            </p>
            <p className="text-gray-400 mt-2">
              Ratings Count: {selectedBook.ratings_count}
            </p>
          </div>
        </div>
        <div className="flex">
          <p className="text-gray-200 mt-4 text-justify">
            {selectedBook.description}
          </p>
        </div>
      </div>
    )
  );
};

export default BookDetails;
