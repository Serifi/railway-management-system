<template>
  <div @click="handleTrackVisualizationClick">
    <ScotTrackList
      :items="tracks"
      :getKey="getTrackKey"
      pageType="Strecke"
      @create="toggleCreateDialog"
      @edit="toggleEditDialog"
      @delete="deleteTrack"
      @toggle="handleTrackToggle"
    >
      <template #title="{ item }">
        <h2>{{ item.trackName }}</h2>
      </template>

      <template #description="{ item }">
        <div class="track-visualization" @click="handleTrackVisualizationClick">
          <div v-for="(section, index) in item.sections" :key="section.sectionID">
            <div class="station">
              <div
                class="station-point"
                :class="{
                  'highlighted-point': isHighlighted(section.sectionID, item.sections, index, true),
                  'dimmed-point': expandedTrack === item.trackID && !isHighlighted(section.sectionID, item.sections, index, true)
                }"
              ></div>
              <div
                class="station-name"
                :class="{
                  'highlighted': expandedTrack === item.trackID && isHighlighted(section.sectionID, item.sections, index, true),
                  'dimmed': expandedTrack === item.trackID && !isHighlighted(section.sectionID, item.sections, index, true)
                }"
              >
                {{ getStationName(section.startStationID) }}
              </div>
            </div>

            <div class="section-container">
              <div
                class="section-line"
                :class="{
                  'warning-line': section.warnings.length > 0,
                  'highlighted-line': expandedSection === section.sectionID,
                  'dimmed-line': expandedTrack === item.trackID && expandedSection !== section.sectionID
                }"
                :style="{ height: `${Math.max(section.length*0.5, 80)}px` }"
                @click.stop="toggleSectionDetails(section.sectionID, item.trackID)"
              ></div>
              <div
                class="section-details"
                v-if="expandedSection === section.sectionID && expandedTrack === item.trackID"
              >
                <div class="details-layout">
                  <div class="top-details">
                    <div class="detail-row">
                      <span class="icon-wrapper">
                        <i class="pi pi-money-bill gray-icon"></i>
                      </span>
                      <span class="detail-value">{{ section.usageFee }}€</span>
                    </div>
                    <div class="detail-row">
                      <span class="icon-wrapper">
                        <i class="pi pi-map gray-icon"></i>
                      </span>
                      <span class="detail-value">{{ section.length }}km</span>
                    </div>
                    <div class="detail-row">
                      <span class="icon-wrapper">
                        <i class="pi pi-send gray-icon"></i>
                      </span>
                      <span class="detail-value">{{ section.maxSpeed }}km/h</span>
                    </div>
                  </div>
                  <div class="warnings-container" v-if="section.warnings.length">
                    <ul class="warnings-list">
                      <li v-for="warning in section.warnings" :key="warning.warningID" class="warning-item">
                        <span class="icon-wrapper">
                          <i class="pi pi-exclamation-triangle gray-icon"></i>
                        </span>
                        <span class="warning-content">
                          <span class="warning-name">{{ warning.warningName }}</span>
                          <span v-if="warning.description" class="warning-description">
                            : {{ warning.description }}
                          </span>
                        </span>
                      </li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>

            <div v-if="index === item.sections.length - 1" class="station">
              <div
                class="station-point"
                :class="{
                  'highlighted-point': isHighlighted(section.sectionID, item.sections, index, false),
                  'dimmed-point': expandedTrack === item.trackID && !isHighlighted(section.sectionID, item.sections, index, false)
                }"
              ></div>
              <div
                class="station-name"
                :class="{
                  'highlighted': expandedTrack === item.trackID && isHighlighted(section.sectionID, item.sections, index, false),
                  'dimmed': expandedTrack === item.trackID && !isHighlighted(section.sectionID, item.sections, index, false)
                }"
              >
                {{ getStationName(section.endStationID) }}
              </div>
            </div>
          </div>
        </div>
      </template>
    </ScotTrackList>

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
import {ref, computed, onMounted} from 'vue';
import {useToast} from 'primevue/usetoast';
import {useTrackStore} from '@/stores/track';
import {useSectionStore} from '@/stores/section';
import {useTrainStationStore} from '@/stores/train-station';
import List from '~/components/ScotTrackList.vue';
import ScotDialog from '~/components/ScotDialog.vue';
import ScotTrack from '~/components/ScotTrack.vue';

const toast = useToast();
const trackStore = useTrackStore();
const sectionStore = useSectionStore();
const trainStationStore = useTrainStationStore();

const tracks = computed(() =>
    trackStore.tracks.map((track) => ({
      ...track,
      sections: sortSections(track.sections),
    }))
);

const sections = computed(() => sectionStore.sections);
const trainStations = computed(() => trainStationStore.trainStations);

const createDialogVisible = ref(false);
const editDialogVisible = ref(false);
const currentTrack = ref({});
const isTrackValid = ref(false);

const expandedSection = ref(null);
const expandedTrack = ref(null);

function getTrackKey(track) {
  return track.trackID;
}

