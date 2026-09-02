import { useState } from "react";
import { useNavigate } from "react-router-dom";

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";

import Button from "../../components/ui/Button";
import Input from "../../components/ui/Input";

import { loginSchema, type LoginFormData } from "../../schemas/authSchema";
import useAuth from "../../hooks/useAuth";

/**
 * Login Form
 *
 * Handles:
 * - Form state
 * - Validation
 * - Calling authentication
 * - Navigation
 *
 * Does NOT handle layout.
 */

export default function LoginForm(){

    const navigate = useNavigate();
    const { login } = useAuth();
    const [serverError, setServerError] = useState("");

    const{
        register,
        handleSubmit,
        formState: {
            errors,
            isSubmitting
        }
    } = useForm<LoginFormData>({
        resolver: zodResolver(loginSchema),
        defaultValues: {
            email: "",
            password: ""
        }
    });

    // called only if validation succeeds
    async function onSubmit(data: LoginFormData){
        setServerError("");
        try{
            await login(data.email,data.password);
            navigate("/dashboard");
        }catch(error){
            setServerError(
                "Invalid email or password"
            );
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
                autoComplete="current-password"
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
                Login
            </Button>

        </form>
    );

}





