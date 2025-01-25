<template>
  <ScotList :items="trains" :getKey="getTrainKey" :rowsPerPage="5" @create="toggleCreateDialog" @edit="toggleEditDialog" @delete="deleteTrain">
    <template #title="{ item }">
      {{ item.name }}
      <!-- Tag whether in maintenance or not -->
      <Tag :severity="item.active ? 'success' : 'danger'" :value="$t(item.active ? 'active' : 'inactive')" class="ml-2 !py-[0px]"/>
    </template>
    <template #description="{ item }">
      <!-- Details -->
      ID: {{ item.trainID }} <br>
      {{ $t('trackGauge') }}: {{ item.railcar.trackGauge }} <br>
      {{ $t('maxTractiveForce') }}: {{ item.railcar.maxTractiveForce }} <br>
      {{ $t('weight') }}: {{ item.totalWeight }} <br>
      {{ $t('numberOfSeats') }}: {{ item.totalSeats }} <br>

      <!-- Images of the carriages -->
      <div class="wagon-container">
        <!-- Railcar -->
        <div class="wagon">
          <img :src="railcarImage" :alt="$t('railcar')" class="wagon-image"/>
          <div class="wagon-id">{{ item.railcar.carriageID }}</div>
        </div>

        <!-- Passenger Cars -->
        <div class="wagon" v-for="passengerCar in sortedPassengerCars(item.passenger_cars)" :key="passengerCar.carriageID">
          <img :src="passengerCarImage" :alt="$t('passengerCar')" class="wagon-image"/>
          <div class="wagon-id">{{ passengerCar.carriageID }}</div>
        </div>
      </div>
    </template>
    <!-- Filters -->
    <template #filters="{ filters }">
      <span v-if="initializeFilters(filters)" />

      <div class="p-4 space-y-4">
        <!-- Status (in-active) -->
        <div class="flex flex-col space-y-1">
          <label for="status">{{ $t('status') }}</label>
          <SelectButton id="status" v-model="filters.status" :options="statusOptions" optionLabel="label" optionValue="value"/>
        </div>

        <!-- Railcar -->
        <div class="flex flex-col space-y-1">
          <label for="railcar">{{ $t('railcar') }}</label>
          <Select id="railcar" v-model="filters.railcarID" :options="railcars" optionLabel="carriageID" optionValue="carriageID" :placeholder="$t('selectPlaceholder')" filter showClear/>
        </div>

        <!-- Passenger Car -->
        <div class="flex flex-col space-y-1">
          <label for="passengerCars">{{ $t('passengerCar') }}</label>
          <MultiSelect id="passengerCars" v-model="filters.passengerCarIDs" :options="passengerCars" optionLabel="carriageID" optionValue="carriageID" :placeholder="$t('selectPlaceholder')" filter showClear/>
        </div>
      </div>
    </template>
  </ScotList>

  <!-- Dialog for adding a train -->
  <ScotDialog :visible="createDialogVisible" type="create" :header="$t('createTrain')" :disable-action="disableAction"
              @update:visible="createDialogVisible = $event" @action="createTrain" @cancel="toggleCreateDialog">
    <ScotTrain @update:train="updateTrain"/>
  </ScotDialog>

  <!-- Dialog for editing a train -->
  <ScotDialog :visible="editDialogVisible" type="edit" :header="$t('editTrain')" :disable-action="disableAction"
              @update:visible="editDialogVisible = $event" @action="editTrain" @cancel="toggleEditDialog">
    <ScotTrain :train="train" @update:train="updateTrain" is-edit/>
  </ScotDialog>
</template>

<script setup>
import {ref, computed, onMounted, watch} from 'vue'
import { useTrainStore } from '@/stores/train'
import { useToast } from 'primevue/usetoast'
import { useI18n } from 'vue-i18n'

import railcarImage from '@/assets/images/railcar.png'
import passengerCarImage from '@/assets/images/passenger_car.png'

const { t } = useI18n()
const toast = useToast()

// Dialog visibility states
const createDialogVisible = ref(false)
const editDialogVisible = ref(false)

const trainStore = useTrainStore()
const trains = computed(() => trainStore.trains)
const train = ref(null) // Currently selected train
const originalTrain = ref(null) // Original state of train before edits
const disableAction = ref(false) // Disable dialog actions

// Computed lists of railcars and passenger cars
const railcars = computed(() => trainStore.railcars)
const passengerCars = computed(() => trainStore.passengerCars)

// Function to sort passenger cars by position
const sortedPassengerCars = (passengerCars) => {
  return passengerCars.slice().sort((a, b) => a.position - b.position)
}

const statusOptions = [
  { label: t('active'), value: true },
  { label: t('inactive'), value: false }
]

function initializeFilters(filters) {
  if (!filters.name) filters.name = ''
  if (!filters.railcarID) filters.railcarID = null
  if (!filters.passengerCarIDs) filters.passengerCarIDs = []
  return false
}

function updateTrain(currentTrain) {
  train.value = currentTrain
}

// Visibility of the dialogs
function toggleCreateDialog() {
  createDialogVisible.value = !createDialogVisible.value
  if (createDialogVisible.value) disableAction.value = true
}

function toggleEditDialog(currentTrain) {
  train.value = currentTrain
  if (!editDialogVisible.value) {
    originalTrain.value = JSON.parse(JSON.stringify(currentTrain))
    disableAction.value = true
  }
  editDialogVisible.value = !editDialogVisible.value
}


function showToast(type, message) {
  toast.add({severity: type, summary: type === 'success' ? t('success') : t('error'), detail: message, life: 3000})
}

// CRUD functions of the store
async function createTrain() {
  try {
    const response = await trainStore.createTrain(train.value)
    toggleCreateDialog()
    showToast('success', response.message)
  } catch (error) {
    toggleCreateDialog()
    showToast('error', error.message)
  }
}

async function editTrain() {
  try {
    const response = await trainStore.editTrain(train.value)
    toggleEditDialog()
    showToast('success', response.message)
  } catch (error) {
    toggleEditDialog()
    showToast('error', error.message)
  }
}

async function deleteTrain(currentTrain) {
  try {
    const response = await trainStore.deleteTrain(currentTrain.trainID)
    showToast('success', response.message)
  } catch (error) {
    showToast('error', error.message)
  }
}

// Get the unique key for each train
function getTrainKey(train) {
  return train.trainID
}

// Watch for changes in train to enable or disable actions for dialog
watch(() => train.value, (newVal) => {
    if (createDialogVisible.value) {
      disableAction.value = (newVal === null)
      return
    }
    if (editDialogVisible.value && originalTrain.value) {
      disableAction.value = newVal === null || JSON.stringify(newVal) === JSON.stringify(originalTrain.value)
    }
  }, { deep: true}
)

onMounted(async () => {
  await trainStore.getCarriagesByType()
  await trainStore.getTrains()
});
</script>