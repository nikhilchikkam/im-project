/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        inter: ['Inter', 'sans-serif'],
        dm: ['"DM Sans"', 'sans-serif'],
      },
      colors: {
        primary: '#2480f8',
        secondary: '#185abc',
        accent: '#34A853',
        error: {
          DEFAULT: '#FF2E1F',
          light: '#FF9283',
          medium: '#FF6051',
        },
        warning: {
          light: '#FFFFC4',
          DEFAULT: '#FFFF9C',
          strong: '#f3f63d',
        },
        success: {
          light: '#82FF82',
          DEFAULT: '#1EEA1E',
          strong: '#00CC00',
        },
        neutral: {
          50: '#ffffff',
          100: '#e8e8e8',
          200: '#d2d2d2',
          300: '#bbbbbb',
          400: '#a4a4a4',
          500: '#8e8e8e',
          600: '#777777',
          700: '#606060',
          800: '#4a4a4a',
          900: '#333333',
        },
      },
      fontSize: {
        h1: ['48px', { lineHeight: '100%', letterSpacing: '-0.02em', fontWeight: '600' }],
        h2: ['24px', { lineHeight: '140%', letterSpacing: '-0.02em', fontWeight: '500' }],
        h3: ['20px', { lineHeight: '140%', letterSpacing: '-0.02em', fontWeight: '400' }],
        h4: ['18px', { lineHeight: '140%', letterSpacing: '-0.02em', fontWeight: '400' }],
        h5: ['16px', { lineHeight: '140%', letterSpacing: '-0.02em', fontWeight: '500' }],
        'h5-1': ['16px', { lineHeight: '140%', letterSpacing: '-0.02em', fontWeight: '400' }],
        h6: ['14px', { lineHeight: '140%', letterSpacing: '-0.02em', fontWeight: '400' }],
        h7: ['12px', { lineHeight: '140%', letterSpacing: '-0.02em', fontWeight: '400' }],
        h8: ['12px', { lineHeight: '140%', letterSpacing: '-0.02em', fontWeight: '500' }],
        p: ['16px', { lineHeight: '24px', fontWeight: '400' }],
        sideheading: ['18px', { lineHeight: '24px', fontWeight: '700' }],
      },
    },
  },
  plugins: [],
};
