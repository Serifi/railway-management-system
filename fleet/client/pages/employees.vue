<template>
  <List
      :items="employees"
      :rowsPerPage="5"
      searchPlaceholder="Mitarbeiter:in suchen..."
      :getKey="getEmployeeKey"
      @edit="showEditDialog"
      @delete="deleteEmployee"
  >
    <template #title="{ item }">
      {{ `${item.firstName} ${item.lastName}` }}
    </template>
    <template #description="{ item }">
      Abteilung: {{ item.department }}<br />
      Rolle: {{ item.role }}
    </template>
  </List>

  <!-- Dialog for Edit/Delete Actions -->
  <Dialog v-model:visible="dialogVisible" header="Aktion" width="400px">
    <p>{{ dialogMessage }}</p>
    <template #footer>
      <Button label="Schließen" @click="dialogVisible = false" />
    </template>
  </Dialog>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useEmployeeStore } from '@/stores/employee'
import List from '~/components/ScotList.vue'

const employeeStore = useEmployeeStore()
const employees = computed(() => employeeStore.employees)

const dialogVisible = ref(false)
const dialogMessage = ref('')

const showEditDialog = (employee) => {
  dialogMessage.value = `Bearbeiten von ${employee.firstName} ${employee.lastName}`
  dialogVisible.value = true
}

const deleteEmployee = (employee) => {
  dialogMessage.value = `Löschen von ${employee.firstName} ${employee.lastName}`
  dialogVisible.value = true
}

function getEmployeeKey (employee) {
  return employee.ssn
}
</script>