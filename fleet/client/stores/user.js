import { defineStore } from 'pinia'

export const useUserStore = defineStore('user', {
    state: () => ({
        user: {
            ssn: "",
            firstName: "",
            lastName: "",
            role: ""
        },
        dummyUsers: [
            { username: "argjent", password: "password", ssn: "0000241102", firstName: "Argjent", lastName: "Serifi", role: "Admin" }
        ]
    }),
    getters: {
        getUser: (state) => state.user,
        getFullName: (state) => `${state.user.firstName} ${state.user.lastName}`,
        getDummyUsers: (state) => state.dummyUsers
    },
    actions: {
        authenticate(username, password) {
            const user = this.dummyUsers.find(u => u.username === username && u.password === password)
            if (user) {
                this.user = {
                    ssn: user.ssn,
                    firstName: user.firstName,
                    lastName: user.lastName,
                    role: user.role
                }
                return true
            }
            return false
        }
    }
})