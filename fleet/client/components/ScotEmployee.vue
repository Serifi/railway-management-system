<template>
  <div class="grid grid-cols-2 gap-4">
    <div class="flex flex-col space-y-1 col-span-2">
      <label for="ssn">{{ $t('socialSecurityNumber') }}</label>
      <div class="flex flex-col lg:flex-row justify-between space-y-2 lg:space-y-0">
        <InputOtp id="ssn1" v-model="ssn1" :length="4" integerOnly :class="{ 'input-disabled': isDisabled('ssn') }"/>
        <InputOtp id="ssn2" v-model="ssn2" :length="6" integerOnly :class="{ 'input-disabled': isDisabled('ssn') }"/>
      </div>
    </div>

    <div class="flex flex-col space-y-1 col-span-2 lg:col-span-1">
      <label for="firstName">{{ $t('firstName') }}</label>
      <InputText id="firstName" v-model="employee.firstName" :placeholder="$t('textPlaceholder')" :class="{ 'input-disabled': isDisabled('firstName') }"/>
    </div>

    <div class="flex flex-col space-y-1 col-span-2 lg:col-span-1">
      <label for="lastName">{{ $t('lastName') }}</label>
      <InputText id="lastName" v-model="employee.lastName" :placeholder="$t('textPlaceholder')" :class="{ 'input-disabled': isDisabled('lastName') }"/>
    </div>

    <div class="flex flex-col space-y-1 col-span-2">
      <label for="password">{{ $t('password') }}</label>
      <div class="flex items-center space-x-2">
        <Password id="password" v-model="employee.password" toggleMask :placeholder="$t('textPlaceholder')" class="flex-1" :disabled="isDisabled('password')">
          <template #header>
            <div class="font-bold">{{ $t('passwordRecommendations') }}</div>
          </template>
          <template #footer>
            <ul>
              <li>{{ $t('passwordMinLength') }}</li>
              <li>{{ $t('passwordNumber') }}</li>
              <li>{{ $t('passwordCase') }}</li>
            </ul>
          </template>
        </Password>
        <i class="pi pi-sparkles text-blue-500 cursor-pointer" @click="generatePassword"/>
      </div>
    </div>

    <div class="flex flex-col space-y-1 col-span-2 lg:col-span-1">
      <label for="role">{{ $t('role') }}</label>
      <Select id="role" v-model="employee.role" :options="roles" optionLabel="label" optionValue="value" :placeholder="$t('selectPlaceholder')" :disabled="isDisabled('role')"/>
    </div>

    <div class="flex flex-col space-y-1 col-span-2 lg:col-span-1">
      <label for="department">{{ $t('department') }}</label>
      <Select id="department" v-model="employee.department" :options="departments" optionLabel="label" optionValue="value" :placeholder="$t('selectPlaceholder')" :disabled="isDisabled('department')"/>
    </div>

    <div class="col-span-2 flex flex-col space-y-2">
      <Message v-if="validationError" severity="error" icon="pi pi-exclamation-circle">
        {{ $t('ssnWarning') }}
      </Message>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import { useEmployeeStore } from '@/stores/employee'

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

const validationError = ref(false) // Für Fehlermeldungen

function validateSsn() {
  const ssn = `${ssn1.value || ''}${ssn2.value || ''}`
  const pattern = /^\d{4}(0[1-9]|[12][0-9]|3[01])(0[1-9]|1[0-2])\d{2}$/
  if (!pattern.test(ssn)) {
    validationError.value = true
    return true
  }
  validationError.value = false
  return false
}

watch(
    [() => ssn1.value, () => ssn2.value, () => employee.value.firstName, () => employee.value.lastName,
             () => employee.value.password, () => employee.value.role, () => employee.value.department],
         ([newSsn1, newSsn2, firstName, lastName, password, role, department]) => {

      if (newSsn1 && newSsn2 && firstName && lastName && password && role && department && !validateSsn())
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

watch(() => props.employee, (newEmp) => {
  if (newEmp) {
    employee.value.password = newEmp.password || ''
  }
})
</script>

<style scoped>
.input-disabled {
  color: #A0A0A0;
  cursor: not-allowed;
  opacity: 0.5;
}
</style>