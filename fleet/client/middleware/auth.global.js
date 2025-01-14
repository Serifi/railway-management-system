import { useUserStore } from '@/stores/user'

export default defineNuxtRouteMiddleware((to) => {
    // Check if the user is not authenticated and the target path is not already the login page
    if (!useUserStore().isAuthenticated && to.path !== '/')
        // Redirect the user to the login page if not authenticated
        return navigateTo('/')
})