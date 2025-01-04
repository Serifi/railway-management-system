import { createI18n } from 'vue-i18n'

export default defineNuxtPlugin(async ({ vueApp }) => {
    const enMessages = await import('../locales/en.json')
    const deMessages = await import('../locales/de.json')

    const i18n = createI18n({
        legacy: false,
        globalInjection: true,
        locale: 'en',
        fallbackLocale: 'en',
        messages: {
            en: enMessages.default,
            de: deMessages.default,
        },
    })

    vueApp.use(i18n)
})