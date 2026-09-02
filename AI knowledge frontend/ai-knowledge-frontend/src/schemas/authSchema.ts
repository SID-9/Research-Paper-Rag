import { z } from "zod";

/**
 * Login validation schema.
 *
 * Equivalent to Spring Boot's
 * LoginRequest DTO validation.
 */

export const loginSchema  = z.object({
    email: z
    .string()
    .trim()
    .min(1,"Email is required")
    .email("Pleaes enter a valid email address"),

    password: z
    .string()
    .trim()
    .min(1,"password is required")

});

/**
 * Signup validation schema.
 *
 * Currently identical to login,
 * but kept separate because
 * signup rules usually grow.
 */


export const signupSchema = z.object({
    email: z
    .string()
    .trim()
    .min(1,"email is required.")
    .email("Please enter a valid email."),

    password:z 
    .string()
    .trim()
    .min(8,"Password must contain atleast 8 characters.")


});

/**
 * Types automatically inferred
 * from the schemas.
 * so its like a DTO automatically being created for us.
 *
 * This prevents us from manually
 * writing interfaces liek we wrote in auth.ts for login request etc.
 * 
 
Instead of writing

interface LoginFormData{
    email:string;
    password:string;
}

we simply say

type LoginFormData =
    z.infer<typeof loginSchema>;

One source of truth.

That is a huge production concept.
 */


export type LoginFormData = z.infer<typeof loginSchema>;

export type SignupFormData = z.infer<typeof signupSchema>;