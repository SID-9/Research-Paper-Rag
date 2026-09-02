import { Navigate, Outlet } from "react-router-dom";

import useAuth  from "../hooks/useAuth";

/**
 * Protected Route
 *
 * Similar to Spring Security's
 * authentication filter.
 *
 * It decides whether the user
 * is allowed to access
 * protected pages.
 */

export default function ProtectedRoute(){

    const{
        isAuthenticated,
        isLoading,
    } = useAuth();

    /**
     * While checking authentication
     * we should not render
     * any page yet.
     */

    if(isLoading){
        return (
            <div className="flex items-center justify-center h-screen">
                <h2 className="text-lg font-semibold">
                    Loading.... 
                </h2>
            </div>
        );
    }

    /**
     * User is not authenticated.
     *
     * Redirect to Login.
     */

    if(!isAuthenticated){
        return <Navigate to="/login" replace/>;
    }

     /**
     * Authentication successful.
     *
     * Render requested page.
     */

     return <Outlet />;

}

