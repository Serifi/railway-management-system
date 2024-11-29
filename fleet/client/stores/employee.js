import { defineStore } from 'pinia'
import axios from "axios"
import bcrypt from 'bcryptjs'

export const useEmployeeStore = defineStore('employee', {
    state: () => ({
        employees: [],
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
        async getEmployees() {
            try {
                const response = await axios.get('http://127.0.0.1:5000/employees')
                this.employees = response.data
            } catch (error) {
                console.error('Error fetching employees:', error)
            }
        },

        async createEmployee(employee) {
            try {
                const password = await bcrypt.hash(employee.password, 12)
                await axios.post('http://127.0.0.1:5000/employees', { ...employee, password: password })
                await this.getEmployees()
            } catch (error) {
                console.error('Error creating employee:', error.response?.data || error)
            }
        },

        async editEmployee(employee) {
            try {
                const password = await bcrypt.hash(employee.password, 12)
                await axios.put(`http://127.0.0.1:5000/employees/${employee.ssn}`, { ...employee, password: password })
                await this.getEmployees()
            } catch (error) {
                console.error('Error editing employee:', error.response?.data || error)
            }
        },

        async deleteEmployee(ssn) {
            try {
                await axios.delete(`http://127.0.0.1:5000/employees/${ssn}`)
                await this.getEmployees()
            } catch (error) {
                console.error('Error deleting employee:', error.response?.data || error)
            }
        },
    },
})