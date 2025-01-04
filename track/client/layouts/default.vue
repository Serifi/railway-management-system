<template>
  <div class="flex flex-col min-h-screen">
    <header class="flex items-center justify-between py-4 border-b">
      <div class="flex items-center space-x-4 me-4">
        <img src="../assets/images/icon.png" alt="Icon" class="w-12 h-12">
        <span class="text-xl font-bold">Scotty</span>
      </div>

      <Navigation />

      <div class="flex items-center space-x-4 mx-4">
        <div class="w-px h-8 bg-gray-300"></div>
        <div class="flex items-center space-x-4 cursor-pointer" @click="showUserPanel">
          <i class="pi pi-user text-xl" />
          <div>
            <div class="text-sm font-bold">{{ userFullName }}</div>
            <div class="text-xs text-gray-500 leading-3">{{ userRole }}</div>
          </div>
        </div>
      </div>

      <Popover ref="userPanel" appendTo="body">
        <div class="flex flex-col">
          <div class="flex items-center p-2 space-x-2 rounded hover:bg-gray-200 transition duration-300 cursor-pointer" @click="editProfile">
            <i class="pi pi-user-edit text-blue-400" />
            <div>Profil</div>
          </div>
          <div class="flex items-center p-2 space-x-2 rounded hover:bg-gray-200 transition duration-300 cursor-pointer" @click="logout">
            <i class="pi pi-power-off text-red-400" />
            <div>Abmelden</div>
          </div>
        </div>
      </Popover>
    </header>

    <main class="flex-grow p-8">
      <NuxtPage />
    </main>

    <Toast />

    <ScotDialog
      :visible="profileDialogVisible"
      type="edit"
      header="Profil bearbeiten"
      :disable-action="disableAction"
      @update:visible="profileDialogVisible = $event"
      @action="saveProfile"
      @cancel="closeProfileDialog"
    >
      <ScotEmployee
        :employee="employee"
        :disabledFields="determineDisabledFields"
        :enableUsernameEdit="false"
        @update:employee="updateEmployee"
      />
    </ScotDialog>
  </div>
</template>

<script setup>
import {ref, computed} from 'vue';
import {useUserStore} from '@/stores/user';
import {useEmployeeStore} from '@/stores/employee';
import {useToast} from 'primevue/usetoast';
import Navigation from '~/components/ScotNavigation.vue';
import ScotDialog from '~/components/ScotDialog.vue';
import ScotEmployee from '~/components/ScotEmployee.vue';
import bcrypt from 'bcryptjs';

const userStore = useUserStore();
const employeeStore = useEmployeeStore();
const toast = useToast();

const userPanel = ref(null);
const profileDialogVisible = ref(false);
const employee = ref({});
const disableAction = ref(false);

const userFullName = computed(() => userStore.getFullName);
const userRole = computed(() => userStore.getUserRole);

const determineDisabledFields = computed(() => {
  if (userRole.value === 'Admin') {
    return ['ssn'];
  }
  return ['ssn', 'role', 'department'];
});

function showUserPanel() {
  userPanel.value.toggle(event);
}

function logout() {
  userStore.logout();
  window.location.href = '/';
}

function editProfile() {
  const loggedInUser = userStore.user;
  if (loggedInUser) {
    employee.value = {...loggedInUser, password: ''};
    profileDialogVisible.value = true;
    disableAction.value = false;
  } else {
    toast.add({severity: 'error', summary: 'Fehler', detail: 'Profil konnte nicht geladen werden.', life: 3000});
  }
}

function closeProfileDialog() {
  profileDialogVisible.value = false;
  resetEmployeeData();
}

function updateEmployee(updatedEmployee) {
  employee.value = updatedEmployee;
  disableAction.value = employee.value === null;
}

async function saveProfile() {
  try {
    if (employee.value.password === '') {
      delete employee.value.password;
    } else if (employee.value.password) {
      employee.value.password = await hashPassword(employee.value.password);
    }

    await employeeStore.editEmployee(employee.value);

    userStore.user = {...userStore.user, ...employee.value};

    toast.add({severity: 'success', summary: 'Erfolgreich', detail: 'Profil wurde aktualisiert.', life: 3000});
    profileDialogVisible.value = false;
    resetEmployeeData();
  } catch (error) {
    handleError(error);
  }
}

function resetEmployeeData() {
  employee.value = {};
  disableAction.value = false;
}

async function hashPassword(password) {
  const salt = await bcrypt.genSalt(10);
  return bcrypt.hash(password, salt);
}

function handleError(error) {
  if (error.response?.status === 400 && error.response?.data?.message) {
    toast.add({severity: 'error', summary: 'Fehler', detail: error.response.data.message, life: 3000});
  } else if (error.response?.status === 401) {
    toast.add({severity: 'error', summary: 'Nicht autorisiert', detail: 'Zugriff verweigert.', life: 3000});
  } else {
    toast.add({severity: 'error', summary: 'Fehler', detail: 'Ein Fehler ist aufgetreten.', life: 3000});
  }
}
</script>