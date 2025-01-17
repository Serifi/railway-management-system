<template>
  <ScotList :items="trains" :getKey="getTrainKey" :rowsPerPage="5"
            @create="toggleCreateDialog" @edit="toggleEditDialog" @delete="deleteTrain">
    <template #title="{ item }">
      {{ item.name }}
      <Tag :severity="item.active ? 'success' : 'danger'" :value="$t(item.active ? 'active' : 'inactive')" class="ml-2 !py-[0px]"/>
    </template>
    <template #description="{ item }">
      ID: {{ item.trainID }} <br>
      {{ $t('trackGauge') }}: {{ item.railcar.trackGauge }} <br>
      {{ $t('maxTractiveForce') }}: {{ item.railcar.maxTractiveForce }} <br>
      {{ $t('weight') }}: {{ item.totalWeight }} <br>
      {{ $t('numberOfSeats') }}: {{ item.totalSeats }} <br>
      <div class="wagon-container">
        <!-- Railcar -->
        <div class="wagon">
          <img :src="railcarImage" :alt="$t('railcar')" class="wagon-image"/>
          <div class="wagon-id">{{ item.railcar.carriageID }}</div>
        </div>

        <!-- Passenger Cars -->
        <div class="wagon"
             v-for="passengerCar in sortedPassengerCars(item.passenger_cars)" :key="passengerCar.carriageID">
          <img :src="passengerCarImage" :alt="$t('passengerCar')" class="wagon-image"/>
          <div class="wagon-id">{{ passengerCar.carriageID }}</div>
        </div>
      </div>
    </template>
    <template #filters="{ filters }">
      <span v-if="initializeFilters(filters)" />

      <div class="p-4 space-y-4">
        <div class="flex flex-col space-y-1">
          <label for="status">{{ $t('status') }}</label>
          <SelectButton id="status" v-model="filters.status" :options="statusOptions" optionLabel="label" optionValue="value"/>
        </div>

        <div class="flex flex-col space-y-1">
          <label for="railcar">{{ $t('railcar') }}</label>
          <Select id="railcar" v-model="filters.railcarID" :options="railcars" optionLabel="carriageID" optionValue="carriageID" :placeholder="$t('selectPlaceholder')" filter showClear/>
        </div>

        <div class="flex flex-col space-y-1">
          <label for="passengerCars">{{ $t('passengerCar') }}</label>
          <MultiSelect id="passengerCars" v-model="filters.passengerCarIDs" :options="passengerCars" optionLabel="carriageID" optionValue="carriageID" :placeholder="$t('selectPlaceholder')" filter showClear/>
        </div>
      </div>
    </template>
  </ScotList>

  <ScotDialog :visible="createDialogVisible" type="create" :header="$t('createTrain')" :disable-action="disableAction"
              @update:visible="createDialogVisible = $event" @action="createTrain" @cancel="toggleCreateDialog">
    <ScotTrain @update:train="updateTrain"/>
  </ScotDialog>

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

const toast = useToast();
const createDialogVisible = ref(false)
const editDialogVisible = ref(false)
const trainStore = useTrainStore()
const trains = computed(() => trainStore.trainsWithStatus)
const train = ref(null)
const originalTrain = ref(null)
const disableAction = ref(false)
const railcars = computed(() => trainStore.railcars)
const passengerCars = computed(() => trainStore.passengerCars)
const sortedPassengerCars = (passengerCars) => {
  return passengerCars.slice().sort((a, b) => a.position - b.position)
}

const { t } = useI18n()
const statusOptions = [
  { label: t('active'), value: true },
  { label: t('inactive'), value: false }
]

function initializeFilters(filters) {
  if (!filters.name) {
    filters.name = ''
  }
  if (!filters.railcarID) {
    filters.railcarID = null
  }
  if (!filters.passengerCarIDs) {
    filters.passengerCarIDs = []
  }
  return false
}

function updateTrain(currentTrain) {
  train.value = currentTrain
  disableAction.value = train.value === null
}

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
  toast.add({
    severity: type,
    summary: type === 'success' ? t('success') : t('error'),
    detail: message,
    life: 3000
  })
}

async function createTrain() {
  try {
    const response = await trainStore.createTrain(train.value)
    toggleCreateDialog()
    showToast('success', response.message || t('trainCreated'))
  } catch (error) {
    toggleCreateDialog()
    showToast('error', error.message || t('trainCreateError'))
  }
}

async function editTrain() {
  try {
    const response = await trainStore.editTrain(train.value)
    toggleEditDialog()
    showToast('success', response.message || t('trainUpdated'))
  } catch (error) {
    toggleEditDialog()
    showToast('error', error.message || t('trainUpdateError'))
  }
}

async function deleteTrain(currentTrain) {
  try {
    const response = await trainStore.deleteTrain(currentTrain.trainID)
    showToast('success', response.message || t('trainDeleted'))
  } catch (error) {
    showToast('error', error.message || t('trainDeleteError'))
  }
}

function getTrainKey(train) {
  return train.trainID
}

watch(train, (newVal) => {
  if (originalTrain.value)
    disableAction.value = JSON.stringify(newVal) === JSON.stringify(originalTrain.value)
}, { deep: true })

onMounted(async () => {
  await trainStore.getCarriagesByType()
  await trainStore.getTrains()
  console.log(trains.value)
});
</script>