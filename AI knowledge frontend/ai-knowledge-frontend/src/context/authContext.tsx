import {
    createContext,
    useEffect,
    useState
} from "react";

import type {ReactNode} from "react";

import authApi from "../api/authApi";

import type { User } from "../types/auth";

/**
 * Everything that components
 * are allowed to access.
 *
 * Think of this like
 * a Service interface.
 */

export interface AuthContextType{

    currentUser: User | null;
    isAuthenticated: boolean;
    isLoading: boolean;

    login(
        email: string,
        password: string,

    ): Promise<void>;

    signup(
        email: string,
        password: string

    ): Promise<void>;

    logout(): Promise<void>;

    checkAuthentication(): Promise<void>;

}

/**
 * Global Authentication Context.
 */

export const AuthContext = createContext<AuthContextType | undefined>(
    undefined
);

interface AuthProviderProps{
    children: ReactNode;
}


/**
 * Provides authentication state
 * to the entire application.
 */

export function AuthProvider({
    children,
}: AuthProviderProps){

    // currently logged in user
    const [currentUser, setCurrentUser] = useState<User|null>(null);

    // authentication state
    const [isAuthenticated,setIsAuthenticated] = useState(false);

    //used while checking authentication on application startup
    const [isLoading,setIsLoading] = useState(true);

     /**
     * Checks whether the browser
     * already has a valid JWT cookie.
     *
     * Called automatically
     * when the application starts.
     */

     async function checkAuthentication(): Promise<void>{

        try{
            const user= await authApi.getCurrentUser();
            setCurrentUser(user);
            setIsAuthenticated(true);
        }catch(error){
            /**
             * 401 is expected
             * if the user has not logged in.
             */
            setCurrentUser(null);
            setIsAuthenticated(false);
        }finally{
            setIsLoading(false);
        }

     }

     // Login workflow
     async function login(
        email: string,
        password: string
     ): Promise<void>{
        await authApi.login(email,password);
        await checkAuthentication();

     }

     //signup workflow
     async function signup(
        email: string,
        password: string
     ): Promise<void>{
        await authApi.signup(email,password);
     }

     //logout workflow
     async function logout(): Promise<void>{
        await authApi.logout();
        setCurrentUser(null);
        setIsAuthenticated(false);
     }

     // runs once when the application starts 
     useEffect(()=>{
        checkAuthentication();
     },[]);

     return(
        <AuthContext.Provider
        value={{
            currentUser,
            isAuthenticated,
            isLoading,
            login,
            signup,
            logout,
            checkAuthentication
        }}
        >
            {children}
        </AuthContext.Provider>
     );
}