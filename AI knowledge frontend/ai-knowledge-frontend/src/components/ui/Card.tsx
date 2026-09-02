import clsx from "clsx";
import type { HTMLAttributes, ReactNode } from "react";

/**
 * Props for the reusable Card component.
 *
 * Extends the native HTML div attributes.
 */

interface CardProps extends HTMLAttributes<HTMLDivElement>{

    children: ReactNode;

}

/**
 * Reusable Card Component
 *
 * Used to wrap forms, content sections,
 * upload panels, chat containers, etc.
 */

export default function Card({
    children,
    className,
    ...props 
}: CardProps){

    return(
        <div
            className={clsx(
                "rounded-xl border border-slate-200 bg-white p-6 shadow-sm",
                className
            )}
            {...props}
        >
            {children}
        </div>
    );

}


