export default defineNuxtRouteMiddleware((to) => {
    const noHeaderRoutes = ['index']
    to.meta.layout = noHeaderRoutes.includes(to.name) ? 'login' : 'default'
})