<template>
  <div class="grid grid-cols-2 gap-4">
    <div class="flex flex-col space-y-1 col-span-2 lg:col-span-1">
      <label for="trackGauge">Spurweite</label>
      <Select id="trackGauge" v-model="carriage.trackGauge" :options="trackGauges" optionLabel="label" optionValue="value" placeholder="Auswahl treffen..." :disabled="isDisabled('trackGauge')"/>
    </div>

    <div class="flex flex-col space-y-1 col-span-2 lg:col-span-1">
      <label for="type">Typ</label>
      <Select id="type" v-model="carriage.type" :options="carriageTypes" optionLabel="label" optionValue="value" placeholder="Auswahl treffen..." :disabled="isDisabled('type')"/>
    </div>

    <div v-if="carriage.type === 'Railcar'" class="flex flex-col space-y-1 col-span-2">
      <label for="maxTractiveForce">Maximale Zugkraft</label>
      <InputNumber id="maxTractiveForce" v-model="carriage.maxTractiveForce" placeholder="Wert eingeben..." suffix="kN" :disabled="isDisabled('maxTractiveForce')"/>
    </div>

    <div v-if="carriage.type === 'PassengerCar'" class="flex flex-col space-y-1 col-span-2 lg:col-span-1">
      <label for="numberOfSeats">Sitzplätze</label>
      <InputNumber id="numberOfSeats" v-model="carriage.numberOfSeats" placeholder="Wert eingeben..." :disabled="isDisabled('numberOfSeats')"/>
    </div>

    <div v-if="carriage.type === 'PassengerCar'" class="flex flex-col space-y-1 col-span-2 lg:col-span-1">
      <label for="maxWeight">Maximales Gewicht</label>
      <InputNumber id="maxWeight" v-model="carriage.maxWeight" placeholder="Wert eingeben..." suffix="t" :disabled="isDisabled('maxWeight')"/>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const emits = defineEmits(['update:carriage'])
const props = defineProps({
  carriage: {
    type: Object,
    default: () => ({
      trackGauge: '',
      type: '',
      maxTractiveForce: null,
      numberOfSeats: null,
      maxWeight: null
    })
  },
  disabledFields: {
    type: Array,
    default: () => []
  }
})

const carriage = ref({ ...props.carriage })
const carriageStore = useCarriageStore()
const trackGauges = computed(() => carriageStore.trackGauges)
const carriageTypes = computed(() => carriageStore.carriageTypes)

const isDisabled = (field) => props.disabledFields.includes(field)

watch(
    [
      () => carriage.value.trackGauge,
      () => carriage.value.type,
      () => carriage.value.maxTractiveForce,
      () => carriage.value.numberOfSeats,
      () => carriage.value.maxWeight
    ],
    ([trackGauge, type, maxTractiveForce, numberOfSeats, maxWeight]) => {
      let allFieldsFilled = false

      if (type === 'Railcar') {
        allFieldsFilled = trackGauge && type && maxTractiveForce !== null
      } else if (type === 'PassengerCar') {
        allFieldsFilled = trackGauge && type && numberOfSeats !== null && maxWeight !== null
      }

      emits('update:carriage', allFieldsFilled ? carriage.value : null)
    }
)
</script>