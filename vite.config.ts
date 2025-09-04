import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "");
  const target = env.VITE_API_BASE || ""; // e.g., https://hou-fin-nav-xxxxx-uc.a.run.app

  return {
    plugins: [react()],
    server: {
      port: 5173,
      proxy: target
        ? {
            "/api": {
              target,
              changeOrigin: true,
              rewrite: (p) => p.replace(/^\/api/, ""),
            },
          }
        : undefined,
    },
    resolve: { alias: { "@": "/src" } },
  };
});