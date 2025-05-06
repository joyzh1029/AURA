import { defineConfig } from "vite";
import react from "@vitejs/plugin-react-swc";
import path from "path";
import { componentTagger } from "lovable-tagger";

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => ({
  server: {
    host: "::",
    port: 8080,
    proxy: {
      "/upload": {
        target: "http://localhost:8001",
        changeOrigin: true,
      },
      "/upload-video": {
        target: "http://localhost:8001",
        changeOrigin: true,
      },  
      "/upload-multiple": {
        target: "http://localhost:8001",
        changeOrigin: true,
      },
      "/upload-audio": {
        target: "http://localhost:8001",
        changeOrigin: true,
      },
    },
  },
  plugins: [
    react(),
    mode === "development" && componentTagger(),
  ].filter(Boolean),
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
}));
