import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";

import ProtectedRoute from "./routes/ProtectedRoute";

import LoginPage from "./pages/auth/LoginPage";
import SignupPage from "./pages/auth/SignupPage";
import DashboardPage from "./pages/DashboardPage";

/**
 * Root Application Router
 *
 * Responsible ONLY for defining
 * application routes.
 *
 * No authentication logic.
 * No API calls.
 * No business logic.
 */

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* -------------------------------
            Public Routes
        -------------------------------- */}

        <Route
          path="/login"
          element={<LoginPage />}
        />

        <Route
          path="/signup"
          element={<SignupPage />}
        />

        {/* -------------------------------
            Protected Routes
        -------------------------------- */}

        <Route element={<ProtectedRoute />}>
          <Route
            path="/dashboard"
            element={<DashboardPage />}
          />
        </Route>

        {/* -------------------------------
            Default Route
        -------------------------------- */}

        <Route
          path="/"
          element={<Navigate to="/dashboard" replace />}
        />

        {/* -------------------------------
            Unknown Routes
        -------------------------------- */}

         <Route
                    path="*"
                    element={<Navigate to="/dashboard" replace />}
                />
                
      </Routes>
    </BrowserRouter>
  );
}