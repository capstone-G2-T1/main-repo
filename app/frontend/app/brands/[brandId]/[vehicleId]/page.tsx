'use client';

import { notFound } from 'next/navigation';
import Link from 'next/link';
import { useState } from 'react';
import { useLanguage } from '@/components/layout/LanguageProvider';
import { t } from '@/lib/utils';
import { VEHICLES, getBrandById, getAllVehicleIds } from '@/lib/vehicles';
import CarImage from '@/components/ui/CarImage';
import Button from '@/components/ui/Button';

export async function generateStaticParams() {
  return getAllVehicleIds().map(id => {
    const v = VEHICLES.find(v => v.id === id)!;
    return { brandId: v.brand, vehicleId: id };
  });
}

interface PageProps {
  params: { brandId: string; vehicleId: string };
}

export default function VehicleDetailPage({ params }: PageProps) {
  const { lang } = useLanguage();
  const [tab, setTab] = useState<'specs' | 'features'>('specs');

  const vehicle = VEHICLES.find(v => v.id === params.vehicleId && v.brand === params.brandId);
  if (!vehicle) notFound();

  const brand    = getBrandById(vehicle.brand);
  const name     = lang === 'ar' ? vehicle.nameAr  : vehicle.name;
  const type     = lang === 'ar' ? vehicle.typeAr  : vehicle.type;
  const price    = lang === 'ar' ? vehicle.priceAr : vehicle.price;
  const features = lang === 'ar' ? vehicle.featuresAr : vehicle.features;

  const specsRows = [
    [t(lang, 'showcase', 'battery'),    vehicle.battery],
    [t(lang, 'showcase', 'power'),      vehicle.power],
    [t(lang, 'showcase', 'range'),      vehicle.range ? `${vehicle.range} km` : '—'],
    [t(lang, 'showcase', 'maxSpeed'),   `${vehicle.maxSpeed} km/h`],
    [t(lang, 'showcase', 'accel'),      vehicle.accel],
    [t(lang, 'showcase', 'seats'),      String(vehicle.seats)],
    [t(lang, 'showcase', 'drivetrain'), vehicle.specs.drivetrain],
    [t(lang, 'showcase', 'length'),     vehicle.specs.length],
    [t(lang, 'showcase', 'width'),      vehicle.specs.width],
    [t(lang, 'showcase', 'height'),     vehicle.specs.height],
    [t(lang, 'showcase', 'wheelbase'),  vehicle.specs.wheelbase],
    [t(lang, 'showcase', 'weight'),     vehicle.specs.weight],
  ];

  return (
    <>
      {/* Hero */}
      <section style={{
        position: 'relative', padding: '80px 0 60px', overflow: 'hidden',
        background: `radial-gradient(ellipse 80% 80% at 30% 50%, ${brand?.hex ?? 'transparent'}0D 0%, transparent 60%), var(--bg1)`,
      }}>
        <div className="hero-grid" />
        <div style={{ maxWidth: 1280, margin: '0 auto', padding: '0 24px', position: 'relative', zIndex: 1 }}>
          <Link href={`/brands/${vehicle.brand}`} style={{ textDecoration: 'none' }}>
            <Button variant="ghost" size="sm" style={{ marginBottom: 32 }}>
              {t(lang, 'vd', 'back')}
            </Button>
          </Link>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 60, alignItems: 'center' }}>
            {/* Image */}
            <div style={{
              borderRadius: 'var(--radius-lg)', overflow: 'hidden',
              background: 'var(--bg2)', border: '1px solid var(--bd)',
              height: 360, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 20,
            }}>
              <CarImage vehicle={vehicle} brand={brand} style={{ padding: 16 }} />
            </div>

            {/* Info */}
            <div>
              {/* Brand tag */}
              <div style={{
                display: 'inline-flex', alignItems: 'center', gap: 8,
                background: 'var(--cyan-dim)', border: '1px solid rgba(0,201,255,0.3)',
                color: 'var(--cyan)', fontFamily: "'Orbitron', monospace",
                fontSize: '0.63rem', letterSpacing: '0.14em', textTransform: 'uppercase',
                padding: '5px 12px', borderRadius: 100, marginBottom: 20,
              }}>
                <div style={{ width: 8, height: 8, borderRadius: '50%', background: brand?.hex }} />
                {lang === 'ar' ? brand?.nameAr : brand?.name}
              </div>

              <h1 style={{ fontFamily: "'Orbitron', monospace", fontSize: 'clamp(1.6rem,4vw,2.8rem)', fontWeight: 800, color: 'var(--txt)', lineHeight: 1.1, marginBottom: 10 }}>
                {name}
              </h1>
              <p style={{ fontSize: '1rem', color: 'var(--txt2)', marginBottom: 28 }}>
                {type} · {vehicle.year}
              </p>

              {/* Key specs */}
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3,1fr)', gap: 12, marginBottom: 28 }}>
                {vehicle.range && (
                  <div style={{ background: 'var(--bg2)', border: '1px solid var(--bd)', borderRadius: 'var(--radius)', padding: 16 }}>
                    <div style={{ fontFamily: "'Orbitron', monospace", fontSize: '1.2rem', fontWeight: 700, color: 'var(--cyan)' }}>{vehicle.range}<span style={{ fontSize: '0.7rem', color: 'var(--txt3)', marginLeft: 3 }}>km</span></div>
                    <div style={{ fontSize: '0.7rem', color: 'var(--txt3)', textTransform: 'uppercase', letterSpacing: '0.08em', marginTop: 6 }}>{t(lang, 'showcase', 'range')}</div>
                  </div>
                )}
                <div style={{ background: 'var(--bg2)', border: '1px solid var(--bd)', borderRadius: 'var(--radius)', padding: 16 }}>
                  <div style={{ fontFamily: "'Orbitron', monospace", fontSize: '1.2rem', fontWeight: 700, color: 'var(--cyan)' }}>{vehicle.accel}</div>
                  <div style={{ fontSize: '0.7rem', color: 'var(--txt3)', textTransform: 'uppercase', letterSpacing: '0.08em', marginTop: 6 }}>0–100 km/h</div>
                </div>
                <div style={{ background: 'var(--bg2)', border: '1px solid var(--bd)', borderRadius: 'var(--radius)', padding: 16 }}>
                  <div style={{ fontFamily: "'Orbitron', monospace", fontSize: '1.2rem', fontWeight: 700, color: 'var(--cyan)' }}>{vehicle.maxSpeed}<span style={{ fontSize: '0.7rem', color: 'var(--txt3)', marginLeft: 3 }}>km/h</span></div>
                  <div style={{ fontSize: '0.7rem', color: 'var(--txt3)', textTransform: 'uppercase', letterSpacing: '0.08em', marginTop: 6 }}>{t(lang, 'showcase', 'maxSpeed')}</div>
                </div>
              </div>

              <div style={{ fontFamily: "'Orbitron', monospace", fontSize: '1.4rem', fontWeight: 700, color: 'var(--gold)', marginBottom: 24 }}>
                {price}
              </div>

              <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
                <Button variant="primary">{t(lang, 'vd', 'request')}</Button>
                <Button variant="secondary">{t(lang, 'vd', 'brochure')}</Button>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Tabs */}
      <section style={{ padding: '60px 0 88px' }}>
        <div style={{ maxWidth: 1280, margin: '0 auto', padding: '0 24px' }}>
          <div style={{ display: 'flex', gap: 4, borderBottom: '1px solid var(--bd)', marginBottom: 36 }}>
            {(['specs', 'features'] as const).map(tb => (
              <button
                key={tb}
                onClick={() => setTab(tb)}
                style={{
                  background: 'transparent', border: 'none',
                  borderBottom: `2px solid ${tab === tb ? 'var(--cyan)' : 'transparent'}`,
                  color: tab === tb ? 'var(--cyan)' : 'var(--txt2)',
                  padding: '12px 20px', cursor: 'pointer',
                  fontFamily: "'Exo 2', sans-serif", fontSize: '0.9rem', fontWeight: 500,
                  transition: 'var(--tr)',
                }}
              >
                {t(lang, 'vd', tb === 'specs' ? 'specs' : 'features')}
              </button>
            ))}
          </div>

          {tab === 'specs' && (
            <table style={{ width: '100%', borderCollapse: 'collapse' }} className="animate-fade-in">
              <tbody>
                {specsRows.map(([lbl, val], i) => val && val !== '—' ? (
                  <tr key={i} style={{ background: i % 2 === 0 ? 'var(--bg2)' : 'transparent' }}>
                    <td style={{ padding: '14px 20px', borderBottom: '1px solid var(--bd)', fontSize: '0.8rem', color: 'var(--txt3)', textTransform: 'uppercase', letterSpacing: '0.06em' }}>{lbl}</td>
                    <td style={{ padding: '14px 20px', borderBottom: '1px solid var(--bd)', fontSize: '0.9rem', color: 'var(--txt)', fontWeight: 500, textAlign: lang === 'ar' ? 'left' : 'right' }}>{val}</td>
                  </tr>
                ) : null)}
              </tbody>
            </table>
          )}

          {tab === 'features' && (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill,minmax(220px,1fr))', gap: 12 }} className="animate-fade-in">
              {features.map((f, i) => (
                <div key={i} style={{
                  display: 'flex', alignItems: 'center', gap: 10,
                  padding: '14px 16px', background: 'var(--bg2)',
                  border: '1px solid var(--bd)', borderRadius: 'var(--radius)',
                }}>
                  <div style={{
                    width: 24, height: 24, background: 'var(--cyan-dim)',
                    borderRadius: 6, display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0,
                  }}>
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="var(--cyan)" strokeWidth="2.5">
                      <polyline points="20 6 9 17 4 12"/>
                    </svg>
                  </div>
                  <span style={{ fontSize: '0.85rem', color: 'var(--txt2)' }}>{f}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      </section>
    </>
  );
}
