"use client";

import React, { useState, useRef, useEffect } from "react";
import { MessageSquare, X, Send, Zap, Minimize2 } from "lucide-react";
import { cn } from "@/lib/utils";
import { useLanguage } from "@/components/providers/LanguageProvider";

interface Message {
  id: string;
  text: string;
  sender: "user" | "bot";
  timestamp: Date;
}

export function ChatbotWidget() {
  const [isOpen, setIsOpen] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const { language } = useLanguage();
  const isRTL = language === "ar";

  // Initialize welcome message
  useEffect(() => {
    setMessages([
      {
        id: "welcome",
        text: isRTL
          ? "مرحباً! أنا دليلك الذكي. اسألني أي شيء عن كتيب سيارتك الصينية!"
          : "Hello! I'm Dalilak AI. Ask me anything about your Chinese vehicle's manual!",
        sender: "bot",
        timestamp: new Date(),
      },
    ]);
  }, [language]);

  useEffect(() => {
    if (isOpen && !isMinimized) {
      setTimeout(() => inputRef.current?.focus(), 300);
    }
  }, [isOpen, isMinimized]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = () => {
    if (!input.trim()) return;

    const userMsg: Message = {
      id: Date.now().toString(),
      text: input.trim(),
      sender: "user",
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setIsTyping(true);

    setTimeout(() => {
      const botResponses = isRTL ? [
        "هذا سؤال رائع! دعني أبحث عن ذلك لك.",
        "يسعدني مساعدتك في ذلك. إليك ما أعرفه...",
        "سؤال مثير للاهتمام! بناءً على مواصفاتنا، إليك الإجابة.",
        "شكراً لسؤالك! سأقدم لك المعلومات الأكثر دقة.",
        "دعني أتحقق من قاعدة بياناتنا لهذه المعلومات.",
      ] : [
        "That's a great question! Let me look that up for you.",
        "I'd be happy to help with that. Here's what I know...",
        "Interesting question! Based on our specs, here's the answer.",
        "Thanks for asking! I'll provide the most accurate information I have.",
        "Let me check our database for that information.",
      ];
      
      const botMsg: Message = {
        id: (Date.now() + 1).toString(),
        text: botResponses[Math.floor(Math.random() * botResponses.length)],
        sender: "bot",
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, botMsg]);
      setIsTyping(false);
    }, 1200 + Math.random() * 800);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const toggleOpen = () => setIsOpen((prev) => !prev);
  const toggleMinimize = () => setIsMinimized((prev) => !prev);

  if (!isOpen) {
    return (
      <button
        onClick={toggleOpen}
        className={cn(
          "fixed bottom-6 z-50 w-14 h-14 rounded-full bg-brand-red text-white",
          "flex items-center justify-center shadow-[0_4px_30px_rgba(227,30,45,0.4)]",
          "hover:scale-105 hover:shadow-[0_6px_40px_rgba(227,30,45,0.5)]",
          "transition-all duration-300 active:scale-95",
          isRTL ? "left-6" : "right-6"
        )}
        aria-label={isRTL ? "فتح المحادثة" : "Open chat"}
      >
        <MessageSquare size={22} />
      </button>
    );
  }

  return (
    <div className={cn(
      "fixed z-50 w-80 sm:w-96 bottom-6",
      isRTL ? "left-6" : "right-6",
      "animate-fade-up animate-fill-both"
    )}>
      <div className="bg-brand-gray-900 border border-white/10 rounded-2xl shadow-2xl overflow-hidden">
        <div className="flex items-center justify-between px-4 py-3 border-b border-white/10 bg-brand-black/50">
          <div className="flex items-center gap-2.5">
            <div className="w-6 h-6 bg-brand-red rounded-lg flex items-center justify-center">
              <Zap size={12} className="text-white fill-white" />
            </div>
            <span className={cn("text-sm font-semibold text-white", isRTL ? "font-arabic" : "")}>
              {isRTL ? "دليلك الذكي" : "Dalilak AI"}
            </span>
          </div>
          <div className="flex items-center gap-1">
            <button
              onClick={toggleMinimize}
              className="p-1.5 rounded-lg text-white/40 hover:text-white hover:bg-white/5 transition-colors"
              aria-label={isRTL ? "تصغير" : "Minimize"}
            >
              <Minimize2 size={14} />
            </button>
            <button
              onClick={toggleOpen}
              className="p-1.5 rounded-lg text-white/40 hover:text-white hover:bg-white/5 transition-colors"
              aria-label={isRTL ? "إغلاق" : "Close"}
            >
              <X size={14} />
            </button>
          </div>
        </div>

        {!isMinimized && (
          <>
            <div className="h-80 overflow-y-auto p-4 space-y-3 no-scrollbar">
              {messages.map((msg) => (
                <div key={msg.id} className={cn(
                  "flex",
                  msg.sender === "user" ? (isRTL ? "flex-row" : "flex-row-reverse") : "",
                  "animate-fade-up animate-fill-both"
                )} style={{ animationDelay: "50ms" }}>
                  <div className={cn(
                    "max-w-[85%] px-3.5 py-2.5 rounded-xl text-sm",
                    msg.sender === "user"
                      ? "bg-brand-red text-white"
                      : "bg-white/5 text-white/90",
                    isRTL ? "font-arabic text-right" : "",
                    msg.sender === "user"
                      ? isRTL ? "rounded-tr-sm" : "rounded-tl-sm"
                      : isRTL ? "rounded-tl-sm" : "rounded-tr-sm"
                  )}>
                    {msg.text}
                  </div>
                </div>
              ))}
              {isTyping && (
                <div className="flex items-center gap-2 text-white/40 text-sm">
                  <div className="flex gap-1">
                    <span className="w-1.5 h-1.5 bg-white/40 rounded-full animate-bounce" style={{ animationDelay: "0ms" }} />
                    <span className="w-1.5 h-1.5 bg-white/40 rounded-full animate-bounce" style={{ animationDelay: "150ms" }} />
                    <span className="w-1.5 h-1.5 bg-white/40 rounded-full animate-bounce" style={{ animationDelay: "300ms" }} />
                  </div>
                  <span className={isRTL ? "font-arabic" : ""}>
                    {isRTL ? "جاري الكتابة..." : "Typing..."}
                  </span>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>

            <div className="flex items-center gap-2 p-3 border-t border-white/10 bg-brand-black/30">
              <input
                ref={inputRef}
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder={isRTL ? "اكتب رسالتك..." : "Type your message..."}
                className={cn(
                  "flex-1 px-3 py-2 text-sm rounded-lg bg-white/5 border border-white/10",
                  "text-white placeholder:text-white/30 outline-none",
                  "focus:border-brand-red transition-colors",
                  isRTL && "font-arabic text-right"
                )}
                dir={isRTL ? "rtl" : "ltr"}
              />
              <button
                onClick={handleSend}
                disabled={!input.trim()}
                className={cn(
                  "p-2 rounded-lg bg-brand-red text-white transition-all",
                  "hover:bg-brand-red-dark active:scale-95",
                  "disabled:opacity-40 disabled:cursor-not-allowed"
                )}
                aria-label={isRTL ? "إرسال" : "Send"}
              >
                <Send size={16} className={isRTL ? "scale-x-[-1]" : ""} />
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
