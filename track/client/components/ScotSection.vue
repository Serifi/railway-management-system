<!-- Komponente zur Eingabe und Bearbeitung von Abschnitten -->
<template>
  <div class="grid grid-cols-2 gap-4">
    <!-- Preis -->
    <div class="flex flex-col">
      <label for="usageFee">Preis (€)</label>
      <InputText
        id="usageFee"
        v-model.number="sectionData.usageFee"
        placeholder="Preis eingeben..."
        type="number"
      />
    </div>

    <!-- Distanz -->
    <div class="flex flex-col">
      <label for="length">Distanz (km)</label>
      <InputText
        id="length"
        v-model.number="sectionData.length"
        placeholder="Distanz eingeben..."
        type="number"
      />
    </div>

    <!-- Maximale Geschwindigkeit -->
    <div class="flex flex-col">
      <label for="maxSpeed">Max. Geschwindigkeit (km/h)</label>
      <InputText
        id="maxSpeed"
        v-model.number="sectionData.maxSpeed"
        placeholder="km/h eingeben..."
        type="number"
      />
    </div>

    <!-- Spurweite -->
    <div class="flex flex-col">
      <label for="trackGauge">Spurweite</label>
      <Dropdown
        id="trackGauge"
        v-model="sectionData.trackGauge"
        :options="trackGaugeOptions"
        optionLabel="label"
        optionValue="value"
        placeholder="Spurweite wählen..."
      />
    </div>

    <!-- Startbahnhof -->
    <div class="flex flex-col">
      <label>Startbahnhof</label>
      <Dropdown
        v-model="sectionData.startStationID"
        :options="trainStations"
        optionLabel="stationName"
        optionValue="stationID"
        placeholder="Startbahnhof wählen..."
      />
    </div>

    <!-- Endbahnhof -->
    <div class="flex flex-col">
      <label>Endbahnhof</label>
      <Dropdown
        v-model="sectionData.endStationID"
        :options="trainStations"
        optionLabel="stationName"
        optionValue="stationID"
        placeholder="Endbahnhof wählen..."
      />
    </div>

    <!-- Warnungen -->
    <div class="flex flex-col col-span-2">
      <label>Warnungen auswählen</label>
      <MultiSelect
        v-model="sectionData.warningIDs"
        :options="warnings"
        optionLabel="warningName"
        optionValue="warningID"
        placeholder="Warnungen auswählen..."
        :filter="true"
        appendTo="body"
        panel-style="z-index: 9999"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue';

const props = defineProps({
  section: {
    type: Object,
    default: () => ({
      usageFee: null,
      length: null,
      maxSpeed: null,
      trackGauge: '',
      startStationID: null,
      endStationID: null,
      warningIDs: []
    })
  },
  trainStations: { type: Array, required: true }, // Liste der verfügbaren Bahnhöfe
  warnings: { type: Array, required: true } // Liste der verfügbaren Warnungen
});

const emits = defineEmits(['update:section', 'validate']);

/* Lokale Datenkopie der Abschnittsdaten */
const sectionData = ref({ ...props.section });

/* Optionen für Spurweiten */
const trackGaugeOptions = [
  { label: '1000mm', value: '1000' },
  { label: '1435mm', value: '1435' }
];

/* Überwachung von Änderungen an Abschnittsdaten */
watch(
  sectionData,
  (updatedSection) => {
    emits('update:section', updatedSection);

    // Validierung der Eingabedaten
    const isValid =
      updatedSection.usageFee !== null &&
      updatedSection.length !== null &&
      updatedSection.maxSpeed !== null &&
      updatedSection.trackGauge &&
      updatedSection.startStationID &&
      updatedSection.endStationID;
    emits('validate', isValid);
  },
  { deep: true }
);
</script>

<style scoped>
label {
  font-weight: bold;
  margin-bottom: 0.25rem;
}
</style>