function getStationName(id) {
  const station = trainStations.value.find((s) => s.stationID === id);
  return station ? station.stationName : 'Unbekannt';
}

function sortSections(sections) {
  if (!sections.length) return sections;

  const sectionMap = new Map();
  sections.forEach((section) => {
    sectionMap.set(section.startStationID, section);
  });

  const sortedSections = [];
  let current = sections.find(
      (section) =>
          !sections.some((s) => s.endStationID === section.startStationID)
  );

  while (current) {
    sortedSections.push(current);
    current = sectionMap.get(current.endStationID);
  }

  return sortedSections;
}

function isHighlighted(sectionID, sections, index, isStart = true) {
  const sortedSections = sortSections(sections);
  const currentIndex = sortedSections.findIndex((section) => section.sectionID === sectionID);

  if (currentIndex === -1) return false;

  if (isStart) {
    const isCurrentStart = expandedSection.value === sectionID;
    const isNextStart =
      currentIndex - 1 < sortedSections.length && expandedSection.value === sortedSections[currentIndex - 1]?.sectionID;

    return isCurrentStart || isNextStart;
  } else {
    const isCurrentEnd = expandedSection.value === sortedSections[currentIndex]?.sectionID;
    const isNextStart =
      currentIndex + 1 < sortedSections.length && expandedSection.value === sortedSections[currentIndex + 1]?.sectionID;

    return isCurrentEnd || isNextStart;
  }
}

function toggleSectionDetails(sectionID, trackID) {
  if (expandedSection.value === sectionID && expandedTrack.value === trackID) {
    expandedSection.value = null;
    expandedTrack.value = null;
  } else {
    expandedSection.value = sectionID;
    expandedTrack.value = trackID;
  }
}

function handleTrackToggle(expandedTrackId) {
  expandedTrack.value = expandedTrackId;
}

function clearFocus() {
  expandedSection.value = null;
  expandedTrack.value = null;
}

function toggleCreateDialog() {
  currentTrack.value = {trackName: '', sectionIDs: []};
  isTrackValid.value = false;
  createDialogVisible.value = true;
}

function toggleEditDialog(track) {
  currentTrack.value = {
    ...track,
    sectionIDs: track.sections.map((s) => s.sectionID),
  };
  isTrackValid.value =
      !!currentTrack.value.trackName.trim() &&
      currentTrack.value.sectionIDs.length > 0;
  editDialogVisible.value = true;
}

async function saveTrack() {
  try {
    if (createDialogVisible.value) {
      await trackStore.createTrack(currentTrack.value);
      showToast('Strecke wurde erfolgreich erstellt', 'success');
    } else {
      await trackStore.editTrack(
          currentTrack.value.trackID,
          currentTrack.value
      );
      showToast('Strecke wurde erfolgreich bearbeitet', 'success');
    }
    closeDialog();
  } catch (error) {
    showToast(
        error.response?.data?.message || 'Ein unbekannter Fehler ist aufgetreten.',
        'error'
    );
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

function handleTrackVisualizationClick(event) {
  const clickedElement = event.target;

  if (!clickedElement.classList.contains('section-line')) {
    clearFocus();
  }
}

onMounted(() => {
  trackStore.getTracks();
  sectionStore.getSections();
  trainStationStore.getTrainStations();
});
</script>

<style scoped>
.track-visualization {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  margin-left: 20px;
}

.station {
  display: flex;
  align-items: center;
}

.station-point {
  width: 12px;
  height: 12px;
  background-color: #3076A7;
  border-radius: 50%;
  margin-right: 10px;
  transition: background-color 0.3s ease;
}

.highlighted-point {
  background-color: #0056A7;
}

.dimmed-point {
  background-color: #ccc;
}

.station-name {
  font-size: 15px;
  color: black;
}

.station-name.highlighted {
  font-weight: bold;
}

.station-name.dimmed {
  color: #999;
}

.section-container {
  display: flex;
  align-items: center;
}

.section-line {
  width: 4px;
  background-color: #3076A7;
  margin-left: 4.3px;
  margin-right: 20px;
  transition: background-color 0.3s ease;
  cursor: pointer;
}

.section-line.dimmed-line {
  background-color: #ccc;
}

.warning-line {
  background-color: #A73030;
}

.section-details {
  display: flex;
  flex-direction: column;
  margin-left: 15px;
  font-size: 5px;
  color: #333;
}

.details-layout {
  display: flex;
  flex-direction: column;
}

.top-details {
  display: flex;
  gap: 20px;
}


.detail-row {
  display: flex;
  align-items: center;
}

.icon-wrapper {
  display: inline-flex;
  align-items: center;
  margin-right: 8px;
}

.gray-icon {
  font-size: 12px;
  color: #b0b0b0;
}

.detail-value {
  font-size: 13px;
}

.warnings-container {
  margin-top: 5px;
}

.warnings-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.warnings-list li {
  font-size: 13px;
  color: #333;
  margin-bottom: 1px;
}

.warning-name {
  font-weight: normal;
}

.warning-description {
  display: inline-block;
}
</style>