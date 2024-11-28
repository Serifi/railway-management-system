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

  <Dialog v-model:visible="createDialogVisible" header="Mitarbeiter:in erstellen" class="w-2/3">
    <ScotEmployee/>

    <template #footer>
      <ScotButton label="Abbrechen" icon="pi pi-times" variant="gray" @click="toggleCreateDialog"/>
      <ScotButton label="Erstellen" icon="pi pi-plus" variant="blue" @click="createEmployee"/>
    </template>
  </Dialog>

  <Dialog v-model:visible="editDialogVisible" header="Mitarbeiter:in bearbeiten" class="w-2/3">
    <template #footer>
      <ScotButton label="Abbrechen" icon="pi pi-times" variant="gray" @click="toggleEditDialog"/>
      <ScotButton label="Bearbeiten" icon="pi pi-pencil" variant="green" @click="editEmployee"/>
    </template>
  </Dialog>
</template>

<script setup>
import {ref, computed} from 'vue'
import { useEmployeeStore } from '@/stores/employee'
import { useToast } from 'primevue/usetoast'
import List from '~/components/ScotList.vue'
import ScotEmployee from '~/components/ScotEmployee.vue'

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