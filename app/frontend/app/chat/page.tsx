'use client';

import { useState, useRef, useEffect } from 'react';
import { useLanguage } from '@/components/layout/LanguageProvider';
import { t } from '@/lib/utils';
import Button from '@/components/ui/Button';

interface Message {
  role: 'bot' | 'user';
  text: string;
  ts: Date;
}

export default function ChatPage() {
  const { lang, isRTL } = useLanguage();
  const [msgs, setMsgs]   = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    setMsgs([{ role: 'bot', text: t(lang, 'chat', 'welcome'), ts: new Date() }]);
  }, [lang]);

  useEffect(() => { endRef.current?.scrollIntoView({ behavior: 'smooth' }); }, [msgs]);

  const send = () => {
    const text = input.trim();
    if (!text) return;
    setMsgs(m => [
      ...m,
      { role: 'user', text, ts: new Date() },
      { role: 'bot',  text: t(lang, 'chat', 'reply'), ts: new Date() },
    ]);
    setInput('');
    // TODO: await sendChatMessage({ message: text, lang })
  };

  return (
    <>
      <section style={{ padding: '80px 0 40px', background: 'var(--bg1)' }}>
        <div style={{ maxWidth: 800, margin: '0 auto', padding: '0 24px', textAlign: 'center' }}>
          <div style={{ fontFamily: "'Orbitron', monospace", fontSize: '0.65rem', fontWeight: 700, letterSpacing: '0.2em', textTransform: 'uppercase', color: 'var(--cyan)', marginBottom: 14 }}>
            {t(lang, 'chat', 'status')}
          </div>
          <h1 style={{ fontFamily: "'Orbitron', monospace", fontSize: 'clamp(1.6rem,4vw,2.6rem)', fontWeight: 700, color: 'var(--txt)', marginBottom: 12 }}>
            {t(lang, 'chat', 'title')}
          </h1>
        </div>
      </section>

      <section style={{ padding: '0 0 88px' }}>
        <div style={{ maxWidth: 800, margin: '0 auto', padding: '0 24px' }}>
          {/* Messages */}
          <div style={{
            background: 'var(--bg2)', border: '1px solid var(--bd)',
            borderRadius: 'var(--radius-lg)', overflow: 'hidden',
            display: 'flex', flexDirection: 'column', minHeight: 480,
          }}>
            <div style={{ flex: 1, overflowY: 'auto', padding: 24, display: 'flex', flexDirection: 'column', gap: 16 }}>
              {msgs.map((m, i) => (
                <div key={i} style={{
                  display: 'flex',
                  justifyContent: m.role === 'user' ? (isRTL ? 'flex-start' : 'flex-end') : (isRTL ? 'flex-end' : 'flex-start'),
                }}>
                  <div style={{
                    maxWidth: '72%', padding: '12px 16px', borderRadius: 14,
                    background: m.role === 'user' ? 'linear-gradient(135deg,var(--cyan),var(--cyan2))' : 'var(--bg3)',
                    color: m.role === 'user' ? '#000' : 'var(--txt)',
                    fontSize: '0.92rem', lineHeight: 1.55,
                    borderBottomRightRadius: m.role === 'user' && !isRTL ? 4 : 14,
                    borderBottomLeftRadius:  m.role === 'bot'  && !isRTL ? 4 : 14,
                  }}>
                    {m.text}
                  </div>
                </div>
              ))}
              <div ref={endRef} />
            </div>

            {/* Input */}
            <div style={{ padding: '16px 20px', borderTop: '1px solid var(--bd)', display: 'flex', gap: 10 }}>
              <input
                value={input}
                onChange={e => setInput(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && send()}
                placeholder={t(lang, 'chat', 'placeholder')}
                style={{
                  flex: 1, background: 'var(--bg3)', border: '1px solid var(--bd)',
                  color: 'var(--txt)', padding: '12px 16px', borderRadius: 'var(--radius)',
                  fontFamily: 'inherit', fontSize: '0.92rem', outline: 'none',
                }}
              />
              <Button variant="primary" onClick={send}>
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                  <path d="M5 12h14M12 5l7 7-7 7"/>
                </svg>
              </Button>
            </div>
          </div>
        </div>
      </section>
    </>
  );
}
