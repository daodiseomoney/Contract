import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

export default defineConfig({
  plugins: [vue()],
  css: {
    postcss: './postcss.config.js'
  },
  resolve: {
    alias: {
      '@': resolve(__dirname, '.'),
    },
  },
  build: {
    outDir: 'static',
    assetsDir: 'js',
    emptyOutDir: false,
    rollupOptions: {
      input: resolve(__dirname, 'main.js'),
      output: {
        entryFileNames: 'js/main.js',
        chunkFileNames: 'js/[name].js',
        assetFileNames: (assetInfo) => {
          if (assetInfo.name && assetInfo.name.endsWith('.png')) {
            return 'images/[name][extname]'
          }
          return 'css/[name].[ext]'
        }
      }
    }
  },
  server: {
    port: 3000
  }
})