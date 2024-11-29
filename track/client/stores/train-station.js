import { defineStore } from 'pinia'
import axios from "axios"

export const useTrainStationStore = defineStore('trainStation', {
    state: () => ({
        trainStations: [],
    }),
    actions: {
        async getTrainStations() {
            try {
                const response = await axios.get('http://127.0.0.1:5000/track/train-stations')
                this.trainStations = response.data
            } catch (error) {
                console.error('Error fetching train stations:', error)
            }
        },

        async createTrainStation(station) {
            try {
                await axios.post('http://127.0.0.1:5000/track/train-stations', station)
                await this.getTrainStations()
            } catch (error) {
                console.error('Error creating train station:', error.response?.data || error)
            }
        },

        async editTrainStation(station) {
            try {
                await axios.put(`http://127.0.0.1:5000/track/train-stations/${station.stationID}`, station)
                await this.getTrainStations()
            } catch (error) {
                console.error('Error editing train station:', error.response?.data || error)
            }
        },

        async deleteTrainStation(stationID) {
            try {
                await axios.delete(`http://127.0.0.1:5000/track/train-stations/${stationID}`)
                await this.getTrainStations()
            } catch (error) {
                console.error('Error deleting train station:', error.response?.data || error)
            }
        },
    },
})