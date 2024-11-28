<template>
  <div class="grid grid-cols-2 gap-4">
    <div class="flex flex-col col-span-2">
      <label for="ssn" class="mb-1">Sozialversicherungsnummer</label>
      <InputOtp id="ssn" v-model="ssn" :length="10" integerOnly placeholder="Text eingeben..." />
    </div>

    <div class="flex flex-col">
      <label for="firstName" class="mb-1">Vorname</label>
      <InputText id="firstName" v-model="employee.firstName" placeholder="Text eingeben..." />
    </div>

    <div class="flex flex-col">
      <label for="lastName" class="mb-1">Nachname</label>
      <InputText id="lastName" v-model="employee.lastName" placeholder="Text eingeben..." />
    </div>

    <div class="flex flex-col col-span-2">
      <label for="password" class="mb-1">Passwort</label>
      <div class="flex items-center space-x-2">
        <Password id="password" v-model="employee.password" toggleMask placeholder="Text eingeben..." class="flex-1">
          <template #header>
            <div class="font-bold">Empfehlungen</div>
          </template>
          <template #footer>
            <ul>
              <li>Mindestens 8 Zeichen</li>
              <li>Mindestens eine numerische Ziffer</li>
              <li>Mindestens ein Klein- und ein Großbuchstabe</li>
            </ul>
          </template>
        </Password>
        <i class="pi pi-sparkles text-blue-500 cursor-pointer" @click="generatePassword"/>
      </div>
    </div>

    <div class="flex flex-col">
      <label for="role" class="mb-1">Rolle</label>
      <Dropdown id="role" v-model="employee.role" :options="roles" optionLabel="label" placeholder="Auswahl treffen..."/>
    </div>

    <div class="flex flex-col">
      <label for="department" class="mb-1">Abteilung</label>
      <Dropdown id="department" v-model="employee.department" :options="departments" optionLabel="label" placeholder="Auswahl treffen..."/>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
const employeeStore = useEmployeeStore()

const ssn = ref(null)
const employee = ref({
  firstName: '',
  lastName: '',
  password: '',
  ssn: null,
  role: '',
  department: '',
})
const roles = computed(() => employeeStore.roles)
const departments = computed(() => employeeStore.departments)

const generatePassword = () => {
  const length = 16;
  const charset = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()_+[]{}|;:,.<>?';
  let password = '';
  for (let i = 0; i < length; i++) password += charset[Math.floor(Math.random() * charset.length)];
  employee.value.password = password
};
</script>