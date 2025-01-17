import Preset from './assets/theme'

export default defineNuxtConfig({
  devtools: { enabled: false },

  app: {
      head: {
          title: 'Scotty',
          charset: 'utf-8',
          viewport: 'width=device-width, initial-scale=1',
          meta: [{ name: 'description', content: 'Flotten-Informationssystem' }]
      }
  },

  modules: [
      '@primevue/nuxt-module',
      '@nuxtjs/tailwindcss',
      '@pinia/nuxt'
  ],

  primevue: {
      autoImport: true,
      usePrimeVue: true,
      options: {
          theme: {
              ripple: true,
              preset: Preset,
              options: {
                  darkModeSelector: false
              },
          }
      }
  },

  css: [
      '~/assets/tailwind.css',
      'primeicons/primeicons.css',
      '@fortawesome/fontawesome-free/css/all.css'
  ],

  postcss: {
      plugins: {
          tailwindcss: {},
          autoprefixer: {},
      },
  },

  plugins: [
      '~/plugins/i18n.config.js',
  ],

  compatibilityDate: '2025-01-17'
})