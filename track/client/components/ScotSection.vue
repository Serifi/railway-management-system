<template>
  <div class="grid grid-cols-2 gap-4">
    <div class="flex flex-col">
      <label for="usageFee">Preis (€)</label>
      <InputText
        id="usageFee"
        v-model.number="sectionData.usageFee"
        placeholder="Preis eingeben..."
        type="number"
      />
    </div>

    <div class="flex flex-col">
      <label for="length">Distanz (km)</label>
      <InputText
        id="length"
        v-model.number="sectionData.length"
        placeholder="Distanz eingeben..."
        type="number"
      />
    </div>

    <div class="flex flex-col">
      <label for="maxSpeed">Max. Geschwindigkeit (km/h)</label>
      <InputText
        id="maxSpeed"
        v-model.number="sectionData.maxSpeed"
        placeholder="km/h eingeben..."
        type="number"
      />
    </div>

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

    <div v-if="errorMessage" class="error-message col-span-2">
      {{ errorMessage }}
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue';

const props = defineProps({
  section: {
    type: Object,
    default: () => ({
      usageFee: 0,
      length: 0,
      maxSpeed: 0,
      trackGauge: '',
      startStationID: null,
      endStationID: null,
      warningIDs: []
    })
  },
  trainStations: {
    type: Array,
    required: true
  },
  warnings: {
    type: Array,
    required: true
  },
  errorMessage: {
    type: String,
    default: ''
  }
});

const emits = defineEmits(['update:section']);
const sectionData = ref({});

onMounted(() => {
  initializeSectionData();
});

watch(
  () => props.section,
  initializeSectionData,
  { deep: true, immediate: true }
);

function initializeSectionData() {
  sectionData.value = { ...props.section };
}

watch(
  sectionData,
  (updatedSection) => {
    emits('update:section', {
      ...updatedSection,
      warnings: updatedSection.warningIDs.map((id) =>
        props.warnings.find((w) => w.warningID === id)
      )
    });
  },
  { deep: true }
);

const trackGaugeOptions = [
  { label: '1000mm', value: '1000' },
  { label: '1435mm', value: '1435' }
];
</script>

<style scoped>
label {
  font-weight: bold;
  margin-bottom: 0.25rem;
}

.error-message {
  color: red;
  font-size: 14px;
  margin-top: 10px;
}
</style>