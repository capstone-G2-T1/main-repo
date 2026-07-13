import type { Config } from 'tailwindcss';

const config: Config = {
  content: [
    './app/**/*.{ts,tsx}',
    './components/**/*.{ts,tsx}',
    './lib/**/*.{ts,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        bg: {
          0: 'var(--bg0)',
          1: 'var(--bg1)',
          2: 'var(--bg2)',
          3: 'var(--bg3)',
        },
        border: {
          DEFAULT: 'var(--bd)',
          bright:  'var(--bd2)',
        },
        cyan:   { DEFAULT: 'var(--cyan)', 2: 'var(--cyan2)' },
        orange: 'var(--orange)',
        gold:   'var(--gold)',
        txt: {
          DEFAULT: 'var(--txt)',
          2: 'var(--txt2)',
          3: 'var(--txt3)',
        },
      },
      fontFamily: {
        display: ['Orbitron', 'monospace'],
        body:    ['Exo 2', 'sans-serif'],
        arabic:  ['Noto Sans Arabic', 'sans-serif'],
      },
      borderRadius: {
        sm: 'var(--radius)',
        lg: 'var(--radius-lg)',
      },
      backgroundImage: {
        'hero-radial': 'radial-gradient(ellipse 80% 60% at 20% 50%, rgba(0,201,255,0.06) 0%, transparent 60%), radial-gradient(ellipse 60% 60% at 80% 60%, rgba(255,94,26,0.05) 0%, transparent 60%)',
        'card-hover':  'linear-gradient(135deg, rgba(0,201,255,0.05), transparent)',
      },
      boxShadow: {
        cyan:  '0 0 28px rgba(0, 201, 255, 0.35)',
        card:  '0 20px 40px rgba(0, 0, 0, 0.4)',
      },
      animation: {
        'fade-up':   'fadeUp 0.6s ease both',
        'fade-in':   'fadeIn 0.4s ease both',
        'slide-l':   'slideFromLeft 0.55s ease both',
        'scale-in':  'scaleIn 0.45s ease both',
        'pulse-cyan':'pulseCyan 2s ease-in-out infinite',
        'scan-y':    'scanY 8s linear infinite',
      },
    },
  },
  plugins: [],
};

export default config;
