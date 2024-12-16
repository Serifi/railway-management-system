import { defineStore } from 'pinia';
import axios from 'axios';

export const useSectionStore = defineStore('sectionStore', {
    state: () => ({
        sections: [],
    }),
    actions: {
        async getSections() {
            try {
                const response = await axios.get('http://127.0.0.1:5000/track/sections');
                this.sections = response.data;
            } catch (error) {
                console.error('Fehler beim Abrufen der Abschnitte:', error);
            }
        },

        async createSection(section) {
            try {
                await axios.post('http://127.0.0.1:5000/track/sections', section);
                await this.getSections();
            } catch (error) {
                console.error('Fehler beim Erstellen des Abschnitts:', error.response?.data || error);
            }
        },

        async editSection(section) {
            try {
                await axios.put(`http://127.0.0.1:5000/track/sections/${section.sectionID}`, section);
                await this.getSections();
            } catch (error) {
                console.error('Fehler beim Bearbeiten des Abschnitts:', error.response?.data || error);
            }
        },

        async deleteSection(sectionID) {
            try {
                await axios.delete(`http://127.0.0.1:5000/track/sections/${sectionID}`);
                await this.getSections();
            } catch (error) {
                console.error('Fehler beim Löschen des Abschnitts:', error.response?.data || error);
            }
        },
    },
});