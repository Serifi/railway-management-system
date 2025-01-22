import { defineStore } from 'pinia'
import axios from "axios";

export const useUserStore = defineStore('user', {
    state: () => ({
        // Aktuell eingeloggter Benutzer
        user: {
            ssn: "",
            firstName: "",
            lastName: "",
            role: "",
            department: "",
            rideExecutions: []
        },
        dummyUsers: [


        ]
    }),
    getters: {
        getUser: (state) => state.user,
        getFullName: (state) => `${state.user.firstName} ${state.user.lastName}`,
        getDummyUsers: (state) => state.dummyUsers
    },
    actions: {
        // Authentifiziert einen Benutzer basierend auf Benutzername und Passwort
         async authenticate(username, password) {
            await this.fetchEmployees();
            const user = this.dummyUsers.find(u => u.username === username && u.password === password)
            if (user) {
                // Setzt den Zustand für den aktuell eingeloggten Benutzer
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
             //Employees vom Server holen
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