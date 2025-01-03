<template>
  <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
    <!-- Train Name -->
    <div class="flex flex-col space-y-1 col-span-2">
      <label for="name">{{ $t('name') }}</label>
      <InputText id="name" v-model="train.name" :placeholder="$t('textPlaceholder')" :disabled="isDisabled('name')" />
    </div>

    <!-- Railcar Select -->
    <div class="flex flex-col space-y-1 col-span-2">
      <label for="railcar">{{ $t('railcar') }}</label>
      <Select
          id="railcar"
          v-model="train.railcarID"
          :options="railcars"
          :optionLabel="formatRailcarOption"
          optionValue="carriageID"
          :placeholder="$t('selectPlaceholder')"
          :disabled="isDisabled('railcarID')"
      />
    </div>

    <!-- Passenger Cars MultiSelect -->
    <div class="flex flex-col space-y-1 col-span-2">
      <label for="passengerCars">{{ $t('passengerCar') }}</label>
      <MultiSelect
          id="passengerCars"
          v-model="train.passengerCarIDs"
          :options="passengerCars"
          :optionLabel="formatPassengerCarOption"
          optionValue="carriageID"
          :placeholder="$t('selectPlaceholder')"
          :disabled="isDisabled('passengerCarIDs')"
      />
    </div>

    <!-- Stats -->
    <div class="flex justify-between col-span-2 mt-4 flex-wrap gap-4">
      <div :class="trackGaugeClass">
        {{ $t('trackGauge') }}: {{ calculatedTrackGauge }}
      </div>
      <div>
        {{ $t('maxTractiveForce') }}: {{ maxTractiveForce }}kN
      </div>
      <div :class="totalWeightClass">
        {{ $t('weight') }}: {{ totalWeight }}kg
      </div>
      <div>
        {{ $t('numberOfSeats') }}: {{ totalSeats }}
      </div>
    </div>

    <div v-if="selectedRailcar || orderedPassengerCars.length" class="flex flex-wrap gap-4 items-center justify-start col-span-2 mt-4">
      <!-- Railcar  -->
      <div v-if="selectedRailcar" class="wagon">
        <img :src="railcarImage" :alt="$t('railcar')" class="wagon-image" />
        <div class="wagon-id">{{ selectedRailcar.carriageID }}</div>
      </div>

      <!-- Passenger Cars -->
      <draggable
          v-if="orderedPassengerCars.length"
          v-model="orderedPassengerCars"
          group="passengerCars"
          item-key="carriageID"
          class="flex flex-wrap gap-4"
          @end="updatePassengerCarOrder"
      >
        <template #item="{ element }">
          <div class="wagon">
            <img :src="passengerCarImage" :alt="$t('passengerCar')" class="wagon-image" />
            <div class="wagon-id">{{ element.carriageID }}</div>
          </div>
        </template>
      </draggable>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useTrainStore } from '@/stores/train'
import { useI18n } from 'vue-i18n'
import draggable from 'vuedraggable'

import railcarImage from '@/assets/images/railcar.png'
import passengerCarImage from '@/assets/images/passenger_car.png'

const { t } = useI18n()
const emits = defineEmits(['update:train'])
const props = defineProps({
  train: {
    type: Object,
    default: () => ({
      name: '',
      railcarID: null,
      passengerCarIDs: []
    })
  },
  disabledFields: {
    type: Array,
    default: () => []
  },
  isEdit: {
    type: Boolean,
    default: false
  }
})

// Initialize the train object
const train = ref({
  name: props.train.name || '',
  trainID: props.train.trainID || -1,
  railcarID: props.isEdit && props.train.railcar ? props.train.railcar.carriageID : null,
  passengerCarIDs: props.isEdit && props.train.passenger_cars
      ? props.train.passenger_cars.map(car => car.carriageID)
      : []
})

const trainStore = useTrainStore()
const railcars = computed(() => trainStore.railcars)
const passengerCars = computed(() => trainStore.passengerCars)

// Ordered Passenger Cars for Drag-and-Drop
const orderedPassengerCars = ref([])

// Watch for changes in passengerCarIDs to update orderedPassengerCars
watch(
    () => train.value.passengerCarIDs,
    (passengerCarIDs) => {
      orderedPassengerCars.value = passengerCarIDs
          .map(id => passengerCars.value.find(car => car.carriageID === id))
          .filter(Boolean)
    },
    { immediate: true }
)

// Handle reordering of passenger cars
const updatePassengerCarOrder = () => {
  train.value.passengerCarIDs = orderedPassengerCars.value.map(car => car.carriageID)
}

// Disable fields based on props
const isDisabled = (field) => props.disabledFields.includes(field)

// Format options for Select and MultiSelect
const formatRailcarOption = (option) => {
  if (!option) return ''
  return `ID: ${option.carriageID} - ${t('trackGauge')}: ${option.trackGauge}mm - ${t('maxTractiveForce')}: ${option.maxTractiveForce}kN`
}

const formatPassengerCarOption = (option) => {
  if (!option) return ''
  return `ID: ${option.carriageID} - ${t('trackGauge')}: ${option.trackGauge}mm - ${t('maxWeight')}: ${option.maxWeight}kg - ${t('numberOfSeats')}: ${option.numberOfSeats}`
}

// Selected Railcar
const selectedRailcar = computed(() =>
    railcars.value.find(railcar => railcar.carriageID === train.value.railcarID)
)

// Selected Passenger Cars based on orderedPassengerCars
const selectedPassengerCars = computed(() =>
    orderedPassengerCars.value.map(car => passengerCars.value.find(c => c.carriageID === car?.carriageID))
)

// Calculated Stats
const calculatedTrackGauge = computed(() => selectedRailcar.value?.trackGauge || 'N/A')
const trackGaugeClass = computed(() =>
    selectedPassengerCars.value.some(car => car?.trackGauge !== selectedRailcar.value?.trackGauge)
        ? 'text-red-500'
        : ''
)

const maxTractiveForce = computed(() => selectedRailcar.value?.maxTractiveForce || 0)
const totalWeight = computed(() =>
    selectedPassengerCars.value.reduce((sum, car) => sum + (car?.maxWeight || 0), 0)
)
const totalWeightClass = computed(() =>
    totalWeight.value > maxTractiveForce.value ? 'text-red-500' : ''
)
const totalSeats = computed(() =>
    selectedPassengerCars.value.reduce((sum, car) => sum + (car?.numberOfSeats || 0), 0)
)

// Watch for changes in train object to emit updates
watch(
    [
      () => train.value.name,
      () => train.value.railcarID,
      () => train.value.passengerCarIDs
    ],
    ([name, railcarID, passengerCarIDs]) => {
      let allFieldsFilled = false

      if (name && railcarID && passengerCarIDs.length > 0) {
        allFieldsFilled = true
      }

      emits('update:train', allFieldsFilled ? train.value : null)
    },
    { deep: true }
)
</script>

<style scoped>
.wagon-container {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  justify-content: start;
  align-items: center;
}

.wagon {
  position: relative;
  width: 100px;
  height: auto;
  flex: 0 0 auto;
}

.wagon-image {
  width: 100%;
  height: auto;
  display: block;
}

.wagon-id {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: white;
  font-size: 12px;
  font-weight: bold;
  pointer-events: none;
}
</style>