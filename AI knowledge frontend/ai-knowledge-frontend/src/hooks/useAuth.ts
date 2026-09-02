import { useContext } from "react";
import { AuthContext } from "../context/authContext";

/**
 * Custom hook used for accessing
 * authentication anywhere
 * inside the application.
 */

export default function useAuth(){
    const context = useContext(AuthContext);
    /**
     * Prevent usage outside
     * AuthProvider.
     */

    if(!context){
        throw new Error(
            "useAuth must be used inside an AuthProvider"
        );
    }

    return context;

}