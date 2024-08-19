import axios from "axios";

const baseURL = "http://localhost:6969/";

const validateToken = (token: string | null): void => {
  if (!token) {
    throw new Error("No token provided");
  }
};

const axiosInstance = axios.create({
  baseURL: baseURL,
  headers: {
    "Content-Type": "application/json",
  },
});

axiosInstance.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("access_token");
    if (token) {
      validateToken(token);
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

axiosInstance.interceptors.response.use(
  (response) => response,
  (error) => {
    if (axios.isAxiosError(error)) {
      if (error.response) {
        const status = error.response.status;
        if (status === 401 || status === 403) {
          console.error("Invalid token:", error.message);
          localStorage.removeItem("access_token");
          localStorage.removeItem("user_info");
          window.location.reload();
        } else {
          console.error(`Error: ${error.response.data.detail}`);
        }
      } else {
        console.error("Network error:", error.message);
      }
    } else {
      console.error("Unexpected error:", error);
    }
    return Promise.reject(error);
  }
);

export default axiosInstance;
