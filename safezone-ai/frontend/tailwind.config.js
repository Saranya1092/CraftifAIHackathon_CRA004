/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        navy: {
          900: '#0a0e1a',
          800: '#0d1224',
          700: '#111827',
          600: '#1a2236',
          500: '#1e2d47',
        },
        danger: {
          600: '#dc2626',
          500: '#ef4444',
          400: '#f87171',
        },
        warning: {
          600: '#d97706',
          500: '#f59e0b',
          400: '#fbbf24',
        },
      },
    },
  },
  plugins: [],
}
