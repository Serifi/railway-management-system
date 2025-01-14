import { defineStore } from 'pinia'
import apiClient from '@/utils/api'
import { useTrainStore } from '@/stores/train'

const BASE_PATH = '/fleet/maintenances'

export const useMaintenanceStore = defineStore('maintenance', {
    state: () => ({
        maintenances: [],
        maintenancesLoading: false,
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

        async initialize() {
            try {
                await this.getTrains()
                //await this.getEmployees()
                await this.getMaintenances()
            } catch (error) {
                console.error('Error initializing maintenance store:', error)
            }
        },

        async getMaintenances() {
            this.maintenancesLoading = true
            try {
                const data = await this.handleRequest(apiClient.get(BASE_PATH))
                this.maintenances = data
            } catch (error) {
                console.error('Error fetching maintenances:', error)
                throw error
            } finally {
                this.maintenancesLoading = false
            }
        },

        async createMaintenance(maintenance) {
            try {
                const data = await this.handleRequest(apiClient.post(BASE_PATH, maintenance))
                await this.getMaintenances()
                return data
            } catch (error) {
                console.error('Error creating maintenance:', error)
                throw error
            }
        },

        async editMaintenance(maintenance) {
            try {
                const data = await this.handleRequest(apiClient.put(`${BASE_PATH}/${maintenance.maintenanceID}`, maintenance))
                await this.getMaintenances()
                return data
            } catch (error) {
                console.error('Error editing maintenance:', error)
                throw error
            }
        },

        async deleteMaintenance(maintenanceID) {
            try {
                const data = await this.handleRequest(apiClient.delete(`${BASE_PATH}/${maintenanceID}`))
                await this.getMaintenances()
                return data
            } catch (error) {
                console.error('Error deleting maintenance:', error)
                throw error
            }
        },

        async getTrains() {
            const trainStore = useTrainStore()
            try {
                await trainStore.getTrains()
            } catch (error) {
                console.error('Error fetching trains from trainStore:', error)
                throw error
            }
        },

        /*async getEmployeees() {
            const employeeStore = useEmployeeStore()
            try {
                await employeeStore.getEmployees()
            } catch (error) {
                console.error('Error fetching employees from employeeStore:', error)
                throw error
            }
        }*/
    },
})