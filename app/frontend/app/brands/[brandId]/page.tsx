'use client';

import { notFound } from 'next/navigation';
import Link from 'next/link';
import { useLanguage } from '@/components/layout/LanguageProvider';
import { t } from '@/lib/utils';
import { BRANDS, VEHICLES, getBrandById } from '@/lib/vehicles';
import VehicleCard from '@/components/ui/VehicleCard';
import Button from '@/components/ui/Button';

// ── Static params for SSG ──────────────────────────────────────────────────
export async function generateStaticParams() {
  return BRANDS.map(b => ({ brandId: b.id }));
}

interface PageProps {
  params: { brandId: string };
}

export default function BrandDetailPage({ params }: PageProps) {
  const { lang } = useLanguage();
  const brand    = getBrandById(params.brandId);

  if (!brand) notFound();

  const vehicles = VEHICLES.filter(v => v.brand === brand.id);
  const name     = lang === 'ar' ? brand.nameAr : brand.name;
  const desc     = lang === 'ar' ? brand.descAr  : brand.desc;

  return (
    <>
      {/* Brand hero */}
      <section style={{
        position: 'relative', padding: '80px 0 60px',
        background: brand.gradient, overflow: 'hidden', minHeight: 280,
        display: 'flex', alignItems: 'center',
      }}>
        <div className="hero-grid" style={{ opacity: 0.2 }} />
        <div style={{
          position: 'absolute', inset: 0,
          background: `radial-gradient(ellipse 60% 80% at 30% 60%, ${brand.hex}40 0%, transparent 70%)`,
        }} />
        <div style={{ maxWidth: 1280, margin: '0 auto', padding: '0 24px', position: 'relative', zIndex: 1, width: '100%' }}>
          <Link href="/brands" style={{ textDecoration: 'none', display: 'inline-flex', alignItems: 'center', gap: 6, color: 'rgba(255,255,255,0.5)', fontSize: '0.85rem', marginBottom: 28 }}>
            ← {t(lang, 'brands', 'eyebrow')}
          </Link>
          <div style={{ display: 'flex', alignItems: 'center', gap: 20 }}>
            <div style={{
              width: 80, height: 80, borderRadius: 16,
              background: brand.hex, display: 'flex', alignItems: 'center', justifyContent: 'center',
              fontFamily: "'Orbitron', monospace",
              fontSize: brand.name.length > 3 ? '1.1rem' : '1.6rem',
              fontWeight: 900, color: '#fff',
              boxShadow: `0 8px 32px ${brand.hex}66`,
            }}>
              {brand.name.length <= 3 ? brand.name : brand.name.slice(0,2).toUpperCase()}
            </div>
            <div>
              <div style={{ fontFamily: "'Orbitron', monospace", fontSize: 'clamp(1.8rem,5vw,3.2rem)', fontWeight: 800, color: '#fff', marginBottom: 8 }}>
                {name}
              </div>
              <p style={{ fontSize: '1rem', color: 'rgba(255,255,255,0.65)' }}>{desc}</p>
            </div>
          </div>
        </div>
      </section>

      {/* Vehicles */}
      <section style={{ padding: '64px 0' }}>
        <div style={{ maxWidth: 1280, margin: '0 auto', padding: '0 24px' }}>
          <div style={{
            fontFamily: "'Orbitron', monospace", fontSize: '0.65rem', fontWeight: 700,
            letterSpacing: '0.2em', textTransform: 'uppercase', color: 'var(--cyan)',
            marginBottom: 14, display: 'flex', alignItems: 'center', gap: 10,
          }}>
            <span style={{ display: 'inline-block', width: 24, height: 2, background: 'var(--cyan)' }} />
            {name} — {vehicles.length} {t(lang, 'brands', 'models')}
          </div>

          {vehicles.length === 0 ? (
            <p style={{ color: 'var(--txt2)', textAlign: 'center', padding: '60px 0' }}>No models found.</p>
          ) : (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill,minmax(300px,1fr))', gap: 20 }}>
              {vehicles.map(v => <VehicleCard key={v.id} vehicle={v} />)}
            </div>
          )}
        </div>
      </section>
    </>
  );
}
