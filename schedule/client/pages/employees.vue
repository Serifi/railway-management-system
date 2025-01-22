<template>
  <List :items="employees" :getKey="getEmployeeKey" :rowsPerPage="5"
        @create="toggleCreateDialog" @edit="toggleEditDialog" >
    <template #title="{ item }">
      {{ `${item.firstName} ${item.lastName}` }}
    </template>
    <template #description="{ item }">
      Abteilung: {{ item.department }}<br/>
      Rolle: {{ item.role }}
    </template>
  </List>

  <Dialog v-model:visible="createDialogVisible" header="Mitarbeiter:in erstellen" class="w-2/3">


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
import List from '~/components/ScotList.vue'

const createDialogVisible = ref(false)
const editDialogVisible = ref(false)
const userStore = useUserStore()
const employees = computed(() => userStore.dummyUsers)
const employee = ref(null)


function toggleCreateDialog() {
  createDialogVisible.value = !createDialogVisible.value
}



function toggleEditDialog(currentEmployee) {
  employee.value = currentEmployee
  editDialogVisible.value = !editDialogVisible.value
}

function editEmployee() {
  employeeStore.editEmployee(employee)
  toggleEditDialog(null)
}



function getEmployeeKey(employee) {
  return employee.ssn
}
</script>