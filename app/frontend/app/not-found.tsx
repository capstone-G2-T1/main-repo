'use client';
import Link from 'next/link';
import { useLanguage } from '@/components/layout/LanguageProvider';
import { t } from '@/lib/utils';
import Button from '@/components/ui/Button';

export default function NotFound() {
  const { lang } = useLanguage();
  return (
    <div style={{
      minHeight: '80vh', display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center', gap: 24,
      background: 'radial-gradient(ellipse 60% 60% at 50% 40%, rgba(0,201,255,0.05) 0%, transparent 70%)',
      textAlign: 'center', padding: '0 24px',
    }}>
      <div style={{ fontFamily: "'Orbitron', monospace", fontSize: 'clamp(5rem,20vw,12rem)', fontWeight: 900, color: 'rgba(0,201,255,0.12)', lineHeight: 1 }}>404</div>
      <h1 style={{ fontFamily: "'Orbitron', monospace", fontSize: 'clamp(1.4rem,4vw,2.2rem)', fontWeight: 700, color: 'var(--txt)', marginTop: -20 }}>
        {t(lang, 'notFound', 'title')}
      </h1>
      <p style={{ fontSize: '1rem', color: 'var(--txt2)', maxWidth: 380 }}>
        {t(lang, 'notFound', 'sub')}
      </p>
      <Link href="/" style={{ textDecoration: 'none' }}>
        <Button variant="primary">{t(lang, 'notFound', 'back')}</Button>
      </Link>
    </div>
  );
}
