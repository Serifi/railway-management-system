export default defineNuxtRouteMiddleware((to) => {
    // Routes where the header should not be displayed
    const noHeaderRoutes = ['index']

    // Assign the 'login' layout if the route is in the noHeaderRoutes array, otherwise assign the 'default' layout to include the navigation header
    to.meta.layout = noHeaderRoutes.includes(to.name) ? 'login' : 'default'
})