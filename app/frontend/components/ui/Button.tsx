import type { ButtonHTMLAttributes, ReactNode } from 'react';
import { cn } from '@/lib/utils';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  children: ReactNode;
}

const BASE = {
  display: 'inline-flex', alignItems: 'center', gap: 8,
  border: 'none', cursor: 'pointer', transition: 'all 0.3s cubic-bezier(0.4,0,0.2,1)',
  fontFamily: "'Orbitron', monospace", fontWeight: 700,
  letterSpacing: '0.1em', textTransform: 'uppercase' as const,
  whiteSpace: 'nowrap' as const, outline: 'none',
};

const VARIANTS = {
  primary: {
    background: 'linear-gradient(135deg,var(--cyan),var(--cyan2))',
    color: '#000',
  },
  secondary: {
    background: 'transparent',
    color: 'var(--cyan)',
    border: '1px solid var(--cyan)',
  },
  ghost: {
    background: 'transparent',
    color: 'var(--txt2)',
    border: '1px solid var(--bd)',
    fontFamily: "'Exo 2', sans-serif",
    letterSpacing: '0.02em',
    textTransform: 'none' as const,
  },
};

const SIZES = {
  sm: { padding: '8px 18px', fontSize: '0.68rem', borderRadius: 'var(--radius)' },
  md: { padding: '12px 26px', fontSize: '0.72rem', borderRadius: 'var(--radius)' },
  lg: { padding: '15px 34px', fontSize: '0.78rem', borderRadius: 'var(--radius)' },
};

export default function Button({
  variant = 'primary',
  size    = 'md',
  children,
  style,
  ...props
}: ButtonProps) {
  return (
    <button
      {...props}
      style={{
        ...BASE,
        ...VARIANTS[variant],
        ...SIZES[size],
        ...style,
      }}
      onMouseEnter={e => {
        if (variant === 'primary')   e.currentTarget.style.transform = 'translateY(-2px)';
        if (variant === 'secondary') { e.currentTarget.style.background = 'var(--cyan-dim)'; e.currentTarget.style.transform = 'translateY(-2px)'; }
        if (variant === 'ghost')     { e.currentTarget.style.color = 'var(--txt)'; e.currentTarget.style.borderColor = 'var(--bd2)'; }
      }}
      onMouseLeave={e => {
        e.currentTarget.style.transform = '';
        if (variant === 'secondary') e.currentTarget.style.background = 'transparent';
        if (variant === 'ghost')     { e.currentTarget.style.color = 'var(--txt2)'; e.currentTarget.style.borderColor = 'var(--bd)'; }
      }}
    >
      {children}
    </button>
  );
}
