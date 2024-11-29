<template>
  <List :items="carriages" :getKey="getCarriageKey" :rowsPerPage="5"
        @create="toggleCreateCarriageDialog" @edit="toggleEditCarriageDialog" @delete="deleteCarriage">
    <template #title="{ item }">
      {{ `Carriage ${item.carriageID} (${item.type})` }}
    </template>
    <template #description="{ item }">
      <template v-if="item.type === 'PassengerCar'">
        Sitzplätze: {{ item.numberOfSeats }}<br/>
        Spurweite: {{ item.trackGauge }} mm<br/>
        Maximalgewicht: {{ item.maxWeight }} kg
      </template>
      <template v-if="item.type === 'Railcar'">
        Spurweite: {{ item.trackGauge }} mm<br/>
        Maximale Zugkraft: {{ item.maxTractiveForce }} N
      </template>
    </template>
  </List>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useCarriageStore } from '@/stores/carriage'
import { useToast } from 'primevue/usetoast'
import List from '~/components/ScotList.vue'

const toast = useToast()
const carriageStore = useCarriageStore()
const carriages = computed(() => carriageStore.carriages)
const carriage = ref(null)
const createCarriageDialogVisible = ref(false)
const editCarriageDialogVisible = ref(false)

function getCarriageKey(carriage) {
  return carriage.carriageID;
}

function toggleCreateCarriageDialog() {
  createCarriageDialogVisible.value = !createCarriageDialogVisible.value;

}

function toggleEditCarriageDialog(currentCarriage) {
  carriage.value = currentCarriage;
  editCarriageDialogVisible.value = !editCarriageDialogVisible.value;
}

function createCarriage() {
  if (carriage.value) {
    carriageStore.carriages.push({ ...carriage.value });
    toggleCreateCarriageDialog();
    toast.add({
      severity: 'success',
      summary: 'Erfolgreich',
      detail: 'Wagen wurde erfolgreich erstellt.',
      life: 3000,
    });
  }
}

function editCarriage() {
  if (carriage.value) {
    const index = carriageStore.carriages.findIndex(c => c.carriageID === carriage.value.carriageID);
    if (index !== -1) {
      carriageStore.carriages[index] = { ...carriage.value };
    }
    toggleEditCarriageDialog();
    toast.add({
      severity: 'success',
      summary: 'Erfolgreich',
      detail: 'Wagen wurde erfolgreich bearbeitet.',
      life: 3000,
    });
  }
}

function deleteCarriage(currentCarriage) {
  const index = carriageStore.carriages.findIndex(c => c.carriageID === currentCarriage.carriageID);
  if (index !== -1) {
    carriageStore.carriages.splice(index, 1);
    toast.add({
      severity: 'success',
      summary: 'Erfolgreich',
      detail: 'Wagen wurde erfolgreich gelöscht.',
      life: 3000,
    });
  }
}
</script>