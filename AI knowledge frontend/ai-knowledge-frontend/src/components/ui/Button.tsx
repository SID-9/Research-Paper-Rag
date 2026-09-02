import clsx from "clsx";
import type { ButtonHTMLAttributes,ReactNode } from "react";

// AVAILABLE FRO BUTTON STYLES

type ButtonVariant = "primary" | "secondary" | "danger";

/**
 * Props accepted by our reusable Button component.
 *
 * We extend the native HTML button attributes
 * so our component automatically supports:
 *
 * - onClick
 * - disabled
 * - type
 * - autoFocus
 * - title
 * - aria-label
 * - ...and many more.
 */

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement>{
    children: ReactNode;
    variant?: ButtonVariant;
    isLoading?: boolean;
}

/**
 * Reusable Button Component
 *
 * Used throughout the application.
 */

export default function Button({
    children,
    variant="primary",
    isLoading=false,
    className,
    disabled,
    ...props 

}: ButtonProps){

    // tailwind css for each variant
    const variants = {
        primary: 
        "bg-slate-900 text-white hover:bg-slate-800",

        secondary:
            "bg-slate-200 text-slate-900 hover:bg-slate-300",

        danger:
            "bg-red-600 text-white hover:bg-red-700",
    };

    return(
        <button 
        className={clsx(
            // base styles are shared for every button 
                "inline-flex items-center justify-center rounded-lg px-4 py-2 text-sm font-medium transition-colors duration-200",

                // variatn styles
                variants[variant],

                // disabled styles
                (disabled||isLoading)&& 
                "cursor-not-allowed opacity-60",

                // allow additionalstyling from parent
                className

        )}
        disabled={disabled || isLoading}
        {...props}
        >

            {isLoading ? "Loading..." : children}
        </button>
    );

}


