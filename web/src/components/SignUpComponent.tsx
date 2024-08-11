import React, { useState } from "react";
import { registerUser } from "../api/userAPI";
import { RegisterUserData } from "../api/interfaces";

interface SignUpComponentProps {
  // Define props here
  // add prop for a function to close the modal
  callback: () => void;
}

const SignUpComponent: React.FC<SignUpComponentProps> = ({ callback }) => {
  const [registerData, setRegisterData] = useState<RegisterUserData>({
    email: "",
    fname: "",
    lname: "",
    username: "",
    password: "",
    role: 0,
  });
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isPasswordValid, setIsPasswordValid] = useState(false);
  const [passwordRequirements, setPasswordRequirements] = useState({
    lengthValid: false,
    numberValid: false,
    symbolsValid: false,
  });

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setRegisterData({ ...registerData, [name]: value });

    if (name === "password") {
      validatePassword(value);
    }
  };

  const validatePassword = (password: string) => {
    const lengthValid = password.length >= 8;
    const numberValid = /\d/.test(password);
    const symbolsValid = /^[A-Za-z0-9]*$/.test(password);

    setIsPasswordValid(lengthValid && numberValid && symbolsValid);
    setPasswordRequirements({ lengthValid, numberValid, symbolsValid });
  };

  const handleRegister = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError(null);

    // Ensure all fields are filled
    if (
      !registerData.email ||
      !registerData.fname ||
      !registerData.lname ||
      !registerData.username ||
      !registerData.password
    ) {
      setError("Please fill out all fields.");
      return;
    }

    console.log("Registration data being sent:", registerData);
    setIsLoading(true);

    try {
      const response = await registerUser(registerData);
      console.log("Registration successful:", response);
      callback();
      // Optionally reset the form or redirect the user
    } catch (err: any) {
      // Handle specific error messages from the server
      if (err.message.includes("already exists")) {
        setError("Email or username is already in use.");
      } else {
        setError(err.message || "Registration failed. Please try again.");
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="bg-[#101936] p-6 rounded-lg shadow-lg w-full max-w-md mx-auto">
      <h2 className="text-center text-white text-2xl font-semibold mb-6">
        Sign Up
      </h2>
      {error && <p className="text-red-500 mb-2">{error}</p>}
      <form onSubmit={handleRegister} className="space-y-6">
        <div>
          <label className="block text-white mb-1" htmlFor="email">
            Email
          </label>
          <input
            id="email"
            type="email"
            name="email"
            placeholder="example@pwc.com"
            value={registerData.email}
            onChange={handleInputChange}
            required
            className="w-full px-4 py-3 rounded border border-gray-500 bg-[#151C32] text-white placeholder-gray-400 focus:ring-2 focus:ring-[#41D0C8] focus:outline-none"
          />
        </div>
        <div>
          <label className="block text-white mb-1" htmlFor="fname">
            First Name
          </label>
          <input
            id="fname"
            type="text"
            name="fname"
            placeholder="First Name"
            value={registerData.fname}
            onChange={handleInputChange}
            required
            className="w-full px-4 py-3 rounded border border-gray-500 bg-[#151C32] text-white placeholder-gray-400 focus:ring-2 focus:ring-[#41D0C8] focus:outline-none"
          />
        </div>
        <div>
          <label className="block text-white mb-1" htmlFor="lname">
            Last Name
          </label>
          <input
            id="lname"
            type="text"
            name="lname"
            placeholder="Last Name"
            value={registerData.lname}
            onChange={handleInputChange}
            required
            className="w-full px-4 py-3 rounded border border-gray-500 bg-[#151C32] text-white placeholder-gray-400 focus:ring-2 focus:ring-[#41D0C8] focus:outline-none"
          />
        </div>
        <div>
          <label className="block text-white mb-1" htmlFor="username">
            Username
          </label>
          <input
            id="username"
            type="text"
            name="username"
            placeholder="Username"
            value={registerData.username}
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
            placeholder="Password"
            value={registerData.password}
            onChange={handleInputChange}
            required
            className={`w-full px-4 py-3 rounded border ${
              isPasswordValid ? "border-gray-500" : "border-red-500"
            } bg-[#151C32] text-white placeholder-gray-400 focus:ring-2 focus:ring-[#41D0C8] focus:outline-none`}
          />
          <div className="mt-2 text-sm">
            <p
              className={
                passwordRequirements.lengthValid
                  ? "text-green-500"
                  : "text-red-500"
              }>
              • 8 characters or more
            </p>
            <p
              className={
                passwordRequirements.numberValid
                  ? "text-green-500"
                  : "text-red-500"
              }>
              • At least one number
            </p>
            <p
              className={
                passwordRequirements.symbolsValid
                  ? "text-green-500"
                  : "text-red-500"
              }>
              • No symbols
            </p>
          </div>
        </div>
        <button
          type="submit"
          className={`w-full py-3 mt-4 text-[#101936] font-bold rounded transition duration-200 ${
            isPasswordValid
              ? "bg-[#41D0C8] hover:bg-[#37b2aa]"
              : "bg-gray-500 cursor-not-allowed"
          }`}
          disabled={!isPasswordValid || isLoading}>
          {isLoading ? (
            <svg className="animate-spin h-2 w-2 mx-auto" viewBox="0 0 24 24">
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"></circle>
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8v8H4z"></path>
            </svg>
          ) : (
            "Sign Up"
          )}
        </button>
      </form>
    </div>
  );
};

export default SignUpComponent;
