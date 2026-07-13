"use client";

import Link from "next/link";
import { Globe, LogIn } from "lucide-react";
import { cn } from "@/lib/utils";
import { useLanguage } from "@/components/providers/LanguageProvider";

function WheelLogo({ className = "" }: { className?: string }) {
  return (
    <svg viewBox="0 0 64 64" aria-hidden="true" className={className} fill="none">
      <circle cx="32" cy="32" r="23" stroke="currentColor" strokeWidth="5" />
      <circle cx="32" cy="32" r="7" stroke="currentColor" strokeWidth="4" />
      <path d="M32 9v16M32 39v16M9 32h16M39 32h16M16 16l11 11M37 37l11 11M48 16 37 27M27 37 16 48" stroke="currentColor" strokeWidth="4" strokeLinecap="round" />
    </svg>
  );
}

export function Navbar() {
  const { language, toggleLanguage } = useLanguage();
  const isRTL = language === "ar";

  return (
    <header className="fixed inset-x-0 top-0 z-40 border-b border-white/5 bg-black/45 py-4 backdrop-blur-xl">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-4 sm:px-6">
        <Link href="/" className="group flex items-center gap-2.5" aria-label="Dalilak">
          <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-brand-red text-white shadow-[0_0_24px_rgba(227,30,45,0.35)] transition-transform group-hover:rotate-12 group-hover:scale-105">
            <WheelLogo className="h-6 w-6" />
          </span>
          <span className="text-lg font-black tracking-tight text-white">
            Dalil<span className="text-brand-red">ak</span>
          </span>
        </Link>

        <div className="flex items-center gap-2">
          <button
            onClick={toggleLanguage}
            className={cn(
              "flex items-center gap-1.5 rounded-lg px-3 py-2 text-sm font-medium text-white/60 transition hover:bg-white/5 hover:text-white",
              isRTL && "font-arabic"
            )}
            aria-label={isRTL ? "تبديل اللغة" : "Toggle language"}
          >
            <Globe size={15} />
            <span className="text-xs font-semibold">{isRTL ? "AR" : "EN"}</span>
          </button>

          <Link
            href="/login"
            className={cn(
              "flex items-center gap-2 rounded-lg bg-brand-red px-4 py-2.5 text-sm font-semibold text-white shadow-[0_4px_18px_rgba(227,30,45,0.3)] transition hover:-translate-y-0.5 hover:bg-brand-red-dark",
              isRTL && "font-arabic"
            )}
          >
            <LogIn size={15} />
            {isRTL ? "تسجيل الدخول" : "Login"}
          </Link>
        </div>
      </div>
    </header>
  );
}
