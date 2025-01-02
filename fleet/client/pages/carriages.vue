<template>
  <ScotList :items="carriages" :getKey="getCarriageKey" :rowsPerPage="5"
            @create="toggleCreateDialog" @edit="toggleEditDialog" @delete="deleteCarriage">
    <template #title="{ item }">
      {{ $t(item.type.toLowerCase()) }} #{{ item.carriageID }}
      <Tag :severity="item.active ? 'danger' : 'success'" :value="item.active ? $t('active') : $t('inactive')" class="ml-2"/>
    </template>
    <template #description="{ item }">
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
    <template #filters="{ filters }">
      <span v-if="initializeFilters(filters)"/>

      <div class="p-4 space-y-4">
        <div class="flex flex-col space-y-1">
          <label for="status">{{ $t('status') }}</label>
          <SelectButton id="status" v-model="filters.status" :options="statusOptions" optionLabel="label" optionValue="value"/>
        </div>

        <div class="flex flex-col space-y-1">
          <label for="type">{{ $t('type') }}</label>
          <SelectButton id="type" v-model="filters.type" :options="carriageTypes" optionLabel="label" optionValue="value" @change="onTypeChange(filters)"/>
        </div>

        <div class="flex flex-col space-y-1">
          <label for="trackGauge">{{ $t('trackGauge') }}</label>
          <SelectButton id="trackGauge" v-model="filters.trackGauge"  :options="trackGauges" optionLabel="label" optionValue="value"/>
        </div>

        <div class="flex flex-col space-y-1" v-if="filters.type === 'Railcar'">
          <label>{{ $t('maxTractiveForce') }}</label>
          <InputNumber v-model="filters.maxTractiveForce.from" suffix="kN" :placeholder="$t('from')" />
          <InputNumber v-model="filters.maxTractiveForce.to" suffix="kN" :placeholder="$t('to')" />
        </div>
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

  <ScotDialog :visible="createDialogVisible" type="create" :header="$t('createCarriage')" :disable-action="disableAction"
              @update:visible="createDialogVisible = $event" @action="createCarriage" @cancel="toggleCreateDialog">
    <ScotCarriage @update:carriage="updateCarriage"/>
  </ScotDialog>

  <ScotDialog :visible="editDialogVisible" type="edit" :header="$t('editCarriage')" :disable-action="disableAction"
              @update:visible="editDialogVisible = $event" @action="editCarriage" @cancel="toggleEditDialog">
    <ScotCarriage :carriage="carriage" @update:carriage="updateCarriage"/> <!-- :disabledFields="['type', 'trackGauge']" -->
  </ScotDialog>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useCarriageStore } from '@/stores/carriage'
import { useToast } from 'primevue/usetoast'
import { useI18n } from 'vue-i18n'
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

const { t } = useI18n()
const statusOptions = [
  { label: t('active'), value: 'active' },
  { label: t('inactive'), value: 'inactive' }
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