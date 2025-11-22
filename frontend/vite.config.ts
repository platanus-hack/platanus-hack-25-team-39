import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { tanstackRouter } from "@tanstack/router-plugin/vite";

export default defineConfig({
  plugins: [tanstackRouter(), react()],
  server: {
    proxy: {
      "/.auth": {
        target: process.env.VITE_PROXY_BACKEND_URL,
        changeOrigin: true,
        secure: false,
        xfwd: true,
      },
      "/api": {
        target: process.env.VITE_PROXY_BACKEND_URL,
        changeOrigin: true,
        secure: false,
        xfwd: true,
      },
    },
  },
});
