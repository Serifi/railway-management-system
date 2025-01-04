import { useUserStore } from '@/stores/user'

export default defineNuxtRouteMiddleware((to) => {
    if (!useUserStore().isAuthenticated && to.path !== '/') return navigateTo('/')
})