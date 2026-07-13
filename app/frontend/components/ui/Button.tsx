import React from "react";
import { cn } from "@/lib/utils";
import { Loader2 } from "lucide-react";

export type ButtonVariant = "primary" | "secondary" | "outline" | "ghost" | "danger";
export type ButtonSize = "sm" | "md" | "lg";

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  size?: ButtonSize;
  loading?: boolean;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
}

const variantClasses: Record<ButtonVariant, string> = {
  primary:
    "bg-brand-red text-white hover:bg-brand-red-dark shadow-[0_4px_14px_rgba(227,30,45,0.3)] hover:shadow-[0_6px_20px_rgba(227,30,45,0.4)] hover:-translate-y-0.5 active:translate-y-0",
  secondary:
    "bg-white/5 text-white hover:bg-white/10 border border-white/10 hover:border-white/20 hover:-translate-y-0.5 active:translate-y-0",
  outline:
    "border-2 border-white/15 text-white hover:border-brand-red hover:text-brand-red hover:-translate-y-0.5 active:translate-y-0",
  ghost:
    "text-white/60 hover:bg-white/5 hover:text-white",
  danger:
    "bg-red-500/10 text-brand-red hover:bg-red-500/20 border border-red-500/20",
};

const sizeClasses: Record<ButtonSize, string> = {
  sm: "px-4 py-2 text-xs gap-1.5 rounded-lg",
  md: "px-6 py-3 text-sm gap-2 rounded-lg",
  lg: "px-8 py-4 text-base gap-2.5 rounded-xl",
};

export function Button({
  variant = "primary",
  size = "md",
  loading = false,
  leftIcon,
  rightIcon,
  children,
  className,
  disabled,
  ...props
}: ButtonProps) {
  return (
    <button
      className={cn(
        "inline-flex items-center justify-center font-semibold transition-all duration-200 cursor-pointer select-none active:scale-[0.97] disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none disabled:shadow-none",
        variantClasses[variant],
        sizeClasses[size],
        className
      )}
      disabled={disabled || loading}
      {...props}
    >
      {loading ? (
        <Loader2 size={16} className="animate-spin shrink-0" />
      ) : leftIcon ? (
        <span className="shrink-0">{leftIcon}</span>
      ) : null}
      {children}
      {!loading && rightIcon && (
        <span className="shrink-0">{rightIcon}</span>
      )}
    </button>
  );
}
