<template>
  <div class="p-6">
    <!-- Search Input -->
    <InputText placeholder="Mitarbeiter suchen..." class="mb-4 w-full" />

    <!-- List of Employees -->
    <List
        v-for="employee in employees"
        :key="employee.ssn"
        :title="`${employee.firstName} ${employee.lastName}`"
        :description="employeeDescription(employee)"
        @edit="showEditDialog(employee)"
        @delete="showDeleteDialog(employee)"
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
import { useEmployeeStore } from '@/stores/employee'
import List from '@/components/List.vue'

const employeeStore = useEmployeeStore()
const employees = computed(() => employeeStore.employees)
const currentPage = ref(1)
const totalRecords = computed(() => employees.value.length)
const dialogVisible = ref(false)
const dialogMessage = ref('')

function employeeDescription(employee) {
  return `Abteilung: ${employee.department}\nRolle: ${employee.role}`
}

function showEditDialog(employee) {
  dialogMessage.value = `Bearbeiten von ${employee.firstName} ${employee.lastName}`
  dialogVisible.value = true
}

function showDeleteDialog(employee) {
  dialogMessage.value = `Löschen von ${employee.firstName} ${employee.lastName}`
  dialogVisible.value = true
}

function onPageChange(event) {
  currentPage.value = event.page
}
</script>
