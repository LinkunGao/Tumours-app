import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import path from "path";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    vue({
      template: {
        compilerOptions: {
          isCustomElement: (tag) => {
            return tag === "ion-icon"; // (return true)
          },
        },
      },
    }),
  ],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "src"),
    },
  },
  base: "/NRRD_Segmentation_Tool/",
  build: {
    outDir: "./build",
  },
  server: {
    host: "0.0.0.0",
    // proxy: {
    //   // 本地开发环境通过代理实现跨域，生产环境使用 nginx 转发
    //   // 正则表达式写法
    //   "^/": {
    //     target: "https://github.com/LinkunGao/copper3d-datasets/", // 后端服务实际地址
    //     changeOrigin: true, //开启代理
    //     // rewrite: (path) => path.replace(/^\/LinkunGao/, ""),
    //   },
    // },
  },
});
