import {defineNuxtPlugin} from 'nuxt/app'
import CountryFlag from 'vue-country-flag-next'
import apiClient from "~/utils/api.js"
import { useUserStore } from "~/stores/user.js"
import { library } from '@fortawesome/fontawesome-svg-core'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import { fas } from '@fortawesome/free-solid-svg-icons'
library.add(fas)

export default defineNuxtPlugin((nuxtApp) => {
    useUserStore().initialize()

    nuxtApp.vueApp
        .component('FontAwesomeIcon', FontAwesomeIcon)
        .component('CountryFlag', CountryFlag)

    nuxtApp.provide('apiClient', apiClient)
})