// stores/user.js
import { defineStore } from 'pinia'
import apiClient from '@/utils/api'

const BASE_PATH = '/employees'

export const useUserStore = defineStore('user', {
    state: () => ({
        user: null,
        token: null,
    }),
    getters: {
        getSSN: (state) => state.user ? state.user.ssn : '',
        getFullName: (state) => state.user ? `${state.user.firstName} ${state.user.lastName}` : "",
        getUserRole: (state) => state.user ? state.user.role : 'Guest',
        isAuthenticated: (state) => !!state.token,
    },
    actions: {
        async handleRequest(promise) {
            try {
                const response = await promise
                return response.data
            } catch (error) {
                throw error.response?.data || error
            }
        },

        initialize() {
            if (process.client) {
                const token = localStorage.getItem('auth_token')
                const username = localStorage.getItem('username')
                if (token) {
                    this.token = token
                    if (username) {
                        this.getEmployee(username)
                    }
                }
            }
        },

        async login(username, password) {
            try {
                const response = await apiClient.post(`${BASE_PATH}/login`, {
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
                const response = await this.handleRequest(apiClient.get(`${BASE_PATH}/${username}`))
                this.user = response
                return response
            } catch (error) {
                console.error(`Error fetching employee with username ${username}:`, error)
                throw error
            }
        },
    }
})