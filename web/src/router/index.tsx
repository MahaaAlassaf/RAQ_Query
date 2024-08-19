import React from "react";
import {
  BrowserRouter,
  Route,
  Routes,
  Navigate,
  useNavigate,
} from "react-router-dom";
import Home from "../pages/Home";
import BookDetails from "../pages/BookDetails";
import AdminPage from "../pages/AdminPage";
import jwtDecode from "jwt-decode";

const AdminRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const navigate = useNavigate();
  const token = localStorage.getItem("access_token");

  if (!token) {
    navigate("/");
    return null;
  }

  const decodedToken: any = jwtDecode(token);
  if (decodedToken.role !== 1) {
    navigate("/");
    return null;
  }

  return <>{children}</>;
};

const Router: React.FC = () => {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/book/:id" element={<BookDetails />} />
        <Route
          path="/admin"
          element={
            <AdminRoute>
              <AdminPage />
            </AdminRoute>
          }
        />
        {/* Fallback Route */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
};

export default Router;
