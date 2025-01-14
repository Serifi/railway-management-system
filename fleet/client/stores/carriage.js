import { defineStore } from 'pinia'
import apiClient from '@/utils/api'
import { useTrainStore } from '@/stores/train'

const BASE_PATH = '/fleet/carriages'
export const useCarriageStore = defineStore('carriage', {
    state: () => ({
        carriages: [],
        trackGauges: [
            { label: 'Standard Gauge', value: '1435' },
            { label: 'Narrow Gauge', value: '1000' }
        ],
        carriageTypes: [
            { label: 'Railcar', value: 'Railcar' },
            { label: 'Passenger Car', value: 'PassengerCar' }
        ]
    }),
    getters: {
        carriagesWithStatus: (state) => {
            const trainStore = useTrainStore()
            const trains = trainStore.trains

            return state.carriages.map(carriage => {
                const isActive = trains.some(train =>
                    (train.railcar && train.railcar.carriageID === carriage.carriageID) ||
                    (train.passenger_cars && train.passenger_cars.some(pc => pc.carriageID === carriage.carriageID))
                )
                return {
                    ...carriage,
                    active: isActive
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

        async getCarriages() {
            const data = await this.handleRequest(apiClient.get(BASE_PATH))
            this.carriages = data
        },

        async createCarriage(carriage) {
            const data = await this.handleRequest(apiClient.post(BASE_PATH, carriage))
            await this.getCarriages()
            return data
        },

        async editCarriage(carriage) {
            const data = await this.handleRequest(apiClient.put(`${BASE_PATH}/${carriage.carriageID}`, carriage))
            await this.getCarriages()
            return data
        },

        async deleteCarriage(carriageID) {
            const data = await this.handleRequest(apiClient.delete(`${BASE_PATH}/${carriageID}`))
            await this.getCarriages()
            return data
        }
    }
})