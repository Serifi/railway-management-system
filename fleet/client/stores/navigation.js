import { defineStore } from 'pinia'
import { useUserStore } from './user'

export const useNavigationStore = defineStore('navigation', {
    state: () => ({
        navItems: [
            { name: 'trains', page: 'trains', icon: 'train', roles: ['Employee', 'Admin'] },
            { name: 'carriages', page: 'carriages', icon: 'trailer', roles: ['Employee', 'Admin'] },
            { name: 'maintenances', page: 'maintenances', icon: 'tools', roles: ['Employee', 'Admin'] },
            { name: 'employees', page: 'employees', icon: 'users', roles: ['Admin'] },
        ],
    }),
    getters: {
        getFilteredNavItems: (state) => {
            return state.navItems.filter((item) =>
                item.roles.includes(useUserStore().getUserRole)
            )
        },
    },
})