"use client";

import React, { useCallback, useEffect, useRef, useState } from "react";
import { Loader2, Send, Zap } from "lucide-react";

import { Spinner } from "@/components/ui/Spinner";
import { askQuestion } from "@/lib/api";
import { cn } from "@/lib/utils";
import { useLanguage } from "@/components/providers/LanguageProvider";

interface Message {
  id: string;
  text: string;
  sender: "user" | "bot";
  citations?: {
    manual_name: string;
    page: number;
  }[];
}

export function AskAISection() {
  const { language } = useLanguage();
  const isRTL = language === "ar";

  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const messagesContainerRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    setMessages([
      {
        id: "welcome",
        sender: "bot",
        text: isRTL
          ? "مرحباً! اكتب سؤالك عن السيارة أو كتيب المالك وسأساعدك في العثور على الإجابة."
          : "Hello! Ask a question about a vehicle or its owner’s manual, and I’ll help you find the answer.",
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

  const handleSubmit = useCallback(async () => {
    const question = input.trim();

    if (!question || loading) {
      textareaRef.current?.focus();
      return;
    }

    const userMessage: Message = {
      id: `${Date.now()}-user`,
      sender: "user",
      text: question,
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    try {
      const data = await askQuestion({ question });
      const botMessage: Message = {
        id: `${Date.now()}-answer`,
        sender: "bot",
        text: data.answer,
        citations: data.citations,
      };
      setMessages((prev) => [...prev, botMessage]);
    } catch {
      const errorText = isRTL
        ? "حدث خطأ أثناء جلب الإجابة. يرجى المحاولة مرة أخرى."
        : "An error occurred while fetching the answer. Please try again.";
      setMessages((prev) => [
        ...prev,
        { id: `${Date.now()}-error`, sender: "bot", text: errorText },
      ]);
    } finally {
      setLoading(false);
      window.setTimeout(() => {
        textareaRef.current?.focus();
      }, 100);
    }
  }, [input, loading, isRTL]);

  return (
    <section
      id="ask-ai"
      className="flex min-h-screen scroll-mt-20 items-center bg-brand-black py-24"
    >
      <div className="mx-auto w-full max-w-4xl px-4 sm:px-6">
        <div className="mb-8 text-center">
          <div className="mb-4 inline-flex items-center gap-2 rounded-full border border-brand-red/20 bg-red-500/5 px-4 py-1.5 text-xs text-brand-red">
            <Zap size={12} className="fill-brand-red" />
            {isRTL ? "ألفا الذكاء" : "Alpha AI"}
          </div>

          <h2
            className={cn(
              "mb-3 text-4xl font-black text-white sm:text-5xl",
              isRTL ? "font-arabic" : "font-sans",
            )}
          >
            {isRTL ? "اسأل عن سيارتك" : "Ask AI"}
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
              placeholder={
                isRTL
                  ? "اكتب سؤالك..."
                  : "Type your question..."
              }
              className={cn(
                "flex-1 resize-none rounded-xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white outline-none transition-colors placeholder:text-white/25 focus:border-brand-red",
                isRTL && "font-arabic text-right",
              )}
            />

            <button
              type="button"
              onClick={handleSubmit}
              disabled={loading}
              className={cn(
                "flex h-12 w-12 shrink-0 items-center justify-center rounded-xl",
                "bg-brand-red text-white shadow-lg shadow-red-500/20",
                "transition-all duration-200",
                "hover:scale-105 hover:bg-brand-red-dark",
                "active:scale-95",
                "disabled:cursor-wait disabled:opacity-60",
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