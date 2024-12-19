<template>
  <div class="flex flex-col gap-4">
    <div class="flex flex-col">
      <label class="font-bold mb-1">Streckenname</label>
      <InputText
        v-model="trackData.trackName"
        placeholder="Streckenname eingeben..."
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
        filter
      />
    </div>

    <div v-if="errorMessage" class="error-message">
      {{ errorMessage }}
    </div>
  </div>
</template>

<script setup>
import { ref, watch, computed } from "vue";

const props = defineProps({
  track: {
    type: Object,
    default: () => ({ trackName: "", sectionIDs: [] }),
  },
  sections: {
    type: Array,
    required: true,
  },
  trainStations: {
    type: Array,
    required: true,
  },
  errorMessage: {
    type: String,
    default: "",
  },
});

const emits = defineEmits(["update:track"]);
const trackData = ref({ ...props.track });

const sectionOptions = computed(() =>
  props.sections.map((section) => ({
    label: `${getStationName(section.startStationID)} - ${getStationName(
      section.endStationID
    )}`,
    sectionID: section.sectionID,
  }))
);

function getStationName(stationID) {
  const station = props.trainStations.find((s) => s.stationID === stationID);
  return station ? station.stationName : "Unbekannt";
}

watch(
  () => trackData.value,
  (newTrack) => {
    emits("update:track", newTrack);
  },
  { deep: true }
);

watch(
  () => props.track,
  (newTrack) => {
    trackData.value = { ...newTrack };
  },
  { deep: true, immediate: true }
);
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