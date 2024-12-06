<template>
  <div class="grid grid-cols-2 gap-4">
    <div class="flex flex-col space-y-1 col-span-2">
      <label for="ssn">Sozialversicherungsnummer</label>
      <div class="flex flex-col lg:flex-row justify-between space-y-2 lg:space-y-0">
        <InputOtp id="ssn1" v-model="ssn1" :length="4" integerOnly :disabled="isDisabled('ssn')"/>
        <InputOtp id="ssn2" v-model="ssn2" :length="6" integerOnly :disabled="isDisabled('ssn')"/>
      </div>
    </div>

    <div class="flex flex-col space-y-1 col-span-2 lg:col-span-1">
      <label for="firstName">Vorname</label>
      <InputText id="firstName" v-model="employee.firstName" placeholder="Text eingeben..." :disabled="isDisabled('firstName')"/>
    </div>

    <div class="flex flex-col space-y-1 col-span-2 lg:col-span-1">
      <label for="lastName">Nachname</label>
      <InputText id="lastName" v-model="employee.lastName" placeholder="Text eingeben..." :disabled="isDisabled('lastName')"/>
    </div>

    <div class="flex flex-col space-y-1 col-span-2">
      <label for="password">Passwort</label>
      <div class="flex items-center space-x-2">
        <Password id="password" v-model="employee.password" toggleMask placeholder="Text eingeben..." class="flex-1" :disabled="isDisabled('password')">
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
        <i class="pi pi-sparkles text-blue-500 cursor-pointer"  @click="generatePassword"/>
      </div>
    </div>

    <div class="flex flex-col space-y-1 col-span-2 lg:col-span-1">
      <label for="role">Rolle</label>
      <Select id="role" v-model="employee.role" :options="roles" optionLabel="label" optionValue="value" placeholder="Auswahl treffen..." :disabled="isDisabled('role')"/>
    </div>

    <div class="flex flex-col space-y-1 col-span-2 lg:col-span-1">
      <label for="department">Abteilung</label>
      <Select id="department" v-model="employee.department" :options="departments" optionLabel="label" optionValue="value" placeholder="Auswahl treffen..." :disabled="isDisabled('department')"/>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
const employeeStore = useEmployeeStore()

const emits = defineEmits(['update:employee']);
const props = defineProps({
  employee: {
    type: Object,
    default: () => ({
      firstName: '',
      lastName: '',
      password: '',
      ssn: '',
      role: '',
      department: '',
    }),
  },
  disabledFields: {
    type: Array,
    default: () => [],
  }
});

const employee = ref({ ...props.employee })
const ssn1 = ref(props.employee.ssn ? props.employee.ssn.slice(0, 4) : null)
const ssn2 = ref(props.employee.ssn ? props.employee.ssn.slice(4) : null)
const roles = computed(() => employeeStore.roles)
const departments = computed(() => employeeStore.departments)
const isDisabled = (field) => props.disabledFields.includes(field)

const isDate = (date) => {
  if (!/^\d{6}$/.test(date)) return false
  const day = parseInt(date.slice(0, 2), 10)
  const month = parseInt(date.slice(2, 4), 10)

  return day >= 1 && day <= 31 && month >= 1 && month <= 12
}

watch(
    [() => ssn1.value, () => ssn2.value, () => employee.value.firstName, () => employee.value.lastName,
             () => employee.value.password, () => employee.value.role, () => employee.value.department],
         ([newSsn1, newSsn2, firstName, lastName, password, role, department]) => {

      if (newSsn1 && newSsn2 && firstName && lastName && password && role && department &&  isDate(newSsn2))
        emits('update:employee', {...employee.value, ssn: `${newSsn1}${newSsn2}`})
      else
        emits('update:employee', null)
    }
)

function generatePassword () {
  const length = 16
  const charset = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()_+[]{}|;:,.<>?'
  let password = ''
  for (let i = 0; i < length; i++) password += charset[Math.floor(Math.random() * charset.length)]
  employee.value.password = password
}
</script>