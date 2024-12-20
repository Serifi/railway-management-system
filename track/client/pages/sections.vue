<template>
  <List
    :items="sectionsWithStationNames"
    :getKey="getSectionKey"
    pageType="Abschnitt"
    :showWarningButton="true"
    @create="toggleCreateDialog"
    @createWarning="toggleWarningDialog"
    @edit="toggleEditDialog"
    @delete="deleteSection"
  >
    <template #title="{ item }">
      {{ item.startStationName }} - {{ item.endStationName }}
    </template>
    <template #description="{ item }">
      <div>
        <p>Preis: {{ item.usageFee }}€</p>
        <p>Distanz: {{ item.length }} km</p>
        <p>Max. Geschwindigkeit: {{ item.maxSpeed }} km/h</p>
        <p>Spurweite: {{ item.trackGauge }}mm</p>
      </div>
    </template>
  </List>

  <ScotDialog
    :visible="createDialogVisible || editDialogVisible"
    :type="createDialogVisible ? 'create' : 'edit'"
    :header="createDialogVisible ? 'Abschnitt erstellen' : 'Abschnitt bearbeiten'"
    :disable-action="disableAction"
    @update:visible="closeDialog"
    @action="saveSection"
    @cancel="closeDialog"
  >
    <ScotSection
      v-model:section="section"
      :trainStations="stations"
      :warnings="warnings"
      :errorMessage="errorMessage"
    />
  </ScotDialog>

  <ScotDialog
    :visible="warningDialogVisible"
    type="create"
    header="Warnung erstellen"
    @update:visible="warningDialogVisible = $event"
    @action="createWarning"
    @cancel="toggleWarningDialog"
  >
    <ScotWarning v-model:warning="newWarning" :errorMessage="errorMessage" />
  </ScotDialog>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useToast } from 'primevue/usetoast';
import { useSectionStore } from '@/stores/section.js';
import { useTrainStationStore } from '@/stores/train-station.js';
import { useWarningStore } from '@/stores/warning.js';
import List from '~/components/ScotList.vue';
import ScotSection from '~/components/ScotSection.vue';
import ScotWarning from '~/components/ScotWarning.vue';
import ScotDialog from '~/components/ScotDialog.vue';

const toast = useToast();

const sectionStore = useSectionStore();
const stationStore = useTrainStationStore();
const warningStore = useWarningStore();

const sections = computed(() => sectionStore.sections);
const stations = computed(() => stationStore.trainStations);
const warnings = computed(() => warningStore.warnings);

const section = ref({
  usageFee: 0,
  length: 0,
  maxSpeed: 0,
  trackGauge: '',
  startStationID: null,
  endStationID: null,
  warningIDs: []
});
const newWarning = ref({
  warningName: '',
  description: '',
  startDate: '',
  endDate: ''
});

const createDialogVisible = ref(false);
const editDialogVisible = ref(false);
const warningDialogVisible = ref(false);
const disableAction = ref(false);
const errorMessage = ref(''); // Neue Fehlermeldung

onMounted(() => {
  sectionStore.getSections();
  stationStore.getTrainStations();
  warningStore.getWarnings();
});

const sectionsWithStationNames = computed(() => {
  return sections.value.map((section) => ({
    ...section,
    startStationName: getStationName(section.startStationID),
    endStationName: getStationName(section.endStationID)
  }));
});

function getSectionKey(section) {
  return section.sectionID;
}

function getStationName(id) {
  const station = stations.value.find((s) => s.stationID === id);
  return station ? station.stationName : 'Unbekannt';
}

function toggleCreateDialog() {
  createDialogVisible.value = true;
  errorMessage.value = '';
  section.value = {
    usageFee: 0,
    length: 0,
    maxSpeed: 0,
    trackGauge: '',
    startStationID: null,
    endStationID: null,
    warningIDs: []
  };
}

function toggleEditDialog(currentSection) {
  editDialogVisible.value = true;
  errorMessage.value = '';

  const warningIDs = currentSection.warnings
    ? currentSection.warnings.map((warning) => warning.warningID)
    : [];

  section.value = {
    sectionID: currentSection.sectionID,
    usageFee: currentSection.usageFee,
    length: currentSection.length,
    maxSpeed: currentSection.maxSpeed,
    trackGauge: currentSection.trackGauge,
    startStationID: currentSection.startStationID,
    endStationID: currentSection.endStationID,
    warningIDs: warningIDs
  };
}

function closeDialog() {
  createDialogVisible.value = false;
  editDialogVisible.value = false;
  errorMessage.value = '';
}

function toggleWarningDialog() {
  warningDialogVisible.value = !warningDialogVisible.value;
  errorMessage.value = '';
}

async function createWarning() {
  try {
    await warningStore.createWarning(newWarning.value);

    toast.add({
      severity: 'success',
      summary: 'Erfolg',
      detail: 'Warnung wurde erfolgreich erstellt',
      life: 3000
    });

    toggleWarningDialog();
    newWarning.value = {
      warningName: '',
      description: '',
      startDate: '',
      endDate: ''
    };
  } catch (error) {
    errorMessage.value = error.response?.data?.message || 'Ein unbekannter Fehler ist aufgetreten.';
  }
}

async function saveSection() {
  try {
    if (createDialogVisible.value) {
      await sectionStore.createSection(section.value);
      toast.add({
        severity: 'success',
        summary: 'Erfolg',
        detail: 'Abschnitt wurde erfolgreich erstellt',
        life: 3000
      });
    } else {
      const { sectionID, ...sectionData } = section.value;

      if (!sectionID) {
        console.error("Fehler: sectionID ist undefined!");
        return;
      }

      await sectionStore.editSection(sectionID, sectionData);
      toast.add({
        severity: 'success',
        summary: 'Erfolg',
        detail: 'Abschnitt wurde erfolgreich bearbeitet',
        life: 3000
      });
    }
    closeDialog();
  } catch (error) {
    errorMessage.value = error.response?.data?.message || 'Ein unbekannter Fehler ist aufgetreten.';
  }
}

async function deleteSection(section) {
  try {
    await sectionStore.deleteSection(section.sectionID);
    toast.add({
      severity: 'success',
      summary: 'Erfolg',
      detail: 'Abschnitt wurde erfolgreich gelöscht',
      life: 3000
    });
  } catch (error) {
    console.error('Fehler beim Löschen der Section:', error);
    toast.add({
      severity: 'error',
      summary: 'Fehler',
      detail: 'Fehler beim Löschen des Abschnitts',
      life: 3000
    });
  }
}
</script>