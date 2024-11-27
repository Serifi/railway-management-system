import { defineStore } from 'pinia';

export const useTrainStore = defineStore('train', {
    state: () => ({
        trains: [
            {
                trainID: "001",
                name: "Express 1",
                carriages: ["001", "002"],
            },
            {
                trainID: "002",
                name: "Regional 5",
                carriages: ["003", "004"],
            },
        ],
    }),
});