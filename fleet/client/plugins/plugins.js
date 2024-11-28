import {defineNuxtPlugin} from 'nuxt/app'
import CountryFlag from 'vue-country-flag-next'
import ToastService from 'primevue/toastservice'

import { library } from '@fortawesome/fontawesome-svg-core'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import { fas } from '@fortawesome/free-solid-svg-icons'
library.add(fas)

export default defineNuxtPlugin((nuxtApp) => {
    nuxtApp.vueApp.use(ToastService)
        .component('FontAwesomeIcon', FontAwesomeIcon)
        .component('CountryFlag', CountryFlag)
})