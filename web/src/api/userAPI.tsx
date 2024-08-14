
import axiosInstance from "./config";
import { RegisterUserData, LoginUserData, LoginResponse, UserResponse, Book } from "./interfaces";

// Register a new user
export const registerUser = async (userData: RegisterUserData) => {
  try {
    const response = await axiosInstance.post("/users/register", userData);
    return response.data;
  } catch (error: any) {
    throw new Error(
      error.response?.data?.detail || "An unexpected error occurred during registration"
    );
  }
};

// Log in an existing user
export const loginUser = async (loginData: LoginUserData) => {
  try {
    const response = await axiosInstance.post<LoginResponse>(
      "/users/login",
      loginData
    );

    localStorage.setItem("access_token", response.data.access_token);
    localStorage.setItem("user_info", JSON.stringify(response.data.user_info));

    return response.data;
  } catch (error: any) {
    throw new Error(
      error.response?.data?.detail || "An unexpected error occurred during login"
    );
  }
};

// Log out the user
export const logoutUser = () => {
  localStorage.removeItem("access_token");
  localStorage.removeItem("user_info");
};

// Fetch all users (admin only)
export const getAllUsers = async (): Promise<UserResponse[]> => {
  try {
    const token = localStorage.getItem('access_token');
    if (!token) throw new Error('No token found');

    const response = await axiosInstance.get<UserResponse[]>('/admin/users', {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    return response.data;
  } catch (error: any) {
    throw new Error(
      error.response?.data?.detail || 'An unexpected error occurred while fetching users'
    );
  }
};

// Delete a user (admin only)
export const deleteUser = async (userEmail: string): Promise<void> => {
  try {
    const token = localStorage.getItem('access_token');
    if (!token) throw new Error('No token found');

    await axiosInstance.delete(`/admin/users/${userEmail}`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
  } catch (error: any) {
    throw new Error(
      error.response?.data?.detail || 'An unexpected error occurred while deleting the user'
    );
  }
};

// Add a new book (admin only)
export const adminAddBook = async (bookData: Book): Promise<void> => {
  try {
    const token = localStorage.getItem('access_token');
    if (!token) throw new Error('No token found');

    await axiosInstance.post('/admin/books', bookData, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
  } catch (error: any) {
    throw new Error(
      error.response?.data?.detail || 'An unexpected error occurred while adding the book'
    );
  }
};

// Delete a book (admin only)
export const adminDeleteBook = async (bookId: number): Promise<void> => {
  try {
    const token = localStorage.getItem('access_token');
    if (!token) throw new Error('No token found');

    await axiosInstance.delete(`/admin/books/${bookId}`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
  } catch (error: any) {
    throw new Error(
      error.response?.data?.detail || 'An unexpected error occurred while deleting the book'
    );
  }
};
