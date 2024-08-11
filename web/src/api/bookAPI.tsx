// src/api/bookAPI.tsx
import axiosInstance from "./config";
import { GetBooksResponse, GetBookByIdResponse } from "./interfaces";

// implement paginated get books API
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
