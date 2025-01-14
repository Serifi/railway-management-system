<template>
  <List
    :items="trainStations"
    :getKey="getTrainStationKey"
    pageType="Bahnhof"
    @create="toggleCreateDialog"
    @edit="toggleEditDialog"
    @delete="deleteTrainStation"
  >
    <template #title="{ item }">{{ item.stationName }}</template>
    <template #description="{ item }">
      <span v-html="item.address.replace(/,/g, '<br>')"></span>
    </template>
  </List>
  <ScotDialog
    :visible="createDialogVisible"
    type="create"
    header="Bahnhof erstellen"
    :disable-action="disableAction"
    @update:visible="createDialogVisible = $event"
    @action="createTrainStation"
    @cancel="toggleCreateDialog"
  >
    <ScotTrainStation @update:trainStation="updateTrainStation" />
  </ScotDialog>
  <ScotDialog
    :visible="editDialogVisible"
    type="edit"
    header="Bahnhof bearbeiten"
    :disable-action="disableAction"
    @update:visible="editDialogVisible = $event"
    @action="editTrainStation"
    @cancel="toggleEditDialog"
  >
    <ScotTrainStation :trainStation="trainStation" @update:trainStation="updateTrainStation" />
  </ScotDialog>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useTrainStationStore } from '@/stores/train-station.js';
import { useToast } from 'primevue/usetoast';
import List from '~/components/ScotList.vue';
import ScotTrainStation from '~/components/ScotTrainStation.vue';
import ScotDialog from '~/components/ScotDialog.vue';

const toast = useToast();
const createDialogVisible = ref(false);
const editDialogVisible = ref(false);
const trainStationStore = useTrainStationStore();
const trainStations = computed(() => trainStationStore.trainStations);
const trainStation = ref({ stationName: '', address: '' });
const disableAction = ref(true);

function handleError(error) {
  if (error.response?.status === 400 && error.response?.data?.message) {
    toast.add({ severity: 'error', summary: 'Fehler', detail: error.response.data.message, life: 3000 });
  } else if (error.response?.status === 404) {
    toast.add({ severity: 'error', summary: 'Nicht gefunden', detail: 'Bahnhof wurde nicht gefunden.', life: 3000 });
  } else {
    toast.add({ severity: 'error', summary: 'Fehler', detail: 'Ein Fehler ist aufgetreten.', life: 3000 });
  }
}

function updateTrainStation(currentStation) {
  trainStation.value = currentStation;
  disableAction.value = !currentStation || !currentStation.stationName || !currentStation.address;
}

function toggleCreateDialog() {
  createDialogVisible.value = !createDialogVisible.value;
  trainStation.value = { stationName: '', address: '' };
  disableAction.value = true;
}

async function createTrainStation() {
  try {
    await trainStationStore.createTrainStation(trainStation.value);
    toggleCreateDialog();
    toast.add({severity: 'success', summary: 'Erfolgreich', detail: 'Bahnhof wurde erfolgreich erstellt', life: 3000});
  } catch (error) {
    handleError(error);
  }
}

function toggleEditDialog(currentStation) {
  trainStation.value = currentStation || {stationName: '', address: ''};
  editDialogVisible.value = !editDialogVisible.value;
  disableAction.value = !trainStation.value.stationName || !trainStation.value.address;
}

async function editTrainStation() {
  try {
    await trainStationStore.editTrainStation(trainStation.value);
    toggleEditDialog();
    toast.add({
      severity: 'success',
      summary: 'Erfolgreich',
      detail: 'Bahnhof wurde erfolgreich bearbeitet',
      life: 3000
    });
  } catch (error) {
    handleError(error);
  }
}

async function deleteTrainStation(currentStation) {
  try {
    await trainStationStore.deleteTrainStation(currentStation.stationID);
    toast.add({severity: 'success', summary: 'Erfolgreich', detail: 'Bahnhof wurde erfolgreich gelöscht', life: 3000});
  } catch (error) {
    handleError(error);
  }
}

function getTrainStationKey(station) {
  return station.stationID;
}

onMounted(() => {
  trainStationStore.getTrainStations();
});
</script>