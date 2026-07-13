'use client';

import Link from 'next/link';
import { useLanguage } from '@/components/layout/LanguageProvider';
import { t } from '@/lib/utils';
import { VEHICLES } from '@/lib/vehicles';
import CarShowcase from '@/components/ui/CarShowcase';
import VehicleCard from '@/components/ui/VehicleCard';
import Button from '@/components/ui/Button';

/* ── Section header helper ──────────────────────────────────────────────── */
function SectionHeader({ eyebrow, title, sub }: { eyebrow: string; title: string; sub?: string }) {
  return (
    <div style={{ marginBottom: 40 }}>
      <div style={{
        fontFamily: "'Orbitron', monospace", fontSize: '0.65rem', fontWeight: 700,
        letterSpacing: '0.2em', textTransform: 'uppercase', color: 'var(--cyan)',
        marginBottom: 14, display: 'flex', alignItems: 'center', gap: 10,
      }}>
        <span style={{ display: 'inline-block', width: 24, height: 2, background: 'var(--cyan)' }} />
        {eyebrow}
      </div>
      <h2 style={{ fontFamily: "'Orbitron', monospace", fontSize: 'clamp(1.6rem,4vw,2.6rem)', fontWeight: 700, color: 'var(--txt)', lineHeight: 1.2 }}>
        {title}
      </h2>
      {sub && <p style={{ fontSize: '1rem', color: 'var(--txt2)', marginTop: 12, lineHeight: 1.65, maxWidth: 600 }}>{sub}</p>}
    </div>
  );
}

