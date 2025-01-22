<template>
  <!-- Stepper-Komponente für die Übersicht der Schritte -->
  <Stepper value="1" class="custom-stepper">
    <StepList style="gap: 10px; justify-content: space-between;">
      <Step value="1">Halteplan Details</Step> <!-- Schritt 1: Details des Halteplans -->
      <Step value="2">Bahnhöfe</Step> <!-- Schritt 2: Auswahl der Bahnhöfe -->
    </StepList>

    <!-- Panels für die Inhalte der einzelnen Schritte -->
    <StepPanels>
      <!-- Inhalt für Schritt 1 -->
      <StepPanel v-slot="{ activateCallback }" value="1">
        <div v-if="currentStep === 1">
          <!-- Details für den Halteplan -->
          <div class="flex flex-col">
            <label for="name" class="mb-1">Name des Halteplans</label>
            <!-- Eingabefeld für den Namen des Halteplans -->
            <InputText id="name" v-model="stopplan.name" placeholder="Text eingeben..."/>
          </div>
          <br>
          <div class="flex flex-col">
            <label for="track" class="mb-1">Strecke</label>
            <!-- Dropdown zur Auswahl der Strecke -->
            <Dropdown
              id="track"
              v-model="stopplan.track"
              :options="tracks"
              optionLabel="name"
              placeholder="Auswahl treffen..."
            />
          </div>
          <br>
<!-- Wechselt zum nächsten Schritt -->
          <ScotButton
            label="Weiter"
            icon="pi pi-arrow-right"
            variant="blue"
            :disabled="!stopplan.track"
            @click="nextStep(); activateCallback('2')"
          />
        </div>
      </StepPanel>

      <!-- Inhalt für Schritt 2 -->
      <StepPanel v-slot="{ activateCallback }" value="2">
        <div v-if="currentStep === 2">
          <!-- Auswahl der Bahnhöfe -->
          <div class="flex flex-col">
            <label for="stations" class="mb-1">Bahnhöfe</label>
            <!-- MultiSelect-Komponente zur Auswahl mehrerer Bahnhöfe -->
            <MultiSelect
              id="stations"
              v-model="stopplan.trainStations"
              :options="trainStations"
              optionLabel="name"
              placeholder="Bahnhöfe auswählen..."
            />
          </div>
          <br>
          <!-- Buttons für Zurück und Erstellen -->
          <div class="flex" style="gap: 0.5rem;">
            <!-- Zurück-Button -->
            <ScotButton
              label="Zurück"
              icon="pi pi-arrow-left"
              variant="gray"
              @click="prevStep(); activateCallback('1')" 
            />
            <!-- Erstellen-Button -->
            <ScotButton
              label="Erstellen"
              icon="pi pi-plus"
              variant="blue"
              @click="createStopplan"
            />
          </div>
        </div>
      </StepPanel>
    </StepPanels>
  </Stepper>
</template>

<script setup>
import Stepper from 'primevue/stepper';
import StepList from 'primevue/steplist';
import Step from 'primevue/step';
import { ref, computed, onMounted } from 'vue';
import { useStopplanStore } from '~/stores/stopplan.js';
import { useToast } from 'primevue/usetoast';

const toast = useToast();
const emit = defineEmits(['stopplan-created']);
const stopplanStore = useStopplanStore();

// Reaktive Daten
const currentStep = ref(1); // Verfolgt den aktuellen Schritt
const stopplan = ref({
  name: '', // Name des Halteplans
  track: null, // Ausgewählte Strecke
  trainStations: [], // Ausgewählte Bahnhöfe
});

// ruft Tracks ab
const tracks = computed(() =>
  stopplanStore.tracks.map(track => ({
    id: track.trackID,
    name: track.trackName,
    sections: track.sections, // Enthält die Abschnitte der Strecke
  }))
);

const trainStations = ref([]); // Liste der verfügbaren Bahnhöfe

// Lifecycle-Hook: Lädt die Tracks beim Mounten der Komponente
onMounted(async () => {
  await stopplanStore.fetchTracks(); // Ruft die Tracks aus dem Store ab
  console.log("Geladene Tracks:", tracks.value); // Debugging: Zeigt die geladenen Tracks an
});

// Funktion zum Wechseln zum nächsten Schritt
function nextStep() {
  if (currentStep.value === 1) { // Wenn aktueller Schritt 1 ist
    loadStations(stopplan.value.track); // Lädt Bahnhöfe basierend auf der ausgewählten Strecke
    currentStep.value = 2; // Wechselt zu Schritt 2
  }
}

// Funktion zum Zurückwechseln zum vorherigen Schritt
function prevStep() {
  currentStep.value = 1; // Setzt auf Schritt 1 zurück
}

// Funktion zum Laden der Bahnhöfe für die ausgewählte Strecke
function loadStations(track) {
  const stationMap = new Map(); // Verwendet eine Map, um Duplikate zu vermeiden

  track.sections.forEach((section) => {
    // Fügt Startbahnhöfe hinzu
    if (section.startStationID) {
      stationMap.set(section.startStationID, { id: section.startStationID, name: `Station ${section.startStationID}` });
    }
    // Fügt Endbahnhöfe hinzu
    if (section.endStationID) {
      stationMap.set(section.endStationID, { id: section.endStationID, name: `Station ${section.endStationID}` });
    }
  });

  trainStations.value = Array.from(stationMap.values()); // Konvertiert die Map in ein Array
}

// Funktion zum Erstellen eines Halteplans
async function createStopplan() {
  const stopplanData = {
    name: stopplan.value.name, // Name des Halteplans
    trackID: stopplan.value.track.id, // ID der ausgewählten Strecke
    trainStations: stopplan.value.trainStations.map(station => ({ id: station.id })), // IDs der ausgewählten Bahnhöfe
  };

  await stopplanStore.createStopplan(stopplanData); // Speichert den Halteplan im Store

  toast.add({
    severity: 'success', // Erfolgsnachricht
    summary: 'Erfolg',
    detail: `Halteplan "${stopplanData.name}" wurde erfolgreich erstellt`,
    life: 3000,
  });

  emit('stopplan-created');
  stopplan.value = { name: '', track: null, trainStations: [] }; // Setzt den Halteplan zurück
  currentStep.value = 1; // Setzt den aktuellen Schritt zurück
}
</script>
