/**
 * Store zur Verwaltung von Warnungen
 * Enthält Methoden zum Abrufen und Erstellen von Warnungen
 */

import { defineStore } from 'pinia';
import axios from 'axios';

export const useWarningStore = defineStore('warningStore', {
  // Zustand: Liste der Warnungen
  state: () => ({
    warnings: [],
  }),
  actions: {
    /**
     * Abrufen aller Warnungen
     * Aktualisiert die `warnings`-Liste im Store
     */
    async getWarnings() {
      try {
        const response = await axios.get('http://127.0.0.1:5001/track/warnings');
        this.warnings = response.data;
      } catch (error) {
        console.error('Fehler beim Abrufen der Warnungen:', error);
      }
    },

    /**
     * Erstellen einer neuen Warnung
     * Aktualisiert die `warnings`-Liste nach erfolgreicher Erstellung
     * @param {Object} warning - Die zu erstellende Warnung
     * @returns {Object} - Die Daten der erstellten Warnung
     */
    async createWarning(warning) {
      try {
        const response = await axios.post('http://127.0.0.1:5001/track/warnings', warning);
        await this.getWarnings();
        return response.data;
      } catch (error) {
        console.error('Fehler beim Erstellen der Warnung:', error.response?.data || error);
        throw error;
      }
    },
  },
});