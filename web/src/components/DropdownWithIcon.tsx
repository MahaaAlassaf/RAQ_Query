import React, { useEffect, useState } from "react";
import LogInComponent from "./LogInComponent";
import SignUpComponent from "./SignUpComponent";
import { logoutUser } from "../api/userAPI";

const DropdownWithIcon: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [showLoginModal, setShowLoginModal] = useState(false);
  const [showSignupModal, setShowSignupModal] = useState(false);
  const [isLogged, setIsLogged] = useState(false);
  const [userName, setUserName] = useState("");

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    const userInfo = localStorage.getItem("user_info");
    const user = JSON.parse(userInfo || "{}");
    if (token && userInfo) {
      setIsLogged(true);
      setUserName(user.fname);
    }
  }, []);

  const toggleDropdown = () => setIsOpen(!isOpen);

  const handleLoginClick = () => {
    setShowLoginModal(true);
    setIsOpen(false);
  };

  const handleSignupClick = () => {
    setShowSignupModal(true);
    setIsOpen(false);
  };

  const closeModal = () => {
    setShowLoginModal(false);
    setShowSignupModal(false);
  };

  const handleLogOut = () => {
    logoutUser();
    setIsLogged(false);
    // force refresh to update the UI
    window.location.reload();
    setIsOpen(false);
  };

  return (
    <div className="flex items-center flex-col rounded-md px-3 py-2 cursor-pointer w-2/12 justify-end">
      <div className="flex flex-row items-center justify-center">
        <p className="text-white mr-2">{isLogged ? userName : "Account"}</p>
        <div onClick={toggleDropdown}>
          <svg width="24" height="24" viewBox="0 0 24 24">
            <g>
              <path
                fillRule="evenodd"
                clipRule="evenodd"
                d="M11.921 15.9961C7.66 15.9961 5.5 16.7281 5.5 18.1731C5.5 19.6311 7.66 20.3701 11.921 20.3701C16.181 20.3701 18.34 19.6381 18.34 18.1931C18.34 16.7351 16.181 15.9961 11.921 15.9961ZM11.921 21.8701C9.962 21.8701 4 21.8701 4 18.1731C4 14.8771 8.521 14.4961 11.921 14.4961C13.88 14.4961 19.84 14.4961 19.84 18.1931C19.84 21.4891 15.32 21.8701 11.921 21.8701Z"
                fill="#41D0C8"
              />
              <path
                fillRule="evenodd"
                clipRule="evenodd"
                d="M11.9209 3.42751C9.77989 3.42751 8.03789 5.16851 8.03789 7.30951C8.03089 9.44351 9.75989 11.1835 11.8919 11.1915L11.9209 11.9055V11.1915C14.0609 11.1915 15.8019 9.44951 15.8019 7.30951C15.8019 5.16851 14.0609 3.42751 11.9209 3.42751ZM11.9209 12.6185H11.8889C8.9669 12.6095 6.59989 10.2265 6.60989 7.30651C6.60989 4.38151 8.99189 1.99951 11.9209 1.99951C14.8489 1.99951 17.2299 4.38151 17.2299 7.30951C17.2299 10.2375 14.8489 12.6185 11.9209 12.6185Z"
                fill="#41D0C8"
              />
            </g>
          </svg>
        </div>
      </div>
      {isOpen && (
        <div className="absolute right-10 top-16 w-40 bg-white border border-gray-300 rounded-md shadow-lg z-20">
          {isLogged ? (
            <>
              <button
                onClick={handleLogOut}
                className="block w-full text-left px-4 py-2 text-gray-700 hover:bg-gray-100">
                Log Out
              </button>
            </>
          ) : (
            <>
              <button
                onClick={handleLoginClick}
                className="block w-full text-left px-4 py-2 text-gray-700 hover:bg-gray-100">
                Log In
              </button>
              <button
                onClick={handleSignupClick}
                className="block w-full text-left px-4 py-2 text-gray-700 hover:bg-gray-100">
                Sign Up
              </button>
            </>
          )}
        </div>
      )}
      {showLoginModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50">
          <div className="bg-[#101936] p-8 rounded-lg w-full max-w-md mx-4">
            <button onClick={closeModal} className="text-red-500 mb-4">
              Close
            </button>
            <LogInComponent callback={closeModal} />
          </div>
        </div>
      )}
      {showSignupModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50">
          <div className="bg-[#101936] p-8 rounded-lg w-full max-w-md mx-4">
            <button onClick={closeModal} className="text-red-500">
              Close
            </button>
            <SignUpComponent
              callback={() => {
                closeModal();
                setShowLoginModal(true);
              }}
            />
          </div>
        </div>
      )}
    </div>
  );
};

export default DropdownWithIcon;
