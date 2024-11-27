import { defineStore } from 'pinia';

export const useEmployeeStore = defineStore('employee', {
    state: () => ({
        employees: [
            {
                ssn: "1000241102",
                firstName: "John",
                lastName: "Doe",
                password: "123456",
                department: "Crew",
                role: "Employee",
            },
            {
                ssn: "2000241102",
                firstName: "Dane",
                lastName: "Smith",
                password: "123456",
                department: "Maintenance",
                role: "Administrator",
            },
            {
                ssn: "3000241102",
                firstName: "Max",
                lastName: "Muster",
                password: "123456",
                department: "Maintenance",
                role: "Employee",
            },
        ],
    }),
});
