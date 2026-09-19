/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class', // useTheme hook toggles .dark class on <html>
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Poppins', '"Noto Sans"', '"Noto Sans Devanagari"', 'system-ui', 'sans-serif'],
        serif: ['Merriweather', '"Noto Serif Devanagari"', 'Georgia', 'serif'],
      },
      colors: {
        mospi: { navy: '#0f172a', blue: '#1e3a5f', steel: '#2d5986' },
        // Government of India portal palette (GIGW-style)
        gov: {
          ink: '#0a1a33',
          navy: '#0b2a55',
          blue: '#12407f',
          sky: '#2f6fbf',
          saffron: '#ff9933',
          'saffron-deep': '#e67e14',
          green: '#138808',
          'green-deep': '#0e6b06',
          gold: '#c9a227',
          // Cool institutional surfaces (matches the reference dashboards)
          paper: '#f4f7fb',
          line: '#e4eaf2',
        },
        // Categorical accents for KPI tiles, status chips and charts.
        // Kept as a named scale so charts and tiles never drift apart.
        accent: {
          blue: '#2563eb',
          'blue-soft': '#eef4ff',
          orange: '#f97316',
          'orange-soft': '#fff3e8',
          green: '#10b981',
          'green-soft': '#e7f7f0',
          purple: '#8b5cf6',
          'purple-soft': '#f2edff',
          sky: '#60a5fa',
          rose: '#e11d48',
          'rose-soft': '#ffeef2',
        },
      },
      boxShadow: {
        gov: '0 1px 2px rgba(10,26,51,0.06), 0 8px 24px -12px rgba(10,26,51,0.18)',
        'gov-lg': '0 2px 4px rgba(10,26,51,0.06), 0 22px 48px -20px rgba(10,26,51,0.35)',
      },
      keyframes: {
        'drawer-in': {
          '0%': { transform: 'translateX(-100%)' },
          '100%': { transform: 'translateX(0)' },
        },
        'fade-up': {
          '0%': { opacity: '0', transform: 'translateY(16px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        'fade-in': { '0%': { opacity: '0' }, '100%': { opacity: '1' } },
        'scale-in': {
          '0%': { opacity: '0', transform: 'scale(0.96) translateY(8px)' },
          '100%': { opacity: '1', transform: 'scale(1) translateY(0)' },
        },
        shimmer: { '0%': { backgroundPosition: '-200% 0' }, '100%': { backgroundPosition: '200% 0' } },
        float: { '0%,100%': { transform: 'translateY(0)' }, '50%': { transform: 'translateY(-10px)' } },
        marquee: { '0%': { transform: 'translateX(0)' }, '100%': { transform: 'translateX(-50%)' } },
        'grow-x': { '0%': { transform: 'scaleX(0)' }, '100%': { transform: 'scaleX(1)' } },
        // Chat message entrance — short and subtle, it fires on every bubble.
        'bubble-in': {
          '0%': { opacity: '0', transform: 'translateY(6px) scale(0.985)' },
          '100%': { opacity: '1', transform: 'translateY(0) scale(1)' },
        },
      },
      animation: {
        'drawer-in': 'drawer-in 0.28s cubic-bezier(0.2,0.7,0.2,1) both',
        'fade-up': 'fade-up 0.7s cubic-bezier(0.2,0.7,0.2,1) both',
        'fade-in': 'fade-in 0.6s ease-out both',
        'scale-in': 'scale-in 0.35s cubic-bezier(0.2,0.7,0.2,1) both',
        shimmer: 'shimmer 1.6s linear infinite',
        float: 'float 6s ease-in-out infinite',
        marquee: 'marquee 40s linear infinite',
        'spin-slow': 'spin 60s linear infinite',
        'grow-x': 'grow-x 0.9s cubic-bezier(0.2,0.7,0.2,1) both',
        'bubble-in': 'bubble-in 0.26s cubic-bezier(0.2,0.7,0.2,1) both',
      },
    },
  },
  plugins: [],
};
