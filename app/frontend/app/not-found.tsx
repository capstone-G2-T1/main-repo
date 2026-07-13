import Link from "next/link";
import { ArrowLeft, Search } from "lucide-react";

export default function NotFound() {
  return (
    <div className="min-h-screen bg-brand-black flex flex-col items-center justify-center p-6 text-center">
      <div className="absolute inset-0 opacity-[0.04]" style={{
        backgroundImage: "linear-gradient(rgba(255,255,255,0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.1) 1px, transparent 1px)",
        backgroundSize: "48px 48px",
      }} />

      <div className="relative z-10 max-w-md">
        <Link href="/" className="inline-flex items-center gap-2 mb-12">
          <div className="w-9 h-9 bg-brand-red rounded-xl flex items-center justify-center">
            <span className="text-white font-black text-lg">α</span>
          </div>
          <span className="font-black text-white text-xl">Dalil<span className="text-brand-red">ak</span></span>
        </Link>

        <div className="mb-6">
          <span className="text-[120px] font-black leading-none select-none" style={{
            background: "linear-gradient(135deg, #E31E2D 0%, #FF6B6B 100%)",
            WebkitBackgroundClip: "text",
            WebkitTextFillColor: "transparent",
            backgroundClip: "text",
          }}>404</span>
        </div>

        <h1 className="text-2xl font-black text-white mb-3">Page Not Found</h1>
        <p className="text-white/35 text-sm leading-relaxed mb-8">The page you're looking for doesn't exist or has been moved.</p>

        <div className="flex flex-col sm:flex-row items-center justify-center gap-3">
          <Link href="/" className="flex items-center gap-2 bg-brand-red text-white px-6 py-3 rounded-xl text-sm font-semibold hover:bg-brand-red-dark transition-all shadow-[0_4px_14px_rgba(227,30,45,0.3)]">
            <ArrowLeft size={15} /> Back to Home
          </Link>
          <Link href="/brands" className="flex items-center gap-2 border border-white/15 text-white/60 px-6 py-3 rounded-xl text-sm font-medium hover:border-white/30 hover:text-white transition-all">
            <Search size={15} /> Browse Vehicles
          </Link>
        </div>
      </div>
    </div>
  );
}
