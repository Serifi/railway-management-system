<!-- components/ScotMaintenance.vue -->
<template>
  <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
    <div class="flex flex-col space-y-1">
      <label for="train">{{ $t('train') }}</label>
      <Select id="train" v-model="maintenance.trainID" :options="trains" optionLabel="name" optionValue="trainID" :placeholder="$t('selectPlaceholder')" :disabled="isDisabled('trainID')"/>
    </div>

    <div class="flex flex-col space-y-1">
      <label for="employee">{{ $t('employee') }}</label>
      <!-- Geänderte Komponente von MultiSelect zu Select und Anpassung des v-model -->
      <Select id="employee" v-model="maintenance.employeeSSN" :options="employees" optionLabel="username" optionValue="ssn" :placeholder="$t('selectPlaceholder')" :disabled="isDisabled('employeeSSN')"/>
    </div>

    <div class="flex flex-col space-y-1">
      <label for="from_time">{{ $t('from') }}</label>
      <Calendar id="from_time" v-model="maintenance.from_time" showTime showSeconds :placeholder="$t('selectPlaceholder')" :disabled="isDisabled('from_time')"/>
    </div>

    <div class="flex flex-col space-y-1">
      <label for="to_time">{{ $t('to') }}</label>
      <Calendar id="to_time" v-model="maintenance.to_time" showTime showSeconds :placeholder="$t('selectPlaceholder')" :disabled="isDisabled('to_time')"/>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useTrainStore } from '@/stores/train' // Import des trainStore
import { useEmployeeStore } from '@/stores/employee' // Import des employeeStore
import { useMaintenanceStore } from '@/stores/maintenance'

const emits = defineEmits(['update:maintenance'])
const props = defineProps({
  maintenance: {
    type: Object,
    default: () => ({
      trainID: null,
      employeeSSN: null, // Geändertes Feld
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
const trainStore = useTrainStore() // Nutzung des trainStore
const employeeStore = useEmployeeStore() // Nutzung des employeeStore
const trains = computed(() => trainStore.trains)
const employees = computed(() => employeeStore.employees)

const isDisabled = (field) => props.disabledFields.includes(field)

watch(
    [
      () => maintenance.value.trainID,
      () => maintenance.value.employeeSSN, // Geändertes Feld
      () => maintenance.value.from_time,
      () => maintenance.value.to_time
    ],
    ([trainID, employeeSSN, from_time, to_time]) => {
      let allFieldsFilled = false

      if (trainID && employeeSSN && from_time && to_time) {
        allFieldsFilled = true
      }

      emits('update:maintenance', allFieldsFilled ? maintenance.value : null)
    },
    { deep: true }
)

onMounted(async () => {
  await trainStore.getTrains()
  await employeeStore.getEmployees()
})
</script>