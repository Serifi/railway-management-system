<template>
  <List :items="carriages" :getKey="getCarriageKey" :rowsPerPage="5"
        @create="toggleCreateDialog" @edit="toggleEditDialog" @delete="deleteCarriage">
    <template #title="{ item }">
      {{ item.type }} #{{ item.carriageID }}
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
  </List>

  <ScotDialog :visible="createDialogVisible" type="create" header="Wagen erstellen" :disable-action="disableAction"
              @update:visible="createDialogVisible = $event" @action="createCarriage" @cancel="toggleCreateDialog">
    <ScotCarriage @update:carriage="updateCarriage"/>
  </ScotDialog>

  <ScotDialog :visible="editDialogVisible" type="edit" header="Wagen bearbeiten" :disable-action="disableAction"
              @update:visible="editDialogVisible = $event" @action="editCarriage" @cancel="toggleEditDialog">
    <ScotCarriage :carriage="carriage" @update:carriage="updateCarriage" :disabledFields="['type', 'trackGauge']"/>
  </ScotDialog>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useCarriageStore } from '@/stores/carriage'
import { useToast } from 'primevue/usetoast'
import List from '~/components/ScotList.vue'
import ScotCarriage from '~/components/ScotCarriage.vue'
import ScotDialog from "~/components/ScotDialog.vue"

const toast = useToast()
const createDialogVisible = ref(false)
const editDialogVisible = ref(false)
const carriageStore = useCarriageStore()
const carriages = computed(() => carriageStore.carriages)
const carriage = ref(null)
const disableAction = ref(false)

function updateCarriage(currentCarriage) {
  carriage.value = currentCarriage
  disableAction.value = carriage.value === null
}

function toggleCreateDialog() {
  createDialogVisible.value = !createDialogVisible.value
  if (createDialogVisible.value) disableAction.value = true
}

function createCarriage() {
  carriageStore.createCarriage(carriage.value)
  toggleCreateDialog()
  toast.add({ severity: 'success', summary: 'Erfolgreich', detail: 'Aktion wurde erfolgreich abgeschlossen', life: 3000 })
}

async function toggleEditDialog(currentCarriage) {
  carriage.value = currentCarriage
  editDialogVisible.value = !editDialogVisible.value
  if (editDialogVisible.value) disableAction.value = false
}

function editCarriage() {
  carriageStore.editCarriage(carriage.value)
  toggleEditDialog(null)
  toast.add({ severity: 'success', summary: 'Erfolgreich', detail: 'Aktion wurde erfolgreich abgeschlossen', life: 3000 })
}

function deleteCarriage(currentCarriage) {
  carriageStore.deleteCarriage(currentCarriage.carriageID)
  toast.add({ severity: 'success', summary: 'Erfolgreich', detail: 'Aktion wurde erfolgreich abgeschlossen', life: 3000 })
}

function getCarriageKey(carriage) {
  return carriage.carriageID
}

onMounted(() => {
  carriageStore.getCarriages()
})
</script>