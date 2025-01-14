import { defineStore } from "pinia";
import axios from "axios";

export const useEmployeeStore = defineStore("employee", {
  state: () => ({
    employees: [],
  }),
  actions: {
    async getEmployees() {
      try {
        const response = await axios.get("http://127.0.0.1:5000/employees");
        this.employees = response.data;
      } catch (error) {
        console.error("Error fetching employees:", error);
      }
    },
    async createEmployee(employee) {
      try {
        console.log(employee)
        await axios.post("http://127.0.0.1:5000/employees", employee);
        await this.getEmployees();
      } catch (error) {
        console.error("Error creating employee:", error.response?.data || error);
        throw error;
      }
    },
    async editEmployee(employee) {
      try {
        await axios.put(`http://127.0.0.1:5000/employees/${employee.ssn}`, employee);
        await this.getEmployees();
      } catch (error) {
        console.error("Error editing employee:", error.response?.data || error);
        throw error;
      }
    },
    async deleteEmployee(ssn) {
      try {
        await axios.delete(`http://127.0.0.1:5000/employees/${ssn}`);
        await this.getEmployees();
      } catch (error) {
        console.error("Error deleting employee:", error.response?.data || error);
        throw error;
      }
    },
  },
});