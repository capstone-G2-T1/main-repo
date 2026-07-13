'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useLanguage } from './LanguageProvider';
import { t } from '@/lib/utils';

const NAV_ITEMS = [
  { key: 'home'   as const, href: '/' },
  { key: 'brands' as const, href: '/brands' },
  { key: 'models' as const, href: '/brands' },
] as const;

export default function Navbar() {
  const { lang, setLang } = useLanguage();
  const pathname = usePathname();

  return (
    <nav
      style={{
        position: 'sticky', top: 0, zIndex: 100,
        background: 'rgba(6,8,15,0.88)',
        backdropFilter: 'blur(24px)', WebkitBackdropFilter: 'blur(24px)',
        borderBottom: '1px solid var(--bd)',
      }}
    >
      <div
        style={{
          maxWidth: 1280, margin: '0 auto', height: 68,
          display: 'flex', alignItems: 'center',
          justifyContent: 'space-between', gap: 24, padding: '0 24px',
        }}
      >
        {/* Logo */}
        <Link href="/" style={{ display: 'flex', alignItems: 'center', gap: 10, textDecoration: 'none' }}>
          <div style={{
            width: 36, height: 36, borderRadius: 6,
            background: 'linear-gradient(135deg,var(--cyan),var(--cyan2))',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
          }}>
            <svg viewBox="0 0 24 24" fill="none" width="20" height="20">
              <path d="M12 2L2 7l10 5 10-5-10-5z" fill="#000"/>
              <path d="M2 17l10 5 10-5" stroke="#000" strokeWidth="2" strokeLinecap="round"/>
              <path d="M2 12l10 5 10-5" stroke="#000" strokeWidth="2" strokeLinecap="round"/>
            </svg>
          </div>
          <span style={{ fontFamily: 'var(--font-display)', fontSize: '1.05rem', fontWeight: 800, letterSpacing: '0.08em', color: 'var(--txt)', textDecoration: 'none' }}>
            ALPHA<span style={{ color: 'var(--cyan)' }}> EV</span>
          </span>
        </Link>

        {/* Centre nav */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
          {NAV_ITEMS.map(item => {
            const active = pathname === item.href || (item.href !== '/' && pathname.startsWith(item.href));
            return (
              <Link
                key={item.key}
                href={item.href}
                style={{
                  background: active ? 'var(--cyan-dim)' : 'transparent',
                  color: active ? 'var(--cyan)' : 'var(--txt2)',
                  padding: '8px 14px', borderRadius: 'var(--radius)',
                  fontFamily: 'var(--font-body)', fontSize: '0.88rem',
                  fontWeight: 500, letterSpacing: '0.04em',
                  textTransform: 'uppercase', textDecoration: 'none',
                  transition: 'var(--tr)',
                }}
              >
                {t(lang, 'nav', item.key)}
              </Link>
            );
          })}
        </div>

        {/* Right side */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          {/* Language toggle */}
          <div style={{ display: 'flex', background: 'var(--bg2)', border: '1px solid var(--bd)', borderRadius: 'var(--radius)', overflow: 'hidden' }}>
            {(['en', 'ar'] as const).map(l => (
              <button
                key={l}
                onClick={() => setLang(l)}
                style={{
                  background: lang === l ? 'var(--cyan)' : 'transparent',
                  color: lang === l ? '#000' : 'var(--txt2)',
                  border: 'none', padding: '6px 12px', cursor: 'pointer',
                  fontFamily: 'var(--font-display)', fontSize: '0.7rem',
                  fontWeight: 700, letterSpacing: '0.08em', transition: 'var(--tr)',
                }}
              >
                {l.toUpperCase()}
              </button>
            ))}
          </div>

          <Link href="/login" style={{
            background: 'transparent', color: 'var(--txt2)',
            border: '1px solid var(--bd)', padding: '9px 18px',
            borderRadius: 'var(--radius)', fontSize: '0.88rem',
            textDecoration: 'none', transition: 'var(--tr)', fontFamily: 'var(--font-body)',
          }}>
            {t(lang, 'nav', 'login')}
          </Link>

          <Link href="/register" style={{
            background: 'linear-gradient(135deg,var(--cyan),var(--cyan2))',
            color: '#000', border: 'none', padding: '10px 20px',
            borderRadius: 'var(--radius)',
            fontFamily: 'var(--font-display)', fontSize: '0.68rem',
            fontWeight: 700, letterSpacing: '0.1em', textTransform: 'uppercase',
            textDecoration: 'none', transition: 'var(--tr)', whiteSpace: 'nowrap',
          }}>
            {t(lang, 'nav', 'register')}
          </Link>
        </div>
      </div>
    </nav>
  );
}
