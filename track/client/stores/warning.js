import { defineStore } from 'pinia';
import axios from 'axios';

export const useWarningStore = defineStore('warningStore', {
    state: () => ({
        warnings: [],
    }),
    actions: {
        async getWarnings() {
            try {
                const response = await axios.get('http://127.0.0.1:5000/track/warnings');
                this.warnings = response.data;
            } catch (error) {
                console.error('Fehler beim Abrufen der Warnungen:', error);
            }
        },

        async createWarning(warning) {
            try {
                const response = await axios.post('http://127.0.0.1:5000/track/warnings', warning);
                await this.getWarnings();
                return response.data;
            } catch (error) {
                console.error('Fehler beim Erstellen der Warnung:', error.response?.data || error);
                throw error;
            }
        },
    },
});