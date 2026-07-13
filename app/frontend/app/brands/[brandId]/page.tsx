"use client";

import React, { useState, useRef, useEffect } from "react";
import { notFound } from "next/navigation";
import Link from "next/link";
import { ChevronLeft, ChevronRight, Gauge, Battery, Zap, Users, Ruler, Award, ArrowLeft } from "lucide-react";
import { Navbar } from "@/components/layout/Navbar";
import { Footer } from "@/components/layout/Footer";
import { getBrandById, Vehicle } from "@/lib/vehicles";
import { cn } from "@/lib/utils";
import { useLanguage } from "@/components/providers/LanguageProvider";

function SpecItem({ icon, label, value }: { icon: React.ReactNode; label: string; value: string }) {
  return (
    <div className="flex items-center gap-3 p-3 rounded-xl bg-white/5 border border-white/5">
      <div className="text-brand-red">{icon}</div>
      <div>
        <p className="text-xs text-white/40">{label}</p>
        <p className="text-sm font-semibold text-white">{value}</p>
      </div>
    </div>
  );
}

function VehicleShowcase({ vehicles, brandName }: { vehicles: Vehicle[]; brandName: string }) {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isTransitioning, setIsTransitioning] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);
  const touchStartX = useRef<number | null>(null);
  const { language } = useLanguage();
  const isRTL = language === "ar";

  const currentVehicle = vehicles[currentIndex];
  const totalVehicles = vehicles.length;

  const goTo = (index: number) => {
    if (isTransitioning || index === currentIndex) return;
    setIsTransitioning(true);
    setCurrentIndex(index);
    setTimeout(() => setIsTransitioning(false), 400);
  };

  const next = () => goTo((currentIndex + 1) % totalVehicles);
  const prev = () => goTo((currentIndex - 1 + totalVehicles) % totalVehicles);

  const handleTouchStart = (e: React.TouchEvent) => { touchStartX.current = e.touches[0].clientX; };
  const handleTouchEnd = (e: React.TouchEvent) => {
    if (touchStartX.current === null) return;
    const diff = touchStartX.current - e.changedTouches[0].clientX;
    if (Math.abs(diff) > 50) {
      diff > 0 ? (isRTL ? prev() : next()) : (isRTL ? next() : prev());
    }
    touchStartX.current = null;
  };

  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.key === "ArrowLeft") isRTL ? next() : prev();
      if (e.key === "ArrowRight") isRTL ? prev() : next();
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [isRTL]);

  if (!currentVehicle) return null;

  const specItems = [
    { icon: <Gauge size={16} />, label: isRTL ? "المدى" : "Range", value: currentVehicle.spec.range },
    { icon: <Battery size={16} />, label: isRTL ? "البطارية" : "Battery", value: currentVehicle.spec.battery },
    { icon: <Zap size={16} />, label: isRTL ? "القوة" : "Power", value: currentVehicle.spec.power },
    { icon: <Award size={16} />, label: isRTL ? "التسارع" : "Acceleration", value: currentVehicle.spec.acceleration },
    { icon: <Users size={16} />, label: isRTL ? "المقاعد" : "Seating", value: `${currentVehicle.spec.seating}` },
    { icon: <Ruler size={16} />, label: isRTL ? "قاعدة العجلات" : "Wheelbase", value: currentVehicle.spec.wheelbase },
  ];

  return (
    <div ref={containerRef} className="relative rounded-2xl border border-white/10 overflow-hidden bg-brand-gray-900/50"
      onTouchStart={handleTouchStart} onTouchEnd={handleTouchEnd}>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-0">
        <div className="relative h-64 lg:h-auto bg-brand-black/50 flex items-center justify-center p-8">
          <div className="relative w-full h-full flex items-center justify-center">
            <div className={cn("transition-all duration-400", isTransitioning ? "opacity-0 scale-95" : "opacity-100 scale-100")}>
              <div className="w-full max-w-sm aspect-[16/9] bg-gradient-to-br from-brand-gray-800/50 to-brand-gray-900/50 rounded-2xl flex items-center justify-center border border-white/5">
                <span className="text-6xl font-black text-white/10">{currentVehicle.name.charAt(0)}</span>
              </div>
            </div>
          </div>
          {totalVehicles > 1 && (
            <>
              <button onClick={prev} className={cn("absolute top-1/2 -translate-y-1/2 p-2 rounded-full bg-black/50 border border-white/10 text-white/60 hover:text-white hover:bg-black/70 transition-all", isRTL ? "right-3" : "left-3")}>
                <ChevronLeft size={20} className={isRTL ? "rotate-180" : ""} />
              </button>
              <button onClick={next} className={cn("absolute top-1/2 -translate-y-1/2 p-2 rounded-full bg-black/50 border border-white/10 text-white/60 hover:text-white hover:bg-black/70 transition-all", isRTL ? "left-3" : "right-3")}>
                <ChevronRight size={20} className={isRTL ? "rotate-180" : ""} />
              </button>
            </>
          )}
        </div>

        <div className="p-6 lg:p-8 flex flex-col justify-between">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <div className="w-8 h-8 bg-brand-red/20 rounded-lg flex items-center justify-center border border-brand-red/30">
                <span className="text-brand-red font-black text-xs">{brandName.slice(0, 2)}</span>
              </div>
              <span className="text-xs text-white/30">{brandName}</span>
            </div>
            <h2 className={cn("text-2xl sm:text-3xl font-black text-white mb-1", isRTL ? "font-arabic" : "font-sans")}>
              {isRTL ? currentVehicle.nameAr : currentVehicle.name}
            </h2>
            <p className="text-sm text-white/30 mb-4">{currentVehicle.year}</p>

            <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 mb-4">
              {specItems.map((item, i) => <SpecItem key={i} icon={item.icon} label={item.label} value={item.value} />)}
            </div>

            {currentVehicle.spec.price && (
              <div className="flex items-center gap-2 text-sm">
                <span className="text-white/40">{isRTL ? "السعر" : "Price"}:</span>
                <span className="text-brand-red font-bold">{currentVehicle.spec.price}</span>
              </div>
            )}

            <div className="mt-4 flex flex-wrap gap-2">
              {(isRTL ? currentVehicle.featuresAr : currentVehicle.features).map((feature, i) => (
                <span key={i} className="px-2.5 py-1 text-xs rounded-lg bg-white/5 border border-white/5 text-white/50">{feature}</span>
              ))}
            </div>
          </div>
        </div>
      </div>

      {totalVehicles > 1 && (
        <div className="flex justify-center gap-1.5 py-4 border-t border-white/5">
          {vehicles.map((_, i) => (
            <button key={i} onClick={() => goTo(i)} className={cn("w-2 h-2 rounded-full transition-all duration-300", i === currentIndex ? "w-8 bg-brand-red" : "bg-white/20 hover:bg-white/40")} />
          ))}
        </div>
      )}
    </div>
  );
}

