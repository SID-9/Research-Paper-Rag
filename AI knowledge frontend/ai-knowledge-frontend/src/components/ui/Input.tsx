import clsx from "clsx";

import type { InputHTMLAttributes } from "react";

/**
 * Props accepted by the reusable Input component.
 *
 * Extends all native HTML input attributes.
 */

interface InputProps extends InputHTMLAttributes<HTMLInputElement>{

    // label dispplayed above the input.
    label: string;

    // original validation error
    error?: string
}


// reusable input component
export default function Input({
    label,
    error,
    className,
    id,
    ...props 
}: InputProps){
    /**
     * Use the provided id if available.
     * Otherwise fall back to the input name.
     */

    const inputId = id ?? props.name;

    return(
        <div className="flex flex-col gap2">
            <label 
                htmlFor={inputId}
                className="text-sm font-medium text-slate-700"
            >
                {label}

            </label>

            <input 
            id={inputId}
                className={clsx(
                    "rounded-lg border border-slate-300 px-4 py-2 outline-none transition-colors",
                    "focus:border-slate-900",
                    "disabled:cursor-not-allowed disabled:bg-slate-100",
                    error && "border-red-500",
                    className
                )}
                {...props}
            
            />

            {error && (
                <p className="text-sm text-red-600">
                    {error}
                </p>
            )}


        </div>
    );


}


