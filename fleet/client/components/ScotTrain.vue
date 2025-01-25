<template>
  <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
    <!-- Name -->
    <div class="flex flex-col space-y-1 col-span-2">
      <label for="name">{{ $t('name') }}</label>
      <InputText id="name" v-model="train.name" :placeholder="$t('textPlaceholder')" :disabled="isDisabled('name')"/>
    </div>

    <!-- Railcar -->
    <div class="flex flex-col space-y-1 col-span-2">
      <label for="railcar">{{ $t('railcar') }}</label>
      <Select id="railcar" v-model="train.railcarID" :placeholder="$t('selectPlaceholder')" :options="availableRailcars"
              :optionLabel="formatRailcarOption" optionValue="carriageID" :disabled="isDisabled('railcarID')" filter/>
    </div>

    <!-- Passenger Cars -->
    <div class="flex flex-col space-y-1 col-span-2">
      <label for="passengerCars">{{ $t('passengerCar') }}</label>
      <MultiSelect id="passengerCars" v-model="train.passengerCarIDs" :placeholder="$t('selectPlaceholder')" :options="availablePassengerCars.map(formatPassengerCarOption)"
                   optionLabel="label" optionValue="carriageID" :disabled="isDisabled('passengerCarIDs')" filter display="comma">
        <template #value="{ value }">
          ID: {{ value }}
        </template>
        <template #option="{ option }">
          {{ option.label }}
        </template>
      </MultiSelect>
    </div>

    <!-- Details -->
    <div class="flex justify-between col-span-2 mt-4 flex-wrap gap-4">
      <div> {{ $t('trackGauge') }}: {{ calculatedTrackGauge }}</div>
      <div> {{ $t('maxTractiveForce') }}: {{ maxTractiveForce }}kN</div>
      <div> {{ $t('weight') }}: {{ totalWeight }}kg</div>
      <div> {{ $t('numberOfSeats') }}: {{ totalSeats }}</div>
    </div>

    <!-- Carriages with drag-and-drop -->
    <div v-if="selectedRailcar || orderedPassengerCars.length" class="flex flex-wrap col-span-2 my-6 cursor-pointer">
      <!-- Railcar -->
      <div v-if="selectedRailcar" class="wagon">
        <img :src="railcarImage" :alt="$t('railcar')" class="wagon-image"/>
        <div class="wagon-id">{{ selectedRailcar.carriageID }}</div>
      </div>

      <!-- Passenger Cars -->
      <draggable v-if="orderedPassengerCars.length" v-model="orderedPassengerCars" group="passengerCars"
                 item-key="carriageID" @update:modelValue="updatePassengerCarOrder" class="flex flex-wrap">
        <template #item="{ element }">
          <div class="wagon">
            <img :src="passengerCarImage" :alt="$t('passengerCar')" class="wagon-image"/>
            <div class="wagon-id">{{ element.carriageID }}</div>
          </div>
        </template>
      </draggable>
    </div>

    <!-- Warnings -->
    <div class="col-span-2 flex flex-col space-y-2">
      <Message v-if="trackGaugeMismatch" severity="error" icon="pi pi-exclamation-circle">
        {{ $t('trackGaugeWarning') }}
      </Message>
      <Message v-if="tractiveForceInsufficient" severity="error" icon="pi pi-exclamation-circle">
        {{ $t('weightWarning') }}
      </Message>
      <Message v-if="isRailcarAssigned" severity="error" icon="pi pi-exclamation-circle">
        {{ $t('railcarAssignmentWarning') }}
      </Message>
      <Message v-if="arePassengerCarsAssigned" severity="error" icon="pi pi-exclamation-circle">
        {{ $t('passengerCarAssignmentWarning') }}
      </Message>
    </div>
  </div>
</template>

<script setup>
import {ref, computed, watch} from 'vue'
import {useTrainStore} from '@/stores/train'
import {useI18n} from 'vue-i18n'
import draggable from 'vuedraggable'

import railcarImage from '@/assets/images/railcar.png'
import passengerCarImage from '@/assets/images/passenger_car.png'

const {t} = useI18n()
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

const trainStore = useTrainStore()

// All rail- and passenger cars
const railcars = computed(() => trainStore.railcars)
const passengerCars = computed(() => trainStore.passengerCars)

// List for the preview of carriages, sorted by position inside the train
const orderedPassengerCars = ref([])

// Local train that adapts depending on isEdit
const train = ref({
  name: props.train.name || '',
  trainID: props.train.trainID || -1,
  railcarID: props.isEdit && props.train.railcar
      ? props.train.railcar.carriageID
      : null,
  passengerCarIDs:
      props.isEdit && props.train.passenger_cars
          ? props.train.passenger_cars
              .slice()
              .sort((a, b) => a.position - b.position)
              .map(car => car.carriageID)
          : []
})

