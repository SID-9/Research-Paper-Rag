import React from "react";
import ReactDOM from "react-dom/client";

import App from "./App";

import "./index.css";

import { AuthProvider } from "./context/authContext";

/**
 * Application Entry Point
 *
 * Similar to Spring Boot's:
 *
 * SpringApplication.run(...)
 *
 * The entire React application starts here.
 */
ReactDOM.createRoot(
    document.getElementById("root")!
).render(

    <React.StrictMode>

        <AuthProvider>

            <App />

        </AuthProvider>

    </React.StrictMode>

);