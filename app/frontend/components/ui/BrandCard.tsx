'use client';

import Link from 'next/link';
import { useLanguage } from '@/components/layout/LanguageProvider';
import { t } from '@/lib/utils';
import { getVehiclesByBrand, type Brand } from '@/lib/vehicles';
import Button from './Button';

interface BrandCardProps {
  brand: Brand;
}

export default function BrandCard({ brand }: BrandCardProps) {
  const { lang } = useLanguage();
  const count = getVehiclesByBrand(brand.id).length;
  const name  = lang === 'ar' ? brand.nameAr : brand.name;
  const desc  = lang === 'ar' ? brand.descAr  : brand.desc;

  return (
    <div
      style={{
        background: 'var(--bg2)', border: '1px solid var(--bd)',
        borderRadius: 'var(--radius-lg)', overflow: 'hidden',
        transition: 'var(--tr)', cursor: 'pointer', textAlign: 'center',
      }}
      onMouseEnter={e => {
        e.currentTarget.style.borderColor = 'var(--bd2)';
        e.currentTarget.style.transform = 'translateY(-4px)';
        e.currentTarget.style.boxShadow = '0 20px 40px rgba(0,0,0,0.4)';
      }}
      onMouseLeave={e => {
        e.currentTarget.style.borderColor = 'var(--bd)';
        e.currentTarget.style.transform = '';
        e.currentTarget.style.boxShadow = '';
      }}
    >
      {/* Header with gradient */}
      <div style={{
        height: 140, background: brand.gradient,
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        position: 'relative', overflow: 'hidden',
      }}>
        {/* Radial shimmer */}
        <div style={{
          position: 'absolute', inset: 0,
          background: `radial-gradient(ellipse 70% 70% at 50% 60%, ${brand.hex}33 0%, transparent 70%)`,
        }} />
        {/* Brand abbreviation icon */}
        <div style={{
          width: 64, height: 64, borderRadius: 12,
          background: brand.hex,
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontFamily: "'Orbitron', monospace",
          fontSize: brand.name.length > 3 ? '0.9rem' : '1.1rem',
          fontWeight: 900, color: '#fff',
          boxShadow: `0 8px 24px ${brand.hex}66`,
          position: 'relative', zIndex: 1,
        }}>
          {brand.name.length <= 3 ? brand.name : brand.name.slice(0,2).toUpperCase()}
        </div>
      </div>

      {/* Body */}
      <div style={{ padding: 20 }}>
        <div style={{ fontFamily: "'Orbitron', monospace", fontSize: '1.05rem', fontWeight: 700, color: 'var(--txt)', marginBottom: 6 }}>
          {name}
        </div>
        <div style={{ fontSize: '0.85rem', color: 'var(--txt2)', marginBottom: 10, lineHeight: 1.5 }}>{desc}</div>
        <div style={{ fontSize: '0.75rem', color: 'var(--txt3)', marginBottom: 16 }}>
          {count} {t(lang, 'brands', 'models')}
        </div>
        <Link href={`/brands/${brand.id}`} style={{ textDecoration: 'none', display: 'block' }}>
          <Button variant="secondary" style={{ width: '100%', justifyContent: 'center', fontSize: '0.65rem' }}>
            {t(lang, 'brands', 'explore')}
          </Button>
        </Link>
      </div>
    </div>
  );
}
