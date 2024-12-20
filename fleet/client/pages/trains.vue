<!-- components/Train.vue -->
<template>
  <ScotList :items="trains" :getKey="getTrainKey" :rowsPerPage="5"
            @create="toggleCreateDialog" @edit="toggleEditDialog" @delete="deleteTrain">
    <template #title="{ item }">
      {{ item.name }}
      <Tag :severity="item.active ? 'success' : 'danger'" :value="item.active ? 'aktiv' : 'inaktiv'" class="ml-2"/>
    </template>
    <template #description="{ item }">
      <div class="wagon-container">
        <!-- Triebwagen -->
        <div class="wagon">
          <img :src="railcarImage" alt="Triebwagen" class="wagon-image"/>
          <div class="wagon-id">{{ item.railcarID }}</div>
        </div>

        <!-- Personenwagen -->
        <div class="wagon" v-for="passengerCarID in item.passengerCarIDs" :key="passengerCarID">
          <img :src="passengerCarImage" alt="Personenwagen" class="wagon-image"/>
          <div class="wagon-id">{{ passengerCarID }}</div>
        </div>
      </div>
    </template>
    <template #filters="{ filters }">
      <span v-if="initializeFilters(filters)" />

      <div class="p-4 space-y-4">
        <div class="flex flex-col space-y-1">
          <label for="status">Status</label>
          <SelectButton id="status" v-model="filters.status" :options="statusOptions" optionLabel="label" optionValue="value"/>
        </div>

        <div class="flex flex-col space-y-1">
          <label for="railcar">Triebwagen</label>
          <Dropdown id="railcar" v-model="filters.railcarID" :options="railcars" optionLabel="carriageID" optionValue="carriageID" placeholder="Triebwagen auswählen..." />
        </div>

        <div class="flex flex-col space-y-1">
          <label for="passengerCars">Personenwagen</label>
          <MultiSelect id="passengerCars" v-model="filters.passengerCarIDs" :options="passengerCars" optionLabel="carriageID" optionValue="carriageID" placeholder="Personenwagen auswählen..." />
        </div>
      </div>
    </template>
  </ScotList>

  <ScotDialog :visible="createDialogVisible" type="create" header="Zug erstellen" :disable-action="disableAction"
              @update:visible="createDialogVisible = $event" @action="createTrain" @cancel="toggleCreateDialog">
    <ScotTrain @update:train="updateTrain"/>
  </ScotDialog>

  <ScotDialog :visible="editDialogVisible" type="edit" header="Zug bearbeiten" :disable-action="disableAction"
              @update:visible="editDialogVisible = $event" @action="editTrain" @cancel="toggleEditDialog">
    <ScotTrain :train="train" @update:train="updateTrain" :disabledFields="['trainID']"/>
  </ScotDialog>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useTrainStore } from '@/stores/train'
import { useToast } from 'primevue/usetoast'

import railcarImage from '@/assets/images/railcar.png'
import passengerCarImage from '@/assets/images/passenger_car.png'

const toast = useToast();
const createDialogVisible = ref(false)
const editDialogVisible = ref(false)
const trainStore = useTrainStore()
const trains = computed(() => trainStore.trainsWithStatus)
const train = ref(null)
const disableAction = ref(false)
const railcars = computed(() => trainStore.railcars)
const passengerCars = computed(() => trainStore.passengerCars)

const statusOptions = [
  { label: 'Aktiv', value: 'aktiv' },
  { label: 'Inaktiv', value: 'inaktiv' }
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

function createTrain() {
  trainStore.createTrain(train.value)
      .then(() => {
        toggleCreateDialog()
        toast.add({ severity: 'success', summary: 'Erfolgreich', detail: 'Zug wurde erstellt', life: 3000 })
      })
      .catch(error => {
        toast.add({ severity: 'error', summary: 'Fehler', detail: error.response?.data?.message || 'Zug konnte nicht erstellt werden', life: 3000 })
      })
}

function toggleEditDialog(currentTrain) {
  train.value = currentTrain
  editDialogVisible.value = !editDialogVisible.value
  if (editDialogVisible.value) disableAction.value = false
}

function editTrain() {
  trainStore.editTrain(train.value)
      .then(() => {
        toggleEditDialog(null)
        toast.add({ severity: 'success', summary: 'Erfolgreich', detail: 'Zug wurde aktualisiert', life: 3000 })
      })
      .catch(error => {
        toast.add({ severity: 'error', summary: 'Fehler', detail: error.response?.data?.message || 'Zug konnte nicht aktualisiert werden', life: 3000 })
      })
}

function deleteTrain(currentTrain) {
  trainStore.deleteTrain(currentTrain.trainID)
      .then(() => {
        toast.add({ severity: 'success', summary: 'Erfolgreich', detail: 'Zug wurde gelöscht', life: 3000 })
      })
      .catch(error => {
        toast.add({ severity: 'error', summary: 'Fehler', detail: error.response?.data?.message || 'Zug konnte nicht gelöscht werden', life: 3000 })
      })
}

function getTrainKey(train) {
  return train.trainID
}

onMounted(async () => {
  await trainStore.getRailcars()
  await trainStore.getPassengerCars()
  await trainStore.getTrains()
});
</script>

<style>
.p-confirm-popup-accept,
.p-confirm-popup-reject {
  padding: 4px;
  margin: 4px;
}

.p-confirm-popup-accept{
  background-color: #FF9999 !important;
}

.wagon-container {
 display: flex;
 align-items: center;
 overflow-x: auto;
 padding: 10px 0;
}

.wagon {
  position: relative;
  margin-right: 0px;
  flex: 0 0 auto;
}

.wagon:last-child {
  margin-right: 0;
}

.wagon-image {
  width: 100px;
  height: auto;
  display: block;
}

.wagon-id {
  position: absolute;
  top: 30%;
  right: 15%;
  transform: translate(-50%, -50%);
  color: white;
  font-weight: bold;
  pointer-events: none;
}
</style>