<template>
  <ScotList :items="carriages" :getKey="getCarriageKey" :rowsPerPage="5" disable-on-active @create="toggleCreateDialog" @edit="toggleEditDialog" @delete="deleteCarriage">
    <template #title="{ item }">
      {{ $t(item.type.toLowerCase()) }} #{{ item.carriageID }}
      <Tag :severity="item.active ? 'danger' : 'success'" :value="item.active ? $t('active') : $t('inactive')" class="ml-2 !py-[0px]"/>
    </template>
    <template #description="{ item }">
      <!-- Details based on type -->
      <span v-if="item.type === 'Railcar'">
        {{ $t('trackGauge') }}: {{ item.trackGauge }} mm<br/>
        {{ $t('maxTractiveForce') }}: {{ item.maxTractiveForce }} kN
      </span>
      <span v-else-if="item.type === 'PassengerCar'">
        {{ $t('trackGauge') }}: {{ item.trackGauge }} mm<br/>
        {{ $t('numberOfSeats') }}: {{ item.numberOfSeats }}<br/>
        {{ $t('maxWeight') }}: {{ item.maxWeight }} kg
      </span>
    </template>
    <!-- Filters -->
    <template #filters="{ filters }">
      <span v-if="initializeFilters(filters)"/>

      <div class="p-4 space-y-4">
        <!-- Status (in-active) -->
        <div class="flex flex-col space-y-1">
          <label for="status">{{ $t('status') }}</label>
          <SelectButton id="status" v-model="filters.status" :options="statusOptions" optionLabel="label" optionValue="value"/>
        </div>

        <!-- Type -->
        <div class="flex flex-col space-y-1">
          <label for="type">{{ $t('type') }}</label>
          <SelectButton id="type" v-model="filters.type" :options="carriageTypes" optionLabel="label" optionValue="value" @change="onTypeChange(filters)"/>
        </div>

        <!-- Track Gauge -->
        <div class="flex flex-col space-y-1">
          <label for="trackGauge">{{ $t('trackGauge') }}</label>
          <SelectButton id="trackGauge" v-model="filters.trackGauge"  :options="trackGauges" optionLabel="label" optionValue="value"/>
        </div>

        <!-- Raiclar: Tractive Force -->
        <div class="flex flex-col space-y-1" v-if="filters.type === 'Railcar'">
          <label>{{ $t('maxTractiveForce') }}</label>
          <InputNumber v-model="filters.maxTractiveForce.from" suffix="kN" :placeholder="$t('from')" />
          <InputNumber v-model="filters.maxTractiveForce.to" suffix="kN" :placeholder="$t('to')" />
        </div>

        <!-- PassengerCar: Weight & Seats -->
        <div class="flex flex-col space-y-1" v-if="filters.type === 'PassengerCar'">
          <label>{{ $t('maxWeight') }}</label>
          <InputNumber v-model="filters.maxWeight.from" suffix="t" :placeholder="$t('from')" />
          <InputNumber v-model="filters.maxWeight.to" suffix="t" :placeholder="$t('to')" />
        </div>
        <div class="flex flex-col space-y-1" v-if="filters.type === 'PassengerCar'">
          <label>{{ $t('numberOfSeats') }}</label>
          <InputNumber v-model="filters.numberOfSeats.from" :placeholder="$t('from')" />
          <InputNumber v-model="filters.numberOfSeats.to" :placeholder="$t('to')" />
        </div>
      </div>
    </template>
  </ScotList>

  <!-- Dialog for creating a carriage -->
  <ScotDialog :visible="createDialogVisible" type="create" :header="$t('createCarriage')" :disable-action="disableAction"
              @update:visible="createDialogVisible = $event" @action="createCarriage" @cancel="toggleCreateDialog">
    <ScotCarriage @update:carriage="updateCarriage"/>
  </ScotDialog>

  <!-- Dialog for editing a carriage -->
  <ScotDialog :visible="editDialogVisible" type="edit" :header="$t('editCarriage')" :disable-action="disableAction"
              @update:visible="editDialogVisible = $event" @action="editCarriage" @cancel="toggleEditDialog">
    <ScotCarriage :carriage="carriage" @update:carriage="updateCarriage"/>
  </ScotDialog>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useCarriageStore } from '@/stores/carriage'
import { useToast } from 'primevue/usetoast'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
const toast = useToast()

// Dialog visibility states
const createDialogVisible = ref(false)
const editDialogVisible = ref(false)

const carriageStore = useCarriageStore()
const carriages = computed(() => carriageStore.carriagesWithStatus)
const carriage = ref(null) // Currently selected train
const originalCarriage = ref(null) // Original state of train before edits
const disableAction = ref(false) // Disable dialog actions

// Options for Type, Track Gauge and Status
const carriageTypes = computed(() => carriageStore.carriageTypes)
const trackGauges = computed(() => carriageStore.trackGauges)
const statusOptions = [
  { label: t('active'), value: true },
  { label: t('inactive'), value: false }
]

function initializeFilters(filters) {
  if (!filters.maxTractiveForce) filters.maxTractiveForce = { from: null, to: null }
  if (!filters.maxWeight) filters.maxWeight = { from: null, to: null }
  if (!filters.numberOfSeats) filters.numberOfSeats = { from: null, to: null }
  return false
}

// Handle changes to the type filter
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
}

// Visibility of the dialogs
function toggleCreateDialog() {
  createDialogVisible.value = !createDialogVisible.value
  if (createDialogVisible.value) disableAction.value = true
}

function toggleEditDialog(currentCarriage) {
  carriage.value = currentCarriage
  if (!editDialogVisible.value) {
    originalCarriage.value = JSON.parse(JSON.stringify(currentCarriage))
    disableAction.value = true
  }
  editDialogVisible.value = !editDialogVisible.value
}

function showToast(type, message) {
  toast.add({severity: type, summary: type === 'success' ? t('success') : t('error'), detail: message, life: 3000})
}

// CRUD functions of the store
async function createCarriage() {
  try {
    const response = await carriageStore.createCarriage(carriage.value)
    toggleCreateDialog()
    showToast('success', response.message)
  } catch (error) {
    toggleCreateDialog()
    showToast('error', error.message)
  }
}

async function editCarriage() {
  try {
    const response = await carriageStore.editCarriage(carriage.value)
    toggleEditDialog(null)
    showToast('success', response.message)
  } catch (error) {
    toggleEditDialog(null)
    showToast('error', error.message)
  }
}

async function deleteCarriage(currentCarriage) {
  try {
    const response = await carriageStore.deleteCarriage(currentCarriage.carriageID)
    showToast('success', response.message)
  } catch (error) {
    showToast('error', error.message)
  }
}

// Get the unique key for each carriage
function getCarriageKey(carriage) {
  return carriage.carriageID
}

// Watch for changes in carriage to enable or disable actions for dialog
watch(carriage, (newVal) => {
  if (createDialogVisible.value) {
    disableAction.value = (newVal === null)
    return
  }
  if (editDialogVisible.value && originalCarriage.value) {
    disableAction.value = newVal === null || JSON.stringify(newVal) === JSON.stringify(originalCarriage.value)
  }
}, { deep: true })

onMounted(() => carriageStore.getCarriages())
</script>