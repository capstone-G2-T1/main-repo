import type { Metadata } from "next";
import "./globals.css";
import { Toaster } from "@/components/ui/Toaster";
import { LanguageProvider } from "@/components/providers/LanguageProvider";

export const metadata: Metadata = {
  title: "Dalilak",
  description: "Dalilak — An AI assistant for Chinese-imported vehicle manuals. Ask questions in Arabic and get grounded, cited answers from your vehicle's manual.",
  keywords: "Dalilak, Chinese vehicles, vehicle manuals, BYD, Geely, GAC, MG, VW, owner's manual assistant",
  authors: [{ name: "Dalilak" }],
  openGraph: {
    title: "Dalilak",
    description: "An AI assistant for Chinese-imported vehicle manuals, grounded with citations.",
    type: "website",
    siteName: "Dalilak",
  },
  robots: "index, follow",
  icons: {
    icon: "/favicon.svg",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className="antialiased">
        <LanguageProvider>
          {children}
          <Toaster />
        </LanguageProvider>
      </body>
    </html>
  );
}
