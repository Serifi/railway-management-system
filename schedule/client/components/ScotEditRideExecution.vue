<template>
  <div>
    <!-- Formular zur Bearbeitung einer Fahrtdurchführung -->

    <div>
      <div class="flex flex-col">
        <!-- Eingabefeld für die Verspätung in Minuten -->
        <label for="name" class="mb-1">Verspätung in min</label>
        <InputText
            id="delay"
            v-model="rideExecution.delay"
            placeholder="Verspätung eingeben..."
        />
      </div>
      <br>
      <div class="flex flex-col mb-4">
        <!-- Auswahlfeld für den Status "Ausfall" -->
        <label for="ausfall" class="mb-1">Ausfall</label>
        <SelectButton id="ausfall" v-model="optionsValue" :options="options" />
        <!-- Bindet die Auswahl an `optionsValue` und stellt Optionen zur Verfügung -->
      </div>
    </div>

    <div class="mt-7">
      <!-- Button, um die Änderungen zu speichern -->
      <ScotButton
          label="Bearbeiten"
          icon="pi pi-pencil"
          variant="blue"
          @click="editRideExecution"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRideExecutionStore } from '~/stores/rideExecution.js';
import { useToast } from 'primevue/usetoast';

const toast = useToast();
const emit = defineEmits(['rideExecution-created']);
const rideExecutionStore = useRideExecutionStore();

// Definiert die erwarteten Eingabe-Props
const props = defineProps({
  rideExecutionID: { type: Number, required: true }, // ID der Fahrtdurchführung
  rideExecutionDelay: { type: Number, required: true }, // Verspätung in Minuten
  rideExecutionIsCanceled: { type: Boolean, required: true }, // Status: Ausfall
});

// Initialisiert den Status der Ausfall-Optionen (Ja oder Nein)
const optionsValue = ref(props.rideExecutionIsCanceled ? 'Ja' : 'Nein');
const options = ref(['Nein', 'Ja']); // Mögliche Optionen

// Initialisiert das lokale Objekt für die Fahrtdurchführung
const rideExecution = ref({
  delay: props.rideExecutionIsCanceled ? 0 : props.rideExecutionDelay, // Setzt Verspätung basierend auf dem Ausfallstatus
});

// Wird beim Mounten der Komponente aufgerufen
onMounted(() => {
  console.log(props.rideExecutionID); // Debug-Ausgabe der Fahrtdurchführungs-ID
});

// Funktion zur Bearbeitung der Fahrtdurchführung
async function editRideExecution() {
  // Erstellt ein Datenobjekt mit den aktuellen Eingaben
  const rideExecutionData = {
    delay: rideExecution.value.delay, // Verspätung
    isCanceled: optionsValue.value, // Ausfallstatus
  };

  console.log(rideExecutionData); // Debug-Ausgabe der Daten

  // Ruft die Bearbeitungsfunktion im Store auf und übergibt die Daten
  await rideExecutionStore.editRideExecution(rideExecutionData, props.rideExecutionID);

  // Zeigt eine Erfolgsmeldung
  toast.add({
    severity: 'success', // Typ der Meldung
    summary: 'Erfolg', // Überschrift der Meldung
    detail: "Fahrtdurchführung wurde erfolgreich bearbeitet", // Details
    life: 3000, // Anzeigezeit in Millisekunden
  });

  emit('stopplanCreated');
}
</script>
