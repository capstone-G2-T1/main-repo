'use client';

import Link from 'next/link';
import { useLanguage } from '@/components/layout/LanguageProvider';
import { t } from '@/lib/utils';
import { getBrandById, type Vehicle } from '@/lib/vehicles';
import CarImage from './CarImage';
import Button from './Button';

interface VehicleCardProps {
  vehicle: Vehicle;
}

export default function VehicleCard({ vehicle }: VehicleCardProps) {
  const { lang } = useLanguage();
  const brand = getBrandById(vehicle.brand);

  const name  = lang === 'ar' ? vehicle.nameAr  : vehicle.name;
  const type  = lang === 'ar' ? vehicle.typeAr  : vehicle.type;
  const price = lang === 'ar' ? vehicle.priceAr : vehicle.price;

  return (
    <div
      style={{
        background: 'var(--bg2)', border: '1px solid var(--bd)',
        borderRadius: 'var(--radius-lg)', overflow: 'hidden',
        transition: 'var(--tr)', cursor: 'pointer',
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
      {/* Image */}
      <div style={{
        height: 200, position: 'relative', overflow: 'hidden',
        background: `linear-gradient(135deg, var(--bg3), ${brand?.hex ?? '#1C2640'}22)`,
        borderBottom: '1px solid var(--bd)',
      }}>
        <div style={{
          position: 'absolute', inset: 0, padding: 16,
          display: 'flex', alignItems: 'center', justifyContent: 'center',
        }}>
          <CarImage vehicle={vehicle} brand={brand} />
        </div>

        {/* Year badge */}
        <div style={{
          position: 'absolute', top: 12, ...(lang === 'ar' ? { right: 12 } : { left: 12 }),
          background: 'var(--cyan-dim)', border: '1px solid rgba(0,201,255,0.3)',
          color: 'var(--cyan)', fontFamily: "'Orbitron', monospace",
          fontSize: '0.58rem', fontWeight: 700, letterSpacing: '0.12em',
          padding: '4px 10px', borderRadius: 100,
        }}>
          {vehicle.year}
        </div>
      </div>

      {/* Body */}
      <div style={{ padding: 20 }}>
        <div style={{ fontSize: '0.7rem', color: 'var(--txt3)', textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: 5 }}>
          {lang === 'ar' ? brand?.nameAr : brand?.name}
        </div>
        <div style={{ fontFamily: "'Orbitron', monospace", fontSize: '0.95rem', fontWeight: 700, color: 'var(--txt)', marginBottom: 3 }}>
          {name}
        </div>
        <div style={{ fontSize: '0.82rem', color: 'var(--txt2)', marginBottom: 16 }}>{type}</div>

        {/* Stats row */}
        <div style={{ display: 'flex', gap: 16, marginBottom: 16 }}>
          {vehicle.range && (
            <div>
              <div style={{ fontFamily: "'Orbitron', monospace", fontSize: '0.85rem', fontWeight: 700, color: 'var(--cyan)' }}>
                {vehicle.range} km
              </div>
              <div style={{ fontSize: '0.68rem', color: 'var(--txt3)', marginTop: 2 }}>
                {t(lang, 'showcase', 'range')}
              </div>
            </div>
          )}
          <div>
            <div style={{ fontFamily: "'Orbitron', monospace", fontSize: '0.85rem', fontWeight: 700, color: 'var(--cyan)' }}>
              {vehicle.power}
            </div>
            <div style={{ fontSize: '0.68rem', color: 'var(--txt3)', marginTop: 2 }}>
              {t(lang, 'showcase', 'power')}
            </div>
          </div>
          <div>
            <div style={{ fontFamily: "'Orbitron', monospace", fontSize: '0.85rem', fontWeight: 700, color: 'var(--cyan)' }}>
              {vehicle.accel}
            </div>
            <div style={{ fontSize: '0.68rem', color: 'var(--txt3)', marginTop: 2 }}>0–100</div>
          </div>
        </div>

        {/* Footer */}
        <div style={{
          display: 'flex', alignItems: 'center', justifyContent: 'space-between',
          paddingTop: 14, borderTop: '1px solid var(--bd)',
        }}>
          <div style={{ fontFamily: "'Orbitron', monospace", fontSize: '0.82rem', fontWeight: 700, color: 'var(--gold)' }}>
            {price}
          </div>
          <Link href={`/brands/${vehicle.brand}/${vehicle.id}`} style={{ textDecoration: 'none' }}>
            <Button variant="primary" size="sm">
              {t(lang, 'vehicles', 'details')}
            </Button>
          </Link>
        </div>
      </div>
    </div>
  );
}
