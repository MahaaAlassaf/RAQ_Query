import axiosInstance from "./config";
import {
  GetBooksResponse,
  GetBookByIdResponse,
  BooksResponse,
  BookCreate,
} from "./interfaces";

export const getBooks = async (
  title: string = "",
  limit: number = 10,
  offset: number = 0
): Promise<GetBooksResponse> => {
  try {
    const response = await axiosInstance.get<GetBooksResponse>("/books", {
      params: {
        title: title,
        limit: limit,
        offset: offset,
      },
    });

    return response.data;
  } catch (error) {
    throw new Error(`Failed to fetch books: ${(error as Error).message}`);
  }
};

// Fetch all books
export const getAllBooks = async (): Promise<BooksResponse> => {
  try {
    const response = await axiosInstance.get<BooksResponse>("/admin/books");
    return response.data;
  } catch (error) {
    throw new Error(`Failed to fetch books: ${(error as Error).message}`);
  }
};

export const getBookById = async (id: string): Promise<GetBookByIdResponse> => {
  try {
    const response = await axiosInstance.get<GetBookByIdResponse>(
      `/books/${id}`
    );
    return response.data;
  } catch (error) {
    throw new Error(`Failed to fetch book: ${(error as Error).message}`);
  }
};

export const addBookToFavorites = async (bookId: number): Promise<void> => {
  try {
    await axiosInstance.post(`/books/add_to_favorites`, {
      book_id: bookId,
    });
  } catch (error) {
    throw new Error(
      `Failed to add book to favorites: ${(error as Error).message}`
    );
  }
};

export const removeBookFromFavorites = async (
  bookId: number
): Promise<void> => {
  try {
    await axiosInstance.post(`/books/remove_from_favorites`, {
      book_id: bookId,
    });
  } catch (error) {
    throw new Error(
      `Failed to remove book from favorites: ${(error as Error).message}`
    );
  }
};

export const deleteBook = async (bookId: number): Promise<void> => {
  try {
    await axiosInstance.delete(`/books/${bookId}`);
  } catch (error) {
    throw new Error(`Failed to delete book: ${(error as Error).message}`);
  }
};

export const createBook = async (book: BookCreate): Promise<void> => {
  try {
    await axiosInstance.post("/books", book);
  } catch (error) {
    throw new Error(`Failed to create book: ${(error as Error).message}`);
  }
};
