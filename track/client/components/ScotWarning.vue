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
        hourFormat="24"
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
        hourFormat="24"
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
      endDate: null,
    }),
  },
});

const emits = defineEmits(['update:warning', 'validate']);

const warningData = ref({ ...props.warning });

function formatDateTime(date) {
  if (!date) return null;
  const isoString = date.toISOString();
  const [datePart, timePart] = isoString.split('T');
  const time = timePart.split('.')[0];
  return `${datePart} ${time}`;
}

watch(
  warningData,
  (updatedWarning) => {
    const formattedWarning = {
      ...updatedWarning,
      startDate: formatDateTime(updatedWarning.startDate),
      endDate: updatedWarning.endDate ? formatDateTime(updatedWarning.endDate) : null,
    };
    emits('update:warning', formattedWarning);

    const isValid = !!updatedWarning.warningName && !!updatedWarning.startDate;
    emits('validate', isValid);
  },
  { deep: true }
);
</script>

<style scoped>
textarea {
  color: var(--text-color) !important;
}

textarea::placeholder {
  color: rgba(var(--text-color), 0.7) !important;
}
</style>