import { useState } from "react";
import { useNavigate } from "react-router-dom";

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";

import Button from "../../components/ui/Button";
import Input from "../../components/ui/Input";

import { type SignupFormData, signupSchema } from "../../schemas/authSchema";
import useAuth from "../../hooks/useAuth";


export default function SignupForm(){

    const navigate = useNavigate();
    const { signup } = useAuth();
    const [serverError, setServerError] = useState("");

    const {
        register,
        handleSubmit,
        formState: {
            errors,
            isSubmitting
        }
    } = useForm<SignupFormData>({
        resolver: zodResolver(signupSchema),
        defaultValues: {
            email: "",
            password: ""
        }
    });

    async function onSubmit(data: SignupFormData) {

        setServerError("");
        try{
            await signup(data.email,data.password);
            navigate("/login");

        }catch(error){
            setServerError("Unable to create account.");
            console.error(error);
        }
        
    }

    return(
        <form 
            onSubmit={handleSubmit(onSubmit)}
            className="space-y-5"
        >
            <Input
                label="Email"
                type="email"
                placeholder="Enter your email"
                autoComplete="email"
                error={errors.email?.message}
                {...register("email")}
            />

            <Input
                label="Password"
                type="password"
                placeholder="Enter your password"
                autoComplete="password"
                error={errors.password?.message}
                {...register("password")}
            />

            {serverError && (
                <p className="text-sm text-red-600">
                    {serverError}
                </p>
            )}

            <Button 
                type="submit"
                className="w-full"
                isLoading={isSubmitting}
            >
                Create Account
            </Button>

        </form>
    );

}


