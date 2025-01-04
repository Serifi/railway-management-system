<template>
  <List
    :items="employees"
    :getKey="getEmployeeKey"
    pageType="Mitarbeiter"
    @create="toggleCreateDialog"
    @edit="toggleEditDialog"
    @delete="deleteEmployee"
  >
    <template #title="{ item }">
      {{ `${item.firstName} ${item.lastName}` }}
    </template>
    <template #description="{ item }">
      <div>
        <p>Abteilung: {{ item.department }}</p>
        <p>Rolle: {{ item.role }}</p>
      </div>
    </template>
  </List>

  <ScotDialog
    :visible="createDialogVisible"
    type="create"
    header="Mitarbeiter:in erstellen"
    :disable-action="!isFormValid"
    @update:visible="createDialogVisible = $event"
    @action="createEmployee"
    @cancel="toggleCreateDialog"
  >
    <ScotEmployee :enableUsernameEdit="enableUsernameEdit" @update:employee="updateEmployee" />
  </ScotDialog>

  <ScotDialog
    :visible="editDialogVisible"
    type="edit"
    header="Mitarbeiter:in bearbeiten"
    :disable-action="disableAction"
    @update:visible="editDialogVisible = $event"
    @action="editEmployee"
    @cancel="toggleEditDialog"
  >
    <ScotEmployee
      :employee="employee"
      :disabledFields="['ssn']"
      :enableUsernameEdit="enableUsernameEdit"
      @update:employee="updateEmployee"
    />
  </ScotDialog>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import bcrypt from 'bcryptjs';
import { useEmployeeStore } from '@/stores/employee';
import { useUserStore } from '@/stores/user';
import { useToast } from 'primevue/usetoast';
import List from '~/components/ScotList.vue';
import ScotEmployee from '~/components/ScotEmployee.vue';
import ScotDialog from "~/components/ScotDialog.vue";

const toast = useToast();
const createDialogVisible = ref(false);
const editDialogVisible = ref(false);
const employeeStore = useEmployeeStore();
const userStore = useUserStore();

const loggedInUserSSN = computed(() => userStore.getSSN);

const employees = computed(() =>
  employeeStore.employees.filter(emp => emp.ssn !== loggedInUserSSN.value)
);

const employee = ref({});
const disableAction = ref(false);
const enableUsernameEdit = ref(false);

employeeStore.triggerEditDialog = (targetEmployee) => {
  toggleEditDialog(targetEmployee);
};

const isFormValid = computed(() => {
  return (
    employee.value &&
    employee.value.firstName &&
    employee.value.lastName &&
    employee.value.password &&
    employee.value.department &&
    employee.value.role &&
    employee.value.ssn
  );
});

function updateEmployee(currentEmployee) {
  employee.value = currentEmployee;
  disableAction.value = employee.value === null;
}

function toggleCreateDialog() {
  createDialogVisible.value = !createDialogVisible.value;
  if (!createDialogVisible.value) {
    resetEmployeeData();
  }
}

async function toggleEditDialog(currentEmployee) {
  if (editDialogVisible.value) {
    resetEmployeeData();
    editDialogVisible.value = false;
  } else {
    const fetchedEmployee = employees.value.find((emp) => emp.ssn === currentEmployee.ssn);
    employee.value = fetchedEmployee ? { ...fetchedEmployee } : { ...currentEmployee };
    editDialogVisible.value = true;
    enableUsernameEdit.value = false;
    disableAction.value = false;
  }
}

async function createEmployee() {
  try {
    if (employee.value.password) {
      employee.value.password = await hashPassword(employee.value.password);
    }
    await employeeStore.createEmployee(employee.value);
    toast.add({ severity: 'success', summary: 'Erfolgreich', detail: 'Mitarbeiter erstellt', life: 3000 });
    toggleCreateDialog();
  } catch (error) {
    handleError(error);
  }
}

async function editEmployee() {
  try {
    if (employee.value.password) {
      employee.value.password = await hashPassword(employee.value.password);
    }
    await employeeStore.editEmployee(employee.value);
    toast.add({ severity: 'success', summary: 'Erfolgreich', detail: 'Mitarbeiter bearbeitet', life: 3000 });
    toggleEditDialog(null);
  } catch (error) {
    handleError(error);
  }
}

function deleteEmployee(currentEmployee) {
  employeeStore.deleteEmployee(currentEmployee.ssn);
  toast.add({ severity: 'success', summary: 'Erfolgreich', detail: 'Mitarbeiter gelöscht', life: 3000 });
}

function getEmployeeKey(employee) {
  return employee.ssn;
}

function resetEmployeeData() {
  employee.value = {};
  disableAction.value = false;
  enableUsernameEdit.value = false;
}

function handleError(error) {
  if (error.response?.status === 400 && error.response?.data?.message) {
    enableUsernameEdit.value = true;
    toast.add({ severity: 'error', summary: 'Fehler', detail: error.response.data.message, life: 3000 });
  } else {
    toast.add({severity: 'error', summary: 'Fehler', detail: 'Ein Fehler ist aufgetreten.', life: 3000});
  }
}

async function hashPassword(password) {
  const salt = await bcrypt.genSalt(10);
  return bcrypt.hash(password, salt);
}

onMounted(() => {
  employeeStore.getEmployees();
});
</script>