export default function BrandDetailPage({ params }: { params: Promise<{ brandId: string }> }) {
  const { brandId } = React.use(params);
  const brand = getBrandById(brandId);
  const { language } = useLanguage();
  const isRTL = language === "ar";

  if (!brand) notFound();

  return (
    <>
      <Navbar />
      <main className="min-h-screen bg-brand-black pt-28 pb-20">
        <div className="container-inner">
          <Link href="/brands" className={cn("inline-flex items-center gap-2 text-sm text-white/30 hover:text-white transition-colors mb-6", isRTL ? "flex-row-reverse" : "")}>
            <ArrowLeft size={16} className={isRTL ? "rotate-180" : ""} />
            {isRTL ? "العودة إلى العلامات" : "Back to Brands"}
          </Link>

          <div className="mb-8 animate-fade-up animate-fill-both">
            <div className="flex items-center gap-4 mb-2">
              <div className="w-14 h-14 rounded-2xl flex items-center justify-center text-2xl font-black"
                style={{ background: `${brand.primaryColor}25`, color: brand.primaryColor, border: `1px solid ${brand.primaryColor}40` }}>
                {brand.name.slice(0, 2)}
              </div>
              <div>
                <h1 className={cn("text-3xl sm:text-4xl font-black text-white", isRTL ? "font-arabic" : "font-sans")}>
                  {isRTL ? brand.nameAr : brand.name}
                </h1>
                <p className={cn("text-sm text-white/40", isRTL ? "font-arabic" : "font-sans")}>
                  {isRTL ? brand.descriptionAr : brand.description}
                </p>
              </div>
            </div>
            <div className="flex items-center gap-3 text-sm text-white/30">
              <span>{brand.models.length} {isRTL ? "موديل" : "models"}</span>
              <span className="w-1 h-1 rounded-full bg-white/20" />
              <span>{brand.country || "China"}</span>
            </div>
          </div>

          {brand.models.length > 0 ? (
            <VehicleShowcase vehicles={brand.models} brandName={isRTL ? brand.nameAr : brand.name} />
          ) : (
            <div className="text-center py-16 text-white/30">{isRTL ? "لا توجد موديلات متاحة" : "No models available"}</div>
          )}
        </div>
      </main>
      <Footer />
    </>
  );
}
