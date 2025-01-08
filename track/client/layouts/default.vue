<template>
  <div class="flex flex-col min-h-screen">
    <header class="flex items-center justify-between py-4 border-b">
      <div class="flex items-center space-x-4 me-4">
        <img src="../assets/images/icon.png" alt="Icon" class="w-12 h-12">
        <span class="text-xl font-bold">Scotty</span>
      </div>

      <Navigation />

      <div class="flex items-center space-x-4 mx-4">
        <!-- Dark Mode Toggle -->
        <div class="theme-switch" @click="toggleDarkMode">
          <div :class="['theme-toggle', isDarkMode ? 'dark' : 'light']">
            <i v-if="!isDarkMode" class="pi pi-sun sun-icon"></i>
            <i v-else class="pi pi-moon moon-icon"></i>
          </div>
        </div>

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
import { ref, computed, onMounted } from 'vue';
import { useUserStore } from '@/stores/user';
import { useEmployeeStore } from '@/stores/employee';
import { useToast } from 'primevue/usetoast';
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

const isDarkMode = ref(false);

function toggleDarkMode() {
  isDarkMode.value = !isDarkMode.value;
  if (isDarkMode.value) {
    document.documentElement.classList.add('dark');
    document.documentElement.setAttribute('data-theme', 'dark');
    localStorage.setItem('theme', 'dark');
  } else {
    document.documentElement.classList.remove('dark');
    document.documentElement.setAttribute('data-theme', 'light');
    localStorage.setItem('theme', 'light');
  }
}

onMounted(() => {
  const savedTheme = localStorage.getItem('theme');
  isDarkMode.value = savedTheme === 'dark';
  if (isDarkMode.value) {
    document.documentElement.classList.add('dark');
    document.documentElement.setAttribute('data-theme', 'dark');
  } else {
    document.documentElement.classList.remove('dark');
    document.documentElement.setAttribute('data-theme', 'light');
  }
});

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

<style scoped>
.theme-switch {
  width: 50px;
  height: 25px;
  background-color: #ccc;
  border-radius: 25px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 2px;
  cursor: pointer;
  position: relative;
}

.theme-toggle {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background-color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.theme-toggle.dark {
  transform: translateX(25px);
  background-color: #4f46e5;
}

.sun-icon {
  font-size: 12px;
  color: #fbbf24;
}

.moon-icon {
  font-size: 12px;
  color: white;
}
</style>