"use client";

import React from "react";
import { CircleGauge } from "lucide-react";

import { useLanguage } from "@/components/providers/LanguageProvider";
import { cn } from "@/lib/utils";

export function Footer() {
  const year = new Date().getFullYear();
  const { language } = useLanguage();
  const isRTL = language === "ar";

  const brandTags = isRTL
    ? ["بي واي دي", "جيلي", "فولكس فاجن"]
    : ["BYD", "Geely", "VW"];

  return (
    <footer className="border-t border-white/5 bg-brand-black">
      <div className="mx-auto max-w-7xl px-4 py-12 sm:px-6">
        <div className="grid grid-cols-1 gap-10 md:grid-cols-2">
          <div>
            <div
              className={cn(
                "mb-4 flex items-center gap-2.5",
                isRTL && "flex-row-reverse justify-end",
              )}
            >
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-brand-red">
                <CircleGauge size={19} className="text-white" />
              </div>

              <span className="text-lg font-black text-white">
                Dalil<span className="text-brand-red">ak</span>
              </span>
            </div>

            <p
              className={cn(
                "max-w-md text-sm leading-relaxed text-white/40",
                isRTL && "font-arabic text-right",
              )}
            >
              {isRTL
                ? "مساعد ذكاء اصطناعي لكتيبات السيارات الصينية المستوردة — اسأل بالعربية واحصل على إجابة موثقة مع رقم الصفحة من كتيب سيارتك (بي واي دي، جيلي، جي إيه سي، إم جي وغيرها)."
                : "An AI assistant for Chinese-imported vehicle manuals — ask a question in Arabic and get a grounded answer with a page citation from your vehicle's manual (BYD, Geely, GAC, MG, and more)."}
            </p>
          </div>

          <div>
            <h3
              className={cn(
                "mb-4 text-sm font-semibold text-white",
                isRTL && "font-arabic text-right",
              )}
            >
              {isRTL ? "العلامات التجارية" : "Brands"}
            </h3>

            <div
              className={cn(
                "flex flex-wrap gap-2",
                isRTL && "justify-end",
              )}
            >
              {brandTags.map((brand) => (
                <span
                  key={brand}
                  className="rounded-lg border border-white/10 bg-white/5 px-3 py-1 text-xs font-medium text-white/40"
                >
                  {brand}
                </span>
              ))}
            </div>
          </div>
        </div>

        <div
          className={cn(
            "mt-10 border-t border-white/5 pt-6 text-center sm:text-left",
            isRTL && "sm:text-right",
          )}
        >
          <p
            className={cn(
              "text-xs text-white/30",
              isRTL && "font-arabic",
            )}
          >
            © {year} Dalilak.{" "}
            {isRTL ? "جميع الحقوق محفوظة." : "All rights reserved."}
          </p>
        </div>
      </div>
    </footer>
  );
}