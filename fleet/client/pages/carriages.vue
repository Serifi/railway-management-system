<template>
  <ScotList :items="carriages" :getKey="getCarriageKey" :rowsPerPage="5"
            @create="toggleCreateDialog" @edit="toggleEditDialog" @delete="deleteCarriage">
    <template #title="{ item }">
      {{ item.type }} #{{ item.carriageID }}
      <Tag :severity="item.active ? 'danger' : 'success'" :value="item.active ? 'aktiv' : 'inaktiv'" class="ml-2"/>
    </template>
    <template #description="{ item }">
      <span v-if="item.type === 'Railcar'">
        Spurweite: {{ item.trackGauge }} mm<br/>
        Maximale Zugkraft: {{ item.maxTractiveForce }} kN
      </span>
      <span v-else-if="item.type === 'PassengerCar'">
        Spurweite: {{ item.trackGauge }} mm<br/>
        Sitzplätze: {{ item.numberOfSeats }}<br/>
        Maximales Gewicht: {{ item.maxWeight }} kg
      </span>
    </template>
    <template #filters="{ filters }">
      <span v-if="initializeFilters(filters)"/>

      <div class="p-4 space-y-4">
        <div class="flex flex-col space-y-1">
          <label for="status">Status</label>
          <SelectButton id="status" v-model="filters.status" :options="statusOptions" optionLabel="label" optionValue="value"/>
        </div>

        <div class="flex flex-col space-y-1">
          <label for="type">Typ</label>
          <SelectButton id="type" v-model="filters.type" :options="carriageTypes" optionLabel="label" optionValue="value" @change="onTypeChange(filters)"/>
        </div>

        <div class="flex flex-col space-y-1">
          <label for="trackGauge">Spurweite</label>
          <SelectButton id="trackGauge" v-model="filters.trackGauge"  :options="trackGauges" optionLabel="label" optionValue="value"/>
        </div>

        <div class="flex flex-col space-y-1" v-if="filters.type === 'Railcar'">
          <label>Maximale Zugkraft</label>
          <InputNumber v-model="filters.maxTractiveForce.from" suffix="kN" placeholder="von" />
          <InputNumber v-model="filters.maxTractiveForce.to" suffix="kN" placeholder="bis" />
        </div>
        <div class="flex flex-col space-y-1" v-if="filters.type === 'PassengerCar'">
          <label>Maximales Gewicht</label>
          <InputNumber v-model="filters.maxWeight.from" suffix="t" placeholder="von" />
          <InputNumber v-model="filters.maxWeight.to" suffix="t" placeholder="bis" />
        </div>

        <div class="flex flex-col space-y-1" v-if="filters.type === 'PassengerCar'">
          <label>Sitzplätze</label>
          <InputNumber v-model="filters.numberOfSeats.from" placeholder="von" />
          <InputNumber v-model="filters.numberOfSeats.to" placeholder="bis" />
        </div>
      </div>
      <div class="flex justify-center border rounded mt-8">
        <ScotButton label="Filter zurücksetzen" icon="pi pi-refresh" variant="grey" :disabled="disableAction" @click="resetFilters(filters)"/>
      </div>
    </template>
  </ScotList>

  <ScotDialog :visible="createDialogVisible" type="create" header="Wagen erstellen" :disable-action="disableAction"
              @update:visible="createDialogVisible = $event" @action="createCarriage" @cancel="toggleCreateDialog">
    <ScotCarriage @update:carriage="updateCarriage"/>
  </ScotDialog>

  <ScotDialog :visible="editDialogVisible" type="edit" header="Wagen bearbeiten" :disable-action="disableAction"
              @update:visible="editDialogVisible = $event" @action="editCarriage" @cancel="toggleEditDialog">
    <ScotCarriage :carriage="carriage" @update:carriage="updateCarriage"/> <!-- :disabledFields="['type', 'trackGauge']" -->
  </ScotDialog>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useCarriageStore } from '@/stores/carriage'
