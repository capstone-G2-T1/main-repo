'use client';

import { useState, useCallback, useEffect } from 'react';
import Link from 'next/link';
import { useLanguage } from '@/components/layout/LanguageProvider';
import { t } from '@/lib/utils';
import { BRANDS, VEHICLES, getBrandById, type Vehicle } from '@/lib/vehicles';
import CarImage from './CarImage';
import Button from './Button';

export default function CarShowcase() {
  const { lang, isRTL } = useLanguage();
  const [filterBrand, setFilterBrand]   = useState<string>('all');
  const [idx, setIdx]                   = useState(0);
  const [animKey, setAnimKey]           = useState(0);
  const [slideDir, setSlideDir]         = useState<'L' | 'R'>('L');

  const filtered: Vehicle[] =
    filterBrand === 'all' ? VEHICLES : VEHICLES.filter(v => v.brand === filterBrand);
  const vehicle = filtered[idx] ?? filtered[0];
  const brand   = vehicle ? getBrandById(vehicle.brand) : undefined;

  // Reset index when filter changes
  const handleBrandFilter = useCallback((id: string) => {
    setFilterBrand(id);
    setIdx(0);
    setAnimKey(k => k + 1);
    setSlideDir('L');
  }, []);

  const go = useCallback((delta: number) => {
    setSlideDir(delta > 0 ? 'L' : 'R');
    setAnimKey(k => k + 1);
    setIdx(i => {
      const n = i + delta;
      if (n < 0) return filtered.length - 1;
      if (n >= filtered.length) return 0;
      return n;
    });
  }, [filtered.length]);

  // Keyboard navigation
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'ArrowRight') go(isRTL ? -1 :  1);
      if (e.key === 'ArrowLeft')  go(isRTL ?  1 : -1);
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [go, isRTL]);

  if (!vehicle) return null;

  const slideClass = slideDir === 'L' ? 'animate-slide-l' : 'animate-slide-r';

  const specCard = (val: string, lbl: string) => (
    <div key={lbl} style={{
      background: 'var(--bg2)', border: '1px solid var(--bd)',
      borderRadius: 'var(--radius)', padding: '14px 16px',
    }}>
      <div style={{ fontFamily: "'Orbitron', monospace", fontSize: '1.05rem', fontWeight: 700, color: 'var(--cyan)' }}>
        {val}
      </div>
      <div style={{ fontSize: '0.7rem', color: 'var(--txt3)', textTransform: 'uppercase', letterSpacing: '0.08em', marginTop: 4 }}>
        {lbl}
      </div>
    </div>
  );

  return (
    <section style={{ background: 'var(--bg1)', position: 'relative', overflow: 'hidden' }}>
      {/* Radial glow */}
      <div style={{
        position: 'absolute', inset: 0,
        background: 'radial-gradient(ellipse 70% 70% at 50% 60%, rgba(0,201,255,0.04) 0%, transparent 70%)',
        pointerEvents: 'none',
      }} />

      {/* Section header */}
      <div style={{ maxWidth: 1280, margin: '0 auto', padding: '64px 24px 32px' }}>
        <div style={{
          fontFamily: "'Orbitron', monospace", fontSize: '0.65rem', fontWeight: 700,
          letterSpacing: '0.2em', textTransform: 'uppercase', color: 'var(--cyan)',
          marginBottom: 14, display: 'flex', alignItems: 'center', gap: 10,
        }}>
          <span style={{ display: 'inline-block', width: 24, height: 2, background: 'var(--cyan)' }} />
          {t(lang, 'showcase', 'eyebrow')}
        </div>
        <h2 style={{ fontFamily: "'Orbitron', monospace", fontSize: 'clamp(1.6rem,4vw,2.6rem)', fontWeight: 700, color: 'var(--txt)', marginBottom: 8 }}>
          {t(lang, 'showcase', 'title')}
        </h2>
        <p style={{ fontSize: '1rem', color: 'var(--txt2)', lineHeight: 1.65 }}>
          {t(lang, 'showcase', 'sub')}
        </p>
      </div>

      {/* Brand filter strip */}
      <div style={{ borderTop: '1px solid var(--bd)', borderBottom: '1px solid var(--bd)', background: 'var(--bg0)', overflowX: 'auto' }}>
        <div style={{ display: 'flex', gap: 6, padding: '16px 24px', maxWidth: 1280, margin: '0 auto', width: 'max-content' }}>
          {/* All */}
          <button
            onClick={() => handleBrandFilter('all')}
            style={{
              display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 6,
              padding: '12px 20px', borderRadius: 'var(--radius)', minWidth: 90,
              border: `1px solid ${filterBrand === 'all' ? 'var(--cyan)' : 'var(--bd)'}`,
              background: filterBrand === 'all' ? 'var(--cyan-dim)' : 'var(--bg2)',
              cursor: 'pointer', transition: 'var(--tr)',
            }}
          >
            <div style={{
              width: 36, height: 36, borderRadius: 6, background: '#283660',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
            }}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--txt2)" strokeWidth="2">
                <circle cx="12" cy="12" r="10"/><path d="M2 12h20"/>
                <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>
              </svg>
            </div>
            <span style={{
              fontSize: '0.75rem', fontWeight: 600,
              color: filterBrand === 'all' ? 'var(--cyan)' : 'var(--txt2)',
            }}>
              {t(lang, 'showcase', 'all')}
            </span>
          </button>

          {/* Brand chips */}
          {BRANDS.map(b => (
            <button
              key={b.id}
              onClick={() => handleBrandFilter(b.id)}
              style={{
                display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 6,
                padding: '12px 20px', borderRadius: 'var(--radius)', minWidth: 90,
                border: `1px solid ${filterBrand === b.id ? 'var(--cyan)' : 'var(--bd)'}`,
                background: filterBrand === b.id ? 'var(--cyan-dim)' : 'var(--bg2)',
                cursor: 'pointer', transition: 'var(--tr)',
              }}
            >
              <div style={{
                width: 36, height: 36, borderRadius: 6, background: b.hex,
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                fontFamily: "'Orbitron', monospace",
                fontSize: b.name.length > 3 ? '0.55rem' : '0.65rem',
                fontWeight: 900, color: '#fff',
              }}>
                {b.name.length <= 3 ? b.name : b.name.slice(0,2).toUpperCase()}
              </div>
              <span style={{
                fontSize: '0.73rem', fontWeight: 600,
                color: filterBrand === b.id ? 'var(--cyan)' : 'var(--txt2)',
              }}>
                {b.name}
              </span>
            </button>
          ))}
        </div>
      </div>

      {/* Main showcase */}
      <div style={{
        display: 'grid', gridTemplateColumns: '1fr 1fr',
        maxWidth: 1280, margin: '0 auto',
      }}>
        {/* Car visual */}
        <div style={{
          position: 'relative', display: 'flex', alignItems: 'center',
          justifyContent: 'center', padding: '60px 40px', minHeight: 480,
        }}>
          {/* Floor glow */}
          <div style={{
            position: 'absolute', bottom: 0, left: '5%', right: '5%', height: 120,
            background: 'radial-gradient(ellipse at 50% 100%, rgba(0,201,255,0.1) 0%, transparent 70%)',
            pointerEvents: 'none',
          }} />
          {/* Floor line */}
          <div style={{
            position: 'absolute', bottom: 40, left: '10%', right: '10%', height: 1,
            background: 'linear-gradient(90deg, transparent, var(--cyan), transparent)',
            opacity: 0.4,
          }} />

          {/* Animated car image */}
          <div
            key={`car-${animKey}`}
            className={slideClass}
            style={{
              position: 'relative', zIndex: 2,
              width: '100%', maxWidth: 520, height: 280,
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              borderRadius: 'var(--radius-lg)',
              background: brand ? `radial-gradient(ellipse 80% 80% at 50% 60%, ${brand.hex}1A 0%, transparent 70%)` : 'transparent',
            }}
          >
            <CarImage vehicle={vehicle} brand={brand} style={{ padding: 16 }} />
          </div>

          {/* Navigation */}
          <div style={{
            position: 'absolute', bottom: 16, left: '50%', transform: 'translateX(-50%)',
            display: 'flex', alignItems: 'center', gap: 16, zIndex: 10,
          }}>
            <button
              onClick={() => go(isRTL ? 1 : -1)}
              aria-label={t(lang, 'showcase', 'prev')}
              style={{
                width: 40, height: 40, borderRadius: '50%',
                background: 'var(--bg2)', border: '1px solid var(--bd2)',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                cursor: 'pointer', transition: 'var(--tr)', color: 'var(--txt2)',
              }}
              onMouseEnter={e => { e.currentTarget.style.background = 'var(--cyan-dim)'; e.currentTarget.style.borderColor = 'var(--cyan)'; e.currentTarget.style.color = 'var(--cyan)'; }}
              onMouseLeave={e => { e.currentTarget.style.background = 'var(--bg2)'; e.currentTarget.style.borderColor = 'var(--bd2)'; e.currentTarget.style.color = 'var(--txt2)'; }}
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M15 18l-6-6 6-6"/></svg>
            </button>

            <div style={{ display: 'flex', gap: 6 }}>
              {filtered.slice(0, Math.min(filtered.length, 9)).map((_, i) => (
                <button
                  key={i}
                  onClick={() => { setAnimKey(k => k + 1); setIdx(i); }}
                  style={{
                    width: i === idx % Math.min(filtered.length, 9) ? 20 : 6,
                    height: 6, borderRadius: 3,
                    background: i === idx % Math.min(filtered.length, 9) ? 'var(--cyan)' : 'var(--bd2)',
                    border: 'none', cursor: 'pointer', transition: 'var(--tr)', padding: 0,
                  }}
                />
              ))}
            </div>

            <button
              onClick={() => go(isRTL ? -1 : 1)}
              aria-label={t(lang, 'showcase', 'next')}
              style={{
                width: 40, height: 40, borderRadius: '50%',
                background: 'var(--bg2)', border: '1px solid var(--bd2)',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                cursor: 'pointer', transition: 'var(--tr)', color: 'var(--txt2)',
              }}
              onMouseEnter={e => { e.currentTarget.style.background = 'var(--cyan-dim)'; e.currentTarget.style.borderColor = 'var(--cyan)'; e.currentTarget.style.color = 'var(--cyan)'; }}
              onMouseLeave={e => { e.currentTarget.style.background = 'var(--bg2)'; e.currentTarget.style.borderColor = 'var(--bd2)'; e.currentTarget.style.color = 'var(--txt2)'; }}
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M9 18l6-6-6-6"/></svg>
            </button>
          </div>
        </div>

        {/* Info panel */}
        <div style={{
          padding: '60px 48px 60px 40px',
          borderLeft: '1px solid var(--bd)',
          display: 'flex', flexDirection: 'column', justifyContent: 'center', gap: 24,
        }}>
          <div key={`info-${animKey}`} className="animate-fade-in" style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
            {/* Brand badge */}
            <div style={{
              display: 'inline-flex', alignItems: 'center', gap: 8,
              fontFamily: "'Orbitron', monospace", fontSize: '0.63rem',
              fontWeight: 700, letterSpacing: '0.14em', color: 'var(--txt3)', textTransform: 'uppercase',
            }}>
              <span style={{ width: 6, height: 6, borderRadius: '50%', background: 'var(--cyan)', display: 'inline-block' }} />
              {lang === 'ar' ? brand?.nameAr : brand?.name}
            </div>

            {/* Name + type */}
            <div>
              <h3 style={{ fontFamily: "'Orbitron', monospace", fontSize: 'clamp(1.4rem,3vw,2.1rem)', fontWeight: 700, color: 'var(--txt)', lineHeight: 1.2, marginBottom: 6 }}>
                {lang === 'ar' ? vehicle.nameAr : vehicle.name}
              </h3>
              <p style={{ fontSize: '0.85rem', color: 'var(--txt2)' }}>
                {lang === 'ar' ? vehicle.typeAr : vehicle.type} · {vehicle.year}
              </p>
            </div>

            {/* 2×2 spec grid */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
              {vehicle.range && specCard(`${vehicle.range} km`, t(lang, 'showcase', 'range'))}
              {specCard(vehicle.battery, t(lang, 'showcase', 'battery'))}
              {specCard(vehicle.power,   t(lang, 'showcase', 'power'))}
              {specCard(String(vehicle.seats), t(lang, 'showcase', 'seats'))}
            </div>

            {/* Details row */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 8 }}>
              {[
                { val: `${vehicle.maxSpeed} km/h`, lbl: t(lang, 'showcase', 'maxSpeed') },
                { val: vehicle.accel,               lbl: t(lang, 'showcase', 'accel') },
                { val: vehicle.specs.drivetrain,    lbl: t(lang, 'showcase', 'drivetrain') },
              ].map(({ val, lbl }) => (
                <div key={lbl} style={{ textAlign: 'center', padding: '10px 8px', background: 'var(--bg3)', borderRadius: 'var(--radius)' }}>
                  <div style={{ fontSize: '0.82rem', fontWeight: 600, color: 'var(--txt)' }}>{val}</div>
                  <div style={{ fontSize: '0.68rem', color: 'var(--txt3)', marginTop: 3 }}>{lbl}</div>
                </div>
              ))}
            </div>

            <Link href={`/brands/${vehicle.brand}/${vehicle.id}`} style={{ textDecoration: 'none', display: 'inline-block' }}>
              <Button variant="primary">
                {t(lang, 'showcase', 'details')}
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                  <path d="M5 12h14M12 5l7 7-7 7"/>
                </svg>
              </Button>
            </Link>
          </div>
        </div>
      </div>
    </section>
  );
}
