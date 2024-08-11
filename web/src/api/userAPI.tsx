// src/api/userAPI.tsx
import axiosInstance from "./config";
import { RegisterUserData, LoginUserData, LoginResponse } from "./interfaces";

// Register a new user
export const registerUser = async (userData: RegisterUserData) => {
  try {
    console.log(userData); // Check the structure and content
    const response = await axiosInstance.post("/users/register", userData);
    return response.data;
  } catch (error: any) {
    throw new Error(
      error.response?.data?.detail ||
        "An unexpected error occurred during registration"
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

    // Save the token and user info to local storage
    localStorage.setItem("access_token", response.data.access_token);
    localStorage.setItem("user_info", JSON.stringify(response.data.user_info));

    return response.data;
  } catch (error: any) {
    throw new Error(
      error.response?.data?.detail ||
        "An unexpected error occurred during login"
    );
  }
};

export const logoutUser = () => {
  localStorage.removeItem("access_token");
  localStorage.removeItem("user_info");
};
