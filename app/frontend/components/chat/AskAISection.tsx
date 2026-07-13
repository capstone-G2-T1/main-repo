"use client";

import React, { useCallback, useEffect, useRef, useState } from "react";
import Link from "next/link";
import { Loader2, Send, Zap } from "lucide-react";

import { Spinner } from "@/components/ui/Spinner";
import { cn } from "@/lib/utils";
import { useLanguage } from "@/components/providers/LanguageProvider";
import { MAKES } from "@/lib/vehicles";
import { askQuestion, ApiError, UnauthenticatedError } from "@/lib/api";
import { getUserDisplayName } from "@/lib/auth";

interface Message {
  id: string;
  text: string;
  sender: "user" | "bot";
  citations?: {
    manual_name: string;
    page: number;
  }[];
  action?: {
    label: string;
    href: string;
  };
}

export function AskAISection() {
  const { language } = useLanguage();
  const isRTL = language === "ar";

  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [selectedMake, setSelectedMake] = useState<string | null>(null);
  const [displayName, setDisplayName] = useState<string | null>(null);

  const messagesContainerRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    setDisplayName(getUserDisplayName());
  }, []);

  useEffect(() => {
    setMessages([
      {
        id: "welcome",
        sender: "bot",
        text: isRTL
          ? "مرحباً! اختر ماركة سيارتك أولاً ثم اكتب سؤالك عن السيارة أو كتيب المالك وسأساعدك في العثور على الإجابة."
          : "Hello! Pick your vehicle's make first, then ask a question about the vehicle or its owner’s manual, and I’ll help you find the answer.",
      },
    ]);
  }, [isRTL]);

  useEffect(() => {
    const container = messagesContainerRef.current;

    if (!container) {
      return;
    }

    container.scrollTo({
      top: container.scrollHeight,
      behavior: "smooth",
    });
  }, [messages, loading]);

  const canSend = Boolean(input.trim()) && Boolean(selectedMake) && !loading;

  const handleSubmit = useCallback(async () => {
    const question = input.trim();

    if (!question || !selectedMake || loading) {
      textareaRef.current?.focus();
      return;
    }

    const userMessage: Message = {
      id: `${Date.now()}-user`,
      sender: "user",
      text: question,
    };

    setMessages((previousMessages) => [...previousMessages, userMessage]);
    setInput("");
    setLoading(true);

    try {
      const result = await askQuestion({
        question,
        selected_vehicle: selectedMake,
      });

      const botMessage: Message = {
        id: `${Date.now()}-answer`,
        sender: "bot",
        text: result.answer,
        citations: result.citations,
      };

      setMessages((previousMessages) => [...previousMessages, botMessage]);
    } catch (error) {
      let text: string;
      let action: Message["action"];

      if (error instanceof UnauthenticatedError) {
        text = isRTL
          ? "يجب تسجيل الدخول أولاً لطرح سؤال."
          : "You need to sign in first to ask a question.";
        action = {
          label: isRTL ? "تسجيل الدخول" : "Sign in",
          href: "/login",
        };
      } else if (error instanceof ApiError) {
        text = error.message;
      } else {
        text = isRTL
          ? "تعذّر الاتصال بالخادم. يرجى المحاولة مرة أخرى."
          : "Could not reach the server. Please try again.";
      }

      setMessages((previousMessages) => [
        ...previousMessages,
        { id: `${Date.now()}-error`, sender: "bot", text, action },
      ]);
    } finally {
      setLoading(false);
      window.setTimeout(() => {
        textareaRef.current?.focus();
      }, 100);
    }
  }, [input, loading, isRTL, selectedMake]);

  return (
    <section
      id="ask-ai"
      className="relative flex min-h-screen scroll-mt-20 items-center overflow-hidden bg-brand-black py-24"
    >
      <div
        className="absolute inset-0 bg-cover bg-center opacity-40"
        style={{ backgroundImage: "url('/hero-ev.png')" }}
      />
      <div className="absolute inset-0 bg-gradient-to-b from-brand-black via-brand-black/80 to-brand-black" />

      <div className="relative mx-auto w-full max-w-4xl px-4 sm:px-6">
        <div className="mb-8 text-center">
          <div className="mb-4 inline-flex items-center gap-2 rounded-full border border-brand-red/20 bg-red-500/5 px-4 py-1.5 text-xs text-brand-red">
            <Zap size={12} className="fill-brand-red" />
            {isRTL ? "دليلك الذكي" : "Dalilak AI"}
          </div>

          <h2
            className={cn(
              "mb-3 text-4xl font-black text-white sm:text-5xl",
              isRTL ? "font-arabic" : "font-sans",
            )}
          >
            {displayName
              ? isRTL
                ? `مرحباً ${displayName}، اسأل عن سيارتك`
                : `Hi ${displayName}, Ask AI`
              : isRTL
                ? "اسأل عن سيارتك"
                : "Ask AI"}
          </h2>

          <p
            className={cn(
              "text-sm text-white/40 sm:text-base",
              isRTL && "font-arabic",
            )}
          >
            {isRTL
              ? "اكتب سؤالك للحصول على إجابة مستخرجة من كتيب السيارة."
              : "Ask a question to retrieve an answer from the vehicle manual."}
          </p>
        </div>

        <div className="rounded-3xl border border-white/10 bg-white/[0.03] p-4 shadow-2xl sm:p-6">
          <div className="mb-4">
            <p
              className={cn(
                "mb-2 text-xs font-semibold uppercase tracking-wider text-white/40",
                isRTL && "font-arabic text-right",
              )}
            >
              {isRTL ? "اختر ماركة السيارة" : "Select your vehicle make"}
            </p>

            <div className={cn("flex flex-wrap gap-2", isRTL && "flex-row-reverse")}>
              {MAKES.map((make) => (
                <button
                  key={make.value}
                  type="button"
                  onClick={() => setSelectedMake(make.value)}
                  className={cn(
                    "rounded-full border px-4 py-2 text-sm font-medium transition-colors",
                    isRTL && "font-arabic",
                    selectedMake === make.value
                      ? "border-brand-red bg-brand-red text-white shadow-lg shadow-red-500/20"
                      : "border-white/10 bg-white/5 text-white/70 hover:border-white/20 hover:text-white",
                  )}
                >
                  {isRTL ? make.labelAr : make.label}
                </button>
              ))}
            </div>
          </div>

          <div
            ref={messagesContainerRef}
            className="mb-4 min-h-[320px] max-h-[460px] space-y-3 overflow-y-auto rounded-2xl border border-white/5 bg-black/30 p-4"
          >
            {messages.map((message) => (
              <div
                key={message.id}
                className={cn(
                  "flex",
                  message.sender === "user"
                    ? "justify-end"
                    : "justify-start",
                )}
              >
                <div
                  className={cn(
                    "max-w-[86%] rounded-2xl px-4 py-3 text-sm leading-relaxed",
                    message.sender === "user"
                      ? "rounded-br-sm bg-brand-red text-white"
                      : "rounded-bl-sm border border-white/5 bg-white/5 text-white/85",
                    isRTL && "font-arabic text-right",
                  )}
                >
                  <p>{message.text}</p>

                  {message.citations?.map((citation, index) => (
                    <p
                      key={`${citation.manual_name}-${citation.page}-${index}`}
                      className="mt-2 border-t border-white/10 pt-2 text-xs text-white/35"
                    >
                      {citation.manual_name} —{" "}
                      {isRTL ? "صفحة" : "Page"} {citation.page}
                    </p>
                  ))}

                  {message.action && (
                    <Link
                      href={message.action.href}
                      className="mt-2 inline-block text-xs font-semibold text-brand-red hover:underline"
                    >
                      {message.action.label}
                    </Link>
                  )}
                </div>
              </div>
            ))}

            {loading && (
              <div
                className={cn(
                  "flex items-center gap-2 text-sm text-white/40",
                  isRTL && "flex-row-reverse font-arabic",
                )}
              >
                <Spinner size="sm" />

                <span>
                  {isRTL ? "جاري البحث..." : "Searching..."}
                </span>
              </div>
            )}
          </div>

          <div
            className={cn(
              "flex items-end gap-3",
              isRTL && "flex-row-reverse",
            )}
          >
            <textarea
              ref={textareaRef}
              value={input}
              onChange={(event) => {
                setInput(event.target.value);
              }}
              onKeyDown={(event) => {
                if (event.key === "Enter" && !event.shiftKey) {
                  event.preventDefault();
                  handleSubmit();
                }
              }}
              rows={2}
              dir={isRTL ? "rtl" : "ltr"}
              disabled={!selectedMake}
              placeholder={
                selectedMake
                  ? isRTL
                    ? "اكتب سؤالك..."
                    : "Type your question..."
                  : isRTL
                    ? "اختر ماركة السيارة أولاً..."
                    : "Select a vehicle make first..."
              }
              className={cn(
                "flex-1 resize-none rounded-xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white outline-none transition-colors placeholder:text-white/25 focus:border-brand-red",
                "disabled:cursor-not-allowed disabled:opacity-50",
                isRTL && "font-arabic text-right",
              )}
            />

            <button
              type="button"
              onClick={handleSubmit}
              disabled={!canSend}
              className={cn(
                "flex h-12 w-12 shrink-0 items-center justify-center rounded-xl",
                "bg-brand-red text-white shadow-lg shadow-red-500/20",
                "transition-all duration-200",
                "hover:scale-105 hover:bg-brand-red-dark",
                "active:scale-95",
                "disabled:cursor-not-allowed disabled:opacity-60 disabled:hover:scale-100",
              )}
              aria-label={isRTL ? "إرسال السؤال" : "Send question"}
            >
              {loading ? (
                <Loader2 size={20} className="animate-spin" />
              ) : (
                <Send
                  size={20}
                  className={isRTL ? "scale-x-[-1]" : ""}
                />
              )}
            </button>
          </div>
        </div>
      </div>
    </section>
  );
}
