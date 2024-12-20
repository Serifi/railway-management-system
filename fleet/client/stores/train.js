import { defineStore } from 'pinia'
import axios from 'axios'

export const useTrainStore = defineStore('train', {
    state: () => ({
        trains: [],
        trainsLoading: false,
        railcars: [],
        passengerCars: [],
        trainTypes: [
            { label: 'Express', value: 'Express' },
            { label: 'Regional', value: 'Regional' }
        ]
    }),
    getters: {
        trainsWithStatus: (state) => {
            const now = new Date()
            const maintenances = useMaintenanceStore().maintenances
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
        async getTrains() {
            this.trainsLoading = true
            try {
                const response = await axios.get('http://127.0.0.1:5000/fleet/trains')
                this.trains = response.data
            } catch (error) {
                console.error('Error fetching trains:', error)
            } finally {
                this.trainsLoading = false
            }
        },
        async createTrain(train) {
            try {
                await axios.post('http://127.0.0.1:5000/fleet/trains', train)
                await this.getTrains()
            } catch (error) {
                console.error('Error creating train:', error.response?.data || error)
                throw error
            }
        },
        async editTrain(train) {
            try {
                await axios.put(`http://127.0.0.1:5000/fleet/trains/${train.trainID}`, train)
                await this.getTrains()
            } catch (error) {
                console.error('Error editing train:', error.response?.data || error)
                throw error
            }
        },
        async deleteTrain(trainID) {
            try {
                await axios.delete(`http://127.0.0.1:5000/fleet/trains/${trainID}`)
                await this.getTrains()
            } catch (error) {
                console.error('Error deleting train:', error.response?.data || error)
                throw error
            }
        },
        async getRailcars() {
            try {
                const response = await axios.get('http://127.0.0.1:5000/fleet/carriages?type=Railcar')
                this.railcars = response.data
            } catch (error) {
                console.error('Error fetching railcars:', error)
            }
        },
        async getPassengerCars() {
            try {
                const response = await axios.get('http://127.0.0.1:5000/fleet/carriages?type=PassengerCar')
                this.passengerCars = response.data
            } catch (error) {
                console.error('Error fetching passenger cars:', error)
            }
        }
    }
})