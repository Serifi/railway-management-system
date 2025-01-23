// stores/maintenance.js
import { defineStore } from 'pinia'
import apiClient from '@/utils/api'

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
                const payload = {
                    employeeSSN: maintenance.employeeSSN, // Geändertes Feld
                    trainID: maintenance.trainID,
                    from_time: maintenance.from_time,
                    to_time: maintenance.to_time
                }
                const data = await this.handleRequest(apiClient.post(BASE_PATH, payload))
                await this.getMaintenances()
                return data
            } catch (error) {
                console.error('Error creating maintenance:', error)
                throw error
            }
        },

        async editMaintenance(maintenance) {
            try {
                const payload = {
                    employeeSSN: maintenance.employeeSSN, // Geändertes Feld
                    trainID: maintenance.trainID,
                    from_time: maintenance.from_time,
                    to_time: maintenance.to_time
                }
                const data = await this.handleRequest(apiClient.put(`${BASE_PATH}/${maintenance.maintenanceID}`, payload))
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
    },
})