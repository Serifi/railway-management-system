import { defineStore } from 'pinia'
import { useUserStore } from './user'

export const useNavigationStore = defineStore('navigation', {
    state: () => ({
        navItems: [
            { name: 'Züge', page: 'trains', icon: 'train', roles: ['Employee', 'Admin'] },
            { name: 'Wägen', page: 'carriages', icon: 'trailer', roles: ['Employee', 'Admin'] },
            { name: 'Wartungen', page: 'maintenances', icon: 'tools', roles: ['Employee', 'Admin'] },
            { name: 'Mitarbeiter:innen', page: 'employees', icon: 'users', roles: ['Admin'] },
        ],
    }),
    getters: {
        getNavItems: (state) => {
            return state.navItems.filter((item) => item.roles.includes(useUserStore().getUserRole))
        },
    },
})