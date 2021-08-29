import { resolve } from "path";
import reactRefresh from "@vitejs/plugin-react-refresh";
import reactSvgPlugin from "vite-plugin-react-svg";

/**
 * @type {import('vite').UserConfig}
 */
const config = {
  plugins: [reactRefresh(), reactSvgPlugin()],
  base: "/static/",
  root: "./src",
  build: {
    manifest: true,
    outDir: resolve("../static/dist"),
    emptyOutDir: true,
    rollupOptions: {
      input: ["./src/js/main.js", "./src/apps/monthly/main.tsx"],
    },
  },
};

export default config;
