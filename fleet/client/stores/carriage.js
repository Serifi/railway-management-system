import { defineStore } from 'pinia'
import axios from 'axios'

export const useCarriageStore = defineStore('carriage', {
    state: () => ({
        carriages: [],
        trackGauges: [
            { label: 'Normalspur', value: '1435' },
            { label: 'Schmalspur', value: '1000' }
        ],
        carriageTypes: [
            { label: 'Triebwagen', value: 'Railcar' },
            { label: 'Personenwagen', value: 'PassengerCar' }
        ]
    }),
    actions: {
        async getCarriages() {
            try {
                const response = await axios.get('http://127.0.0.1:5000/fleet/carriages')
                this.carriages = response.data
            } catch (error) {
                console.error('Error fetching carriages:', error)
            }
        },
        async createCarriage(carriage) {
            try {
                await axios.post('http://127.0.0.1:5000/fleet/carriages', carriage)
                await this.getCarriages()
            } catch (error) {
                console.error('Error creating carriage:', error.response?.data || error)
            }
        },
        async editCarriage(carriage) {
            try {
                await axios.put(`http://127.0.0.1:5000/fleet/carriages/${carriage.carriageID}`, carriage)
                await this.getCarriages()
            } catch (error) {
                console.error('Error editing carriage:', error.response?.data || error)
            }
        },
        async deleteCarriage(carriageID) {
            try {
                await axios.delete(`http://127.0.0.1:5000/fleet/carriages/${carriageID}`)
                await this.getCarriages()
            } catch (error) {
                console.error('Error deleting carriage:', error.response?.data || error)
            }
        }
    }
})