'use client';

import { useState } from 'react';
import type { Vehicle, Brand } from '@/lib/vehicles';

interface CarImageProps {
  vehicle: Vehicle;
  brand?: Brand;
  style?: React.CSSProperties;
}

export default function CarImage({ vehicle, brand, style }: CarImageProps) {
  const [hasError, setHasError] = useState(false);

  if (hasError || !vehicle.image) {
    return (
      <div style={{
        display: 'flex', flexDirection: 'column', alignItems: 'center',
        justifyContent: 'center', gap: 8, width: '100%', height: '100%',
        ...style,
      }}>
        <svg viewBox="0 0 120 50" width="180" fill="none" style={{ opacity: 0.35 }}>
          <rect x="10" y="28" width="100" height="14" rx="3" fill={brand?.hex ?? '#00C9FF'} opacity="0.5"/>
          <path d="M20 28 C24 14 36 10 52 9 L72 9 C84 9 96 13 102 24 L108 28Z" fill={brand?.hex ?? '#00C9FF'} opacity="0.6"/>
          <circle cx="32" cy="42" r="8" fill="#0a0e1c" stroke={brand?.hex ?? '#00C9FF'} strokeWidth="2"/>
          <circle cx="88" cy="42" r="8" fill="#0a0e1c" stroke={brand?.hex ?? '#00C9FF'} strokeWidth="2"/>
          <circle cx="32" cy="42" r="3" fill={brand?.hex ?? '#00C9FF'} opacity="0.7"/>
          <circle cx="88" cy="42" r="3" fill={brand?.hex ?? '#00C9FF'} opacity="0.7"/>
        </svg>
        <span style={{
          fontFamily: "'Orbitron', monospace", fontSize: '0.58rem',
          letterSpacing: '0.14em', color: 'var(--txt3)',
        }}>
          {vehicle.name.toUpperCase()}
        </span>
      </div>
    );
  }

  return (
    // eslint-disable-next-line @next/next/no-img-element
    <img
      src={vehicle.image}
      alt={vehicle.name}
      onError={() => setHasError(true)}
      style={{
        width: '100%', height: '100%',
        objectFit: 'contain',
        filter: 'drop-shadow(0 16px 32px rgba(0,0,0,0.5))',
        ...style,
      }}
    />
  );
}
