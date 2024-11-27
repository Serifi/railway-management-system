<template>
  <div class="p-6">
    <!-- Search -->
    <InputText placeholder="Wagen suchen..." class="p-2"/>

    <!-- List -->
    <List
        v-for="carriage in carriages"
        :key="carriage.carriageID"
        :title="carriageTitle(carriage)"
        :description="carriageDescription(carriage)"
        :titleClass="carriage.type === 'Railcar' ? 'text-green-600' : 'text-red-500'"
        @edit="showEditDialog(carriage)"
        @delete="showDeleteDialog(carriage)"
    />

    <!-- Pagination -->
    <Paginator :rows="10" :totalRecords="totalRecords" :page="currentPage" @page="onPageChange" />

    <!-- Dialog for Edit/Delete Actions -->
    <Dialog v-model:visible="dialogVisible" header="Aktion" width="400px">
      <p>{{ dialogMessage }}</p>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useCarriageStore } from '@/stores/carriage'
import List from '@/components/List.vue'

const carriageStore = useCarriageStore()
const carriages = computed(() => carriageStore.carriages)
const currentPage = ref(1)
const totalRecords = computed(() => carriages.value.length)
const dialogVisible = ref(false)
const dialogMessage = ref('')

function carriageTitle(carriage) {
  return `${carriage.type === 'Railcar' ? 'Triebwagen' : 'Personenwagen'} ${carriage.carriageID}`
}

function carriageDescription(carriage) {
  if (carriage.type === "Railcar") {
    return `max. Zugkraft: ${carriage.maxTractiveForce}kg\nSpurbreite: ${carriage.trackGauge}mm`
  } else if (carriage.type === "PassengerCar") {
    return `max. Gewicht: ${carriage.maxWeight}kg\nSpurbreite: ${carriage.trackGauge}mm\nSitzplätze: ${carriage.numberOfSeats}`
  }
}

function showEditDialog(carriage) {
  dialogMessage.value = `Bearbeiten von ${carriage.name}`
  dialogVisible.value = true
}

function showDeleteDialog(carriage) {
  dialogMessage.value = `Löschen von ${carriage.name}`
  dialogVisible.value = true
}

function onPageChange(event) {
  currentPage.value = event.page
}
</script>