export default {
  content: [
    "./components/**/*.{vue,js,ts}",
    "./main.js",
    "./App.vue",
    "./*.{vue,js,ts}",
    "../../../templates/**/*.html"
  ],
  theme: {
    extend: {
      colors: {
        violet: {
          400: '#8F43E9',
          500: '#8F43E9',
          600: '#8F43E9'
        }
      }
    },
  },
  plugins: [],
}