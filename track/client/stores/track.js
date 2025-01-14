import { defineStore } from 'pinia';
import axios from 'axios';

export const useTrackStore = defineStore('trackStore', {
  state: () => ({
    tracks: [],
  }),
  actions: {
    async getTracks() {
      try {
        const response = await axios.get('http://127.0.0.1:5000/track/tracks');
        this.tracks = response.data;
      } catch (error) {
        console.error('Fehler beim Abrufen der Tracks:', error.response?.data?.message || error.message);
      }
    },

    async getTrackById(trackID) {
      try {
        const response = await axios.get(`http://127.0.0.1:5000/track/tracks/${trackID}`);
        return response.data;
      } catch (error) {
        console.error(`Fehler beim Abrufen des Tracks mit ID ${trackID}:`, error.response?.data?.message || error.message);
        throw error;
      }
    },

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