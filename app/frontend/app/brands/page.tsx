'use client';

import { useLanguage } from '@/components/layout/LanguageProvider';
import { t } from '@/lib/utils';
import { BRANDS } from '@/lib/vehicles';
import BrandCard from '@/components/ui/BrandCard';

export default function BrandsPage() {
  const { lang } = useLanguage();

  return (
    <>
      {/* Hero */}
      <section style={{
        position: 'relative', padding: '100px 0 60px', textAlign: 'center',
        background: 'radial-gradient(ellipse 70% 60% at 50% 50%, rgba(0,201,255,0.05) 0%, transparent 70%), var(--bg1)',
        overflow: 'hidden',
      }}>
        <div className="hero-grid" />
        <div style={{ maxWidth: 1280, margin: '0 auto', padding: '0 24px', position: 'relative', zIndex: 1 }}>
          <div style={{
            fontFamily: "'Orbitron', monospace", fontSize: '0.65rem', fontWeight: 700,
            letterSpacing: '0.2em', textTransform: 'uppercase', color: 'var(--cyan)',
            marginBottom: 14, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 10,
          }}>
            <span style={{ display: 'inline-block', width: 24, height: 2, background: 'var(--cyan)' }} />
            {t(lang, 'brands', 'eyebrow')}
          </div>
          <h1 style={{ fontFamily: "'Orbitron', monospace", fontSize: 'clamp(1.8rem,5vw,3.2rem)', fontWeight: 700, color: 'var(--txt)', marginBottom: 16 }}>
            {t(lang, 'brands', 'title')}
          </h1>
          <p style={{ fontSize: '1rem', color: 'var(--txt2)', maxWidth: 560, margin: '0 auto', lineHeight: 1.65 }}>
            {t(lang, 'brands', 'sub')}
          </p>
        </div>
      </section>

      <div style={{ height: 1, background: 'linear-gradient(90deg,transparent,var(--bd2),transparent)' }} />

      {/* Brands grid */}
      <section style={{ padding: '88px 0' }}>
        <div style={{ maxWidth: 1280, margin: '0 auto', padding: '0 24px' }}>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill,minmax(280px,1fr))', gap: 20 }}>
            {BRANDS.map(brand => (
              <BrandCard key={brand.id} brand={brand} />
            ))}
          </div>
        </div>
      </section>
    </>
  );
}
