import { defineStore } from 'pinia'
import axios from 'axios'

export const useMaintenanceStore = defineStore('maintenance', {
    state: () => ({
        maintenances: [],
        maintenancesLoading: false,
        trains: [],
        employees: []
    }),
    actions: {
        async getMaintenances() {
            this.maintenancesLoading = true
            try {
                const response = await axios.get('http://127.0.0.1:5000/fleet/maintenances')
                this.maintenances = response.data
            } catch (error) {
                console.error('Error fetching maintenances:', error)
            } finally {
                this.maintenancesLoading = false
            }
        },
        async createMaintenance(maintenance) {
            try {
                await axios.post('http://127.0.0.1:5000/fleet/maintenances', maintenance)
                await this.getMaintenances()
            } catch (error) {
                console.error('Error creating maintenance:', error.response?.data || error)
                throw error
            }
        },
        async editMaintenance(maintenance) {
            try {
                await axios.put(`http://127.0.0.1:5000/fleet/maintenances/${maintenance.maintenanceID}`, maintenance)
                await this.getMaintenances()
            } catch (error) {
                console.error('Error editing maintenance:', error.response?.data || error)
                throw error
            }
        },
        async deleteMaintenance(maintenanceID) {
            try {
                await axios.delete(`http://127.0.0.1:5000/fleet/maintenances/${maintenanceID}`)
                await this.getMaintenances()
            } catch (error) {
                console.error('Error deleting maintenance:', error.response?.data || error)
                throw error
            }
        },
        async getTrains() {
            try {
                const response = await axios.get('http://127.0.0.1:5000/fleet/trains')
                this.trains = response.data
            } catch (error) {
                console.error('Error fetching trains:', error)
            }
        },
        async getEmployees() {
            try {
                const response = await axios.get('http://127.0.0.1:5000/fleet/employees')
                this.employees = response.data
            } catch (error) {
                console.error('Error fetching employees:', error)
            }
        }
    }
})