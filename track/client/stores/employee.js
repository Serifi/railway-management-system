/**
 * Store zur Verwaltung von Mitarbeitern
 * Enthält Methoden zum Abrufen, Erstellen, Bearbeiten und Löschen von Mitarbeitern
 */

import { defineStore } from "pinia";
import axios from "axios";

export const useEmployeeStore = defineStore("employee", {
  // Zustand: Liste der Mitarbeiter
  state: () => ({
    employees: [],
  }),
  actions: {
    /**
     * Abrufen aller Mitarbeiter
     * Aktualisiert die `employees`-Liste im Store
     */
    async getEmployees() {
      try {
        const response = await axios.get("http://127.0.0.1:5001/employees");
        this.employees = response.data;
      } catch (error) {
        console.error("Error fetching employees:", error);
      }
    },

    /**
     * Erstellen eines neuen Mitarbeiters
     * Aktualisiert die `employees`-Liste nach erfolgreicher Erstellung
     * @param {Object} employee - Der zu erstellende Mitarbeiter
     */
    async createEmployee(employee) {
      try {
        console.log(employee);
        await axios.post("http://127.0.0.1:5001/employees", employee);
        await this.getEmployees();
      } catch (error) {
        console.error("Error creating employee:", error.response?.data || error);
        throw error;
      }
    },

    /**
     * Bearbeiten eines bestehenden Mitarbeiters
     * Aktualisiert die `employees`-Liste nach erfolgreicher Bearbeitung
     * @param {Object} employee - Der zu bearbeitende Mitarbeiter
     */
    async editEmployee(employee) {
      try {
        await axios.put(`http://127.0.0.1:5001/employees/${employee.ssn}`, employee);
        await this.getEmployees();
      } catch (error) {
        console.error("Error editing employee:", error.response?.data || error);
        throw error;
      }
    },

    /**
     * Löschen eines Mitarbeiters
     * Aktualisiert die `employees`-Liste nach erfolgreichem Löschen
     * @param {string} ssn - Die Sozialversicherungsnummer des zu löschenden Mitarbeiters
     */
    async deleteEmployee(ssn) {
      try {
        await axios.delete(`http://127.0.0.1:5001/employees/${ssn}`);
        await this.getEmployees();
      } catch (error) {
        console.error("Error deleting employee:", error.response?.data || error);
        throw error;
      }
    },
  },
});