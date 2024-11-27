import { defineStore } from 'pinia';

export const useMaintenanceStore = defineStore('maintenance', {
    state: () => ({
        maintenances: [
            {
                employeeSSN: "2000241102",
                trainID: "001",
                start: "2024-11-01T08:00:00Z",
                end: "2024-11-01T12:00:00Z",
            },
            {
                employeeSSN: ["2000241102", "3000241102"],
                trainID: "002",
                start: "2024-11-02T10:00:00Z",
                end: "2024-11-02T14:00:00Z",
            },
        ],
    }),
});