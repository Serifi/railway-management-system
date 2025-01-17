import { defineStore } from 'pinia'

export const useNavigationStore = defineStore('navigation', {
    state: () => ({
        navItems: [
            { name: 'Fahrtdurchführungen', page: 'rideExecutions', icon: 'train' },
            { name: 'Haltepläne', page: 'stopplans', icon: 'trailer' },
            { name: 'Mitarbeiter:innen', page: 'employees', icon: 'users' },
        ],
        navItems2: [
            { name: 'Fahrtdurchführungen', page: 'rideExecutions', icon: 'train' },
            { name: 'Haltepläne', page: 'stopplans', icon: 'trailer' },

        ]
    }),
    getters: {
        getNavItems: (state) => state.navItems,
        getNavItems2: (state) => state.navItems2
    }
})