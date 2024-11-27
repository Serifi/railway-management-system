import { defineStore } from 'pinia'

export const useNavigationStore = defineStore('navigation', {
    state: () => ({
        navItems: [
            { name: 'Züge', page: 'trains', icon: 'train' },
            { name: 'Wägen', page: 'carriages', icon: 'trailer' },
            { name: 'Wartungen', page: 'maintenances', icon: 'tools' },
            { name: 'Mitarbeiter:innen', page: 'employees', icon: 'users' },
        ]
    }),
    getters: {
        getNavItems: (state) => state.navItems
    }
})