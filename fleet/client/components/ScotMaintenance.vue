<template>
  <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
    <!-- Train -->
    <div class="flex flex-col space-y-1">
      <label for="train">{{ $t('train') }}</label>
      <Select id="train" v-model="maintenance.trainID" :options="trains" optionLabel="name" optionValue="trainID"
              :placeholder="$t('selectPlaceholder')" :disabled="isDisabled('trainID')"/>
    </div>

    <!-- Employee -->
    <div class="flex flex-col space-y-1">
      <label for="employee">{{ $t('employee') }}</label>
      <Select id="employee" v-model="maintenance.employeeSSN" :options="filteredEmployees" :optionLabel="getEmployeeDisplayName"
              optionValue="ssn" :placeholder="$t('selectPlaceholder')" filter/>
    </div>

    <!-- From -->
    <div class="flex flex-col space-y-1">
      <label for="from_time">{{ $t('from') }}</label>
      <DatePicker id="from_time" v-model="maintenance.from_time" showTime showSeconds :placeholder="$t('selectPlaceholder')" :disabled="isDisabled('from_time')"/>
    </div>

    <!-- To -->
    <div class="flex flex-col space-y-1">
      <label for="to_time">{{ $t('to') }}</label>
      <DatePicker id="to_time" v-model="maintenance.to_time" showTime showSeconds :placeholder="$t('selectPlaceholder')" :disabled="isDisabled('to_time')"/>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useTrainStore } from '@/stores/train'
import { useEmployeeStore } from '@/stores/employee'
import { useMaintenanceStore } from '@/stores/maintenance'

const emits = defineEmits(['update:maintenance'])
const props = defineProps({
  maintenance: {
    type: Object,
    default: () => ({
      trainID: null,
      employeeSSN: null,
      from_time: '',
      to_time: ''
    })
  },
  disabledFields: {
    type: Array,
    default: () => []
  }
})

const maintenance = ref({ ...props.maintenance })
const maintenanceStore = useMaintenanceStore()
const trainStore = useTrainStore()
const employeeStore = useEmployeeStore()
const trains = computed(() => trainStore.trains)
const employees = computed(() => employeeStore.employees)

// Filter employees to include only those in the 'Maintenance' department
const filteredEmployees = computed(() => employees.value.filter(employee => employee.department === 'Maintenance'))

function getEmployeeDisplayName(employee) {
  return `${employee.firstName} ${employee.lastName}`
}

// Watch for maintenance changes and emit updates
watch(
    [
      () => maintenance.value.trainID,
      () => maintenance.value.employeeSSN,
      () => maintenance.value.from_time,
      () => maintenance.value.to_time
    ],
    ([trainID, employeeSSN, from_time, to_time]) => {
      // Emit an update if all fields are valid, otherwise emit null
      if (trainID && employeeSSN && from_time && to_time) {
        emits('update:maintenance', {
          ...maintenance.value,
          from_time: from_time.toISOString(),
          to_time: to_time.toISOString(),
        });
      } else {
        emits('update:maintenance', null)
      }
    },
    { deep: true }
)

// Check if a field should be disabled
const isDisabled = (field) => props.disabledFields.includes(field)

onMounted(async () => {
  await trainStore.getTrains()
  await employeeStore.getEmployees()

  if (maintenance.value.from_time) maintenance.value.from_time = new Date(maintenance.value.from_time)
  if (maintenance.value.to_time) maintenance.value.to_time = new Date(maintenance.value.to_time)
})
</script>