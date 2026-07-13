"use client";

import React, { useState, useRef, useEffect } from "react";
import { ChevronDown, Check } from "lucide-react";
import { cn } from "@/lib/utils";
import { useLanguage } from "@/components/providers/LanguageProvider";

interface SelectOption {
  value: string;
  label: string;
  group?: string;
}

interface SelectProps {
  options: SelectOption[];
  value?: string;
  onChange: (value: string) => void;
  placeholder?: string;
  label?: string;
  error?: string;
  disabled?: boolean;
  className?: string;
  searchable?: boolean;
}

export function Select({
  options,
  value,
  onChange,
  placeholder = "Select...",
  label,
  error,
  disabled = false,
  className,
  searchable = true,
}: SelectProps) {
  const [open, setOpen] = useState(false);
  const [search, setSearch] = useState("");
  const containerRef = useRef<HTMLDivElement>(null);
  const searchRef = useRef<HTMLInputElement>(null);
  const { language } = useLanguage();
  const isRTL = language === "ar";

  const selected = options.find((o) => o.value === value);
  const groups = options.reduce<Record<string, SelectOption[]>>((acc, opt) => {
    const key = opt.group ?? "__default";
    if (!acc[key]) acc[key] = [];
    acc[key].push(opt);
    return acc;
  }, {});

  const filtered = search
    ? options.filter((o) =>
        o.label.toLowerCase().includes(search.toLowerCase())
      )
    : null;

  useEffect(() => {
    function handleClick(e: MouseEvent) {
      if (!containerRef.current?.contains(e.target as Node)) setOpen(false);
    }
    document.addEventListener("mousedown", handleClick);
    return () => document.removeEventListener("mousedown", handleClick);
  }, []);

  useEffect(() => {
    if (open && searchable) {
      setTimeout(() => searchRef.current?.focus(), 50);
    }
    if (!open) setSearch("");
  }, [open, searchable]);

  const renderOptions = (opts: SelectOption[]) =>
    opts.map((opt) => (
      <button
        key={opt.value}
        type="button"
        onClick={() => {
          onChange(opt.value);
          setOpen(false);
        }}
        className={cn(
          "w-full flex items-center justify-between px-4 py-2.5 text-sm transition-colors",
          isRTL ? "text-right font-arabic" : "text-left",
          value === opt.value
            ? "bg-red-50/10 text-brand-red font-medium"
            : "text-white/70 hover:bg-white/5"
        )}
      >
        <span>{opt.label}</span>
        {value === opt.value && (
          <Check size={14} className="shrink-0 text-brand-red" />
        )}
      </button>
    ));

  return (
    <div className={cn("relative w-full", className)} ref={containerRef}>
      {label && (
        <label className={cn("label", isRTL && "font-arabic text-right")}>
          {label}
        </label>
      )}

      <button
        type="button"
        onClick={() => !disabled && setOpen((v) => !v)}
        disabled={disabled}
        className={cn(
          "input-base flex items-center justify-between cursor-pointer",
          isRTL && "font-arabic text-right",
          error && "border-brand-red",
          open && "border-brand-red ring-[3px] ring-brand-red/10",
          disabled && "opacity-50 cursor-not-allowed bg-white/5"
        )}
      >
        <span className={selected ? "text-white" : "text-white/30"}>
          {selected?.label ?? placeholder}
        </span>
        <ChevronDown
          size={16}
          className={cn(
            "shrink-0 text-white/40 transition-transform duration-200",
            open && "rotate-180"
          )}
        />
      </button>

      {open && (
        <div className={cn(
          "absolute z-50 mt-1 w-full bg-brand-gray-900 border border-white/10 rounded-xl shadow-xl overflow-hidden animate-scale-in animate-fill-both",
          isRTL ? "text-right" : "text-left"
        )}>
          {searchable && (
            <div className="p-2 border-b border-white/10">
              <input
                ref={searchRef}
                type="text"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder={isRTL ? "بحث..." : "Search..."}
                className={cn(
                  "w-full px-3 py-2 text-sm rounded-lg border border-white/10 bg-black/30 text-white outline-none focus:border-brand-red",
                  isRTL && "font-arabic text-right"
                )}
              />
            </div>
          )}

          <div className="max-h-60 overflow-y-auto no-scrollbar py-1">
            {filtered ? (
              filtered.length > 0 ? (
                renderOptions(filtered)
              ) : (
                <p className={cn(
                  "px-4 py-3 text-sm text-white/40 text-center",
                  isRTL && "font-arabic"
                )}>
                  {isRTL ? "لا توجد نتائج" : "No results found"}
                </p>
              )
            ) : (
              Object.entries(groups).map(([group, opts]) => (
                <div key={group}>
                  {group !== "__default" && (
                    <div className={cn(
                      "px-4 py-1.5 text-xs font-semibold text-white/30 uppercase tracking-wider bg-white/5 sticky top-0",
                      isRTL ? "text-right" : "text-left"
                    )}>
                      {group}
                    </div>
                  )}
                  {renderOptions(opts)}
                </div>
              ))
            )}
          </div>
        </div>
      )}

      {error && (
        <p className={cn("error-text", isRTL && "justify-end")}>
          <span>⚠</span> {error}
        </p>
      )}
    </div>
  );
}
