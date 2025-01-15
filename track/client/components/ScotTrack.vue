<!-- Komponente zur Eingabe und Bearbeitung von Strecken -->
<template>
  <div class="flex flex-col gap-4">
    <!-- Eingabefeld für Streckennamen -->
    <div class="flex flex-col">
      <label class="font-bold mb-1">Streckenname</label>
      <InputText
        v-model="trackData.trackName"
        placeholder="Streckenname eingeben..."
        @input="validateTrack"
      />
    </div>

    <!-- Auswahl der Abschnitte -->
    <div class="flex flex-col">
      <label class="font-bold mb-1">Abschnitte wählen</label>
      <MultiSelect
        v-model="trackData.sectionIDs"
        :options="filteredSectionOptions"
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
  sections: { type: Array, required: true }, // Liste der Abschnitte
  trainStations: { type: Array, required: true }, // Liste der Bahnhöfe
});

const emits = defineEmits(['update:track', 'validate']);

const trackData = ref({ ...props.track });

const sectionOptions = computed(() =>
  props.sections.map((section) => ({
    label: `${getStationName(section.startStationID)} - ${getStationName(section.endStationID)}`,
    sectionID: section.sectionID,
    trackGauge: section.trackGauge,
  }))
);

/* Gefilterte Abschnitte basierend auf Spurweite */
const filteredSectionOptions = ref(sectionOptions.value);

/* Hilfsfunktion zur Ermittlung des Bahnhofnamens */
function getStationName(stationID) {
  const station = props.trainStations.find((s) => s.stationID === stationID);
  return station ? station.stationName : 'Unbekannt';
}

/* Validierung der Eingaben */
function validateTrack() {
  const isValid = !!trackData.value.trackName.trim() && trackData.value.sectionIDs.length > 0;
  emits('validate', isValid);
}

/* Überwachung der ausgewählten Abschnitte, um weitere Auswahlmöglichkeiten einzugrenzen */
watch(
  () => trackData.value.sectionIDs,
  (selectedIDs) => {
    if (selectedIDs.length === 0) {
      filteredSectionOptions.value = sectionOptions.value;
    } else {
      const selectedSections = sectionOptions.value.filter((option) =>
        selectedIDs.includes(option.sectionID)
      );
      const allowedTrackGauges = new Set(selectedSections.map((section) => section.trackGauge));

      filteredSectionOptions.value = sectionOptions.value.filter((option) =>
        allowedTrackGauges.has(option.trackGauge)
      );
    }
  },
  { immediate: true }
);

/* Überwachung der Streckendaten und Validierung */
watch(
  () => trackData.value,
  (newTrack) => {
    emits('update:track', newTrack); // Aktuelle Daten weitergeben
    validateTrack();
  },
  { deep: true }
);

watch(
  () => props.track,
  (newTrack) => {
    trackData.value = { ...newTrack };
    validateTrack();
  },
  { deep: true, immediate: true }
);
</script>

<style scoped>
label {
  font-weight: bold;
  margin-bottom: 0.25rem;
}
</style>