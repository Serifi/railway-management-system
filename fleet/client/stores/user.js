// stores/user.js
import { defineStore } from 'pinia'
import apiClient from '@/utils/api' // Importieren der Axios-Instanz

export const useUserStore = defineStore('user', {
    state: () => ({
        user: null,
        token: null, // Neuer Zustand für den Token
    }),
    getters: {
        getSSN: (state) => state.user ? state.user.ssn : '',
        getFullName: (state) => state.user ? `${state.user.firstName} ${state.user.lastName}` : "",
        getUserRole: (state) => state.user ? state.user.role : 'Guest',
        isAuthenticated: (state) => !!state.token,
    },
    actions: {
        // Initialisierung des Stores mit einem gespeicherten Token
        initialize() {
            if (process.client) { // Sicherstellen, dass wir auf der Client-Seite sind
                const token = localStorage.getItem('auth_token')
                if (token) {
                    this.token = token
                    // Laden der Benutzerdaten basierend auf dem Token
                    // Annahme: Der Username ist im gespeicherten User oder muss separat gespeichert werden
                    // Hier speichern wir den Username zusätzlich im localStorage
                    const username = localStorage.getItem('username')
                    if (username) {
                        this.getEmployee(username)
                    }
                }
            }
        },

        async login(username, password) {
            try {
                const response = await apiClient.post(`/employees/login`, {
                    username,
                    password
                })
                if (response.data.token) {
                    this.token = response.data.token
                    if (process.client) { // Sicherstellen, dass wir auf der Client-Seite sind
                        localStorage.setItem('auth_token', this.token)
                        localStorage.setItem('username', username) // Username speichern
                    }
                    // Laden der Benutzerdaten
                    this.user = await this.getEmployee(username)
                    return true
                }
                return false
            } catch (error) {
                console.error("Login failed:", error.response?.data || error)
                this.user = null
                this.token = null
                if (process.client) { // Sicherstellen, dass wir auf der Client-Seite sind
                    localStorage.removeItem('auth_token')
                    localStorage.removeItem('username')
                }
                return false
            }
        },

        logout() {
            this.user = null
            this.token = null
            if (process.client) { // Sicherstellen, dass wir auf der Client-Seite sind
                localStorage.removeItem('auth_token')
                localStorage.removeItem('username')
            }
        },

        async getEmployee(username) {
            try {
                const response = await apiClient.get(`/employees/${username}`)
                this.user = response.data
                return response.data
            } catch (error) {
                console.error(`Error fetching employee with username ${username}:`, error.response?.data || error)
                throw error
            }
        },
    }
})