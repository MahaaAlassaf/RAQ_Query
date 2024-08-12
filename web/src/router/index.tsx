import React from "react";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import Home from "../pages/Home";
import BookDetails from "../pages/BookDetails";
import AdminPage from "../pages/AdminPage"; // Import AdminPage

const Router: React.FC = () => {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" Component={Home} />
        <Route path="/book/:id" Component={BookDetails} />
        <Route path="/admin" Component={AdminPage} />
      </Routes>
    </BrowserRouter>
  );
};

export default Router;
