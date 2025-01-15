/**
 * Store zur Verwaltung von Strecken
 * Enthält Methoden zum Abrufen, Erstellen, Bearbeiten und Löschen von Abschnitten
 */

import { defineStore } from 'pinia';
import axios from 'axios';

export const useTrackStore = defineStore('trackStore', {
  // Zustand: Liste der Tracks
  state: () => ({
    tracks: [],
  }),
  actions: {
    /**
     * Abrufen aller Abschnitte
     * Aktualisiert die `tracks`-Liste im Store
     */
    async getTracks() {
      try {
        const response = await axios.get('http://127.0.0.1:5000/track/tracks');
        this.tracks = response.data;
      } catch (error) {
        console.error('Fehler beim Abrufen der Tracks:', error.response?.data?.message || error.message);
      }
    },

    /**
     * Abrufen einer spezifischen Strecke anhand der ID
     * @param {string} trackID - Die ID der abzurufenden Strecke
     * @returns {Object} - Die Daten der abgerufenen Strecke
     */
    async getTrackById(trackID) {
      try {
        const response = await axios.get(`http://127.0.0.1:5000/track/tracks/${trackID}`);
        return response.data;
      } catch (error) {
        console.error(`Fehler beim Abrufen des Tracks mit ID ${trackID}:`, error.response?.data?.message || error.message);
        throw error;
      }
    },

    /**
     * Erstellen einer neuen Strecke
     * Aktualisiert die `tracks`-Liste nach erfolgreicher Erstellung
     * @param {Object} trackData - Die Daten der zu erstellenden Strecke
     * @returns {Object} - Die Daten der erstellten Strecke
     */
    async createTrack(trackData) {
      try {
        const response = await axios.post('http://127.0.0.1:5000/track/tracks', trackData);
        await this.getTracks();
        return response.data;
      } catch (error) {
        console.error('Fehler beim Erstellen des Tracks:', error.response?.data?.message || error.message);
        throw error;
      }
    },

    /**
     * Bearbeiten einer bestehenden Strecke
     * Aktualisiert die `tracks`-Liste nach erfolgreicher Bearbeitung
     * @param {string} trackID - Die ID der zu bearbeitenden Strecke
     * @param {Object} trackData - Die aktualisierten Daten der Strecke
     * @returns {Object} - Die Daten der aktualisierten Strecke
     */
    async editTrack(trackID, trackData) {
      try {
        const response = await axios.put(`http://127.0.0.1:5000/track/tracks/${trackID}`, trackData);
        await this.getTracks();
        return response.data;
      } catch (error) {
        console.error(`Fehler beim Bearbeiten des Tracks mit ID ${trackID}:`, error.response?.data?.message || error.message);
        throw error;
      }
    },

    /**
     * Löschen einer Strecke
     * Aktualisiert die `tracks`-Liste nach erfolgreichem Löschen
     * @param {string} trackID - Die ID der zu löschenden Strecke
     */
    async deleteTrack(trackID) {
      try {
        await axios.delete(`http://127.0.0.1:5000/track/tracks/${trackID}`);
        await this.getTracks();
      } catch (error) {
        console.error(`Fehler beim Löschen des Tracks mit ID ${trackID}:`, error.response?.data?.message || error.message);
        throw error;
      }
    },
  },
});