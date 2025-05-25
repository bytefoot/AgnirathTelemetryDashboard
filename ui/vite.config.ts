import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';
import tailwindcss from '@tailwindcss/vite';

export default defineConfig({
  plugins: [
    tailwindcss(),
    sveltekit(),
  ],
  resolve: {
    alias: {
      "plotly.js-dist": "plotly.js-basic-dist-min",
      lodash: "lodash-es",
    },
  }
});