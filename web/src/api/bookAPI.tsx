// src/api/bookAPI.tsx
import axiosInstance from "./config";
import { GetBooksResponse, GetBookByIdResponse } from "./interfaces";

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


