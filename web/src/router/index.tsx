import React from "react";
import { BrowserRouter, Route, Routes, Navigate } from "react-router-dom";
import Home from "../pages/Home";
import BookDetails from "../pages/BookDetails";
import AdminPage from "../pages/AdminPage";
import jwtDecode from "jwt-decode";

const Router: React.FC = () => {
  const isAdmin = () => {
    const token = localStorage.getItem("access_token");
    if (!token) return false;

    const decodedToken: any = jwtDecode(token);
    return decodedToken.role === 1;
  };

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/book/:id" element={<BookDetails />} />
        <Route
          path="/admin"
          element={isAdmin() ? <AdminPage /> : <Navigate to="/" replace />}
        />
      </Routes>
    </BrowserRouter>
  );
};

export default Router;
