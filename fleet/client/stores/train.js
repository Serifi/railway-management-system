// stores/train.js
import { defineStore } from 'pinia'
import apiClient from '@/utils/api'
import { useMaintenanceStore } from '@/stores/maintenance'

const BASE_PATH = '/fleet/trains'

export const useTrainStore = defineStore('train', {
    state: () => ({
        trains: [],
        trainsLoading: false,
        railcars: [],
        passengerCars: [],
    }),
    getters: {
        trainsWithStatus: (state) => {
            const now = new Date()
            const maintenanceStore = useMaintenanceStore()
            const maintenances = maintenanceStore.maintenances
            return state.trains.map(train => {
                const isUnderMaintenance = maintenances.some(maintenance => {
                    return maintenance.trainID === train.trainID &&
                        new Date(maintenance.from_time) <= now &&
                        new Date(maintenance.to_time) >= now
                })
                return {
                    ...train,
                    active: !isUnderMaintenance
                }
            })
        }
    },
    actions: {
        async handleRequest(promise) {
            try {
                const response = await promise
                return response.data
            } catch (error) {
                throw error.response?.data || error
            }
        },

        async getTrains() {
            this.trainsLoading = true
            try {
                const data = await this.handleRequest(apiClient.get(BASE_PATH))
                this.trains = data
            } catch (error) {
                console.error('Error fetching trains:', error)
                throw error
            } finally {
                this.trainsLoading = false
            }
        },

        async createTrain(train) {
            try {
                const data = await this.handleRequest(apiClient.post(BASE_PATH, train))
                await this.getTrains()
                return data
            } catch (error) {
                console.error('Error creating train:', error)
                throw error
            }
        },

        async editTrain(train) {
            try {
                const data = await this.handleRequest(apiClient.put(`${BASE_PATH}/${train.trainID}`, train))
                await this.getTrains()
                return data
            } catch (error) {
                console.error('Error editing train:', error)
                throw error
            }
        },

        async deleteTrain(trainID) {
            try {
                const data = await this.handleRequest(apiClient.delete(`${BASE_PATH}/${trainID}`))
                await this.getTrains()
                return data
            } catch (error) {
                console.error('Error deleting train:', error)
                throw error
            }
        },

        async getRailcars() {
            try {
                const data = await this.handleRequest(apiClient.get('/fleet/carriages', { params: { type: 'Railcar' } }))
                this.railcars = data
            } catch (error) {
                console.error('Error fetching railcars:', error)
                throw error
            }
        },

        async getPassengerCars() {
            try {
                const data = await this.handleRequest(apiClient.get('/fleet/carriages', { params: { type: 'PassengerCar' } }))
                this.passengerCars = data
            } catch (error) {
                console.error('Error fetching passenger cars:', error)
                throw error
            }
        }
    }
})