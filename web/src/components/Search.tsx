import React from "react";
import { useDispatch, useSelector } from "react-redux";
import { fetchBooks, setLimit } from "../store/bookSlice";
import { RootState, AppDispatch } from "../store";

interface SearchProps {
  title: string;
  setTitle: React.Dispatch<React.SetStateAction<string>>;
}

const Search: React.FC<SearchProps> = ({ title, setTitle }) => {
  const dispatch = useDispatch<AppDispatch>();
  const limit = useSelector((state: RootState) => state.books.limit);

  const handlePerPageChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    const newLimit = Number(event.target.value);
    dispatch(setLimit(newLimit));
    dispatch(fetchBooks({ title, limit: newLimit, offset: 0 }));
  };

  const handleSearch = () => {
    dispatch(fetchBooks({ title, limit, offset: 0 }));
  };

  return (
    <header className="flex justify-between items-center w-10/12">
      <h1 className="flex-none text-2xl  font-bold text-white w-1/6">
        Library
      </h1>
      <div className="flex items-center flex-grow justify-center w-3/6">
        <input
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="Search by title"
          className="px-5 py-1 bg-[#445A9A] text-white rounded mr-2 w-full"
        />
        <button
          onClick={handleSearch}
          className="p-2 text-white rounded bg-transparent hover:bg-blue-800 transition"
          aria-label="Search">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
            <mask
              id="mask0_1_1778"
              style={{ maskType: "luminance" }}
              maskUnits="userSpaceOnUse"
              x="2"
              y="2"
              width="20"
              height="20">
              <path d="M2 2H21.4768V21.477H2V2Z" fill="white" />
            </mask>
            <g mask="url(#mask0_1_1778)">
              <path
                d="M11.739 3.5C7.196 3.5 3.5 7.195 3.5 11.738C3.5 16.281 7.196 19.977 11.739 19.977C16.281 19.977 19.977 16.281 19.977 11.738C19.977 7.195 16.281 3.5 11.739 3.5ZM11.739 21.477C6.369 21.477 2 17.108 2 11.738C2 6.368 6.369 2 11.739 2C17.109 2 21.477 6.368 21.477 11.738C21.477 17.108 17.109 21.477 11.739 21.477Z"
                fill="#F7F5FF"
              />
            </g>
            <mask
              id="mask1_1_1778"
              style={{ maskType: "luminance" }}
              maskUnits="userSpaceOnUse"
              x="17"
              y="17"
              width="6"
              height="6">
              <path
                d="M17.2397 17.707H22.2638V22.7218H17.2397V17.707Z"
                fill="white"
              />
            </mask>
            <g mask="url(#mask1_1_1778)">
              <path
                d="M21.514 22.7218C21.323 22.7218 21.131 22.6488 20.984 22.5028L17.46 18.9888C17.167 18.6958 17.166 18.2208 17.459 17.9278C17.751 17.6328 18.226 17.6348 18.52 17.9258L22.044 21.4408C22.337 21.7338 22.338 22.2078 22.045 22.5008C21.899 22.6488 21.706 22.7218 21.514 22.7218Z"
                fill="#F7F5FF"
              />
            </g>
          </svg>
        </button>
      </div>
      <div className="flex justify-end items-center w-2/6">
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
      </div>
    </header>
  );
};

export default Search;
