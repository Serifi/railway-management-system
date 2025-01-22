/**
 * Store zur Verwaltung von Abschnitten
 * Enthält Methoden zum Abrufen, Erstellen, Bearbeiten und Löschen von Abschnitten
 */

import { defineStore } from 'pinia';
import axios from 'axios';

export const useSectionStore = defineStore('sectionStore', {
    // Zustand: Liste der Abschnitte
    state: () => ({
        sections: [],
    }),
    actions: {
        /**
         * Abrufen aller Abschnitte
         * Aktualisiert die `sections`-Liste im Store
         */
        async getSections() {
            try {
                const response = await axios.get('http://127.0.0.1:5001/track/sections');
                this.sections = response.data;
            } catch (error) {
                console.error('Fehler beim Abrufen der Abschnitte:', error);
            }
        },

        /**
         * Erstellen eines neuen Abschnitts
         * Aktualisiert die `sections`-Liste nach erfolgreicher Erstellung
         * @param {Object} section - Der zu erstellende Abschnitt
         * @returns {Object} - Das erstellte Abschnittsobjekt
         */
        async createSection(section) {
            try {
                const response = await axios.post('http://127.0.0.1:5001/track/sections', section);
                await this.getSections();
                return response.data;
            } catch (error) {
                console.error('Fehler beim Erstellen des Abschnitts:', error.response?.data || error);
                throw error;
            }
        },

        /**
         * Bearbeiten eines bestehenden Abschnitts
         * Aktualisiert die `sections`-Liste nach erfolgreicher Bearbeitung
         * @param {string} sectionID - Die ID des zu bearbeitenden Abschnitts
         * @param {Object} sectionData - Die aktualisierten Abschnittsdaten
         * @returns {Object} - Die aktualisierten Abschnittsdaten
         */
        async editSection(sectionID, sectionData) {
            try {
                const response = await axios.put(`http://127.0.0.1:5001/track/sections/${sectionID}`, sectionData);
                await this.getSections();
                return response.data;
            } catch (error) {
                console.error('Fehler beim Bearbeiten des Abschnitts:', error.response?.data || error);
                throw error;
            }
        },

        /**
         * Löschen eines Abschnitts
         * Aktualisiert die `sections`-Liste nach erfolgreichem Löschen
         * @param {string} sectionID - Die ID des zu löschenden Abschnitts
         */
        async deleteSection(sectionID) {
            try {
                await axios.delete(`http://127.0.0.1:5001/track/sections/${sectionID}`);
                await this.getSections();
            } catch (error) {
                console.error('Fehler beim Löschen des Abschnitts:', error.response?.data || error);
                throw error;
            }
        },
    },
});