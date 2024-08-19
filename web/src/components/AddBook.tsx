import React, { useState } from "react";
import { createBook } from "../api/bookAPI";
import { BookCreate } from "../api/interfaces";

interface NewBookFormProps {
  callback: () => void; // Function to close the modal
}

const NewBookForm: React.FC<NewBookFormProps> = ({ callback }) => {
  const [bookData, setBookData] = useState<BookCreate>({
    title: "",
    subtitle: "",
    thumbnail: "",
    genre: "",
    published_year: new Date().getFullYear(),
    description: "",
    average_rating: 0,
    num_pages: 0,
    ratings_count: 0,
    authors: [],
  });

  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleInputChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => {
    const { name, value } = e.target;
    setBookData({ ...bookData, [name]: value });
  };

  const handleAuthorChange = (
    index: number,
    e: React.ChangeEvent<HTMLInputElement>
  ) => {
    const { value } = e.target;
    const authors = [...bookData.authors];
    authors[index].name = value;
    setBookData({ ...bookData, authors });
  };

  const handleAddAuthor = () => {
    setBookData({
      ...bookData,
      authors: [...bookData.authors, { name: authorName }],
    });
    setAuthorName("");
  };

  const handleRemoveAuthor = (index: number) => {
    const authors = bookData.authors.filter((_, i) => i !== index);
    setBookData({ ...bookData, authors });
  };

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError(null);
    setIsLoading(true);

    try {
      await createBook(bookData);
      callback();
    } catch (err: any) {
      setError(err.message || "Failed to add book. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  const [authorName, setAuthorName] = useState("");

  return (
    <div className="bg-[#101936] p-6 rounded-lg w-full">
      <h2 className="text-center text-white text-2xl font-semibold mb-6">
        Add New Book
      </h2>
      {error && <p className="text-red-500 mb-2">{error}</p>}
      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="grid grid-cols-2 gap-6">
          <div>
            <label className="block text-white mb-1" htmlFor="title">
              Title
            </label>
            <input
              id="title"
              type="text"
              name="title"
              placeholder="Book Title"
              value={bookData.title}
              onChange={handleInputChange}
              required
              className="w-full px-4 py-3 rounded border border-gray-500 bg-[#151C32] text-white placeholder-gray-400 focus:ring-2 focus:ring-[#41D0C8] focus:outline-none"
            />
          </div>
          <div>
            <label className="block text-white mb-1" htmlFor="subtitle">
              Subtitle
            </label>
            <input
              id="subtitle"
              type="text"
              name="subtitle"
              placeholder="Book Subtitle"
              value={bookData.subtitle}
              onChange={handleInputChange}
              className="w-full px-4 py-3 rounded border border-gray-500 bg-[#151C32] text-white placeholder-gray-400 focus:ring-2 focus:ring-[#41D0C8] focus:outline-none"
            />
          </div>
          <div>
            <label className="block text-white mb-1" htmlFor="thumbnail">
              Thumbnail URL
            </label>
            <input
              id="thumbnail"
              type="url"
              name="thumbnail"
              placeholder="http://example.com/image.jpg"
              value={bookData.thumbnail}
              onChange={handleInputChange}
              className="w-full px-4 py-3 rounded border border-gray-500 bg-[#151C32] text-white placeholder-gray-400 focus:ring-2 focus:ring-[#41D0C8] focus:outline-none"
            />
          </div>
          <div>
            <label className="block text-white mb-1" htmlFor="genre">
              Genre
            </label>
            <input
              id="genre"
              type="text"
              name="genre"
              placeholder="Book Genre"
              value={bookData.genre}
              onChange={handleInputChange}
              className="w-full px-4 py-3 rounded border border-gray-500 bg-[#151C32] text-white placeholder-gray-400 focus:ring-2 focus:ring-[#41D0C8] focus:outline-none"
            />
          </div>
          <div>
            <label className="block text-white mb-1" htmlFor="published_year">
              Published Year
            </label>
            <input
              id="published_year"
              type="number"
              name="published_year"
              placeholder="2024"
              value={bookData.published_year}
              onChange={handleInputChange}
              className="w-full px-4 py-3 rounded border border-gray-500 bg-[#151C32] text-white placeholder-gray-400 focus:ring-2 focus:ring-[#41D0C8] focus:outline-none"
            />
          </div>
          <div>
            <label className="block text-white mb-1" htmlFor="description">
              Description
            </label>
            <textarea
              id="description"
              name="description"
              placeholder="Book Description"
              value={bookData.description}
              onChange={handleInputChange}
              className="w-full px-4 py-3 rounded border border-gray-500 bg-[#151C32] text-white placeholder-gray-400 focus:ring-2 focus:ring-[#41D0C8] focus:outline-none"
            />
          </div>
          <div>
            <label className="block text-white mb-1" htmlFor="average_rating">
              Average Rating
            </label>
            <input
              id="average_rating"
              type="number"
              name="average_rating"
              placeholder="4.5"
              value={bookData.average_rating}
              onChange={handleInputChange}
              className="w-full px-4 py-3 rounded border border-gray-500 bg-[#151C32] text-white placeholder-gray-400 focus:ring-2 focus:ring-[#41D0C8] focus:outline-none"
            />
          </div>
          <div>
            <label className="block text-white mb-1" htmlFor="num_pages">
              Number of Pages
            </label>
            <input
              id="num_pages"
              type="number"
              name="num_pages"
              placeholder="350"
              value={bookData.num_pages}
              onChange={handleInputChange}
              className="w-full px-4 py-3 rounded border border-gray-500 bg-[#151C32] text-white placeholder-gray-400 focus:ring-2 focus:ring-[#41D0C8] focus:outline-none"
            />
          </div>
          <div>
            <label className="block text-white mb-1" htmlFor="ratings_count">
              Ratings Count
            </label>
            <input
              id="ratings_count"
              type="number"
              name="ratings_count"
              placeholder="100"
              value={bookData.ratings_count}
              onChange={handleInputChange}
              className="w-full px-4 py-3 rounded border border-gray-500 bg-[#151C32] text-white placeholder-gray-400 focus:ring-2 focus:ring-[#41D0C8] focus:outline-none"
            />
          </div>
          <div>
            <label className="block text-white mb-1">Authors</label>
            <input
              type="text"
              placeholder="Author Name"
              value={authorName}
              onChange={(e) => setAuthorName(e.target.value)}
              className="flex-1 w-full mb-2 px-4 py-3 rounded border border-gray-500 bg-[#151C32] text-white placeholder-gray-400 focus:ring-2 focus:ring-[#41D0C8] focus:outline-none"
            />
            {bookData.authors.map((author, index) => (
              <div key={index} className="flex mb-2 justify-between w-full">
                <input
                  type="text"
                  placeholder="Author Name"
                  value={author.name}
                  required
                  className="flex w-2/3 px-4 py-3 rounded border border-gray-500 bg-[#151C32] text-white placeholder-gray-400 focus:ring-2 focus:ring-[#41D0C8] focus:outline-none"
                  readOnly={true}
                />
                <button
                  type="button"
                  onClick={() => handleRemoveAuthor(index)}
                  className="flex w-1/3 text-red-500 items-center justify-center">
                  Remove
                </button>
              </div>
            ))}
            <button
              type="button"
              onClick={handleAddAuthor}
              className="text-blue-500">
              Add Author
            </button>
          </div>
        </div>
        <div className="flex justify-between items-center">
          <button
            type="submit"
            className={`w-full py-3 mt-4 text-white font-bold rounded transition duration-200 ${
              isLoading
                ? "bg-gray-500 cursor-not-allowed"
                : "bg-green-600 hover:bg-green-700"
            }`}
            disabled={isLoading}>
            {isLoading ? (
              <svg className="animate-spin h-2 w-2 mx-auto" viewBox="0 0 24 24">
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"></circle>
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8v8H4z"></path>
              </svg>
            ) : (
              "Add Book"
            )}
          </button>
        </div>
      </form>
    </div>
  );
};

export default NewBookForm;
