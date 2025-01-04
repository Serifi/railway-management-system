<template>
  <div class="flex flex-col gap-4">
    <div class="flex flex-col">
      <label class="font-bold mb-1">Streckenname</label>
      <InputText
        v-model="trackData.trackName"
        placeholder="Streckenname eingeben..."
        @input="validateTrack"
      />
    </div>

    <div class="flex flex-col">
      <label class="font-bold mb-1">Abschnitte wählen</label>
      <MultiSelect
        v-model="trackData.sectionIDs"
        :options="sectionOptions"
        optionLabel="label"
        optionValue="sectionID"
        placeholder="Abschnitte auswählen..."
        @change="validateTrack"
        filter
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue';
import InputText from 'primevue/inputtext';
import MultiSelect from 'primevue/multiselect';

const props = defineProps({
  track: {
    type: Object,
    default: () => ({ trackName: '', sectionIDs: [] }),
  },
  sections: {
    type: Array,
    required: true,
  },
  trainStations: {
    type: Array,
    required: true,
  },
});

const emits = defineEmits(['update:track', 'validate']);
const trackData = ref({ ...props.track });

const sectionOptions = computed(() =>
  props.sections.map((section) => ({
    label: `${getStationName(section.startStationID)} - ${getStationName(section.endStationID)}`,
    sectionID: section.sectionID,
  }))
);

function getStationName(stationID) {
  const station = props.trainStations.find((s) => s.stationID === stationID);
  return station ? station.stationName : 'Unbekannt';
}

function validateTrack() {
  const isValid =
    !!trackData.value.trackName.trim() && trackData.value.sectionIDs.length > 0;
  emits('validate', isValid);
}

watch(
  () => trackData.value,
  (newTrack) => {
    emits('update:track', newTrack);
    validateTrack();
  },
    {deep: true}
);

watch(
    () => props.track,
    (newTrack) => {
      trackData.value = {...newTrack};
      validateTrack();
    },
    {deep: true, immediate: true}
);
</script>

<style scoped>
label {
  font-weight: bold;
  margin-bottom: 0.25rem;
}
</style>