import React from "react";
import { cn } from "@/lib/utils";
import { useLanguage } from "@/components/providers/LanguageProvider";

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  hint?: string;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
}

export function Input({
  label,
  error,
  hint,
  leftIcon,
  rightIcon,
  className,
  id,
  ...props
}: InputProps) {
  const { language } = useLanguage();
  const isRTL = language === "ar";
  const inputId = id ?? label?.toLowerCase().replace(/\s+/g, "-");

  return (
    <div className="w-full">
      {label && (
        <label
          htmlFor={inputId}
          className={cn("label", isRTL && "font-arabic text-right")}
        >
          {label}
        </label>
      )}
      <div className="relative">
        {leftIcon && (
          <span className={cn(
            "absolute top-1/2 -translate-y-1/2 text-white/30 pointer-events-none",
            isRTL ? "right-3" : "left-3"
          )}>
            {leftIcon}
          </span>
        )}
        <input
          id={inputId}
          className={cn(
            "input-base",
            isRTL && "input-base-arabic",
            leftIcon && (isRTL ? "pr-10" : "pl-10"),
            rightIcon && (isRTL ? "pl-10" : "pr-10"),
            error && "border-brand-red focus:border-brand-red",
            className
          )}
          dir={isRTL ? "rtl" : "ltr"}
          {...props}
        />
        {rightIcon && (
          <span className={cn(
            "absolute top-1/2 -translate-y-1/2 text-white/30",
            isRTL ? "left-3" : "right-3"
          )}>
            {rightIcon}
          </span>
        )}
      </div>
      {error && (
        <p className={cn("error-text", isRTL && "justify-end")} role="alert">
          <span>⚠</span> {error}
        </p>
      )}
      {hint && !error && (
        <p className={cn(
          "text-xs text-white/30 mt-1.5",
          isRTL && "font-arabic text-right"
        )}>{hint}</p>
      )}
    </div>
  );
}

interface TextareaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  label?: string;
  error?: string;
  hint?: string;
}

export function Textarea({
  label,
  error,
  hint,
  className,
  id,
  ...props
}: TextareaProps) {
  const { language } = useLanguage();
  const isRTL = language === "ar";
  const inputId = id ?? label?.toLowerCase().replace(/\s+/g, "-");

  return (
    <div className="w-full">
      {label && (
        <label
          htmlFor={inputId}
          className={cn("label", isRTL && "font-arabic text-right")}
        >
          {label}
        </label>
      )}
      <textarea
        id={inputId}
        className={cn(
          "input-base resize-none",
          isRTL && "input-base-arabic",
          error && "border-brand-red",
          className
        )}
        dir={isRTL ? "rtl" : "ltr"}
        {...props}
      />
      {error && (
        <p className={cn("error-text", isRTL && "justify-end")} role="alert">
          <span>⚠</span> {error}
        </p>
      )}
      {hint && !error && (
        <p className={cn(
          "text-xs text-white/30 mt-1.5",
          isRTL && "font-arabic text-right"
        )}>{hint}</p>
      )}
    </div>
  );
}
