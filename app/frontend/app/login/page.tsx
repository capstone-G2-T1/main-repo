"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Eye, EyeOff, Zap, AlertCircle, ArrowLeft } from "lucide-react";
import { cn } from "@/lib/utils";
import { useLanguage } from "@/components/providers/LanguageProvider";
import { loginUser, ApiError } from "@/lib/api";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPass, setShowPass] = useState(false);
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState<{ email?: string; password?: string; general?: string }>({});
  const { language } = useLanguage();
  const isRTL = language === "ar";
  const router = useRouter();

  const validate = () => {
    const e: typeof errors = {};
    if (!email) e.email = isRTL ? "يرجى إدخال البريد الإلكتروني" : "Please enter your email";
    else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) e.email = isRTL ? "بريد إلكتروني غير صالح" : "Invalid email address";
    if (!password) e.password = isRTL ? "يرجى إدخال كلمة المرور" : "Please enter your password";
    else if (password.length < 6) e.password = isRTL ? "كلمة المرور قصيرة جداً (6 أحرف على الأقل)" : "Password too short (min 6 characters)";
    setErrors(e);
    return Object.keys(e).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate()) return;
    setLoading(true);
    setErrors({});
    try {
      await loginUser(email, password);
      router.push("/");
    } catch (error) {
      const message =
        error instanceof ApiError
          ? error.message
          : isRTL
            ? "تعذّر الاتصال بالخادم. يرجى المحاولة مرة أخرى."
            : "Could not reach the server. Please try again.";
      setErrors({ general: message });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-brand-black flex">
      <div className="hidden lg:flex lg:w-1/2 relative overflow-hidden items-center justify-center p-12">
        <div className="absolute inset-0 bg-gradient-to-br from-[#1a1a1a] to-[#0a0a0a]" />
        <div className="absolute inset-0 opacity-20" style={{ backgroundImage: "linear-gradient(rgba(255,255,255,0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.03) 1px, transparent 1px)", backgroundSize: "40px 40px" }} />
        <div className="absolute top-1/4 left-1/4 w-96 h-96 rounded-full opacity-15 blur-3xl" style={{ background: "#E31E2D" }} />
        <div className="relative z-10 text-center">
          <div className="w-20 h-20 bg-brand-red rounded-3xl flex items-center justify-center mx-auto mb-8 shadow-[0_0_50px_rgba(227,30,45,0.4)]">
            <span className="text-white font-black text-3xl">α</span>
          </div>
          <h2 className="text-4xl font-black text-white mb-4 leading-tight">Dalil<span className="text-brand-red">ak</span></h2>
          <p className={cn("text-white/40 text-base leading-relaxed max-w-xs mx-auto", isRTL ? "font-arabic" : "font-sans")}>
            {isRTL ? "دليلك الذكي لكتيبات السيارات الصينية" : "Your smart guide to Chinese vehicle manuals"}
          </p>
          <div className="mt-10 grid grid-cols-3 gap-4">
            {["BYD", "Geely", "VW"].map((b) => (
              <div key={b} className="px-3 py-2 rounded-xl bg-white/5 border border-white/5 text-white/30 text-xs font-medium text-center">{b}</div>
            ))}
          </div>
        </div>
      </div>

      <div className="flex-1 flex items-center justify-center p-6 sm:p-10">
        <div className="w-full max-w-md animate-fade-up animate-fill-both">
          <div className="flex items-center gap-2 mb-10 lg:hidden">
            <div className="w-8 h-8 bg-brand-red rounded-lg flex items-center justify-center"><span className="text-white font-black text-sm">α</span></div>
            <span className="font-black text-white text-lg">Dalil<span className="text-brand-red">ak</span></span>
          </div>

          <div className={cn("mb-8", isRTL ? "text-right" : "")}>
            <h1 className={cn("text-3xl font-black text-white mb-2", isRTL ? "font-arabic" : "font-sans")}>
              {isRTL ? "أهلاً بعودتك" : "Welcome Back"}
            </h1>
            <p className={cn("text-white/40 text-sm", isRTL ? "font-arabic" : "font-sans")}>
              {isRTL ? "سجّل دخولك للوصول إلى منصة دليلك" : "Sign in to access your Dalilak platform"}
            </p>
          </div>

          {errors.general && (
            <div className={cn("flex items-start gap-3 p-4 bg-red-500/10 border border-red-500/20 rounded-xl mb-5 animate-fade-in animate-fill-both", isRTL ? "flex-row-reverse" : "")}>
              <AlertCircle size={16} className="text-brand-red shrink-0 mt-0.5" />
              <p className={cn("text-sm text-brand-red", isRTL ? "font-arabic" : "font-sans")}>{errors.general}</p>
            </div>
          )}

          <form onSubmit={handleSubmit} noValidate className="space-y-4">
            <div>
              <label className={cn("block text-sm font-medium text-white/50 mb-1.5", isRTL ? "font-arabic text-right" : "font-sans")}>
                {isRTL ? "البريد الإلكتروني" : "Email Address"}
              </label>
              <input type="email" value={email} onChange={(e) => { setEmail(e.target.value); setErrors((p) => ({ ...p, email: undefined })); }}
                placeholder="example@email.com" dir="ltr" autoComplete="email"
                className={cn("w-full bg-white/5 border text-white placeholder:text-white/20 rounded-xl px-4 py-3 text-sm outline-none transition-all duration-200 text-left", errors.email ? "border-red-500/60 focus:border-red-500" : "border-white/10 focus:border-brand-red/60 focus:bg-white/8")} />
              {errors.email && <p className={cn("text-xs text-brand-red mt-1.5 flex items-center gap-1", isRTL ? "flex-row-reverse font-arabic" : "")}><AlertCircle size={11} /> {errors.email}</p>}
            </div>

            <div>
              <label className={cn("block text-sm font-medium text-white/50 mb-1.5", isRTL ? "font-arabic text-right" : "font-sans")}>
                {isRTL ? "كلمة المرور" : "Password"}
              </label>
              <div className="relative">
                <input type={showPass ? "text" : "password"} value={password} onChange={(e) => { setPassword(e.target.value); setErrors((p) => ({ ...p, password: undefined })); }}
                  placeholder="••••••••" dir="ltr" autoComplete="current-password"
                  className={cn("w-full bg-white/5 border text-white placeholder:text-white/20 rounded-xl px-4 py-3 pl-11 text-sm outline-none transition-all duration-200", errors.password ? "border-red-500/60 focus:border-red-500" : "border-white/10 focus:border-brand-red/60 focus:bg-white/8")} />
                <button type="button" onClick={() => setShowPass((v) => !v)} className="absolute left-3 top-1/2 -translate-y-1/2 text-white/30 hover:text-white/60 transition-colors" aria-label={showPass ? (isRTL ? "إخفاء" : "Hide") : (isRTL ? "إظهار" : "Show")}>
                  {showPass ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>
              {errors.password && <p className={cn("text-xs text-brand-red mt-1.5 flex items-center gap-1", isRTL ? "flex-row-reverse font-arabic" : "")}><AlertCircle size={11} /> {errors.password}</p>}
            </div>

            <div className={cn("flex", isRTL ? "justify-start" : "justify-end")}>
              <Link href="#" className={cn("text-xs text-brand-red hover:underline", isRTL ? "font-arabic" : "font-sans")}>
                {isRTL ? "نسيت كلمة المرور؟" : "Forgot Password?"}
              </Link>
            </div>

            <button type="submit" disabled={loading} className={cn("w-full py-3.5 rounded-xl text-sm font-semibold transition-all duration-200 flex items-center justify-center gap-2", loading ? "bg-brand-red/50 text-white/60 cursor-not-allowed" : "bg-brand-red text-white hover:bg-brand-red-dark shadow-[0_4px_20px_rgba(227,30,45,0.35)] hover:-translate-y-0.5 active:scale-[0.98]", isRTL ? "font-arabic" : "font-sans")}>
              {loading ? <><span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" /> {isRTL ? "جار تسجيل الدخول..." : "Signing in..."}</> : (isRTL ? "تسجيل الدخول" : "Sign In")}
            </button>
          </form>

          <p className={cn("text-center text-sm text-white/30 mt-6", isRTL ? "font-arabic" : "font-sans")}>
            {isRTL ? "ليس لديك حساب؟" : "Don't have an account?"}{" "}
            <Link href="/register" className="text-brand-red hover:underline font-semibold">{isRTL ? "إنشاء حساب جديد" : "Sign Up"}</Link>
          </p>

          <div className="mt-8">
            <Link href="/" className={cn("flex items-center justify-center gap-2 text-xs text-white/20 hover:text-white/40 transition-colors", isRTL ? "flex-row-reverse font-arabic" : "font-sans")}>
              <ArrowLeft size={12} className={isRTL ? "rotate-180" : ""} />
              {isRTL ? "العودة للرئيسية" : "Back to Home"}
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
