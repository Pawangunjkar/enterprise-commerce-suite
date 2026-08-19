/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["../../apps/**/*.{ts,tsx}", "../../packages/ui-components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        saffron: "#FF9933",
        indiaGreen: "#138808",
        navy: "#0B1F3A"
      }
    }
  },
  plugins: []
};
