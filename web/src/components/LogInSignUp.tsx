import React, { useState } from "react";

const DropdownWithIcon: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);

  const toggleDropdown = () => {
    setIsOpen(!isOpen);
  };

  return (
    <div className="relative inline-block text-left">
      <div
        className="flex items-center rounded-md px-3 py-2 cursor-pointer" 
        onClick={toggleDropdown}
      >
        <svg
          width="24"
          height="24"
          viewBox="0 0 24 24"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
          className="ml-auto"
        >
          <mask id="mask0_1_1254" style={{ maskType: "luminance" }} maskUnits="userSpaceOnUse" x="4" y="14" width="16" height="8">
            <path fillRule="evenodd" clipRule="evenodd" d="M4 14.4961H19.8399V21.8701H4V14.4961Z" fill="white"/>
          </mask>
          <g mask="url(#mask0_1_1254)">
            <path fillRule="evenodd" clipRule="evenodd" d="M11.921 15.9961C7.66 15.9961 5.5 16.7281 5.5 18.1731C5.5 19.6311 7.66 20.3701 11.921 20.3701C16.181 20.3701 18.34 19.6381 18.34 18.1931C18.34 16.7351 16.181 15.9961 11.921 15.9961ZM11.921 21.8701C9.962 21.8701 4 21.8701 4 18.1731C4 14.8771 8.521 14.4961 11.921 14.4961C13.88 14.4961 19.84 14.4961 19.84 18.1931C19.84 21.4891 15.32 21.8701 11.921 21.8701Z" fill="#41D0C8"/>
          </g>
          <mask id="mask1_1_1254" style={{ maskType: "luminance" }} maskUnits="userSpaceOnUse" x="6" y="2" width="12" height="11">
            <path fillRule="evenodd" clipRule="evenodd" d="M6.60986 2H17.2299V12.6186H6.60986V2Z" fill="white"/>
          </mask>
          <g mask="url(#mask1_1_1254)">
            <path fillRule="evenodd" clipRule="evenodd" d="M11.9209 3.42751C9.77989 3.42751 8.03789 5.16851 8.03789 7.30951C8.03089 9.44351 9.75989 11.1835 11.8919 11.1915L11.9209 11.9055V11.1915C14.0609 11.1915 15.8019 9.44951 15.8019 7.30951C15.8019 5.16851 14.0609 3.42751 11.9209 3.42751ZM11.9209 12.6185H11.8889C8.9669 12.6095 6.59989 10.2265 6.60989 7.30651C6.60989 4.38151 8.99189 1.99951 11.9209 1.99951C14.8489 1.99951 17.2299 4.38151 17.2299 7.30951C17.2299 10.2375 14.8489 12.6185 11.9209 12.6185Z" fill="#41D0C8"/>
          </g>
        </svg>
      </div>
      {isOpen && (
        <div className="absolute right-0 mt-2 w-40 bg-white border border-gray-300 rounded-md shadow-lg">
          <div className="py-1">
            <a href="#" className="block px-4 py-2 text-gray-700 hover:bg-gray-100">Log In</a>
            <a href="#" className="block px-4 py-2 text-gray-700 hover:bg-gray-100">Sign Up</a>
          </div>
        </div>
      )}
    </div>
  );
};

export default DropdownWithIcon;
