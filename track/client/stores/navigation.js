import { defineStore } from 'pinia'
import { useUserStore } from './user'

export const useNavigationStore = defineStore('navigation', {
    state: () => ({
        navItems: [
            { name: 'Bahnhöfe', page: 'train-stations', icon: 'train', roles: ['Employee', 'Admin'] },
            { name: 'Strecken', page: 'sections', icon: 'trailer', roles: ['Employee', 'Admin'] },
            { name: 'Warnungen', page: 'warnings', icon: 'tools', roles: ['Employee', 'Admin'] },
            { name: 'Mitarbeiter:innen', page: 'employees', icon: 'users', roles: ['Admin'] },
        ],
    }),
    getters: {
        getNavItems: (state) => {
            return state.navItems.filter((item) => item.roles.includes(useUserStore().getUserRole))
        },
    },
})