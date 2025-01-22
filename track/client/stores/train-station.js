/**
 * Store zur Verwaltung von Bahnhöfen
 * Enthält Methoden zum Abrufen, Erstellen, Bearbeiten und Löschen von Bahnhöfen
 */

import { defineStore } from 'pinia';
import axios from 'axios';

export const useTrainStationStore = defineStore('trainStation', {
  // Zustand: Liste der Bahnhöfe
  state: () => ({
    trainStations: [],
  }),
  actions: {
    /**
     * Abrufen aller Bahnhöfe
     * Aktualisiert die `trainStations`-Liste im Store
     */
    async getTrainStations() {
      try {
        const response = await axios.get('http://127.0.0.1:5001/track/train-stations');
        this.trainStations = response.data;
      } catch (error) {
        console.error('Fehler beim Abrufen der Bahnhöfe:', error);
        throw error;
      }
    },

    /**
     * Erstellen eines neuen Bahnhofs
     * Aktualisiert die `trainStations`-Liste nach erfolgreicher Erstellung
     * @param {Object} station - Der zu erstellende Bahnhof
     */
    async createTrainStation(station) {
      try {
        await axios.post('http://127.0.0.1:5001/track/train-stations', station);
        await this.getTrainStations();
      } catch (error) {
        console.error('Fehler beim Erstellen des Bahnhofs:', error.response?.data || error);
        throw error;
      }
    },

    /**
     * Bearbeiten eines bestehenden Bahnhofs
     * Aktualisiert die `trainStations`-Liste nach erfolgreicher Bearbeitung
     * @param {Object} station - Der zu bearbeitende Bahnhof
     */
    async editTrainStation(station) {
      try {
        await axios.put(`http://127.0.0.1:5001/track/train-stations/${station.stationID}`, station);
        await this.getTrainStations();
      } catch (error) {
        console.error('Fehler beim Bearbeiten des Bahnhofs:', error.response?.data || error);
        throw error;
      }
    },

    /**
     * Löschen eines Bahnhofs
     * Aktualisiert die `trainStations`-Liste nach erfolgreichem Löschen
     * @param {string} stationID - Die ID des zu löschenden Bahnhofs
     */
    async deleteTrainStation(stationID) {
      try {
        await axios.delete(`http://127.0.0.1:5001/track/train-stations/${stationID}`);
        await this.getTrainStations();
      } catch (error) {
        console.error('Fehler beim Löschen des Bahnhofs:', error.response?.data || error);
        throw error;
      }
    },
  },
});