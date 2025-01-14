import { defineStore } from 'pinia'
import apiClient from '@/utils/api'

const BASE_PATH = '/employees'

export const useEmployeeStore = defineStore('employee', {
    state: () => ({
        employees: [],
        roles: [
            { label: 'Employee', value: 'Employee' },
            { label: 'Admin', value: 'Admin' },
        ],
        departments: [
            { label: 'Maintenance', value: 'Maintenance' },
            { label: 'Crew', value: 'Crew' },
        ],
    }),
    actions: {
        async handleRequest(promise) {
            try {
                const response = await promise
                return response.data
            } catch (error) {
                throw error.response?.data || error
            }
        },

        async getEmployees() {
            const data = await this.handleRequest(apiClient.get(BASE_PATH))
            this.employees = data
        },

        async createEmployee(employee) {
            try {
                const data = await this.handleRequest(apiClient.post(BASE_PATH, employee))
                await this.getEmployees()
                return data
            } catch (error) {
                console.error('Error creating employee:', error)
                throw error
            }
        },

        async editEmployee(employee) {
            try {
                const data = await this.handleRequest(apiClient.put(`${BASE_PATH}/${employee.ssn}`, employee))
                await this.getEmployees()
                return data
            } catch (error) {
                console.error('Error editing employee:', error)
                throw error
            }
        },

        async deleteEmployee(ssn) {
            try {
                const data = await this.handleRequest(apiClient.delete(`${BASE_PATH}/${ssn}`))
                await this.getEmployees()
                return data
            } catch (error) {
                console.error('Error deleting employee:', error)
                throw error
            }
        },
    },
})