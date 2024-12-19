import { defineStore } from 'pinia'
import axios from "axios"
import bcrypt from "bcryptjs"

export const useUserStore = defineStore('user', {
    state: () => ({
        user: {firstName: 'Kadir', lastName: 'Demir', password: '1234', username: 'kadir.demir', ssn: 1234310119, role: 'Admin', department: 'Crew'},
    }),
    getters: {
        getSSN: (state) => state.user ? state.user.ssn : '',
        getFullName: (state) => state.user ? `${state.user.firstName} ${state.user.lastName}` : "",
        getUserRole: (state) => state.user ? state.user.role : 'Guest'
    },
    actions: {
        async login(username, password) {
            try {
                //const hashedPassword = await bcrypt.hash(password, 12)
                //await axios.post(`http://127.0.0.1:5000/employees/login`, { username: username, password: password })
                //this.user = await this.getEmployee(username)
                return true
            } catch (error) {
                //console.error("Login failed:", error)
                //this.user = null
                return false
            }
        },
        logout() {
            //this.user = null
        },
        async getEmployee(username) {
            try {
                const response = await axios.get(`http://127.0.0.1:5000/employees/${username}`)
                return response.data
            } catch (error) {
                console.error(`Error fetching employee with username ${username}:`, error)
                throw error
            }
        },
    }
})