import { useToast } from 'primevue/usetoast'
import ScotList from '~/components/ScotList.vue'
import ScotCarriage from '~/components/ScotCarriage.vue'
import ScotDialog from "~/components/ScotDialog.vue"

const toast = useToast();
const createDialogVisible = ref(false)
const editDialogVisible = ref(false)
const carriageStore = useCarriageStore()
const carriages = computed(() => carriageStore.carriagesWithStatus)
const carriage = ref(null)
const disableAction = ref(false)
const trackGauges = computed(() => carriageStore.trackGauges)
const carriageTypes = computed(() => carriageStore.carriageTypes)

const statusOptions = [
  { label: 'Aktiv', value: 'aktiv' },
  { label: 'Inaktiv', value: 'inaktiv' }
]

function initializeFilters(filters) {
  if (!filters.maxTractiveForce) {
    filters.maxTractiveForce = { from: null, to: null }
  }
  if (!filters.maxWeight) {
    filters.maxWeight = { from: null, to: null }
  }
  if (!filters.numberOfSeats) {
    filters.numberOfSeats = { from: null, to: null }
  }
  return false
}

function onTypeChange(filters) {
  if (filters.type !== 'Railcar') {
    filters.maxTractiveForce = { from: null, to: null }
  }
  if (filters.type !== 'PassengerCar') {
    filters.maxWeight = { from: null, to: null }
    filters.numberOfSeats = { from: null, to: null }
  }
}

function updateCarriage(currentCarriage) {
  carriage.value = currentCarriage
  disableAction.value = carriage.value === null
}

function toggleCreateDialog() {
  createDialogVisible.value = !createDialogVisible.value
  if (createDialogVisible.value) disableAction.value = true
}

async function createCarriage() {
  try {
    const response = await carriageStore.createCarriage(carriage.value)
    toggleCreateDialog()
    toast.add({
      severity: 'success',
      summary: 'Erfolgreich',
      detail: response.message || 'Wagen wurde erfolgreich erstellt.',
      life: 3000
    })
  } catch (error) {
    toggleCreateDialog()
    toast.add({
      severity: 'error',
      summary: 'Fehler',
      detail: error.message || 'Beim Erstellen des Wagens ist ein Fehler aufgetreten.',
      life: 5000
    })
  }
}

async function toggleEditDialog(currentCarriage) {
  carriage.value = currentCarriage
  editDialogVisible.value = !editDialogVisible.value
  if (editDialogVisible.value) disableAction.value = false
}

async function editCarriage() {
  try {
    const response = await carriageStore.editCarriage(carriage.value)
    toggleEditDialog(null)
    toast.add({
      severity: 'success',
      summary: 'Erfolgreich',
      detail: response.message || 'Wagen wurde erfolgreich bearbeitet.',
      life: 3000
    })
  } catch (error) {
    toggleEditDialog(null)
    toast.add({
      severity: 'error',
      summary: 'Fehler',
      detail: error.message || 'Beim Bearbeiten des Wagens ist ein Fehler aufgetreten.',
      life: 5000
    })
  }
}

async function deleteCarriage(currentCarriage) {
  try {
    const response = await carriageStore.deleteCarriage(currentCarriage.carriageID)
    toast.add({
      severity: 'success',
      summary: 'Erfolgreich',
      detail: response.message || 'Wagen wurde erfolgreich gelöscht.',
      life: 3000
    })
  } catch (error) {
    toast.add({
      severity: 'error',
      summary: 'Fehler',
      detail: error.message || 'Beim Löschen des Wagens ist ein Fehler aufgetreten.',
      life: 5000
    })
  }
}

function getCarriageKey(carriage) {
  return carriage.carriageID
}

function resetFilters(filters) {
  Object.keys(filters).forEach(key => {
    if (typeof filters[key] === 'object' && filters[key] !== null) {
      Object.keys(filters[key]).forEach(subKey => {
        filters[key][subKey] = null
      })
    } else {
      filters[key] = null
    }
  })
}

onMounted(() => {
  carriageStore.getCarriages()
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
</style>