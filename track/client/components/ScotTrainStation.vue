<template>
  <div class="grid grid-cols-2 gap-4">
    <div class="flex flex-col col-span-2">
      <label for="stationName" class="mb-1">Stationsname</label>
      <InputText id="stationName" v-model="station.stationName" placeholder="Text eingeben..." />
    </div>
    <div class="flex flex-col col-span-2">
      <label for="address" class="mb-1">Adresse</label>
      <InputText id="address" v-model="station.address" placeholder="Text eingeben..." />
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue';

const emits = defineEmits(['update:trainStation']);
const props = defineProps({
  trainStation: {type: Object, default: () => ({stationName: '', address: ''})},
});

const station = ref({...props.trainStation});

watch(
    [() => station.value.stationName, () => station.value.address],
    ([stationName, address]) => {
      if (stationName && address) emits('update:trainStation', station.value);
      else emits('update:trainStation', null);
    }
);
</script>