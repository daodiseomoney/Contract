export default {
  content: [
    "./src/layer3_external_interfaces/ui/**/*.{vue,js,ts,jsx,tsx,html}",
    "./templates/**/*.html"
  ],
  safelist: [
    'glass-card-neon',
    'glass-card-reference',
    'sidebar-icon-glass',
    'sidebar-icon-active-glass',
    'h-full',
    'gap-6',
    'rounded-full',
    'backdrop-blur',
    'bg-gradient-to-r',
    'from-yellow-500',
    'to-yellow-600',
    'filter',
    'drop-shadow'
  ],
  theme: {
    extend: {
      colors: {
        violet: {
          400: '#8F43E9',
          500: '#8F43E9'
        }
      }
    },
  },
  plugins: [],
}