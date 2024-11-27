import { useUserStore } from '@/stores/user'

export default defineNuxtRouteMiddleware((to) => {
    const userStore = useUserStore()
    if (!userStore.user.ssn && to.path !== '/') return navigateTo('/')
})