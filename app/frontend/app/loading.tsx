'use client';
import { useLanguage } from '@/components/layout/LanguageProvider';
import { t } from '@/lib/utils';

export default function Loading() {
  const { lang } = useLanguage();
  return (
    <div style={{
      minHeight: '60vh', display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center', gap: 20,
    }}>
      <div style={{
        width: 48, height: 48, borderRadius: '50%',
        border: '3px solid var(--bd)', borderTopColor: 'var(--cyan)',
        animation: 'spin 0.8s linear infinite',
      }} />
      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
      <p style={{ fontFamily: "'Orbitron', monospace", fontSize: '0.7rem', letterSpacing: '0.16em', color: 'var(--txt3)', textTransform: 'uppercase' }}>
        {t(lang, 'hero', 'eyebrow')}
      </p>
    </div>
  );
}
