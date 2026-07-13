"use client";

import React, { createContext, useContext, useState, useEffect, ReactNode } from "react";

type Language = "en" | "ar";

interface LanguageContextType {
  language: Language;
  setLanguage: (lang: Language) => void;
  toggleLanguage: () => void;
  dir: "ltr" | "rtl";
  t: (key: string) => string;
}

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

const translations: Record<Language, Record<string, string>> = {
  en: {
    "nav.home": "Home",
    "nav.brands": "Brands",
    "nav.vehicles": "Vehicles",
    "nav.chat": "Ask AI",
    "nav.login": "Login",
    "nav.register": "Sign Up",
    "nav.logout": "Logout",
    "home.hero.title": "The Smart Chinese Car Guide",
    "home.hero.subtitle": "Ask questions and get grounded answers from your Chinese vehicle's manual",
    "home.hero.cta": "Explore Vehicles",
    "home.hero.secondary": "Learn More",
    "home.brands.title": "Featured Brands",
    "home.brands.subtitle": "Discover our supported Chinese vehicle brands",
    "home.features.title": "Why Dalilak?",
    "home.features.subtitle": "The ultimate assistant for Chinese vehicle manuals",
    "brands.title": "All Brands",
    "brands.subtitle": "Explore our complete lineup of Chinese vehicle brands",
    "chat.title": "Ask Dalilak AI",
    "chat.subtitle": "Get instant answers about any vehicle",
    "chat.placeholder": "Ask about range, specs, features...",
    "chat.send": "Send",
    "auth.login.title": "Welcome Back",
    "auth.login.subtitle": "Sign in to your Dalilak account",
    "auth.login.button": "Sign In",
    "auth.login.register": "Don't have an account?",
    "auth.register.title": "Create Account",
    "auth.register.subtitle": "Join Dalilak today",
    "auth.register.button": "Create Account",
    "auth.register.login": "Already have an account?",
    "common.learnMore": "Learn More",
    "common.viewDetails": "View Details",
    "common.range": "Range",
    "common.battery": "Battery",
    "common.power": "Power",
    "common.acceleration": "Acceleration",
    "common.drivetrain": "Drivetrain",
    "common.seating": "Seating",
    "common.dimensions": "Dimensions",
    "common.year": "Year",
    "common.search": "Search",
    "common.loading": "Loading...",
    "common.error": "Something went wrong",
  },
  ar: {
    "nav.home": "الرئيسية",
    "nav.brands": "العلامات",
    "nav.vehicles": "السيارات",
    "nav.chat": "اسأل الذكاء",
    "nav.login": "تسجيل الدخول",
    "nav.register": "إنشاء حساب",
    "nav.logout": "تسجيل الخروج",
    "home.hero.title": "الدليل الذكي لكتيبات السيارات الصينية",
    "home.hero.subtitle": "اسأل واحصل على إجابات موثقة من كتيب سيارتك الصينية",
    "home.hero.cta": "استعراض السيارات",
    "home.hero.secondary": "اعرف المزيد",
    "home.brands.title": "العلامات المميزة",
    "home.brands.subtitle": "اكتشف العلامات الصينية المدعومة لدينا",
    "home.features.title": "لماذا دليلك؟",
    "home.features.subtitle": "المساعد الأمثل لكتيبات السيارات الصينية",
    "brands.title": "جميع العلامات",
    "brands.subtitle": "استكشف مجموعتنا الكاملة من علامات السيارات الصينية",
    "chat.title": "اسأل دليلك الذكي",
    "chat.subtitle": "احصل على إجابات فورية عن أي سيارة",
    "chat.placeholder": "اسأل عن المدى، المواصفات، المميزات...",
    "chat.send": "إرسال",
    "auth.login.title": "أهلاً بعودتك",
    "auth.login.subtitle": "سجل الدخول إلى حسابك في دليلك",
    "auth.login.button": "تسجيل الدخول",
    "auth.login.register": "ليس لديك حساب؟",
    "auth.register.title": "إنشاء حساب",
    "auth.register.subtitle": "انضم إلى دليلك اليوم",
    "auth.register.button": "إنشاء حساب",
    "auth.register.login": "لديك حساب بالفعل؟",
    "common.learnMore": "اعرف المزيد",
    "common.viewDetails": "عرض التفاصيل",
    "common.range": "المدى",
    "common.battery": "البطارية",
    "common.power": "القوة",
    "common.acceleration": "التسارع",
    "common.drivetrain": "نظام الدفع",
    "common.seating": "المقاعد",
    "common.dimensions": "الأبعاد",
    "common.year": "السنة",
    "common.search": "بحث",
    "common.loading": "جار التحميل...",
    "common.error": "حدث خطأ ما",
  },
};

export function LanguageProvider({ children }: { children: ReactNode }) {
  const [language, setLanguage] = useState<Language>("en");
  const [dir, setDir] = useState<"ltr" | "rtl">("ltr");

  useEffect(() => {
    const saved = localStorage.getItem("alpha-ev-language") as Language;
    if (saved && (saved === "en" || saved === "ar")) {
      setLanguage(saved);
    }
  }, []);

  useEffect(() => {
    const newDir = language === "ar" ? "rtl" : "ltr";
    setDir(newDir);
    document.documentElement.dir = newDir;
    document.documentElement.lang = language;
    localStorage.setItem("alpha-ev-language", language);
  }, [language]);

  const toggleLanguage = () => {
    setLanguage(prev => prev === "en" ? "ar" : "en");
  };

  const t = (key: string): string => {
    return translations[language]?.[key] || key;
  };

  return (
    <LanguageContext.Provider value={{ language, setLanguage, toggleLanguage, dir, t }}>
      {children}
    </LanguageContext.Provider>
  );
}

export function useLanguage() {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error("useLanguage must be used within a LanguageProvider");
  }
  return context;
}
