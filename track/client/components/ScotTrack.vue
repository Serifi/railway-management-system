<!-- Komponente zur Eingabe und Bearbeitung von Strecken -->
<template>
  <div class="flex flex-col gap-4">
    <!-- Streckenname -->
    <div class="flex flex-col">
      <label class="font-bold mb-1">Streckenname</label>
      <InputText
        v-model="trackData.trackName"
        placeholder="Streckenname eingeben..."
        @input="validateTrack"
      />
    </div>

    <!-- Abschnitte auswählen -->
    <div class="flex flex-col">
      <label class="font-bold mb-1">Abschnitte wählen</label>
      <MultiSelect
        v-model="trackData.sectionIDs"
        :options="groupedSections"
        optionLabel="label"
        optionValue="sectionID"
        optionGroupLabel="trackGaugeLabel"
        optionGroupChildren="items"
        placeholder="Abschnitte auswählen..."
        @change="validateTrack"
        filter
      >
        <!-- Anzeige der Gruppierung mittels Spurweite -->
        <template #optiongroup="slotProps">
          <div class="flex items-center">
            <i class="pi pi-arrows-h mr-2"></i>
            <div>{{ slotProps.option.trackGaugeLabel }}mm</div>
          </div>
        </template>
      </MultiSelect>
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

/* Gruppierung der Abschnitte nach Spurweite */
const groupedSections = computed(() => {
  const groups = {};

  props.sections.forEach((section) => {
    const gauge = section.trackGauge || 'Unbekannte Spurweite';
    if (!groups[gauge]) {
      groups[gauge] = {
        trackGaugeLabel: `${gauge}`,
        items: [],
      };
    }
    groups[gauge].items.push({
      label: `${getStationName(section.startStationID)} - ${getStationName(section.endStationID)}`, // Abschnitt von Start- bis Endbahnhof
      sectionID: section.sectionID,
    });
  });

  return Object.values(groups);
});

/* Funktion zur Ermittlung des Bahnhofsnamens anhand der ID */
function getStationName(stationID) {
  const station = props.trainStations.find((s) => s.stationID === stationID);
  return station ? station.stationName : 'Unbekannt';
}

/* Validierung der Streckendaten */
function validateTrack() {
  const isValid =
    !!trackData.value.trackName.trim() && trackData.value.sectionIDs.length > 0; // Überprüfung auf leeren Namen oder leere Abschnittsauswahl
  emits('validate', isValid);
}

/* Überwachung der Streckendaten und automatische Validierung */
watch(
  () => trackData.value,
  (newTrack) => {
    emits('update:track', newTrack);
    validateTrack();
  },
  { deep: true }
);

/* Überwachung von Änderungen an den übergebenen Streckendaten */
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