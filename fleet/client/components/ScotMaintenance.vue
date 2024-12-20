<!-- components/ScotMaintenance.vue -->
<template>
  <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
    <div class="flex flex-col space-y-1">
      <label for="train">Zug</label>
      <Dropdown id="train" v-model="maintenance.trainID" :options="trains" optionLabel="name" optionValue="trainID" placeholder="Zug auswählen..." :disabled="isDisabled('trainID')"/>
    </div>

    <div class="flex flex-col space-y-1">
      <label for="employees">Mitarbeiter</label>
      <MultiSelect id="employees" v-model="maintenance.employeeSSNs" :options="employees" optionLabel="username" optionValue="ssn" placeholder="Mitarbeiter auswählen..." :disabled="isDisabled('employeeSSNs')"/>
    </div>

    <div class="flex flex-col space-y-1">
      <label for="from_time">Von</label>
      <Calendar id="from_time" v-model="maintenance.from_time" showTime showSeconds placeholder="Startzeitpunkt" :disabled="isDisabled('from_time')"/>
    </div>

    <div class="flex flex-col space-y-1">
      <label for="to_time">Bis</label>
      <Calendar id="to_time" v-model="maintenance.to_time" showTime showSeconds placeholder="Endzeitpunkt" :disabled="isDisabled('to_time')"/>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useMaintenanceStore } from '@/stores/maintenance'

const emits = defineEmits(['update:maintenance'])
const props = defineProps({
  maintenance: {
    type: Object,
    default: () => ({
      trainID: null,
      employeeSSNs: [],
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
const trains = computed(() => maintenanceStore.trains)
const employees = computed(() => maintenanceStore.employees)

const isDisabled = (field) => props.disabledFields.includes(field)

watch(
    [
      () => maintenance.value.trainID,
      () => maintenance.value.employeeSSNs,
      () => maintenance.value.from_time,
      () => maintenance.value.to_time
    ],
    ([trainID, employeeSSNs, from_time, to_time]) => {
      let allFieldsFilled = false

      if (trainID && employeeSSNs.length > 0 && from_time && to_time) {
        allFieldsFilled = true
      }

      emits('update:maintenance', allFieldsFilled ? maintenance.value : null)
    },
    { deep: true }
)
</script>