/* ── Hero Section ───────────────────────────────────────────────────────── */
function Hero() {
  const { lang } = useLanguage();

  return (
    <section style={{
      position: 'relative', minHeight: '100vh',
      display: 'flex', alignItems: 'center', overflow: 'hidden',
      background: 'radial-gradient(ellipse 80% 60% at 20% 50%, rgba(0,201,255,0.06) 0%, transparent 60%), radial-gradient(ellipse 60% 60% at 80% 60%, rgba(255,94,26,0.05) 0%, transparent 60%), var(--bg0)',
    }}>
      <div className="hero-grid" />
      <div className="hero-scan" />

      {/* Background watermark */}
      <div style={{
        position: 'absolute', right: -40, top: '50%', transform: 'translateY(-50%)',
        fontFamily: "'Orbitron', monospace",
        fontSize: 'clamp(6rem, 18vw, 18rem)',
        fontWeight: 900, color: 'rgba(255,255,255,0.018)',
        pointerEvents: 'none', userSelect: 'none', letterSpacing: '0.1em', whiteSpace: 'nowrap',
      }}>
        ALPHA EV
      </div>

      <div style={{ maxWidth: 1280, margin: '0 auto', padding: '0 24px', position: 'relative', zIndex: 2, width: '100%' }}>
        {/* Eyebrow */}
        <div
          className="animate-fade-in"
          style={{
            display: 'inline-flex', alignItems: 'center', gap: 8,
            background: 'var(--cyan-dim)', border: '1px solid rgba(0,201,255,0.25)',
            padding: '6px 14px', borderRadius: 100, marginBottom: 28,
            fontFamily: "'Orbitron', monospace", fontSize: '0.66rem', fontWeight: 600,
            letterSpacing: '0.16em', color: 'var(--cyan)', textTransform: 'uppercase',
          }}
        >
          <span style={{
            width: 6, height: 6, borderRadius: '50%', background: 'var(--cyan)',
            animation: 'pulseCyan 2s ease-in-out infinite', display: 'inline-block',
          }} />
          {t(lang, 'hero', 'eyebrow')}
        </div>

        {/* Title */}
        <h1 className="animate-fade-up" style={{ fontFamily: "'Orbitron', monospace", lineHeight: 1.05, marginBottom: 8 }}>
          <span style={{ fontSize: 'clamp(3.5rem,10vw,8rem)', fontWeight: 900, display: 'block', color: 'var(--txt)' }}>
            {t(lang, 'hero', 'title1')}
          </span>
          <span style={{ display: 'block', width: '100%', height: 4, margin: '12px 0', background: 'linear-gradient(90deg,var(--cyan),var(--orange),transparent)', borderRadius: 2 }} />
          <span style={{
            fontSize: 'clamp(2rem,6vw,5rem)', fontWeight: 400, display: 'block',
            color: 'var(--cyan)', letterSpacing: '0.3em',
            textShadow: '0 0 40px rgba(0,201,255,0.4)',
          }}>
            {t(lang, 'hero', 'title2')}
          </span>
        </h1>

        <p className="animate-fade-up" style={{
          fontSize: '1.08rem', color: 'var(--txt2)', maxWidth: 520,
          lineHeight: 1.7, margin: '28px 0 40px',
        }}>
          {t(lang, 'hero', 'sub')}
        </p>

        <div className="animate-fade-up" style={{ display: 'flex', gap: 14, flexWrap: 'wrap' }}>
          <Link href="/brands" style={{ textDecoration: 'none' }}>
            <Button variant="primary" size="lg">
              {t(lang, 'hero', 'cta1')}
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                <path d="M5 12h14M12 5l7 7-7 7"/>
              </svg>
            </Button>
          </Link>
          <Link href="/brands" style={{ textDecoration: 'none' }}>
            <Button variant="secondary" size="lg">{t(lang, 'hero', 'cta2')}</Button>
          </Link>
        </div>

        {/* Stats */}
        <div style={{
          display: 'flex', gap: 40, marginTop: 64, paddingTop: 40,
          borderTop: '1px solid var(--bd)', flexWrap: 'wrap',
        }}>
          {[
            { val: '7+',   lbl: t(lang, 'hero', 'stat1') },
            { val: '26',   lbl: t(lang, 'hero', 'stat2') },
            { val: '12',   lbl: t(lang, 'hero', 'stat3') },
            { val: '50K+', lbl: t(lang, 'hero', 'stat4') },
          ].map(s => (
            <div key={s.lbl}>
              <div style={{ fontFamily: "'Orbitron', monospace", fontSize: '2rem', fontWeight: 700, color: 'var(--cyan)' }}>
                {s.val}
              </div>
              <div style={{ fontSize: '0.8rem', color: 'var(--txt3)', textTransform: 'uppercase', letterSpacing: '0.08em', marginTop: 4 }}>
                {s.lbl}
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

/* ── CTA Section ────────────────────────────────────────────────────────── */
function CTASection() {
  const { lang } = useLanguage();
  return (
    <section style={{
      textAlign: 'center', padding: '100px 0',
      background: 'radial-gradient(ellipse 70% 60% at 50% 50%, rgba(0,201,255,0.06) 0%, transparent 70%), var(--bg1)',
      borderTop: '1px solid var(--bd)', borderBottom: '1px solid var(--bd)',
    }}>
      <div style={{ maxWidth: 1280, margin: '0 auto', padding: '0 24px' }}>
        <h2 style={{ fontFamily: "'Orbitron', monospace", fontSize: 'clamp(1.8rem,5vw,3rem)', fontWeight: 800, color: 'var(--txt)', marginBottom: 16 }}>
          {t(lang, 'cta', 'title')}
        </h2>
        <p style={{ fontSize: '1rem', color: 'var(--txt2)', maxWidth: 520, margin: '0 auto 36px', lineHeight: 1.65 }}>
          {t(lang, 'cta', 'sub')}
        </p>
        <div style={{ display: 'flex', gap: 14, justifyContent: 'center', flexWrap: 'wrap' }}>
          <Button variant="primary" size="lg">{t(lang, 'cta', 'btn1')}</Button>
          <Button variant="secondary" size="lg">{t(lang, 'cta', 'btn2')}</Button>
        </div>
      </div>
    </section>
  );
}

/* ── Home Page ──────────────────────────────────────────────────────────── */
export default function HomePage() {
  const { lang } = useLanguage();
  const featured = VEHICLES.slice(0, 6);

  return (
    <>
      <Hero />
      <div style={{ height: 1, background: 'linear-gradient(90deg,transparent,var(--bd2),transparent)' }} />
      <CarShowcase />
      <div style={{ height: 1, background: 'linear-gradient(90deg,transparent,var(--bd2),transparent)' }} />

      {/* Featured vehicles */}
      <section style={{ padding: '88px 0' }}>
        <div style={{ maxWidth: 1280, margin: '0 auto', padding: '0 24px' }}>
          <div style={{ display: 'flex', alignItems: 'flex-end', justifyContent: 'space-between', flexWrap: 'wrap', gap: 16, marginBottom: 40 }}>
            <SectionHeader
              eyebrow={t(lang, 'vehicles', 'eyebrow')}
              title={t(lang, 'vehicles', 'title')}
              sub={t(lang, 'vehicles', 'sub')}
            />
            <Link href="/brands" style={{ textDecoration: 'none', flexShrink: 0 }}>
              <Button variant="secondary">{t(lang, 'vehicles', 'viewAll')}</Button>
            </Link>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill,minmax(300px,1fr))', gap: 20 }}>
            {featured.map(v => <VehicleCard key={v.id} vehicle={v} />)}
          </div>
        </div>
      </section>

      <CTASection />
    </>
  );
}
