import Card from "../../components/ui/Card";
import SignupForm from "./SignupForm";

export default function SignupPage() {

    return(

        <div className="flex min-h-screen items-center justify-center bg-slate-100 px-4">
            <Card className="w-full max-w-md">
                <div className="mb-8 text-center">

                    <h1 className="text-3xl font-bold text-slate-900">
                        AI Knowldege Assistant
                    </h1>

                    <p className="mt-2 text-sm text-slate-600">
                        Create your account.

                    </p>

                </div>

                <SignupForm/>

            </Card>

        </div>

    );

}