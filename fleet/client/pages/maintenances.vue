<template>
  <ScotList :items="maintenances" :getKey="getMaintenanceKey" :rowsPerPage="5"
            @create="toggleCreateDialog" @edit="toggleEditDialog" @delete="deleteMaintenance">
    <template #title="{ item }">
      {{ $t('maintenance') }} #{{ item.maintenanceID }}
    </template>
    <template #description="{ item }">
      <span>
        {{ $t('trainID') }}: {{ getTrainName(item.trainID) }}<br/>
        {{ $t('timePeriod') }}: {{ formatDate(item.from_time) }} - {{ formatDate(item.to_time) }}<br/>
      </span>
    </template>
    <template #filters="{ filters }">
      <span v-if="initializeFilters(filters)" />

      <div class="p-4 space-y-4">
        <div class="flex flex-col space-y-1">
          <label for="train">{{ $t('train') }}</label>
          <Select id="train" v-model="filters.trainID" :options="trains" optionLabel="name" optionValue="trainID" :placeholder="$t('selectPlaceholder')" filter showClear/>
        </div>

        <div class="flex flex-col space-y-1">
          <label for="employee">{{ $t('employee') }}</label>
          <!-- Geänderte Komponente von MultiSelect zu Select und Anpassung des v-model -->
          <Select id="employee" v-model="filters.employeeSSN" :options="employees" optionLabel="username" optionValue="ssn" :placeholder="$t('selectPlaceholder')" filter showClear/>
        </div>

        <div class="flex flex-col space-y-1">
          <label for="from_time">{{ $t('from') }}</label>
          <DatePicker id="from_time" v-model="filters.from_time" showTime showSeconds :placeholder="$t('selectPlaceholder')"/>
        </div>

        <div class="flex flex-col space-y-1">
          <label for="to_time">{{ $t('to') }}</label>
          <DatePicker id="to_time" v-model="filters.to_time" showTime showSeconds :placeholder="$t('selectPlaceholder')"/>
        </div>
      </div>
    </template>
  </ScotList>

  <ScotDialog :visible="createDialogVisible" type="create" :header="$t('createMaintenance')" :disable-action="disableAction"
              @update:visible="createDialogVisible = $event" @action="createMaintenance" @cancel="toggleCreateDialog">
    <ScotMaintenance @update:maintenance="updateMaintenance"/>
  </ScotDialog>

  <ScotDialog :visible="editDialogVisible" type="edit" :header="$t('editMaintenance')" :disable-action="disableAction"
              @update:visible="editDialogVisible = $event" @action="editMaintenance" @cancel="toggleEditDialog">
    <ScotMaintenance :maintenance="maintenance" @update:maintenance="updateMaintenance" :disabledFields="['maintenanceID']"/>
  </ScotDialog>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useMaintenanceStore } from '@/stores/maintenance'
import { useTrainStore } from '@/stores/train' // Import des trainStore
import { useEmployeeStore } from '@/stores/employee' // Import des employeeStore
import { useToast } from 'primevue/usetoast'

const toast = useToast()
const createDialogVisible = ref(false)
const editDialogVisible = ref(false)
const maintenanceStore = useMaintenanceStore()
const trainStore = useTrainStore() // Nutzung des trainStore
const employeeStore = useEmployeeStore() // Nutzung des employeeStore
const maintenances = computed(() => maintenanceStore.maintenances)
const maintenance = ref(null)
const disableAction = ref(false)
const trains = computed(() => trainStore.trains)
const employees = computed(() => employeeStore.employees)

function initializeFilters(filters) {
  if (!filters.trainID) {
    filters.trainID = null
  }
  if (!filters.employeeSSN) { // Geändertes Feld
    filters.employeeSSN = null
  }
  if (!filters.from_time) {
    filters.from_time = null
  }
  if (!filters.to_time) {
    filters.to_time = null
  }
  return false
}

function formatDate(dateStr) {
  const date = new Date(dateStr)
  return date.toLocaleString()
}

function getTrainName(trainID) {
  const train = trains.value.find(t => t.trainID === trainID)
  return train ? train.name : 'Unbekannt'
}

function updateMaintenance(currentMaintenance) {
  maintenance.value = currentMaintenance
  disableAction.value = maintenance.value === null
}

function toggleCreateDialog() {
  createDialogVisible.value = !createDialogVisible.value
  if (createDialogVisible.value) disableAction.value = true
}

function createMaintenance() {
  maintenanceStore.createMaintenance(maintenance.value)
      .then(() => {
        toggleCreateDialog()
        toast.add({ severity: 'success', summary: 'Erfolgreich', detail: 'Wartung wurde erstellt', life: 3000 })
      })
      .catch(error => {
        toast.add({ severity: 'error', summary: 'Fehler', detail: error.response?.data?.message || 'Wartung konnte nicht erstellt werden', life: 3000 })
      })
}

function toggleEditDialog(currentMaintenance) {
  maintenance.value = currentMaintenance
  editDialogVisible.value = !editDialogVisible.value
  if (editDialogVisible.value) disableAction.value = false
}

function editMaintenance() {
  maintenanceStore.editMaintenance(maintenance.value)
      .then(() => {
        toggleEditDialog(null)
        toast.add({ severity: 'success', summary: 'Erfolgreich', detail: 'Wartung wurde aktualisiert', life: 3000 })
      })
      .catch(error => {
        toast.add({ severity: 'error', summary: 'Fehler', detail: error.response?.data?.message || 'Wartung konnte nicht aktualisiert werden', life: 3000 })
      })
}

function deleteMaintenance(currentMaintenance) {
  maintenanceStore.deleteMaintenance(currentMaintenance.maintenanceID)
      .then(() => {
        toast.add({ severity: 'success', summary: 'Erfolgreich', detail: 'Wartung wurde gelöscht', life: 3000 })
      })
      .catch(error => {
        toast.add({ severity: 'error', summary: 'Fehler', detail: error.response?.data?.message || 'Wartung konnte nicht gelöscht werden', life: 3000 })
      })
}

function getMaintenanceKey(maintenance) {
  return maintenance.maintenanceID
}

onMounted(async () => {
  await trainStore.getTrains()
  await employeeStore.getEmployees()
  await maintenanceStore.getMaintenances()
});
</script>