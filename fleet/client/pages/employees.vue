<template>
  <List :items="employees" :getKey="getEmployeeKey" :rowsPerPage="5"
        @create="toggleCreateDialog" @edit="toggleEditDialog" @delete="deleteEmployee">
    <template #title="{ item }">
      {{ `${item.firstName} ${item.lastName}` }}
    </template>
    <template #description="{ item }">
      {{ $t('department') }}: {{ $t(item.department.toLowerCase())}}<br/>
      {{ $t('role') }}: {{ $t(item.role.toLowerCase())}}
    </template>
    <template #filters="{ filters }">
      <div class="p-4 space-y-4">
        <div class="flex flex-col space-y-1">
          <label for="department">{{ $t('department') }}</label>
          <Select id="department" v-model="filters.department" :options="departments" optionLabel="label" optionValue="value" :placeholder="$t('selectPlaceholder')" showClear/>
        </div>

        <div class="flex flex-col space-y-1">
          <label for="role">{{ $t('role') }}</label>
          <Select id="role" v-model="filters.role" :options="roles" optionLabel="label" optionValue="value" :placeholder="$t('selectPlaceholder')" showClear/>
        </div>
      </div>
    </template>
  </List>

  <ScotDialog :visible="createDialogVisible" type="create" :header="$t('createEmployee')"
              @update:visible="createDialogVisible = $event" @action="createEmployee" @cancel="toggleCreateDialog">
    <ScotEmployee @update:employee="updateEmployee"/>
  </ScotDialog>
  <!-- :disable-action="disableAction" -->
  <ScotDialog :visible="editDialogVisible" type="edit" :header="$t('editEmployee')"
              @update:visible="editDialogVisible = $event" @action="editEmployee" @cancel="toggleEditDialog">
    <ScotEmployee :employee="employee" :disabledFields="['ssn']" @update:employee="updateEmployee"/>
  </ScotDialog>
</template>

<script setup>
import {ref, computed, onMounted} from 'vue'
import { useEmployeeStore } from '@/stores/employee'
import { useToast } from 'primevue/usetoast'
import List from '~/components/ScotList.vue'
import ScotEmployee from '~/components/ScotEmployee.vue'
import ScotDialog from "~/components/ScotDialog.vue"

const toast = useToast()
const createDialogVisible = ref(false)
const editDialogVisible = ref(false)
const employeeStore = useEmployeeStore()
const employees = computed(() => employeeStore.employees)
const departments = computed(() => employeeStore.departments)
const roles = computed(() => employeeStore.roles)
const employee = ref(null)
const disableAction = ref(false)

function updateEmployee(currentEmployee) {
  employee.value = currentEmployee
  disableAction.value = employee.value === null
}

function toggleCreateDialog() {
  createDialogVisible.value = !createDialogVisible.value
  if (createDialogVisible.value) disableAction.value = true
}

function createEmployee() {
  employeeStore.createEmployee(employee.value)
  toggleCreateDialog()
  toast.add({ severity: 'success', summary: 'Erfolgreich', detail: 'Aktion wurde erfolgreich abgeschlossen', life: 3000 })
}

async function toggleEditDialog(currentEmployee) {
  employee.value = currentEmployee
  editDialogVisible.value = !editDialogVisible.value
  if (editDialogVisible.value) disableAction.value = false
}

function editEmployee() {
  employeeStore.editEmployee(employee.value)
  toggleEditDialog(null)
  toast.add({ severity: 'success', summary: 'Erfolgreich', detail: 'Aktion wurde erfolgreich abgeschlossen', life: 3000 })
}

function deleteEmployee(currentEmployee) {
  employeeStore.deleteEmployee(currentEmployee.ssn)
  toast.add({ severity: 'success', summary: 'Erfolgreich', detail: 'Aktion wurde erfolgreich abgeschlossen', life: 3000 })
}

function getEmployeeKey(employee) {
  return employee.ssn
}

onMounted(() => {
  employeeStore.getEmployees()
})
</script>