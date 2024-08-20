import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";
import { getBooks, getBookById } from "../api/bookAPI";
import { Book } from "../api/interfaces";

interface BookState {
  books: Book[];
  selectedBook: Book | null;
  loading: boolean;
  error: string | null;
  limit: number;
  offset: number;
}

const initialState: BookState = {
  books: [],
  selectedBook: null,
  loading: false,
  error: null,
  limit: 10,
  offset: 0,
};

// Async thunk to fetch books from API
export const fetchBooks = createAsyncThunk(
  "books/fetchBooks",
  async (params: { title: string; limit: number; offset: number }) => {
    const response = await getBooks(params.title, params.limit, params.offset);
    return response.books;
  }
);

export const fetchBookById = createAsyncThunk(
  "books/fetchBookById",
  async (id: string) => {
    const response = await getBookById(id);
    return response;
  }
);

const bookSlice = createSlice({
  name: "books",
  initialState,
  reducers: {
    setLimit: (state, action) => {
      state.limit = action.payload;
    },
    setOffset: (state, action) => {
      state.offset = action.payload;
    },
    setBooks: (state, action) => {
      state.books = action.payload;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchBooks.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchBooks.fulfilled, (state, action) => {
        state.loading = false;
        state.books = action.payload;
      })
      .addCase(fetchBooks.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || "Failed to fetch books";
      })
      .addCase(fetchBookById.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchBookById.fulfilled, (state, action) => {
        state.loading = false;
        state.selectedBook = action.payload.book;
      })
      .addCase(fetchBookById.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || "Failed to fetch book";
      });
  },
});

export const { setLimit, setOffset, setBooks } = bookSlice.actions;
export default bookSlice.reducer;