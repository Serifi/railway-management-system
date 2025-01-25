<template>
  <ScotList :items="maintenances" :getKey="getMaintenanceKey" :rowsPerPage="5"
            @create="toggleCreateDialog" @edit="toggleEditDialog" @delete="deleteMaintenance">
    <template #title="{ item }">
      {{ $t('maintenance') }} #{{ item.maintenanceID }}
    </template>
    <!-- Details -->
    <template #description="{ item }">
      <span>
        {{ $t('trainID') }}: {{ item.trainID }}<br/>
        {{ $t('employee') }}: {{ getEmployeeName(item.employeeSSN) }}<br/>
        {{ $t('from') }}: {{ formatDate(item.from_time) }}<br/>
        {{ $t('to') }}: {{ formatDate(item.to_time) }}<br/>
      </span>
    </template>
    <!-- Filters -->
    <template #filters="{ filters }">
      <span v-if="initializeFilters(filters)" />

      <!-- Trains -->
      <div class="p-4 space-y-4">
        <div class="flex flex-col space-y-1">
          <label for="train">{{ $t('train') }}</label>
          <Select id="train" v-model="filters.trainID" :options="trains" optionLabel="name" optionValue="trainID" :placeholder="$t('selectPlaceholder')" filter showClear/>
        </div>

        <!-- Employee -->
        <div class="flex flex-col space-y-1">
          <label for="employee">{{ $t('employee') }}</label>
          <Select id="employee" v-model="filters.employeeSSN" :options="employees" :optionLabel="getEmployeeDisplayName"
                  optionValue="ssn" :placeholder="$t('selectPlaceholder')" filter showClear/>
        </div>
      </div>
    </template>
  </ScotList>

  <!-- Dialog for adding a maintenance -->
  <ScotDialog :visible="createDialogVisible" type="create" :header="$t('createMaintenance')" :disable-action="disableAction"
              @update:visible="createDialogVisible = $event" @action="createMaintenance" @cancel="toggleCreateDialog">
    <ScotMaintenance @update:maintenance="updateMaintenance"/>
  </ScotDialog>

  <!-- Dialog for editing a maintenance -->
  <ScotDialog :visible="editDialogVisible" type="edit" :header="$t('editMaintenance')" :disable-action="disableAction"
              @update:visible="editDialogVisible = $event" @action="editMaintenance" @cancel="toggleEditDialog">
    <ScotMaintenance :maintenance="maintenance" @update:maintenance="updateMaintenance"/>
  </ScotDialog>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useMaintenanceStore } from '@/stores/maintenance'
import { useTrainStore } from '@/stores/train'
import { useEmployeeStore } from '@/stores/employee'
import { useToast } from 'primevue/usetoast'

const toast = useToast()

// Dialog visibility states
const createDialogVisible = ref(false)
const editDialogVisible = ref(false)

// Maintenance, Train and Employee with respective store
const maintenanceStore = useMaintenanceStore()
const trainStore = useTrainStore()
const employeeStore = useEmployeeStore()
const maintenances = computed(() => maintenanceStore.maintenances)
const maintenance = ref(null) // Currently selected maintenance
const trains = computed(() => trainStore.trains)
const employees = computed(() => employeeStore.employees)

const disableAction = ref(false) // Disable dialog actions

function initializeFilters(filters) {
  if (!filters.trainID) filters.trainID = null
  if (!filters.employeeSSN) filters.employeeSSN = null
  return false
}

function formatDate(dateStr) {
  const date = new Date(dateStr)
  return date.toLocaleString()
}

function getEmployeeName(ssn) {
  const employee = employees.value.find(e => e.ssn === ssn)
  return `${employee.firstName} ${employee.lastName}`
}

function getEmployeeDisplayName(employee) {
  return `${employee.firstName} ${employee.lastName}`
}

function updateMaintenance(currentMaintenance) {
  maintenance.value = currentMaintenance
  disableAction.value = maintenance.value === null
}

// Visibility of the dialogs
function toggleCreateDialog() {
  createDialogVisible.value = !createDialogVisible.value
  if (createDialogVisible.value) disableAction.value = true
}

function toggleEditDialog(currentMaintenance) {
  maintenance.value = currentMaintenance
  editDialogVisible.value = !editDialogVisible.value
  if (editDialogVisible.value) disableAction.value = false
}

function showToast(type, message) {
  toast.add({severity: type, summary: type === 'success' ? 'Erfolgreich' : 'Fehler', detail: message, life: 3000})
}

// CRUD functions of the store
async function createMaintenance() {
  try {
    const response = await maintenanceStore.createMaintenance(maintenance.value)
    toggleCreateDialog()
    showToast('success', response.message)
  } catch (error) {
    toggleCreateDialog()
    showToast('error', error.message)
  }
}

async function editMaintenance() {
  try {
    const response = await maintenanceStore.editMaintenance(maintenance.value)
    toggleEditDialog()
    showToast('success', response.message)
  } catch (error) {
    toggleEditDialog()
    showToast('error', error.message)
  }
}

async function deleteMaintenance(currentMaintenance) {
  try {
    const response = await maintenanceStore.deleteMaintenance(currentMaintenance.maintenanceID)
    showToast('success', response.message)
  } catch (error) {
    showToast('error', error.message)
  }
}

// Get the unique key for each maintenance
function getMaintenanceKey(maintenance) {
  return maintenance.maintenanceID
}

onMounted(async () => {
  await trainStore.getTrains()
  await employeeStore.getEmployees()
  await maintenanceStore.getMaintenances()
})
</script>