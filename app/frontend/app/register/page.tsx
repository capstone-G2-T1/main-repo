"use client";

import React, { useState } from "react";
import Link from "next/link";
import { Eye, EyeOff, Zap, AlertCircle, CheckCircle, ArrowLeft, User, Mail, Lock } from "lucide-react";
import { cn } from "@/lib/utils";
import { useLanguage } from "@/components/providers/LanguageProvider";
import { registerUser, ApiError } from "@/lib/api";

interface FormState {
  name: string;
  email: string;
  password: string;
  confirmPassword: string;
}

const PASSWORD_RULES = [
  { label: (r: boolean) => r ? "8 أحرف على الأقل" : "At least 8 characters", test: (p: string) => p.length >= 8 },
  { label: (r: boolean) => r ? "حرف كبير واحد على الأقل" : "At least one uppercase letter", test: (p: string) => /[A-Z]/.test(p) },
  { label: (r: boolean) => r ? "رقم واحد على الأقل" : "At least one number", test: (p: string) => /[0-9]/.test(p) },
];

export default function RegisterPage() {
  const [form, setForm] = useState<FormState>({ name: "", email: "", password: "", confirmPassword: "" });
  const [showPass, setShowPass] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [errors, setErrors] = useState<{ name?: string; email?: string; password?: string; confirmPassword?: string; general?: string }>({});
  const { language } = useLanguage();
  const isRTL = language === "ar";

  const set = (field: keyof FormState) => (e: React.ChangeEvent<HTMLInputElement>) => {
    setForm((prev) => ({ ...prev, [field]: e.target.value }));
    setErrors((prev) => ({ ...prev, [field]: undefined }));
  };

  const validate = (): boolean => {
    const e: typeof errors = {};
    if (!form.name.trim()) e.name = isRTL ? "يرجى إدخال الاسم الكامل" : "Please enter your full name";
    else if (form.name.trim().length < 2) e.name = isRTL ? "الاسم قصير جداً" : "Name is too short";
    if (!form.email) e.email = isRTL ? "يرجى إدخال البريد الإلكتروني" : "Please enter your email";
    else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) e.email = isRTL ? "بريد إلكتروني غير صالح" : "Invalid email address";
    if (!form.password) e.password = isRTL ? "يرجى إدخال كلمة المرور" : "Please enter a password";
    else if (form.password.length < 8) e.password = isRTL ? "كلمة المرور قصيرة جداً (8 أحرف على الأقل)" : "Password too short (min 8 characters)";
    if (!form.confirmPassword) e.confirmPassword = isRTL ? "يرجى تأكيد كلمة المرور" : "Please confirm your password";
    else if (form.password !== form.confirmPassword) e.confirmPassword = isRTL ? "كلمتا المرور غير متطابقتين" : "Passwords do not match";
    setErrors(e);
    return Object.keys(e).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate()) return;
    setLoading(true);
    setErrors({});
    try {
      await registerUser(form.email, form.password);
      setSuccess(true);
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

  if (success) {
    return (
      <div className="min-h-screen bg-brand-black flex items-center justify-center p-6">
        <div className="w-full max-w-md text-center animate-scale-in animate-fill-both">
          <div className="w-20 h-20 rounded-full bg-green-500/15 border border-green-500/30 flex items-center justify-center mx-auto mb-6">
            <CheckCircle size={36} className="text-green-400" />
          </div>
          <h2 className={cn("text-3xl font-black text-white mb-3", isRTL ? "font-arabic" : "font-sans")}>
            {isRTL ? "تم إنشاء الحساب!" : "Account Created!"}
          </h2>
          <p className={cn("text-white/40 text-sm mb-8", isRTL ? "font-arabic" : "font-sans")}>
            {isRTL ? `مرحباً ${form.name}! تم إنشاء حسابك بنجاح. يمكنك الآن تسجيل الدخول.` : `Welcome ${form.name}! Your account has been created. You can now sign in.`}
          </p>
          <Link href="/login" className="inline-flex items-center gap-2 bg-brand-red text-white px-8 py-3.5 rounded-xl font-semibold text-sm hover:bg-brand-red-dark transition-all shadow-[0_4px_20px_rgba(227,30,45,0.35)]">
            {isRTL ? "تسجيل الدخول" : "Sign In"}
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-brand-black flex">
      <div className="hidden lg:flex lg:w-5/12 relative overflow-hidden items-center justify-center p-12 flex-col">
        <div className="absolute inset-0 bg-gradient-to-br from-[#1a1a1a] to-[#0a0a0a]" />
        <div className="absolute inset-0 opacity-[0.07]" style={{ backgroundImage: "linear-gradient(rgba(255,255,255,0.08) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.08) 1px, transparent 1px)", backgroundSize: "36px 36px" }} />
        <div className="absolute bottom-0 right-0 w-80 h-80 rounded-full opacity-20 blur-3xl" style={{ background: "#E31E2D", transform: "translate(40%, 40%)" }} />
        <div className="relative z-10 w-full max-w-xs">
          <div className="flex items-center gap-3 mb-12">
            <div className="w-10 h-10 bg-brand-red rounded-xl flex items-center justify-center shadow-[0_0_30px_rgba(227,30,45,0.4)]">
              <span className="text-white font-black text-xl">α</span>
            </div>
            <span className="text-2xl font-black text-white">Dalil<span className="text-brand-red">ak</span></span>
          </div>
          <h2 className={cn("text-3xl font-black text-white mb-4 leading-tight", isRTL ? "font-arabic" : "font-sans")}>
            {isRTL ? "انضم إلى" : "Join"} <br /><span className="text-brand-red">Dalilak</span> {isRTL ? "اليوم" : "Today"}
          </h2>
          <p className={cn("text-white/35 text-sm leading-relaxed mb-10", isRTL ? "font-arabic" : "font-sans")}>
            {isRTL ? "أنشئ حسابك واحصل على وصول كامل إلى مساعد كتيبات السيارات الصينية" : "Create your account and get full access to the Chinese vehicle manual assistant"}
          </p>
          <div className="space-y-4">
            {[isRTL ? "استعراض جميع السيارات" : "Browse all vehicles", isRTL ? "مقارنة المواصفات" : "Compare specifications", isRTL ? "حفظ المفضلة" : "Save favorites", isRTL ? "مجاني تماماً" : "Completely free"].map((b) => (
              <div key={b} className={cn("flex items-center gap-3", isRTL ? "flex-row-reverse" : "")}>
                <div className="w-5 h-5 rounded-full bg-brand-red/20 border border-brand-red/40 flex items-center justify-center shrink-0">
                  <CheckCircle size={11} className="text-brand-red" />
                </div>
                <span className={cn("text-white/50 text-sm", isRTL ? "font-arabic" : "font-sans")}>{b}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="flex-1 flex items-center justify-center p-6 sm:p-10 overflow-y-auto">
        <div className="w-full max-w-md animate-fade-up animate-fill-both">
          <div className="flex items-center gap-2 mb-8 lg:hidden">
            <div className="w-8 h-8 bg-brand-red rounded-lg flex items-center justify-center"><span className="text-white font-black text-sm">α</span></div>
            <span className="font-black text-white text-lg">Dalil<span className="text-brand-red">ak</span></span>
          </div>

          <div className={cn("mb-8", isRTL ? "text-right" : "")}>
            <h1 className={cn("text-3xl font-black text-white mb-1.5", isRTL ? "font-arabic" : "font-sans")}>
              {isRTL ? "إنشاء حساب جديد" : "Create Account"}
            </h1>
            <p className={cn("text-white/35 text-sm", isRTL ? "font-arabic" : "font-sans")}>
              {isRTL ? "أدخل بياناتك لإنشاء حسابك مجاناً" : "Enter your details to create your free account"}
            </p>
          </div>

          {errors.general && (
            <div className={cn("flex items-start gap-3 p-4 bg-red-500/10 border border-red-500/20 rounded-xl mb-5 animate-fade-in animate-fill-both", isRTL ? "flex-row-reverse" : "")}>
              <AlertCircle size={16} className="text-brand-red shrink-0 mt-0.5" />
              <p className="text-sm text-brand-red">{errors.general}</p>
            </div>
          )}

          <form onSubmit={handleSubmit} noValidate className="space-y-4">
            <div>
              <label className={cn("block text-sm font-medium text-white/50 mb-1.5", isRTL ? "font-arabic text-right" : "font-sans")}>
                {isRTL ? "الاسم الكامل" : "Full Name"}
              </label>
              <div className="relative">
                <User size={15} className={cn("absolute top-1/2 -translate-y-1/2 text-white/25 pointer-events-none", isRTL ? "right-3.5" : "left-3.5")} />
                <input type="text" value={form.name} onChange={set("name")} placeholder={isRTL ? "محمد أحمد" : "John Doe"} dir={isRTL ? "rtl" : "ltr"} autoComplete="name"
                  className={cn("w-full bg-white/5 border text-white placeholder:text-white/20 rounded-xl px-4 py-3 text-sm outline-none transition-all duration-200", isRTL ? "pr-10 text-right font-arabic" : "pl-10 text-left font-sans", errors.name ? "border-red-500/60 focus:border-red-500" : "border-white/10 focus:border-brand-red/60 focus:bg-white/8")} />
              </div>
              {errors.name && <p className={cn("text-xs text-brand-red mt-1.5 flex items-center gap-1", isRTL ? "flex-row-reverse font-arabic" : "")}><AlertCircle size={11} /> {errors.name}</p>}
            </div>

            <div>
              <label className={cn("block text-sm font-medium text-white/50 mb-1.5", isRTL ? "font-arabic text-right" : "font-sans")}>
                {isRTL ? "البريد الإلكتروني" : "Email Address"}
              </label>
              <div className="relative">
                <Mail size={15} className={cn("absolute top-1/2 -translate-y-1/2 text-white/25 pointer-events-none", isRTL ? "right-3.5" : "left-3.5")} />
                <input type="email" value={form.email} onChange={set("email")} placeholder="example@email.com" dir="ltr" autoComplete="email"
                  className={cn("w-full bg-white/5 border text-white placeholder:text-white/20 rounded-xl px-4 py-3 text-sm outline-none transition-all duration-200 text-left", isRTL ? "pr-10" : "pl-10", errors.email ? "border-red-500/60 focus:border-red-500" : "border-white/10 focus:border-brand-red/60 focus:bg-white/8")} />
              </div>
              {errors.email && <p className={cn("text-xs text-brand-red mt-1.5 flex items-center gap-1", isRTL ? "flex-row-reverse font-arabic" : "")}><AlertCircle size={11} /> {errors.email}</p>}
            </div>

            <div>
              <label className={cn("block text-sm font-medium text-white/50 mb-1.5", isRTL ? "font-arabic text-right" : "font-sans")}>
                {isRTL ? "كلمة المرور" : "Password"}
              </label>
              <div className="relative">
                <Lock size={15} className={cn("absolute top-1/2 -translate-y-1/2 text-white/25 pointer-events-none", isRTL ? "right-3.5" : "left-3.5")} />
                <input type={showPass ? "text" : "password"} value={form.password} onChange={set("password")} placeholder="••••••••" dir="ltr" autoComplete="new-password"
                  className={cn("w-full bg-white/5 border text-white placeholder:text-white/20 rounded-xl px-4 py-3 text-sm outline-none transition-all duration-200", isRTL ? "pr-10 pl-11" : "pl-10 pr-11", errors.password ? "border-red-500/60 focus:border-red-500" : "border-white/10 focus:border-brand-red/60 focus:bg-white/8")} />
                <button type="button" onClick={() => setShowPass((v) => !v)} className={cn("absolute top-1/2 -translate-y-1/2 text-white/25 hover:text-white/50 transition-colors", isRTL ? "left-3.5" : "right-3.5")} aria-label={showPass ? (isRTL ? "إخفاء" : "Hide") : (isRTL ? "إظهار" : "Show")}>
                  {showPass ? <EyeOff size={15} /> : <Eye size={15} />}
                </button>
              </div>
              {errors.password && <p className={cn("text-xs text-brand-red mt-1.5 flex items-center gap-1", isRTL ? "flex-row-reverse font-arabic" : "")}><AlertCircle size={11} /> {errors.password}</p>}
              {form.password && (
                <div className="mt-2 space-y-1.5">
                  {PASSWORD_RULES.map((rule) => {
                    const ok = rule.test(form.password);
                    return (
                      <div key={rule.label(isRTL)} className={cn("flex items-center gap-2", isRTL ? "flex-row-reverse" : "")}>
                        <div className={cn("w-3.5 h-3.5 rounded-full flex items-center justify-center shrink-0 transition-colors duration-200", ok ? "bg-green-500/20 border border-green-500/40" : "bg-white/5 border border-white/10")}>
                          {ok && <CheckCircle size={8} className="text-green-400" />}
                        </div>
                        <span className={cn("text-[11px] transition-colors duration-200", ok ? "text-green-400" : "text-white/25", isRTL ? "font-arabic" : "font-sans")}>
                          {rule.label(isRTL)}
                        </span>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>

            <div>
              <label className={cn("block text-sm font-medium text-white/50 mb-1.5", isRTL ? "font-arabic text-right" : "font-sans")}>
                {isRTL ? "تأكيد كلمة المرور" : "Confirm Password"}
              </label>
              <div className="relative">
                <Lock size={15} className={cn("absolute top-1/2 -translate-y-1/2 text-white/25 pointer-events-none", isRTL ? "right-3.5" : "left-3.5")} />
                <input type={showConfirm ? "text" : "password"} value={form.confirmPassword} onChange={set("confirmPassword")} placeholder="••••••••" dir="ltr" autoComplete="new-password"
                  className={cn("w-full bg-white/5 border text-white placeholder:text-white/20 rounded-xl px-4 py-3 text-sm outline-none transition-all duration-200", isRTL ? "pr-10 pl-11" : "pl-10 pr-11", errors.confirmPassword ? "border-red-500/60 focus:border-red-500" : form.confirmPassword && form.password === form.confirmPassword ? "border-green-500/40 focus:border-green-500/60" : "border-white/10 focus:border-brand-red/60 focus:bg-white/8")} />
                <button type="button" onClick={() => setShowConfirm((v) => !v)} className={cn("absolute top-1/2 -translate-y-1/2 text-white/25 hover:text-white/50 transition-colors", isRTL ? "left-3.5" : "right-3.5")} aria-label={showConfirm ? (isRTL ? "إخفاء" : "Hide") : (isRTL ? "إظهار" : "Show")}>
                  {showConfirm ? <EyeOff size={15} /> : <Eye size={15} />}
                </button>
              </div>
              {errors.confirmPassword && <p className={cn("text-xs text-brand-red mt-1.5 flex items-center gap-1", isRTL ? "flex-row-reverse font-arabic" : "")}><AlertCircle size={11} /> {errors.confirmPassword}</p>}
              {form.confirmPassword && form.password === form.confirmPassword && !errors.confirmPassword && (
                <p className={cn("text-xs text-green-400 mt-1.5 flex items-center gap-1", isRTL ? "flex-row-reverse font-arabic" : "")}>
                  <CheckCircle size={11} /> {isRTL ? "كلمتا المرور متطابقتان" : "Passwords match"}
                </p>
              )}
            </div>

            <p className={cn("text-xs text-white/25 leading-relaxed", isRTL ? "font-arabic text-right" : "font-sans")}>
              {isRTL ? "بإنشاء حساب، أنت توافق على" : "By creating an account, you agree to our"}{" "}
              <Link href="#" className="text-brand-red hover:underline">{isRTL ? "شروط الاستخدام" : "Terms of Service"}</Link>{" "}
              {isRTL ? "و" : "and"}{" "}
              <Link href="#" className="text-brand-red hover:underline">{isRTL ? "سياسة الخصوصية" : "Privacy Policy"}</Link>
            </p>

            <button type="submit" disabled={loading} className={cn("w-full py-3.5 rounded-xl text-sm font-semibold transition-all duration-200 flex items-center justify-center gap-2", loading ? "bg-brand-red/50 text-white/60 cursor-not-allowed" : "bg-brand-red text-white hover:bg-brand-red-dark shadow-[0_4px_20px_rgba(227,30,45,0.35)] hover:-translate-y-0.5 active:scale-[0.98]", isRTL ? "font-arabic" : "font-sans")}>
              {loading ? <><span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" /> {isRTL ? "جار إنشاء الحساب..." : "Creating account..."}</> : (isRTL ? "إنشاء الحساب" : "Create Account")}
            </button>
          </form>

          <p className={cn("text-center text-sm text-white/30 mt-6", isRTL ? "font-arabic" : "font-sans")}>
            {isRTL ? "لديك حساب بالفعل؟" : "Already have an account?"}{" "}
            <Link href="/login" className="text-brand-red hover:underline font-semibold">{isRTL ? "تسجيل الدخول" : "Sign In"}</Link>
          </p>

          <div className="mt-6">
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
