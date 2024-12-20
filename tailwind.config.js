// tailwind.config.js
module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'blackjack-bg': '#111827', // Dark background color
        'blackjack-card': '#1F2937', // Card background color
        'blackjack-blue': '#60A5FA', // Blue accent color
        'blackjack-green': '#10B981', // Green button color
        'blackjack-orange': '#F97316', // Orange accent color
        'blackjack-yellow': '#FBBF24', // Yellow accent color
        'blackjack-red': '#EF4444', // Red accent color
      },
      animation: {
        'fade-in-out': 'fadeInOut 3s ease-in-out',
      },
      keyframes: {
        fadeInOut: {
          '0%, 100%': { opacity: 0 },
          '10%, 90%': { opacity: 1 },
        },
      },
    },
  },
  plugins: [],
}

