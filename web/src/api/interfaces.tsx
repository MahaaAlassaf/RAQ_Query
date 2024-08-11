// src/api/interfaces.tsx

export interface Book {
  id: number;
  title: string;
  subtitle: string;
  thumbnail: string;
  genre: string;
  published_year: number;
  description: string;
  average_rating: number;
  num_pages: number;
  ratings_count: number;
  authors: string[];
  is_fav: boolean;
}

export interface GetBooksResponse {
  message: string;
  books: Book[];
  limit: number;
  offset: number;
}

export interface GetBookByIdResponse {
  message: string;
  book: Book;
}

export interface ChatResponse {
  message: string;
  response: string;
}

export interface RegisterUserData {
  email: string;
  fname: string;
  lname: string;
  username: string;
  password: string;
  role: number;
}

export interface LoginUserData {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user_info: {
    email: string;
    fname: string;
    lname: string;
    role: number;
  };
}

export interface BookGalleryProps {
  books: Book[];
  searchMessage?: string;
}
