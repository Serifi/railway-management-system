import Preset from './assets/theme'

export default defineNuxtConfig({
    devtools: { enabled: false },
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
        '~/assets/button.css',
        'primeicons/primeicons.css',
        '@fortawesome/fontawesome-free/css/all.css'
    ],
    postcss: {
        plugins: {
            tailwindcss: {},
            autoprefixer: {},
        },
    },
})