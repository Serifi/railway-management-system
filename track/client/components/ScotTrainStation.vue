<!-- Komponente zur Bearbeitung von Bahnhöfen -->
<template>
  <div class="grid grid-cols-2 gap-4">
    <!-- Eingabe für den Stationsnamen -->
    <div class="flex flex-col col-span-2">
      <label for="stationName" class="mb-1">Stationsname</label>
      <InputText
        id="stationName"
        v-model="station.stationName"
        placeholder="Text eingeben..."
      />
    </div>

    <!-- Eingabe für die Adresse -->
    <div class="flex flex-col col-span-2">
      <label for="address" class="mb-1">Adresse</label>
      <InputText
        id="address"
        v-model="station.address"
        placeholder="Text eingeben..."
      />
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue';

const emits = defineEmits(['update:trainStation']);

const props = defineProps({
  trainStation: {
    type: Object,
    default: () => ({ stationName: '', address: '' }),
  },
});

const station = ref({ ...props.trainStation });

/* Überwachung der Eingabewerte und Weitergabe der Änderungen */
watch(
  [() => station.value.stationName, () => station.value.address],
  ([stationName, address]) => {
    // Nur gültige Eingaben weitergeben
    if (stationName && address) {
      emits('update:trainStation', station.value);
    } else {
      emits('update:trainStation', null);
    }
  }
);
</script>