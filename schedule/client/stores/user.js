import { defineStore } from 'pinia'
import axios from "axios";

export const useUserStore = defineStore('user', {
    state: () => ({
        user: {
            ssn: "",
            firstName: "",
            lastName: "",
            role: "",
            department: "",
            rideExecutions: []
        },
        dummyUsers: [
            //{ username: "argjent", password: "password", ssn: "0000241102", firstName: "Argjent", lastName: "Serifi", role: "Admin" },
            //{ username: "ömer", password: "password", ssn: "0000291102", firstName: "Ömer", lastName: "Türkoglu", role: "Admin" }

        ]
    }),
    getters: {
        getUser: (state) => state.user,
        getFullName: (state) => `${state.user.firstName} ${state.user.lastName}`,
        getDummyUsers: (state) => state.dummyUsers
    },
    actions: {
         async authenticate(username, password) {
            await this.fetchEmployees();
            const user = this.dummyUsers.find(u => u.username === username && u.password === password)
            if (user) {
                this.user = {
                    ssn: user.ssn,
                    firstName: user.firstName,
                    lastName: user.lastName,
                    role: user.role,
                    department: user.department,
                    rideExecutions: user.rideExecutions
                }
                return true
            }
            return false
        },
        async fetchEmployees() {
            try {
                const response = await axios.get("http://127.0.0.1:5000/employees");
                console.log('API Response:', response.data);
                this.dummyUsers = response.data;
            } catch (error) {
                console.error("Fehler beim Laden der Daten", error);
            }
        }
    }
})