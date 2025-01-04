<template>
  <div>
    <List
      :items="tracks"
      :getKey="getTrackKey"
      pageType="Strecke"
      @create="toggleCreateDialog"
      @edit="toggleEditDialog"
      @delete="deleteTrack"
    >
      <template #title="{ item }">
        <h2>{{ item.trackName }}</h2>
      </template>

      <template #description="{ item }">
        <div class="track-visualization">
          <div
            v-for="section in item.sections"
            :key="section.sectionID"
            class="track-row"
          >
            <div class="station-container">
              <div class="station-point"></div>
              <div class="station-name">{{ getStationName(section.startStationID) }}</div>
            </div>
            <div class="section-line" :style="{ width: section.length * 3 + 'px' }"></div>
            <div class="station-container">
              <div class="station-point"></div>
              <div class="station-name">{{ getStationName(section.endStationID) }}</div>
            </div>
          </div>

          <div v-for="section in item.sections" :key="section.sectionID">
            <div
              v-for="warning in section.warnings"
              :key="warning.warningID"
              class="warning-message"
            >
              ⚠️ Achtung: {{ warning.warningName }} im Abschnitt
              {{ getStationName(section.startStationID) }} - {{ getStationName(section.endStationID) }}
            </div>
          </div>
        </div>
      </template>
    </List>

    <ScotDialog
      :visible="createDialogVisible || editDialogVisible"
      :type="createDialogVisible ? 'create' : 'edit'"
      :header="createDialogVisible ? 'Strecke erstellen' : 'Strecke bearbeiten'"
      :disable-action="!isTrackValid"
      @update:visible="closeDialog"
      @action="saveTrack"
      @cancel="closeDialog"
    >
      <ScotTrack
        v-model:track="currentTrack"
        :sections="sections"
        :trainStations="trainStations"
        @validate="updateTrackValidity"
      />
    </ScotDialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useToast } from 'primevue/usetoast';
import { useTrackStore } from '@/stores/track';
import { useSectionStore } from '@/stores/section';
import { useTrainStationStore } from '@/stores/train-station';
import List from '~/components/ScotList.vue';
import ScotDialog from '~/components/ScotDialog.vue';
import ScotTrack from '~/components/ScotTrack.vue';

const toast = useToast();
const trackStore = useTrackStore();
const sectionStore = useSectionStore();
const trainStationStore = useTrainStationStore();

const tracks = computed(() => trackStore.tracks);
const sections = computed(() => sectionStore.sections);
const trainStations = computed(() => trainStationStore.trainStations);

const createDialogVisible = ref(false);
const editDialogVisible = ref(false);
const currentTrack = ref({});
const isTrackValid = ref(false);

function getTrackKey(track) {
  return track.trackID;
}

function getStationName(id) {
  const station = trainStations.value.find((s) => s.stationID === id);
  return station ? station.stationName : 'Unbekannt';
}

function toggleCreateDialog() {
  currentTrack.value = { trackName: '', sectionIDs: [] };
  isTrackValid.value = false;
  createDialogVisible.value = true;
}

function toggleEditDialog(track) {
  currentTrack.value = { ...track, sectionIDs: track.sections.map((s) => s.sectionID) };
  isTrackValid.value = !!currentTrack.value.trackName.trim() && currentTrack.value.sectionIDs.length > 0;
  editDialogVisible.value = true;
}

async function saveTrack() {
  try {
    if (createDialogVisible.value) {
      await trackStore.createTrack(currentTrack.value);
      showToast('Strecke wurde erfolgreich erstellt', 'success');
    } else {
      await trackStore.editTrack(currentTrack.value.trackID, currentTrack.value);
      showToast('Strecke wurde erfolgreich bearbeitet', 'success');
    }
    closeDialog();
  } catch (error) {
    showToast(error.response?.data?.message || 'Ein unbekannter Fehler ist aufgetreten.', 'error');
  }
}

async function deleteTrack(track) {
  try {
    await trackStore.deleteTrack(track.trackID);
    showToast('Strecke wurde erfolgreich gelöscht', 'success');
  } catch (error) {
    showToast('Fehler beim Löschen der Strecke', 'error');
  }
}

function closeDialog() {
  createDialogVisible.value = false;
  editDialogVisible.value = false;
}

function updateTrackValidity(isValid) {
  isTrackValid.value = isValid;
}

function showToast(message, type = 'success') {
  toast.add({
    severity: type,
    summary: type === 'success' ? 'Erfolg' : 'Fehler',
    detail: message,
    life: 3000,
  });
}

onMounted(() => {
  trackStore.getTracks();
  sectionStore.getSections();
  trainStationStore.getTrainStations();
});
</script>