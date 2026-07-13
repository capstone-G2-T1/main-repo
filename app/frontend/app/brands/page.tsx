"use client";

import React from "react";
import Link from "next/link";
import { ArrowRight } from "lucide-react";
import { Navbar } from "@/components/layout/Navbar";
import { Footer } from "@/components/layout/Footer";
import { BRANDS } from "@/lib/vehicles";
import { cn } from "@/lib/utils";
import { useLanguage } from "@/components/providers/LanguageProvider";

export default function BrandsPage() {
  const { language } = useLanguage();
  const isRTL = language === "ar";

  return (
    <>
      <Navbar />
      <main className="min-h-screen bg-brand-black pt-28 pb-20">
        <div className="container-inner">
          <div className="text-center mb-12 animate-fade-up animate-fill-both">
            <h1 className={cn("text-4xl sm:text-5xl font-black text-white tracking-tight mb-3", isRTL ? "font-arabic" : "font-sans")}>
              {isRTL ? "جميع العلامات التجارية" : "All Brands"}
            </h1>
            <p className={cn("text-white/40 text-sm", isRTL ? "font-arabic" : "font-sans")}>
              {isRTL ? "استكشف مجموعتنا الكاملة من علامات السيارات الصينية" : "Explore our complete lineup of Chinese vehicle brands"}
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {BRANDS.map((brand, i) => (
              <Link key={brand.id} href={`/brands/${brand.id}`} className={cn(
                "group relative overflow-hidden rounded-2xl p-8 cursor-pointer border border-white/5 transition-all duration-400",
                "hover:-translate-y-2 hover:border-brand-red/30 hover:shadow-[0_20px_60px_rgba(0,0,0,0.3)]",
                "animate-fade-up animate-fill-both"
              )} style={{ animationDelay: `${i * 80}ms`, background: `linear-gradient(135deg, ${brand.gradient})` }}>
                <div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-400 pointer-events-none"
                  style={{ background: `radial-gradient(circle at 30% 50%, ${brand.primaryColor}30, transparent 70%)` }} />
                <div className="relative z-10">
                  <div className="w-16 h-16 rounded-2xl flex items-center justify-center mb-5 font-black text-xl transition-transform duration-300 group-hover:scale-110"
                    style={{ background: `${brand.primaryColor}25`, color: brand.primaryColor, border: `1px solid ${brand.primaryColor}40` }}>
                    {brand.name.slice(0, 2)}
                  </div>
                  <h3 className={cn("text-white font-black text-2xl tracking-tight mb-1", isRTL ? "font-arabic" : "font-sans")}>
                    {isRTL ? brand.nameAr : brand.name}
                  </h3>
                  <p className={cn("text-white/40 text-sm mb-2", isRTL ? "font-arabic" : "font-sans")}>
                    {isRTL ? brand.descriptionAr : brand.description}
                  </p>
                  <div className={cn("flex items-center gap-2 text-sm text-white/30", isRTL ? "flex-row-reverse" : "")}>
                    <span>{brand.models.length} {isRTL ? "موديل" : "models"}</span>
                    <span className="w-1 h-1 rounded-full bg-white/20" />
                    <span>{brand.country || "China"}</span>
                  </div>
                  <div className={cn("mt-4 flex items-center gap-2 text-brand-red text-sm font-semibold group-hover:gap-3 transition-all", isRTL ? "flex-row-reverse" : "")}>
                    {isRTL ? "استعراض السيارات" : "View Models"}
                    <ArrowRight size={14} className={isRTL ? "rotate-180" : ""} />
                  </div>
                </div>
              </Link>
            ))}
          </div>
        </div>
      </main>
      <Footer />
    </>
  );
}
