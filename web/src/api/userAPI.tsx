// src/api/userAPI.ts
import axios from "axios";
import { RegisterUserData, LoginUserData } from "./interfaces";

// Register a new user
export const registerUser = async (userData: RegisterUserData) => {
  try {
    console.log(userData); 
    const response = await axios.post('http://localhost:6969/users/register', userData);
    return response.data;
  } catch (error: any) {
    throw new Error(error.response?.data?.detail || 'An unexpected error occurred during registration');
  }
};


// Log in an existing user
export const loginUser = async (loginData: LoginUserData) => {
  try {
    const response = await axios.post('http://localhost:6969/users/login', loginData, {
      headers: {
        'Content-Type': 'application/json', 
      },
    });
    return response.data;
  } catch (error: any) {
    throw new Error(error.response?.data?.detail || 'An unexpected error occurred during login');
  }
};


