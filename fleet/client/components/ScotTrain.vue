<template>
  <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
    <!-- Train Name -->
    <div class="flex flex-col space-y-1 col-span-2">
      <label for="name">{{ $t('name') }}</label>
      <InputText
          id="name"
          v-model="train.name"
          :placeholder="$t('textPlaceholder')"
          :disabled="isDisabled('name')"
      />
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
          filter
      />
    </div>

    <!-- Passenger Cars MultiSelect -->
    <div class="flex flex-col space-y-1 col-span-2">
      <label for="passengerCars">{{ $t('passengerCar') }}</label>
      <MultiSelect
          id="passengerCars"
          v-model="train.passengerCarIDs"
          :options="formatPassengerCarOption"
          optionLabel="label"
          optionValue="carriageID"
          :placeholder="$t('selectPlaceholder')"
          :disabled="isDisabled('passengerCarIDs')"
          filter
          display="comma"
      >
        <template #value="{ value }">
          ID: {{ value }}
        </template>
        <template #option="{ option }">
          {{ option.label }}
        </template>
      </MultiSelect>
    </div>

    <!-- Stats -->
    <div class="flex justify-between col-span-2 mt-4 flex-wrap gap-4">
      <div>
        {{ $t('trackGauge') }}: {{ calculatedTrackGauge }}
      </div>
      <div>
        {{ $t('maxTractiveForce') }}: {{ maxTractiveForce }}kN
      </div>
      <div>
        {{ $t('weight') }}: {{ totalWeight }}kg
      </div>
      <div>
        {{ $t('numberOfSeats') }}: {{ totalSeats }}
      </div>
    </div>

    <!-- Live Preview mit Drag-and-Drop -->
    <div v-if="selectedRailcar || orderedPassengerCars.length" class="flex flex-wrap col-span-2 my-6 cursor-pointer">
      <!-- Railcar Preview -->
      <div v-if="selectedRailcar" class="wagon">
        <img :src="railcarImage" :alt="$t('railcar')" class="wagon-image" />
        <div class="wagon-id">{{ selectedRailcar.carriageID }}</div>
      </div>

      <!-- Passenger Cars Drag-and-Drop -->
      <draggable
          v-if="orderedPassengerCars.length"
          v-model="orderedPassengerCars"
          group="passengerCars"
          item-key="carriageID"
          class="flex flex-wrap"
          @update:modelValue="updatePassengerCarOrder"
      >
        <template #item="{ element }">
          <div class="wagon">
            <img :src="passengerCarImage" :alt="$t('passengerCar')" class="wagon-image" />
            <div class="wagon-id">{{ element.carriageID }}</div>
          </div>
        </template>
      </draggable>
    </div>

    <!-- Validation/Warnungen -->
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

// Lokales Zugobjekt
const train = ref({
  name: props.train.name || '',
  trainID: props.train.trainID || -1,
  // falls Bearbeiten, übernehmen wir vorhandene
  railcarID: props.isEdit && props.train.railcar ? props.train.railcar.carriageID : null,
  passengerCarIDs:
      props.isEdit && props.train.passenger_cars
          ? props.train.passenger_cars
              .slice()
              .sort((a, b) => a.position - b.position)
              .map(car => car.carriageID)
          : []
})

const trainStore = useTrainStore()
const railcars = computed(() => trainStore.railcars)
const passengerCars = computed(() => trainStore.passengerCars)

// Dieses Array steuert das Live-Preview + Drag&Drop
const orderedPassengerCars = ref([])

/**
 * Sobald passengerCarIDs sich ändern, erzeugen wir ein Array in genau DER Reihenfolge,
 * in der die IDs in train.value.passengerCarIDs liegen (also KEINE Sortierung nach position).
 */
watch(
    () => train.value.passengerCarIDs,
    (newIDs) => {
      const selectedInOrder = []
      newIDs.forEach(carID => {
        const foundCar = passengerCars.value.find(pc => pc.carriageID === carID)
        if (foundCar) {
          // Kopie, um reaktive Probleme zu vermeiden
          selectedInOrder.push({ ...foundCar })
        }
      })
      orderedPassengerCars.value = selectedInOrder
    },
    { immediate: true }
)

