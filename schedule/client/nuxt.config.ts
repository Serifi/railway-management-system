import Aura from '@primevue/themes/aura'

export default defineNuxtConfig({
    devtools: { enabled: false },
    modules: ['@primevue/nuxt-module', '@pinia/nuxt'],
    primevue: {
        options: {
            theme: {
                ripple: true,
                preset: Aura,
            }
        }
    },
    css: ['~/assets/tailwind.css'],
    postcss: {
        plugins: {
            tailwindcss: {},
            autoprefixer: {},
        },
    },
})