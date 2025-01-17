<!-- Komponente zur Verwaltung der Eingabefelder für Mitarbeiterdaten -->
<template>
  <div class="grid grid-cols-2 gap-4">
    <!-- Sozialversicherungsnummer -->
    <div class="flex flex-col col-span-2">
      <label for="ssn" class="mb-1">Sozialversicherungsnummer</label>
      <div class="flex flex-col lg:flex-row justify-between space-y-2 lg:space-y-0">
        <InputOtp
          id="ssn1"
          v-model="ssn1"
          :length="4"
          integerOnly
          :class="{ 'input-otp-disabled': isDisabled('ssn') }"
          :disabled="isDisabled('ssn')"
        />
        <InputOtp
          id="ssn2"
          v-model="ssn2"
          :length="6"
          integerOnly
          :class="{ 'input-otp-disabled': isDisabled('ssn') }"
          :disabled="isDisabled('ssn')"
        />
      </div>
    </div>

    <!-- Vorname -->
    <div class="flex flex-col col-span-2 lg:col-span-1">
      <label for="firstName" class="mb-1">Vorname</label>
      <InputText
        id="firstName"
        v-model="employee.firstName"
        placeholder="Text eingeben..."
        :disabled="isDisabled('firstName')"
      />
    </div>

    <!-- Nachname -->
    <div class="flex flex-col col-span-2 lg:col-span-1">
      <label for="lastName" class="mb-1">Nachname</label>
      <InputText
        id="lastName"
        v-model="employee.lastName"
        placeholder="Text eingeben..."
        :disabled="isDisabled('lastName')"
      />
    </div>

    <!-- Benutzername -->
    <div class="flex flex-col col-span-2 lg:col-span-2">
      <label for="username" class="mb-1">Benutzername</label>
      <InputText
        id="username"
        v-model="employee.username"
        placeholder="Benutzername"
        :disabled="!enableUsernameEdit"
      />
    </div>

    <!-- Passwort -->
    <div class="flex flex-col col-span-2">
      <label for="password" class="mb-1">Passwort</label>
      <div class="flex items-center space-x-2">
        <Password
          id="password"
          v-model="employee.password"
          toggleMask
          placeholder="Text eingeben..."
          class="flex-1"
          :disabled="isDisabled('password')"
        >
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
        <i
          class="pi pi-sparkles text-blue-500 cursor-pointer"
          @click="generatePassword"
        />
      </div>
    </div>

    <!-- Rolle -->
    <div class="flex flex-col col-span-2 lg:col-span-1">
      <label for="role" class="mb-1">Rolle</label>
      <Dropdown
        id="role"
        v-model="employee.role"
        :options="roleOptions"
        optionLabel="label"
        optionValue="value"
        placeholder="Rolle wählen..."
        :class="{ 'p-disabled': isDisabled('role') }"
        :disabled="isDisabled('role')"
      />
    </div>

    <!-- Abteilung -->
    <div class="flex flex-col col-span-2 lg:col-span-1">
      <label for="department" class="mb-1">Abteilung</label>
      <Dropdown
        id="department"
        v-model="employee.department"
        :options="departmentOptions"
        optionLabel="label"
        optionValue="value"
        placeholder="Abteilung wählen..."
        :class="{ 'p-disabled': isDisabled('department') }"
        :disabled="isDisabled('department')"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from "vue";

const emits = defineEmits(["update:employee"]);
const props = defineProps({
  employee: {
    type: Object, // Mitarbeiterdaten
    default: () => ({
      firstName: "",
      lastName: "",
      password: "",
      ssn: "",
      username: "",
      role: "",
      department: "",
    }),
  },
  disabledFields: {
    type: Array, // Felder, die deaktiviert werden sollen
    default: () => [],
  },
  enableUsernameEdit: {
    type: Boolean, // Steuerung, ob der Benutzername bearbeitet werden kann
    default: false,
  },
});

const employee = ref({ ...props.employee });
const ssn1 = ref(props.employee.ssn ? props.employee.ssn.slice(0, 4) : null);
const ssn2 = ref(props.employee.ssn ? props.employee.ssn.slice(4) : null);
const roleOptions = [
  { label: "Administrator", value: "Admin" },
  { label: "Mitarbeiter", value: "Employee" },
];
const departmentOptions = [
  { label: "Bordpersonal", value: "Crew" },
  { label: "Wartung", value: "Maintenance" },
];

/* Funktion zur Überprüfung, ob ein Feld deaktiviert ist */
const isDisabled = (field) => props.disabledFields.includes(field);

watch(
  () => props.employee,
  (newVal) => {
    Object.assign(employee.value, newVal);
    ssn1.value = newVal.ssn ? newVal.ssn.slice(0, 4) : null;
    ssn2.value = newVal.ssn ? newVal.ssn.slice(4) : null;
  },
  { immediate: true }
);

/* Änderungen an Eingabewerten beobachten */
watch(
  [
    () => ssn1.value,
    () => ssn2.value,
    () => employee.value.firstName,
    () => employee.value.lastName,
    () => employee.value.password,
    () => employee.value.role,
    () => employee.value.department,
    () => employee.value.username,
  ],
  () => {
    if (!props.enableUsernameEdit) {
      employee.value.username = `${employee.value.firstName.toLowerCase()}.${employee.value.lastName.toLowerCase()}`;
    }
    emits("update:employee", {
      ...employee.value,
      ssn: `${ssn1.value}${ssn2.value}`,
    });
  }
);

/* Funktion zur Passwortgenerierung */
function generatePassword() {
  const length = 16;
  const charset =
    "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()_+[]{}|;:,.<>?";
  let password = "";
  for (let i = 0; i < length; i++)
    password += charset[Math.floor(Math.random() * charset.length)];
  employee.value.password = password;
}
</script>
