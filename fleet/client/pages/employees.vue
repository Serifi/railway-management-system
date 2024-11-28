<template>
  <List :items="employees" :getKey="getEmployeeKey" :rowsPerPage="5"
        @create="toggleCreateDialog" @edit="toggleEditDialog" @delete="deleteEmployee">
    <template #title="{ item }">
      {{ `${item.firstName} ${item.lastName}` }}
    </template>
    <template #description="{ item }">
      Abteilung: {{ item.department }}<br/>
      Rolle: {{ item.role }}
    </template>
  </List>

  <ScotDialog :visible="createDialogVisible" type="create" header="Mitarbeiter:in erstellen"
              @update:visible="createDialogVisible = $event" @action="createEmployee" @cancel="toggleCreateDialog">
    <ScotEmployee />
  </ScotDialog>

  <ScotDialog :visible="editDialogVisible" type="edit" header="Mitarbeiter:in bearbeiten"
              @update:visible="editDialogVisible = $event" @action="editEmployee" @cancel="toggleEditDialog">
    <ScotEmployee />
  </ScotDialog>
</template>

<script setup>
import {ref, computed} from 'vue'
import { useEmployeeStore } from '@/stores/employee'
import { useToast } from 'primevue/usetoast'
import List from '~/components/ScotList.vue'
import ScotEmployee from '~/components/ScotEmployee.vue'
import ScotDialog from "~/components/ScotDialog.vue";

const toast = useToast()
const createDialogVisible = ref(false)
const editDialogVisible = ref(false)
const employeeStore = useEmployeeStore()
const employees = computed(() => employeeStore.employees)
const employee = ref(null)

function toggleCreateDialog() {
  createDialogVisible.value = !createDialogVisible.value
}

function createEmployee() {



  employeeStore.createEmployee(null)
  toggleCreateDialog()
}

function toggleEditDialog(currentEmployee) {
  employee.value = currentEmployee
  editDialogVisible.value = !editDialogVisible.value
}

function editEmployee() {
  employeeStore.editEmployee(employee)
  toggleEditDialog(null)
}

function deleteEmployee(currentEmployee) {
  employeeStore.deleteEmployee(currentEmployee.ssn)
  toast.add({ severity: 'success', summary: 'Erfolgreich', detail: 'Aktion wurde erfolgreich abgeschlossen', life: 3000 })
}

function getEmployeeKey(employee) {
  return employee.ssn
}
</script>