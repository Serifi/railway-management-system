// stores/train.js
import { defineStore } from 'pinia'
import apiClient from '@/utils/api'
import { useCarriageStore } from '@/stores/carriage'

const BASE_PATH = '/fleet/trains'

export const useTrainStore = defineStore('train', {
    state: () => ({
        trains: [],
        trainsLoading: false,
        railcars: [],
        passengerCars: [],
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

        async getTrains() {
            this.trainsLoading = true
            try {
                const data = await this.handleRequest(apiClient.get(BASE_PATH))
                this.trains = data.map(train => ({
                    ...train,
                    totalWeight: train.passenger_cars.reduce((sum, pc) => sum + (pc.maxWeight || 0), 0),
                    totalSeats: train.passenger_cars.reduce((sum, pc) => sum + (pc.numberOfSeats || 0), 0)
                }))
            } catch (error) {
                console.error('Error fetching trains:', error)
                throw error
            } finally {
                this.trainsLoading = false
            }
        },

        async createTrain(train) {
            const payload = {
                name: train.name,
                railcarID: train.railcarID,
                passenger_cars: train.passengerCarIDs.map((id, index) => ({
                    carriageID: id,
                    position: index + 1,
                })),
            };
            try {
                const data = await this.handleRequest(apiClient.post(BASE_PATH, payload));
                await this.getTrains();
                return data;
            } catch (error) {
                console.error('Error creating train:', error);
                throw error;
            }
        },

        async editTrain(train) {
            const payload = {
                name: train.name,
                railcarID: train.railcarID,
                passenger_cars: train.passengerCarIDs.map((id, index) => ({
                    carriageID: id,
                    position: index + 1,
                })),
            };
            try {
                const data = await this.handleRequest(apiClient.put(`${BASE_PATH}/${train.trainID}`, payload))
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

        async getCarriagesByType() {
            try {
                const carriageStore = useCarriageStore()
                await carriageStore.getCarriages()

                this.railcars = carriageStore.carriages.filter(carriage => carriage.type === 'Railcar')
                this.passengerCars = carriageStore.carriages.filter(carriage => carriage.type === 'PassengerCar')
            } catch (error) {
                console.error('Error fetching carriages by type:', error)
                throw error
            }
        }
    }
})