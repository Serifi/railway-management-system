import { defineStore } from 'pinia';
import axios from 'axios';

export const useStopplanStore = defineStore('stopplan', {
    state: () => ({
        stopplans: [],
        tracks: [],
        stopplan: null,
    }),

    actions: {
        //Haltepläne vom Server holen
        async fetchStopplans() {
            try {
                const response = await axios.get('http://127.0.0.1:5000/stopplans');
                console.log('API Response:', response.data);
                this.stopplans = response.data;
            } catch (error) {
                console.error("Fehler beim Laden der Daten:", error);
            }
        },
        //Halteplan nach ID holen
        async fetchStopplanByID(id) {
            try {
                const response = await axios.get(`http://127.0.0.1:5000/stopplan/${id}`);
                console.log('API Response:', response.data);
                this.stopplan = response.data;
            } catch (error) {
                console.error("Fehler beim Laden der Daten:", error);
            }
        },
        //Tracks vom Server holen
        async fetchTracks() {
            try {
                const response = await axios.get('http://127.0.0.1:8000/track/tracks');
                console.log('API Response:', response.data);
                this.tracks = response.data.map(track => ({
                    id: track.trackID,
                    name: track.trackName,
                    sections: track.sections,
                }));
            } catch (error) {
                console.error("Fehler beim Laden der Tracks:", error);
            }
        },
        //züge vom Server holen
        async fetchTrainStationById(stationID) {
            try {
                const response = await axios.get(`http://127.0.0.1:8000/track/train-stations/${stationID}`);
                return response.data;
            } catch (error) {
                console.error(`Fehler beim Abrufen der Station mit ID ${stationID}:`, error);
                return null;
            }
        },
        //halteplan löschen
        async deleteStopplan(id) {
            try {
                const response = await axios.delete(`http://127.0.0.1:5000/stopplan/${id}`);
                console.log(response.data.message);

                const index = this.stopplans.findIndex(stopplan => stopplan.id === id);
                if (index !== -1) {
                    this.stopplans.splice(index, 1);
                }
            } catch (error) {
                console.error("Fehler beim Löschen des Stopplans:", error);
            }
        },
        //Halteplan erstellen
        async createStopplan(stopplanData) {
            try {
                const response = await axios.post('http://127.0.0.1:5000/create_stopplan/', stopplanData);
                console.log("Erstellter Stopplan:", response.data);

                this.stopplans.push(response.data);
            } catch (error) {
                console.error("Fehler beim Erstellen des Stopplans:", error.response?.data || error.message);
            }
        },
        //Halteplan bearbeiten
        async editStopplan(stopplanData, stopplanId) {
            try {
                const response = await axios.put(`http://127.0.0.1:5000/stopplan/${stopplanId}`, stopplanData);
                console.log("Bearbeiteter Stopplan:", response.data);
            } catch (error) {
                console.error("Fehler beim Bearbeiten der Daten:", error);
            }
        },
    }
});