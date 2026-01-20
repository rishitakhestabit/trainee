/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: '#007bff',
        danger: '#dc3545',
        warning: '#ffc107',
        success: '#28a745',
        dark: '#343a40',
      },
    },
  },
  plugins: [],
}