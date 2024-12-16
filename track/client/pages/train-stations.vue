<template>
  <List
    :items="trainStations"
    :getKey="getTrainStationKey"
    pageType="Bahnhof"
    :showWarningButton="false"
    @create="toggleCreateDialog"
    @edit="toggleEditDialog"
    @delete="deleteTrainStation"
  >
    <template #title="{ item }">
      {{ item.stationName }}
    </template>

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
    <ScotTrainStation :trainStation="trainStation" @update:trainStation="updateTrainStation"/>
  </ScotDialog>
</template>

<script setup>
import {ref, computed, onMounted} from 'vue';
import {useTrainStationStore} from '@/stores/train-station.js';
import {useToast} from 'primevue/usetoast';
import List from '~/components/ScotList.vue';
import ScotTrainStation from '~/components/ScotTrainStation.vue';
import ScotDialog from '~/components/ScotDialog.vue';

const toast = useToast();

const createDialogVisible = ref(false);
const editDialogVisible = ref(false);
const trainStationStore = useTrainStationStore();
const trainStations = computed(() => trainStationStore.trainStations);
const trainStation = ref(null);
const disableAction = ref(false);

function updateTrainStation(currentStation) {
  trainStation.value = currentStation;
  disableAction.value = trainStation.value === null;
}

function toggleCreateDialog() {
  createDialogVisible.value = !createDialogVisible.value;
  if (createDialogVisible.value) disableAction.value = true;
}

function createTrainStation() {
  trainStationStore.createTrainStation(trainStation.value);
  toggleCreateDialog();
  toast.add({severity: 'success', summary: 'Erfolgreich', detail: 'Bahnhof wurde erfolgreich erstellt', life: 3000});
}

async function toggleEditDialog(currentStation) {
  trainStation.value = currentStation;
  editDialogVisible.value = !editDialogVisible.value;
  if (editDialogVisible.value) disableAction.value = false;
}

function editTrainStation() {
  trainStationStore.editTrainStation(trainStation.value);
  toggleEditDialog(null);
  toast.add({severity: 'success', summary: 'Erfolgreich', detail: 'Bahnhof wurde erfolgreich bearbeitet', life: 3000});
}

function deleteTrainStation(currentStation) {
  trainStationStore.deleteTrainStation(currentStation.stationID);
  toast.add({severity: 'success', summary: 'Erfolgreich', detail: 'Bahnhof wurde erfolgreich gelöscht', life: 3000});
}

function getTrainStationKey(station) {
  return station.stationID;
}

onMounted(() => {
  trainStationStore.getTrainStations();
});
</script>