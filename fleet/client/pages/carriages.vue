<template>
  <ScotList :items="carriages" :getKey="getCarriageKey" :rowsPerPage="5" disable-on-active
            @create="toggleCreateDialog" @edit="toggleEditDialog" @delete="deleteCarriage">
    <template #title="{ item }">
      {{ $t(item.type.toLowerCase()) }} #{{ item.carriageID }}
      <Tag :severity="item.active ? 'danger' : 'success'" :value="item.active ? $t('active') : $t('inactive')" class="ml-2 !py-[0px]"/>
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
    <ScotCarriage :carriage="carriage" @update:carriage="updateCarriage"/>
  </ScotDialog>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useCarriageStore } from '@/stores/carriage'
import { useToast } from 'primevue/usetoast'
import { useI18n } from 'vue-i18n'
import ScotList from '~/components/ScotList.vue'
import ScotCarriage from '~/components/ScotCarriage.vue'
import ScotDialog from "~/components/ScotDialog.vue"

const toast = useToast()
const createDialogVisible = ref(false)
const editDialogVisible = ref(false)
const carriageStore = useCarriageStore()
const carriages = computed(() => carriageStore.carriagesWithStatus)
const carriage = ref(null)
const originalCarriage = ref(null)
const disableAction = ref(false)
const trackGauges = computed(() => carriageStore.trackGauges)
const carriageTypes = computed(() => carriageStore.carriageTypes)

const { t } = useI18n()
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

function toggleEditDialog(currentCarriage) {
  carriage.value = currentCarriage
  if (!editDialogVisible.value) {
    originalCarriage.value = JSON.parse(JSON.stringify(currentCarriage))
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

async function createCarriage() {
  try {
    const response = await carriageStore.createCarriage(carriage.value)
    toggleCreateDialog()
    showToast('success', response.message || t('carriageCreated'))
  } catch (error) {
    toggleCreateDialog()
    showToast('error', error.message || t('carriageCreateError'))
  }
}

async function editCarriage() {
  try {
    const response = await carriageStore.editCarriage(carriage.value)
    toggleEditDialog(null)
    showToast('success', response.message || t('carriageUpdated'))
  } catch (error) {
    toggleEditDialog(null)
    showToast('error', error.message || t('carriageUpdateError'))
  }
}

async function deleteCarriage(currentCarriage) {
  try {
    const response = await carriageStore.deleteCarriage(currentCarriage.carriageID)
    showToast('success', response.message || t('carriageDeleted'))
  } catch (error) {
    showToast('error', error.message || t('carriageDeleteError'))
  }
}

function getCarriageKey(carriage) {
  return carriage.carriageID
}

watch(carriage, (newVal) => {
  if (originalCarriage.value)
    disableAction.value = JSON.stringify(newVal) === JSON.stringify(originalCarriage.value)
}, { deep: true })

onMounted(() => carriageStore.getCarriages())
</script>