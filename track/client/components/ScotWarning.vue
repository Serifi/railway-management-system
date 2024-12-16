<template>
  <div class="grid grid-cols-2 gap-4">
    <div class="flex flex-col col-span-2">
      <label for="warningName" class="mb-1">Name</label>
      <InputText id="warningName" v-model="warningData.warningName" placeholder="Name eingeben..." />
    </div>

    <div class="flex flex-col col-span-2">
      <label for="description" class="mb-1">Beschreibung</label>
      <Textarea id="description" v-model="warningData.description" rows="3" placeholder="Beschreibung eingeben..." />
    </div>

    <div class="flex flex-col">
      <label for="startDate" class="mb-1">Startzeitpunkt</label>
      <Calendar
        id="startDate"
        v-model="warningData.startDate"
        showTime
        dateFormat="yy-mm-dd"
        placeholder="Startdatum wählen"
      />
    </div>

    <div class="flex flex-col">
      <label for="endDate" class="mb-1">Endzeitpunkt</label>
      <Calendar
        id="endDate"
        v-model="warningData.endDate"
        showTime
        dateFormat="yy-mm-dd"
        placeholder="Enddatum wählen"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue';
import InputText from 'primevue/inputtext';
import Textarea from 'primevue/textarea';
import Calendar from 'primevue/calendar';

const props = defineProps({
  warning: {
    type: Object,
    default: () => ({
      warningName: '',
      description: '',
      startDate: null,
      endDate: null
    })
  }
});
const emits = defineEmits(['update:warning']);

const warningData = ref({ ...props.warning });

watch(warningData, (updatedWarning) => {
  const formattedWarning = {
    ...updatedWarning,
    startDate: updatedWarning.startDate
      ? updatedWarning.startDate.toISOString().split('T')[0]
      : null,
    endDate: updatedWarning.endDate
      ? updatedWarning.endDate.toISOString().split('T')[0]
      : null
  };

  emits('update:warning', formattedWarning);
}, { deep: true });
</script>

<style scoped>
label {
  font-weight: bold;
  margin-bottom: 0.25rem;
}
</style>