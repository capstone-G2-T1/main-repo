'use client';

import Link from 'next/link';
import { useLanguage } from './LanguageProvider';
import { t } from '@/lib/utils';
import { BRANDS } from '@/lib/vehicles';

export default function Footer() {
  const { lang } = useLanguage();

  const logoIcon = (
    <div style={{
      width: 32, height: 32, borderRadius: 6,
      background: 'linear-gradient(135deg,var(--cyan),var(--cyan2))',
      display: 'flex', alignItems: 'center', justifyContent: 'center',
    }}>
      <svg viewBox="0 0 24 24" fill="none" width="16" height="16">
        <path d="M12 2L2 7l10 5 10-5-10-5z" fill="#000"/>
        <path d="M2 17l10 5 10-5" stroke="#000" strokeWidth="2" strokeLinecap="round"/>
        <path d="M2 12l10 5 10-5" stroke="#000" strokeWidth="2" strokeLinecap="round"/>
      </svg>
    </div>
  );

  const colTitle = (label: string) => (
    <div style={{
      fontFamily: 'var(--font-display)', fontSize: '0.65rem', fontWeight: 700,
      letterSpacing: '0.16em', textTransform: 'uppercase',
      color: 'var(--txt3)', marginBottom: 16,
    }}>{label}</div>
  );

  const footerLink = (label: string, href = '#') => (
    <Link key={label} href={href} style={{
      color: 'var(--txt2)', fontSize: '0.88rem', textDecoration: 'none',
      transition: 'color 0.2s',
    }}
      onMouseEnter={e => (e.currentTarget.style.color = 'var(--cyan)')}
      onMouseLeave={e => (e.currentTarget.style.color = 'var(--txt2)')}
    >{label}</Link>
  );

  return (
    <footer style={{ background: 'var(--bg1)', borderTop: '1px solid var(--bd)', padding: '60px 0 32px' }}>
      <div style={{ maxWidth: 1280, margin: '0 auto', padding: '0 24px' }}>

        {/* Grid */}
        <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr 1fr 1fr', gap: 40, marginBottom: 48 }}>
          {/* Brand */}
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 14 }}>
              {logoIcon}
              <span style={{ fontFamily: 'var(--font-display)', fontSize: '1rem', fontWeight: 800, letterSpacing: '0.08em', color: 'var(--txt)' }}>
                ALPHA<span style={{ color: 'var(--cyan)' }}> EV</span>
              </span>
            </div>
            <p style={{ fontSize: '0.88rem', color: 'var(--txt2)', lineHeight: 1.65, maxWidth: 260 }}>
              {t(lang, 'footer', 'desc')}
            </p>
          </div>

          {/* Company */}
          <div>
            {colTitle(t(lang, 'footer', 'company'))}
            <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
              {footerLink(t(lang, 'footer', 'about'))}
              {footerLink(t(lang, 'footer', 'careers'))}
              {footerLink(t(lang, 'footer', 'press'))}
            </div>
          </div>

          {/* Brands */}
          <div>
            {colTitle(t(lang, 'footer', 'brandsCol'))}
            <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
              {BRANDS.map(b => footerLink(b.name, `/brands/${b.id}`))}
            </div>
          </div>

          {/* Support */}
          <div>
            {colTitle(t(lang, 'footer', 'support'))}
            <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
              {footerLink(t(lang, 'footer', 'contact'))}
              {footerLink(t(lang, 'footer', 'faq'))}
              {footerLink(t(lang, 'footer', 'warranty'))}
            </div>
          </div>
        </div>

        {/* Divider */}
        <div style={{ height: 1, background: 'linear-gradient(90deg,transparent,var(--bd2),transparent)', marginBottom: 28 }} />

        {/* Bottom row */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 12 }}>
          <p style={{ fontSize: '0.8rem', color: 'var(--txt3)' }}>{t(lang, 'footer', 'copy')}</p>
          <div style={{ display: 'flex', gap: 20 }}>
            {[t(lang, 'footer', 'privacy'), t(lang, 'footer', 'terms')].map(l => (
              <Link key={l} href="#" style={{ fontSize: '0.8rem', color: 'var(--txt3)', textDecoration: 'none' }}>{l}</Link>
            ))}
          </div>
        </div>
      </div>
    </footer>
  );
}
