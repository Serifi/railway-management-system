import { defineStore } from 'pinia';
import axios from 'axios';

export const useRideExecutionStore = defineStore('rideExecution', {
    state: () => ({
        rideExecutions: [],
        stopplans2: [],
        trains: [],
        employees: []
    }),

    actions: {
        async createRideExecution(rideExecutionData) {
            try {
                const response = await axios.post('http://127.0.0.1:5000/create_ride_execution/', rideExecutionData);
                console.log("Erstellte Fahrtdurchführung:", response.data);

                this.fetchRideExecutions()
            } catch (error) {
                console.error("Fehler beim Erstellen der Fahrtdurchführung:", error.response?.data || error.message);
            }
        },
        async editRideExecution(rideExecutionData, id) {
            try {
                const response = await axios.put(`http://127.0.0.1:5000/ride_execution/${id}`, rideExecutionData);
            } catch (error) {
                console.error("Fehler beim Bearbeiten der Fahrtdurchführung:", error);
            }
        },
        async fetchRideExecutions() {
            try {
                const response = await axios.get('http://127.0.0.1:5000/ride_executions');
                console.log('API Response:', response.data);
                this.rideExecutions = response.data;
            } catch (error) {
                console.error("Fehler beim Laden der Daten:", error);
            }
        },
        async fetchTrains(dateAndTimeData) {
            try {
                const response = await axios.post('http://127.0.0.1:5000/available_trains', dateAndTimeData);
                console.log('API Response:', response.data);
                this.trains = response.data;
            } catch (error) {
                console.error("Fehler beim Laden der Daten:", error);
            }
        },

        async fetchEmployees() {
            try {
                const response = await axios.get('http://127.0.0.1:5000/employees');
                this.employees = response.data.map(emp => ({
                    ...emp,
                    fullName: `${emp.firstName} ${emp.lastName}`
                }));
                console.log('Transformierte Mitarbeiter:', this.employees);
                console.log('API Response:', response.data);
                this.employees = response.data;
            } catch (error) {
                console.error("Fehler beim Laden der Daten:", error);
            }
        },

        async deleteRideExecution(id) {
            try {
                const response = await axios.delete(`http://127.0.0.1:5000/ride_execution/${id}`);
                console.log(response.data.message);

                const index = this.rideExecutions.findIndex(rideExecution => rideExecution.id === id);
                if (index !== -1) {
                    this.rideExecutions.splice(index, 1);
                }
            } catch (error) {
                console.error("Fehler beim Löschen der Fahrtdurchführung:", error);
            }
        },


    },
});