// Compute the list of available railcars for selection
const availableRailcars = computed(() =>
    railcars.value.filter(rc =>
        !otherTrains.value.some(t => t.railcar?.carriageID === rc.carriageID)
    )
)

// Compute the list of available passenger cars for selection
const availablePassengerCars = computed(() =>
    passengerCars.value.filter(pc =>
        !otherTrains.value.some(t =>
            t.passenger_cars.some(assignedPc => assignedPc.carriageID === pc.carriageID)
        )
    )
)

// Format railcar options for the selection
const formatRailcarOption = (option) => {
  if (!option) return ''
  return `ID: ${option.carriageID} - ${t('trackGauge')}: ${option.trackGauge}mm - ${t('maxTractiveForce')}: ${option.maxTractiveForce}kN`
}

// Format passenger car options for the selection
const formatPassengerCarOption = (pc) => ({
  carriageID: pc.carriageID,
  label: `ID: ${pc.carriageID} - ${t('trackGauge')}: ${pc.trackGauge} - ${t('numberOfSeats')}: ${pc.numberOfSeats} - ${t('maxWeight')}: ${pc.maxWeight}kg`
})

// Watch for changes in the passenger cars and update their order
watch(() => train.value.passengerCarIDs,
    (newIDs) => {
      const selectedInOrder = []
      newIDs.forEach(carID => {
        const foundCar = passengerCars.value.find(pc => pc.carriageID === carID)
        if (foundCar) selectedInOrder.push({...foundCar})
      })
      orderedPassengerCars.value = selectedInOrder
    },
    {immediate: true}
)

// Function to update the order of passenger cars after drag-and-drop
const updatePassengerCarOrder = () => {
  orderedPassengerCars.value.forEach((car, index) => {
    car.position = index + 1
  })
  train.value.passengerCarIDs = orderedPassengerCars.value.map(car => car.carriageID)
}

// Compute the currently selected rail- and passenger cars
const selectedRailcar = computed(() =>
    railcars.value.find(r => r.carriageID === train.value.railcarID)
)
const selectedPassengerCars = computed(() => orderedPassengerCars.value)

// Compute the total weight of the train by summing weights of passenger cars
const totalWeight = computed(() =>
    selectedPassengerCars.value.reduce((sum, car) => sum + (car?.maxWeight || 0), 0)
)

// Compute the total number of seats in the train by summing seats of passenger cars
const totalSeats = computed(() =>
    selectedPassengerCars.value.reduce((sum, car) => sum + (car?.numberOfSeats || 0), 0)
)

// Get the track gauge and tractive force of the selected railcar
const calculatedTrackGauge = computed(() => selectedRailcar.value?.trackGauge || '-')
const maxTractiveForce = computed(() => selectedRailcar.value?.maxTractiveForce || 0)

// Compute whether there is a mismatch in track gauge
const trackGaugeMismatch = computed(() =>
    selectedRailcar.value &&
    selectedPassengerCars.value.some(car => car.trackGauge !== selectedRailcar.value.trackGauge)
)

// Compute whether the total weight exceeds the tractive force
const tractiveForceInsufficient = computed(() =>
    selectedRailcar.value && totalWeight.value > selectedRailcar.value.maxTractiveForce
)

// List other trains, excluding the current one if in edit mode
const otherTrains = computed(() => {
  if (!props.isEdit || !train.value.trainID) {
    return trainStore.trains
  }
  return trainStore.trains.filter(t => t.trainID !== train.value.trainID)
})

// Check if the railcar is already assigned to another train
const isRailcarAssigned = computed(() => {
  if (!train.value.railcarID) return false
  return otherTrains.value.some(t => t.railcar && t.railcar.carriageID === train.value.railcarID)
})

// Check if any of the passenger cars are assigned to other trains
const arePassengerCarsAssigned = computed(() => {
  if (train.value.passengerCarIDs.length === 0) return false
  return otherTrains.value.some(t =>
      t.passenger_cars.some(pc => train.value.passengerCarIDs.includes(pc.carriageID))
  )
})

// Watch for train changes and emit updates
watch([
      () => train.value.name,
      () => train.value.railcarID,
      () => train.value.passengerCarIDs
    ],
    () => {
      if (
          !train.value.name ||
          !train.value.railcarID ||
          train.value.passengerCarIDs.length === 0 ||
          trackGaugeMismatch.value ||
          tractiveForceInsufficient.value ||
          isRailcarAssigned.value ||
          arePassengerCarsAssigned.value
      ) {
        emits('update:train', null) // Emit null if invalid
        return
      }
      emits('update:train', train.value) // Emit train if valid
    },
    {deep: true}
)

// Check if a field should be disabled
const isDisabled = (field) => props.disabledFields.includes(field)
</script>