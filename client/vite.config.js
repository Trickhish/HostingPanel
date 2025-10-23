import { defineConfig } from 'vite';

export default defineConfig({
  server: {
    allowedHosts: [
      'hosting.austerfortia.fr',
      'localhost'
    ]
  }
});