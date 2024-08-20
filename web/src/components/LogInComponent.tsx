import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { loginUser } from "../api/userAPI";
import { LoginUserData } from "../api/interfaces";
import { setLogged, setIsAdmin, setToken } from "../store/authSlice";

interface LogInComponentProps {
  callback: () => void;
}

const LogInComponent: React.FC<LogInComponentProps> = ({ callback }) => {
  const [loginData, setLoginData] = useState<LoginUserData>({
    email: "",
    password: "",
  });
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setLoginData({ ...loginData, [name]: value });
  };

  const handleLogin = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError(null);

    if (!loginData.email || !loginData.password) {
      setError("Please fill out all fields.");
      return;
    }

    setIsLoading(true);

    try {
      const response = await loginUser(loginData);

      if (response.user_info.role === 1) {
        setIsAdmin(true);
        console.log("Admin login successful");
        navigate("/admin");
      } else {
        callback(); // Close the modal
        navigate("/");
        window.location.reload();
      }
      setToken(response.access_token);
      setLogged(true);
    } catch (err) {
      setError("Login failed. Please check your credentials and try again.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="bg-[#101936] p-6 rounded-lg shadow-lg w-full max-w-md mx-auto">
      <h2 className="text-center text-white text-2xl font-semibold mb-6">
        Log In
      </h2>
      {error && <p className="text-red-500 mb-2">{error}</p>}
      <form onSubmit={handleLogin} className="space-y-6">
        <div>
          <label className="block text-white mb-1" htmlFor="email">
            Email
          </label>
          <input
            id="email"
            type="email"
            name="email"
            placeholder="example@pwc.com"
            value={loginData.email}
            onChange={handleInputChange}
            required
            className="w-full px-4 py-3 rounded border border-gray-500 bg-[#151C32] text-white placeholder-gray-400 focus:ring-2 focus:ring-[#41D0C8] focus:outline-none"
          />
        </div>
        <div>
          <label className="block text-white mb-1" htmlFor="password">
            Password
          </label>
          <input
            id="password"
            type="password"
            name="password"
            placeholder="password"
            value={loginData.password}
            onChange={handleInputChange}
            required
            className="w-full px-4 py-3 rounded border border-gray-500 bg-[#151C32] text-white placeholder-gray-400 focus:ring-2 focus:ring-[#41D0C8] focus:outline-none"
          />
        </div>
        <button
          type="submit"
          className={`w-full py-3 text-[#101936] font-bold rounded transition duration-200 ${
            isLoading ? "bg-gray-400" : "bg-[#41D0C8] hover:bg-[#37b2aa]"
          }`}
          disabled={isLoading}>
          {isLoading ? "Loading..." : "Log In"}
        </button>
      </form>
    </div>
  );
};

export default LogInComponent;