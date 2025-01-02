<!-- components/Maintenance.vue -->
<template>
  <ScotList :items="maintenances" :getKey="getMaintenanceKey" :rowsPerPage="5"
            @create="toggleCreateDialog" @edit="toggleEditDialog" @delete="deleteMaintenance">
    <template #title="{ item }">
      Wartung #{{ item.maintenanceID }}
    </template>
    <template #description="{ item }">
      <span>
        Zug ID: {{ item.trainID }}<br/>
        Zeitraum: {{ formatDate(item.from_time) }} - {{ formatDate(item.to_time) }}<br/>
      </span>
    </template>
    <template #filters="{ filters }">
      <span v-if="initializeFilters(filters)" />

      <div class="p-4 space-y-4">
        <div class="flex flex-col space-y-1">
          <label for="train">Zug</label>
          <Select id="train" v-model="filters.trainID" :options="trains" optionLabel="name" optionValue="trainID" placeholder="Zug auswählen..." />
        </div>

        <div class="flex flex-col space-y-1">
          <label for="employee">Mitarbeiter:innen</label>
          <MultiSelect id="employee" v-model="filters.employeeSSNs" :options="employees" optionLabel="username" optionValue="ssn" placeholder="Mitarbeiter auswählen..." />
        </div>

        <div class="flex flex-col space-y-1">
          <label for="from_time">Von</label>
          <Calendar id="from_time" v-model="filters.from_time" showTime showSeconds placeholder="Startzeitpunkt" />
        </div>

        <div class="flex flex-col space-y-1">
          <label for="to_time">Bis</label>
          <Calendar id="to_time" v-model="filters.to_time" showTime showSeconds placeholder="Endzeitpunkt" />
        </div>
      </div>
    </template>
  </ScotList>

  <ScotDialog :visible="createDialogVisible" type="create" header="Wartung erstellen" :disable-action="disableAction"
              @update:visible="createDialogVisible = $event" @action="createMaintenance" @cancel="toggleCreateDialog">
    <ScotMaintenance @update:maintenance="updateMaintenance"/>
  </ScotDialog>

  <ScotDialog :visible="editDialogVisible" type="edit" header="Wartung bearbeiten" :disable-action="disableAction"
              @update:visible="editDialogVisible = $event" @action="editMaintenance" @cancel="toggleEditDialog">
    <ScotMaintenance :maintenance="maintenance" @update:maintenance="updateMaintenance" :disabledFields="['maintenanceID']"/>
  </ScotDialog>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useMaintenanceStore } from '@/stores/maintenance'
import { useToast } from 'primevue/usetoast'

const toast = useToast();
const createDialogVisible = ref(false)
const editDialogVisible = ref(false)
const maintenanceStore = useMaintenanceStore()
const maintenances = computed(() => maintenanceStore.maintenances)
const maintenance = ref(null)
const disableAction = ref(false)
const trains = computed(() => maintenanceStore.trains)
const employees = computed(() => maintenanceStore.employees)

function initializeFilters(filters) {
  if (!filters.trainID) {
    filters.trainID = null
  }
  if (!filters.employeeSSNs) {
    filters.employeeSSNs = []
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
  await maintenanceStore.getTrains()
  //await maintenanceStore.getEmployees()
  await maintenanceStore.getMaintenances()
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