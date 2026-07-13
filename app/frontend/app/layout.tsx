import type { Metadata } from 'next';
import './globals.css';
import { LanguageProvider } from '@/components/layout/LanguageProvider';
import Navbar from '@/components/layout/Navbar';
import Footer from '@/components/layout/Footer';
import FloatingChatbot from '@/components/chat/FloatingChatbot';

export const metadata: Metadata = {
  title:       'Alpha EV — Electric Vehicles Showcase',
  description: 'Explore the world\'s finest electric and hybrid vehicles at Alpha EV. Browse BYD, GAC, Geely, Haval, MG, ORA, and Volkswagen models.',
  keywords:    ['Alpha EV', 'electric vehicles', 'EV', 'hybrid', 'BYD', 'GAC', 'MG', 'Haval', 'Volkswagen', 'Geely', 'ORA'],
  openGraph: {
    title:       'Alpha EV — Electric Vehicles Showcase',
    description: 'Your destination for premium electric and hybrid vehicles.',
    siteName:    'Alpha EV',
    type:        'website',
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" dir="ltr" suppressHydrationWarning>
      <body>
        <LanguageProvider>
          <Navbar />
          <main>{children}</main>
          <Footer />
          <FloatingChatbot />
        </LanguageProvider>
      </body>
    </html>
  );
}
