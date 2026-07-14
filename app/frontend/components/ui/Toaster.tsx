"use client";

import React, { createContext, useContext, useState, useCallback } from "react";
import { X, CheckCircle, AlertCircle, Info } from "lucide-react";
import { cn } from "@/lib/utils";
import { useLanguage } from "@/components/providers/LanguageProvider";

type ToastType = "success" | "error" | "info";

interface Toast {
  id: string;
  message: string;
  type: ToastType;
}

interface ToastContextValue {
  addToast: (message: string, type?: ToastType) => void;
}

const ToastContext = createContext<ToastContextValue>({
  addToast: () => {},
});

export function useToast() {
  return useContext(ToastContext);
}

export function Toaster() {
  const [toasts, setToasts] = useState<Toast[]>([]);
  const { language } = useLanguage();
  const isRTL = language === "ar";

  const addToast = useCallback((message: string, type: ToastType = "info") => {
    const id = Math.random().toString(36).slice(2);
    setToasts((prev) => [...prev, { id, message, type }]);
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, 4000);
  }, []);

  const remove = (id: string) =>
    setToasts((prev) => prev.filter((t) => t.id !== id));

  const icons: Record<ToastType, React.ReactNode> = {
    success: <CheckCircle size={16} className="text-green-400 shrink-0" />,
    error: <AlertCircle size={16} className="text-brand-red shrink-0" />,
    info: <Info size={16} className="text-blue-400 shrink-0" />,
  };

  return (
    <ToastContext.Provider value={{ addToast }}>
      <div
        className={cn(
          "fixed bottom-6 z-[200] flex flex-col gap-2",
          isRTL ? "right-6" : "left-6"
        )}
        aria-live="polite"
      >
        {toasts.map((t) => (
          <div
            key={t.id}
            className={cn(
              "flex items-center gap-3 px-4 py-3 rounded-xl shadow-xl",
              "bg-brand-gray-900 border border-white/10 text-white text-sm",
              "animate-fade-up animate-fill-both max-w-sm",
              isRTL ? "flex-row-reverse" : ""
            )}
          >
            {icons[t.type]}
            <span className={cn(
              "flex-1 font-medium",
              isRTL ? "font-arabic text-right" : ""
            )}>{t.message}</span>
            <button
              onClick={() => remove(t.id)}
              className="text-white/30 hover:text-white transition-colors shrink-0"
              aria-label={isRTL ? "إغلاق" : "Close"}
            >
              <X size={14} />
            </button>
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
}
