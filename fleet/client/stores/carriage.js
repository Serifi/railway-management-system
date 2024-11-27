import { defineStore } from 'pinia';

export const useCarriageStore = defineStore('carriage', {
    state: () => ({
        carriages: [
            {
                carriageID: "001",
                type: "Railcar",
                trackGauge: 1000,
                maxTractiveForce: 20000,
            },
            {
                carriageID: "002",
                type: "PassengerCar",
                trackGauge: 1000,
                numberOfSeats: 100,
                maxWeight: 50000,
            },
            {
                carriageID: "003",
                type: "Railcar",
                trackGauge: 1425,
                maxTractiveForce: 15000,
            },
            {
                carriageID: "004",
                type: "PassengerCar",
                trackGauge: 1425,
                numberOfSeats: 50,
                maxWeight: 25000,
            },
        ],
    }),
});
