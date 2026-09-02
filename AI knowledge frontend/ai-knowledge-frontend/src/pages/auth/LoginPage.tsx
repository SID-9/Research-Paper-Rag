import Card from "../../components/ui/Card";
import LoginForm from "./LoginForm";

/**
 * Login Page
 *
 * Responsible only for page layout.
 *
 * Business logic lives inside LoginForm.
 */


export default function LoginPage(){

    return(

        <div className="flex min-h-screen items-center justify-center bg-slate-100 px-4">
            <Card className="w-full max-w-md">

                <div className="mb-8 text-center">
                    <h1 className="text-3xl font-bold text-slate-900">
                        AI Knowledge Assistant
                    </h1>

                    <p className="mt-2 text-sm text-slate-600">
                        Sign in to continue.
                    </p>

                </div>

                <LoginForm/>

            </Card>

        </div>

    );

}