/**
 * Drag&Drop: nach Umsortieren aktualisieren wir train.value.passengerCarIDs,
 * sodass die Reihenfolge permanent übernommen wird.
 */
const updatePassengerCarOrder = () => {
  // OPTIONAL: Wenn du position bei den Wagen aktualisieren willst
  orderedPassengerCars.value.forEach((car, index) => {
    // position = index+1
    car.position = index + 1
  })
  // IDs zurückschreiben
  train.value.passengerCarIDs = orderedPassengerCars.value.map(car => car.carriageID)
}

/**
 * Computed: selectedRailcar, selectedPassengerCars
 */
const selectedRailcar = computed(() =>
    railcars.value.find(r => r.carriageID === train.value.railcarID)
)
const selectedPassengerCars = computed(() => orderedPassengerCars.value)

/**
 * Berechne Stats (Gewicht, Sitze, etc.)
 */
const totalWeight = computed(() =>
    selectedPassengerCars.value.reduce((sum, car) => sum + (car?.maxWeight || 0), 0)
)
const totalSeats = computed(() =>
    selectedPassengerCars.value.reduce((sum, car) => sum + (car?.numberOfSeats || 0), 0)
)
const calculatedTrackGauge = computed(() => selectedRailcar.value?.trackGauge || '-')
const maxTractiveForce = computed(() => selectedRailcar.value?.maxTractiveForce || 0)

/**
 * Warnungen/Validierungen
 */
const trackGaugeMismatch = computed(() =>
    selectedRailcar.value &&
    selectedPassengerCars.value.some(car => car.trackGauge !== selectedRailcar.value.trackGauge)
)
const tractiveForceInsufficient = computed(() =>
    selectedRailcar.value && totalWeight.value > selectedRailcar.value.maxTractiveForce
)

// Prüfen, ob Wagen/Lok schon woanders zugewiesen
const otherTrains = computed(() => {
  if (!props.isEdit || !train.value.trainID) {
    return trainStore.trains
  }
  return trainStore.trains.filter(t => t.trainID !== train.value.trainID)
})
const isRailcarAssigned = computed(() => {
  if (!train.value.railcarID) return false
  return otherTrains.value.some(t => t.railcar && t.railcar.carriageID === train.value.railcarID)
})
const arePassengerCarsAssigned = computed(() => {
  if (train.value.passengerCarIDs.length === 0) return false
  return otherTrains.value.some(t =>
      t.passenger_cars.some(pc => train.value.passengerCarIDs.includes(pc.carriageID))
  )
})

  watch(
      [
        () => train.value.name,
        () => train.value.railcarID,
        () => train.value.passengerCarIDs
      ],
      () => {
        // Blockier-Logik:
        if (
            !train.value.name ||
            !train.value.railcarID ||
            train.value.passengerCarIDs.length === 0 ||
            trackGaugeMismatch.value ||
            tractiveForceInsufficient.value ||
            isRailcarAssigned.value ||
            arePassengerCarsAssigned.value
        ) {
          emits('update:train', null)
          return
        }
        // Andernfalls => valid
        emits('update:train', train.value)
      },
      { deep: true }
  )

  /**
   * Hilfsfunktionen
   */
  const isDisabled = (field) => props.disabledFields.includes(field)
  const formatRailcarOption = (option) => {
    if (!option) return ''
    return `ID: ${option.carriageID} - ${t('trackGauge')}: ${option.trackGauge}mm - ${t('maxTractiveForce')}: ${option.maxTractiveForce}kN`
  }
  const formatPassengerCarOption = computed(() =>
      passengerCars.value.map(pc => ({
        carriageID: pc.carriageID,
        label: `ID: ${pc.carriageID} - ${t('trackGauge')}: ${pc.trackGauge} - ${t('numberOfSeats')}: ${pc.numberOfSeats} - ${t('maxWeight')}: ${pc.maxWeight}kg`
      }))
  )
</script>