<template>
  <Stepper value="1" class="custom-stepper">
    <StepList style="gap: 10px; justify-content: space-between;">
      <Step value="1">Halteplan Details</Step>
      <Step value="2">Bahnhöfe</Step>
    </StepList>
  </Stepper>
  <div>
    <div v-if="currentStep === 1">
      <!-- Erster Schritt  -->
      <div class="flex flex-col">
        <label for="name" class="mb-1">Name des Halteplans</label>
        <InputText id="name" v-model="stopplan.name" placeholder="Text eingeben..." />
      </div>
      <br>
      <div class="flex flex-col">
        <label for="track" class="mb-1">Strecke</label>
        <Dropdown
            id="track"
            v-model="stopplan.track"
            :options="tracks"
            optionLabel="name"
            placeholder="Auswahl treffen..."
        />
      </div>
      <br>
      <ScotButton
          label="Weiter"
          icon="pi pi-arrow-right"
          variant="blue"
          :disabled="!stopplan.track"
          @click="nextStep"
      />
    </div>

    <div v-else-if="currentStep === 2">
      <!-- Zweiter Schritt -->
      <div class="flex flex-col">
        <label for="stations" class="mb-1">Bahnhöfe</label>
        <MultiSelect
            id="stations"
            v-model="stopplan.trainStations"
            :options="trainStations"
            optionLabel="name"
            placeholder="Bahnhöfe auswählen..."
        />
      </div>
      <br>
      <div class="flex" style="gap: 0.5rem;">
        <ScotButton
            label="Zurück"
            icon="pi pi-arrow-left"
            variant="gray"
            @click="prevStep"
        />
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


import {computed, onMounted, ref} from 'vue';
import {useStopplanStore} from '~/stores/stopplan.js';
import {useToast} from 'primevue/usetoast'

const stopplanStore = useStopplanStore();
const tracks = computed(() => stopplanStore.tracks);
const { stopplanID, stopplanName, stopplanTrackID, stopplanTrainstations } = defineProps({
  stopplanID: {
    type: Number,
    required: true
  },
  stopplanName: {
    type: String,
    required: true
  },
  stopplanTrackID: {
    type: Number,
    required: true
  },
  stopplanTrainstations: {
    type: Array,
    required: true
  }
});

function getSelectedTrack() {
  return tracks.value.find((track) => track.id === stopplanTrackID);
}
const toast = useToast()
  const emit = defineEmits(['stopplan-created']);


  const currentStep = ref(1); // Track den aktuellen Schritt
  const stopplan = ref({
    name: stopplanName,
    track: getSelectedTrack(),
    trainStations: stopplanTrainstations,
  });


  const trainStations = ref([]);

  onMounted(async () => {
    await stopplanStore.fetchTracks();
    stopplan.value.track = getSelectedTrack();
    trainStations.value = stopplanTrainstations;
  });

  // Schritt wechseln
  function nextStep() {
    if (currentStep.value === 1) {
      loadStations(stopplan.value.track);
      currentStep.value = 2;
    }
  }
  function prevStep() {
    currentStep.value = 1;
  }


  function loadStations(track) {
    const stationMap = new Map();


    track.sections.forEach((section) => {

      if (section.start_station) {
        stationMap.set(section.start_station.id, section.start_station);
      }


      if (section.end_station) {
        stationMap.set(section.end_station.id, section.end_station);
      }
    });


    trainStations.value = Array.from(stationMap.values());
  }

  //defineProps(['close']);



  async function updateStopplan() {

    const stopplanData = {
      name: stopplan.value.name,
      trackID: stopplan.value.track.id,
      trainStations: stopplan.value.trainStations.map(station => ({ id: station.id })),
    };


    await stopplanStore.editStopplan(stopplanData, stopplanID);

    toast.add({
      severity: 'success',
      summary: 'Erfolg',
      detail: `Halteplan "${stopplanData.name}" wurde erfolgreich bearbeitet`,
      life: 3000
    });

    emit('stopplan-created');

    stopplan.value = { name: '', track: null, trainStations: [] };
    currentStep.value = 1;
  }

</script>