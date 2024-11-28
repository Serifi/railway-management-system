import { defineStore } from 'pinia'

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
                role: "Admin",
            },
            {
                ssn: "3000241112",
                firstName: "Max",
                lastName: "Muster",
                password: "123456",
                department: "Maintenance",
                role: "Employee",
            },
            {
                ssn: "1000241122",
                firstName: "John",
                lastName: "Doe",
                password: "123456",
                department: "Crew",
                role: "Employee",
            },
            {
                ssn: "2000241142",
                firstName: "Dane",
                lastName: "Smith",
                password: "123456",
                department: "Maintenance",
                role: "Admin",
            },
            {
                ssn: "3000241162",
                firstName: "Max",
                lastName: "Muster",
                password: "123456",
                department: "Maintenance",
                role: "Employee",
            },
        ],
        roles: [
            { label: 'Mitarbeiter:in', value: 'Employee' },
            { label: 'Administrator:in', value: 'Admin' },
        ],
        departments: [
            { label: 'Wartung', value: 'Maintenance' },
            { label: 'Bordpersonal', value: 'Crew' },
        ],
    }),
    actions: {
        createEmployee(employee) {
            this.employees.push(employee)
        },

        editEmployee(employee) {
            const index = this.employees.findIndex(e => e.ssn === employee.ssn)
            if (index !== -1) this.employees[index] = { ...employee }
        },

        deleteEmployee(ssn) {
            const index = this.employees.findIndex(employee => employee.ssn === ssn)
            if (index !== -1) this.employees.splice(index, 1)
        },
    },
})