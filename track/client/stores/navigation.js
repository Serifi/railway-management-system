import { defineStore } from 'pinia'
import { useUserStore } from './user'

export const useNavigationStore = defineStore('navigation', {
    state: () => ({
        navItems: [
            { name: 'Bahnhöfe', page: 'train-stations', icon: 'location-dot', roles: ['Employee', 'Admin'] },
            { name: 'Abschnitte', page: 'sections', icon: 'road-circle-exclamation', roles: ['Employee', 'Admin'] },
            { name: 'Strecken', page: 'tracks', icon: 'route', roles: ['Employee', 'Admin'] },
            { name: 'Mitarbeiter:innen', page: 'employees', icon: 'users', roles: ['Admin'] },
        ],
    }),
    getters: {
        getNavItems: (state) => {
            return state.navItems.filter((item) => item.roles.includes(useUserStore().getUserRole))
        },
    },
})