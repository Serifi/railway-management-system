/**
 * Store zur Verwaltung von Benutzerdaten
 * Enthält Methoden zur Benutzeranmeldung, -abmeldung und zum Abrufen von Benutzerinformationen
 */

import { defineStore } from 'pinia';
import axios from "axios";

export const useUserStore = defineStore('user', {
  state: () => ({
    user: null,
  }),

  getters: {
    /**
     * Sozialversicherungsnummer des Benutzers
     * @returns {string} - Die SSN des Benutzers oder ein leerer String
     */
    getSSN: (state) => state.user ? state.user.ssn : '',

    /**
     * Vollständiger Name des Benutzers
     * @returns {string} - Der vollständige Name oder ein leerer String
     */
    getFullName: (state) => state.user ? `${state.user.firstName} ${state.user.lastName}` : "",

    /**
     * Rolle des Benutzers
     * @returns {string} - Die Rolle des Benutzers oder 'Guest'
     */
    getUserRole: (state) => state.user ? state.user.role : 'Guest',
  },

  actions: {
    /**
     * Benutzeranmeldung
     * Aktualisiert den Benutzerzustand nach erfolgreichem Login
     * @param {string} username - Benutzername
     * @param {string} password - Passwort
     * @returns {boolean} - Erfolgreich oder fehlgeschlagen
     */
    async login(username, password) {
      try {
        await axios.post(`http://127.0.0.1:5001/employees/login`, { username: username, password: password });
        this.user = await this.getEmployee(username);
        return true;
      } catch (error) {
        console.error("Login fehlgeschlagen:", error);
        this.user = null;
        return false;
      }
    },

    /**
     * Benutzerabmeldung
     * Setzt den Benutzerzustand zurück
     */
    logout() {
      this.user = null;
    },

    /**
     * Abrufen der Benutzerdaten
     * @param {string} username - Benutzername
     * @returns {Object} - Die Benutzerdaten
     */
    async getEmployee(username) {
      try {
        const response = await axios.get(`http://127.0.0.1:5001/employees/${username}`);
        return response.data;
      } catch (error) {
        console.error(`Fehler beim Abrufen des Benutzers mit Benutzername ${username}:`, error);
        throw error;
      }
    },
  },
});