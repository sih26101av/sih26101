/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'selector', // Using 'selector' for Tailwind v3.4.1+ instead of 'class'
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      fontFamily: { sans: ['Inter', 'system-ui', 'sans-serif'] },
      colors: {
        mospi: { navy: '#0f172a', blue: '#1e3a5f', steel: '#2d5986' },
      },
    },
  },
  plugins: [],
};
