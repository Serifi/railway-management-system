<template>
  <!-- Stepper-Komponente, die den aktuellen Schritt anzeigt -->
  <Stepper value="1" class="custom-stepper">
    <StepList style="gap: 10px; justify-content: space-between;">
      <!-- Schritt 1: Halteplan Details -->
      <Step value="1">Halteplan Details</Step>
      <!-- Schritt 2: Bahnhöfe -->
      <Step value="2">Bahnhöfe</Step>
    </StepList>
  </Stepper>

  <div>
    <!-- Anzeige des ersten Schritts -->
    <div v-if="currentStep === 1">
      <div class="flex flex-col">
        <!-- Eingabefeld für den Namen des Halteplans -->
        <label for="name" class="mb-1">Name des Halteplans</label>
        <InputText
          id="name"
          v-model="stopplan.name"
          placeholder="Text eingeben..."
        />
      </div>
      <br>
      <div class="flex flex-col">
        <!-- Dropdown für die Auswahl der Strecke -->
        <label for="track" class="mb-1">Strecke</label>
        <Dropdown
          id="track"
          v-model="stopplan.track"
          :options="tracks"
          optionLabel="trackName"
          placeholder="Auswahl treffen..."
        />
      </div>
      <br>
      <!-- Button zum Wechseln zum nächsten Schritt -->
      <ScotButton
        label="Weiter"
        icon="pi pi-arrow-right"
        variant="blue"
        :disabled="!stopplan.track"
        @click="nextStep"
      />
    </div>

    <!-- Anzeige des zweiten Schritts -->
    <div v-else-if="currentStep === 2">
      <div class="flex flex-col">
        <!-- MultiSelect für die Auswahl von Bahnhöfen -->
        <label for="stations" class="mb-1">Bahnhöfe</label>
        <MultiSelect
          id="stations"
          v-model="stopplan.trainStations"
          :options="trainStations"
          optionLabel="stationName"
          placeholder="Bahnhöfe auswählen..."
        />
      </div>
      <br>
      <div class="flex" style="gap: 0.5rem;">
        <!-- Zurück-Button -->
        <ScotButton
          label="Zurück"
          icon="pi pi-arrow-left"
          variant="gray"
          @click="prevStep"
        />
        <!-- Bearbeiten-Button -->
        <ScotButton
          label="Bearbeiten"
          icon="pi pi-pencil"
          variant="blue"
          @click="updateStopplan"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import Stepper from 'primevue/stepper';
import StepList from 'primevue/steplist';
import Step from 'primevue/step';

import { computed, onMounted, ref } from 'vue'; // Vue-Funktionen
import { useStopplanStore } from '~/stores/stopplan.js'; // Store für Haltepläne
import { useToast } from 'primevue/usetoast'; // Toast für Benachrichtigungen

// Zugriff auf den Store für Haltepläne
const stopplanStore = useStopplanStore();
// Tracks werden aus dem Store abgeleitet
// const tracks = computed(() => stopplanStore.tracks);
const tracks = ref([]) // Liste der Strecken


// Props: Eingabeparameter von der übergeordneten Komponente
const { stopplanID, stopplanName, stopplanTrackID, stopplanTrainstations } = defineProps({
  stopplanID: { type: Number, required: true }, // ID des Halteplans
  stopplanName: { type: String, required: true }, // Name des Halteplans
  stopplanTrackID: { type: Number, required: true }, // ID der Strecke
  stopplanTrainstations: { type: Array, required: true }, // Liste der Bahnhöfe
});

// Funktion, um die aktuell ausgewählte Strecke zu finden
function getSelectedTrack() {
  return tracks.value.find((track) => track.id === stopplanTrackID);
}

const toast = useToast();
const emit = defineEmits(['stopplan-created']);

// Lokale Zustände
const currentStep = ref(1); // Der aktuelle Schritt im Formular
const stopplan = ref({
  name: stopplanName, // Initialer Name des Halteplans
  track: getSelectedTrack(), // Initiale Strecke
  trainStations: stopplanTrainstations, // Initiale Bahnhöfe
});

// Liste der verfügbaren Bahnhöfe
const trainStations = ref([]);

// Initialisierung beim Mounten der Komponente
onMounted(async () => {
  await stopplanStore.fetchTracks(); // Lädt die verfügbaren Strecken
  stopplan.value.track = getSelectedTrack(); // Setzt die Strecke
  trainStations.value = stopplanTrainstations; // Initialisiert die Bahnhöfe
  tracks.value = stopplanStore.tracks;
  console.log(stopplanID)
  console.log(stopplanName)
  console.log(stopplanTrackID)
  console.log(stopplanTrainstations)

});

// Funktion zum Wechseln zum nächsten Schritt
function nextStep() {
  if (currentStep.value === 1) {
    loadStations(stopplan.value.track); // Lädt die Bahnhöfe basierend auf der Strecke
    currentStep.value = 2; // Wechselt zum zweiten Schritt
  }
}

// Funktion zum Wechseln zum vorherigen Schritt
function prevStep() {
  currentStep.value = 1;
}

// Funktion zum Laden der Bahnhöfe für die ausgewählte Strecke
// function loadStations(track) {
//   const stationMap = new Map(); // Map für einzigartige Bahnhöfe
//
//   track.sections.forEach((section) => {
//     // Fügt stations hinzu
//     if (section.start_station) {
//       stationMap.set(section.start_station.id, section.start_station);
//     }
//     if (section.end_station) {
//       stationMap.set(section.end_station.id, section.end_station);
//     }
//   });
//
//   trainStations.value = Array.from(stationMap.values()); // Setzt die Bahnhöfe
// }

// Funktion zum Laden der Bahnhöfe für die ausgewählte Strecke
async function loadStations(track) {
  const stationMap = new Map(); // Verwendet eine Map, um Duplikate zu vermeiden

  for (const section of track.sections) {
    // Startbahnhöfe abrufen
    if (section.startStationID && !stationMap.has(section.startStationID)) {
      const station = await stopplanStore.fetchTrainStationById(section.startStationID);
      if (station) {
        stationMap.set(section.startStationID, station);
      }
    }
    // Endbahnhöfe abrufen
    if (section.endStationID && !stationMap.has(section.endStationID)) {
      const station = await stopplanStore.fetchTrainStationById(section.endStationID);
      if (station) {
        stationMap.set(section.endStationID, station);
      }
    }
  }

  trainStations.value = Array.from(stationMap.values()); // Konvertiert die Map in ein Array
  console.log(trainStations.value)
}



// Funktion zum Aktualisieren des Halteplans
async function updateStopplan() {
  // Datenobjekt für die Aktualisierung
  const stopplanData = {
    name: stopplan.value.name, // Name des Halteplans
    trackID: stopplan.value.track.trackID, // ID der Strecke
    trainStations: stopplan.value.trainStations.map(station => ({ id: station.stationID })), // Liste der Bahnhof-IDs
  };

  await stopplanStore.editStopplan(stopplanData, stopplanID); // Aktualisiert den Halteplan im Store

  // Erfolgsmeldung anzeigen
  toast.add({
    severity: 'success',
    summary: 'Erfolg',
    detail: `Halteplan "${stopplanData.name}" wurde erfolgreich bearbeitet`,
    life: 3000,
  });

  emit('stopplan-created');
  stopplan.value = { name: '', track: null, trainStations: [] }; // Zurücksetzen des Formulars
  currentStep.value = 1; // Zurück zum ersten Schritt
}
</script>
