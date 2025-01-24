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
          <Select id="department" v-model="filters.department" :options="departments" optionLabel="label" optionValue="value" :placeholder="$t('selectPlaceholder')" filter showClear/>
        </div>

        <div class="flex flex-col space-y-1">
          <label for="role">{{ $t('role') }}</label>
          <Select id="role" v-model="filters.role" :options="roles" optionLabel="label" optionValue="value" :placeholder="$t('selectPlaceholder')" filter showClear/>
        </div>
      </div>
    </template>
  </List>

  <ScotDialog :visible="createDialogVisible" type="create" :header="$t('createEmployee')" :disable-action="disableAction"
              @update:visible="createDialogVisible = $event" @action="createEmployee" @cancel="toggleCreateDialog">
    <ScotEmployee @update:employee="updateEmployee"/>
  </ScotDialog>

  <ScotDialog :visible="editDialogVisible" type="edit" :header="$t('editEmployee')" :disable-action="disableAction"
              @update:visible="editDialogVisible = $event" @action="editEmployee" @cancel="toggleEditDialog">
    <ScotEmployee :employee="employee" :disabledFields="['ssn', 'firstName', 'lastName']" @update:employee="updateEmployee"/>
  </ScotDialog>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useEmployeeStore } from '@/stores/employee'
import { useToast } from 'primevue/usetoast'
import { useI18n } from 'vue-i18n'
import List from '~/components/ScotList.vue'
import ScotEmployee from '~/components/ScotEmployee.vue'
import ScotDialog from "~/components/ScotDialog.vue"

const toast = useToast()
const { t } = useI18n()

const createDialogVisible = ref(false)
const editDialogVisible = ref(false)
const employeeStore = useEmployeeStore()
const employees = computed(() => employeeStore.employees)
const departments = computed(() => employeeStore.departments)
const roles = computed(() => employeeStore.roles)
const employee = ref(null)
const originalEmployee = ref(null)
const disableAction = ref(false)

function updateEmployee(currentEmployee) {
  employee.value = currentEmployee
}

function toggleCreateDialog() {
  createDialogVisible.value = !createDialogVisible.value
  if (createDialogVisible.value) disableAction.value = true
}

async function toggleEditDialog(currentEmployee) {
  if (!editDialogVisible.value) {
    try {
      const fullEmployee = await employeeStore.getEmployeeByUsername(currentEmployee.username)
      employee.value = fullEmployee
      originalEmployee.value = JSON.parse(JSON.stringify(fullEmployee))
      disableAction.value = true
    } catch (error) {
      showToast('error', error.message || t('employeeFetchError'))
      return
    }
  } else {
    employee.value = currentEmployee
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

async function createEmployee() {
  try {
    const response = await employeeStore.createEmployee(employee.value)
    toggleCreateDialog()
    showToast('success', response.message || t('employeeCreated'))
  } catch (error) {
    toggleCreateDialog()
    showToast('error', error.message || t('employeeCreateError'))
  }
}

async function editEmployee() {
  try {
    const response = await employeeStore.editEmployee(employee.value)
    toggleEditDialog()
    showToast('success', response.message || t('employeeUpdated'))
  } catch (error) {
    toggleEditDialog()
    showToast('error', error.message || t('employeeUpdateError'))
  }
}

async function deleteEmployee(currentEmployee) {
  try {
    const response = await employeeStore.deleteEmployee(currentEmployee.ssn)
    showToast('success', response.message || t('employeeDeleted'))
  } catch (error) {
    showToast('error', error.message || t('employeeDeleteError'))
  }
}

function getEmployeeKey(employee) {
  return employee.ssn
}

watch(() => employee.value, (newVal) => {
  if (createDialogVisible.value) {
    disableAction.value = (newVal === null)
    return
  }
  if (editDialogVisible.value && originalEmployee.value) {
    disableAction.value = newVal === null || JSON.stringify(newVal) === JSON.stringify(originalEmployee.value)
  }
}, { deep: true })

onMounted(async () => {
  await employeeStore.getEmployees()
})
</script>