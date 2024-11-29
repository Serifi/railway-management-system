import { useUserStore } from '@/stores/user'

export default defineNuxtRouteMiddleware((to) => {
    const userStore = useUserStore()
    if (!userStore.getSSN && to.path !== '/') return navigateTo('/')
})