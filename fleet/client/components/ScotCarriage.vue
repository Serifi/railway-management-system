<template>
  <div class="grid grid-cols-2 gap-4">
    <!-- Track Gauge -->
    <div class="flex flex-col space-y-1 col-span-2 lg:col-span-1">
      <label for="trackGauge">{{ $t('trackGauge') }}</label>
      <Select id="trackGauge" v-model="carriage.trackGauge" :options="trackGauges" optionLabel="label" optionValue="value" :placeholder="$t('selectPlaceholder')" :disabled="isDisabled('trackGauge')"/>
    </div>

    <!-- Carriage Type -->
    <div class="flex flex-col space-y-1 col-span-2 lg:col-span-1">
      <label for="type">{{ $t('type') }}</label>
      <Select id="type" v-model="carriage.type" :options="carriageTypes" optionLabel="label" optionValue="value" :placeholder="$t('selectPlaceholder')" :disabled="isDisabled('type')"/>
    </div>

    <!-- Max Tractive Force for Railcar -->
    <div v-if="carriage.type === 'Railcar'" class="flex flex-col space-y-1 col-span-2">
      <label for="maxTractiveForce">{{ $t('maxTractiveForce') }}</label>
      <InputNumber id="maxTractiveForce" v-model="carriage.maxTractiveForce" :placeholder="$t('textPlaceholder')" suffix="kN" :disabled="isDisabled('maxTractiveForce')"/>
    </div>

    <!-- Number of Seats for Passenger Car -->
    <div v-if="carriage.type === 'PassengerCar'" class="flex flex-col space-y-1 col-span-2 lg:col-span-1">
      <label for="numberOfSeats">{{ $t('numberOfSeats') }}</label>
      <InputNumber id="numberOfSeats" v-model="carriage.numberOfSeats" :placeholder="$t('textPlaceholder')" :disabled="isDisabled('numberOfSeats')"/>
    </div>

    <!-- Max Weight for Passenger Car -->
    <div v-if="carriage.type === 'PassengerCar'" class="flex flex-col space-y-1 col-span-2 lg:col-span-1">
      <label for="maxWeight">{{ $t('maxWeight') }}</label>
      <InputNumber id="maxWeight" v-model="carriage.maxWeight" :placeholder="$t('textPlaceholder')" suffix="t" :disabled="isDisabled('maxWeight')"/>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const emits = defineEmits(['update:carriage'])
const props = defineProps({
  // Carriage object to be updated
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
  // List of fields that are disabled for editing
  disabledFields: {
    type: Array,
    default: () => []
  }
})

// Local copy of the carriage object
const carriage = ref({ ...props.carriage })

// Access to the carriage store for options
const carriageStore = useCarriageStore()
const trackGauges = computed(() => carriageStore.trackGauges)
const carriageTypes = computed(() => carriageStore.carriageTypes)

// Determines if a field is disabled
const isDisabled = (field) => props.disabledFields.includes(field)

// Watches for carriage changes and emit updates
watch([
      () => carriage.value.trackGauge,
      () => carriage.value.type,
      () => carriage.value.maxTractiveForce,
      () => carriage.value.numberOfSeats,
      () => carriage.value.maxWeight
    ],
    ([trackGauge, type, maxTractiveForce, numberOfSeats, maxWeight]) => {
      let allFieldsFilled = false

      // Check if all required fields are filled based on carriage type
      if (type === 'Railcar') allFieldsFilled = trackGauge && type && maxTractiveForce !== null
      else if (type === 'PassengerCar') allFieldsFilled = trackGauge && type && numberOfSeats !== null && maxWeight !== null

      // Emit an update if all fields are valid, otherwise emit null
      emits('update:carriage', allFieldsFilled ? carriage.value : null)
    }
)
</script>