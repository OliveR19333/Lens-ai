/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        // Brand palette pulled from the spec document styling.
        gas: {
          navy: '#1B3A5C',
          blue: '#7BAFD4',
          sky: '#D5E8F0'
        }
      },
      // Respect the iPhone safe area (notch / home indicator).
      padding: {
        safe: 'env(safe-area-inset-bottom)'
      }
    }
  },
  plugins: []
}
