import { useNavigate } from "react-router-dom";

import Button from "../ui/Button";
import useAuth from "../../hooks/useAuth";

/**
 * Application Header
 *
 * Responsible for:
 * - Showing current user
 * - Logout button
 *
 * No page-specific logic.
 */


export default function Header(){

    const navigate= useNavigate();

    const{ currentUser, logout } = useAuth();

    async function handleLogout(){

        try{
            await logout();
            navigate("/login");
        }catch(error){
            console.error("Logout failed",error);
        }

    }

    return(
        <header className="border-b bg-white">

            <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-6">

                <div>

                    <h1 className="text-xl font-bold text-slate-900">

                        AI Knowledge Assistant

                    </h1>

                </div>

                <div className="flex items-center gap-4">

                    <span className="text-sm text-slate-600">

                        {currentUser?.email}

                    </span>

                    <Button
                        variant="secondary"
                        onClick={handleLogout}
                    >

                        Logout

                    </Button>

                </div>

            </div>

        </header>
    );

}



