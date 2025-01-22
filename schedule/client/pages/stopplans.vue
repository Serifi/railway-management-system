<template>
  <!-- Liste der Stoppläne anzeigen -->
  <List
    :items="stopplans"
    :getKey="getStopplanKey"
    :rowsPerPage="5"
    @create="toggleCreateDialog"
    @edit="toggleEditDialog"
    @delete="deleteStopplan"
  >
    <!-- Titel-Slot für jeden Stopplan -->
    <template #title="{ item }">
      {{ `Halteplan ${item.name}` }}         <!-- Zeigt den Namen des Halteplans -->
      <!-- Tag anzeigen, wenn der Stopplan aktive Fahrtdurchführungen hat -->
      <span v-if="item.rideExecutions && item.rideExecutions.length > 0">
        <Tag severity="success" value="Aktiv"></Tag>
      </span>
    </template>

    <!-- Beschreibung-Slot für jeden Stopplan -->
    <template #description="{ item }">
      Mindestpreis zwischen 2 Haltestellen: {{ item.minPrice }}€<br/>

      <!-- Liste der Stationen des Stopplans anzeigen -->
      Stationen:
      <span v-for="(station, index) in item.trainStations" :key="station.id">
        {{ station.name }}
        <span v-if="index < item.trainStations.length - 1">, </span> <!-- Komma zwischen den Stationen -->
      </span>
    </template>
  </List>

  <!-- Dialog zum Erstellen eines neuen Stopplans -->
  <Dialog v-model:visible="createDialogVisible" header="Halteplan erstellen" class="w-2/3">
    <!-- Komponente zum Erstellen eines Stopplans -->
    <ScotStopplan @stopplan-created="toggleCreateDialog" />
    <template #footer>
      <!-- Button zum Schließen des Dialogs -->
      <ScotButton label="Abbrechen" icon="pi pi-times" variant="gray" @click="toggleCreateDialog" />
    </template>
  </Dialog>

  <!-- Dialog zum Bearbeiten eines bestehenden Stopplans -->
  <Dialog v-model:visible="editDialogVisible" header="Halteplan bearbeiten" class="w-2/3">
    <!-- Komponente zum Bearbeiten eines Stopplans -->
    <ScotEditStopplan
      @stopplan-created="toggleEditDialog"
      :stopplanID="stopplan?.id"
      :stopplanName="stopplan?.name"
      :stopplanTrackID="stopplan?.trackID"
      :stopplanTrainstations="stopplan?.trainStations"
    />
    <template #footer>
      <!-- Button zum Schließen des Dialogs -->
      <ScotButton label="Abbrechen" icon="pi pi-times" variant="gray" @click="toggleEditDialog" />
    </template>
  </Dialog>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useToast } from 'primevue/usetoast';
import { useStopplanStore } from '~/stores/stopplan.js';
import List from '~/components/ScotList.vue';
import ScotStopplan from '~/components/ScotStopplan.vue';

// Toast für Benachrichtigungen
const toast = useToast();

// Sichtbarkeitsstatus für die Dialoge
const createDialogVisible = ref(false); // Erstellen-Dialog
const editDialogVisible = ref(false);  // Bearbeiten-Dialog

// Zugriff auf den Stopplan-Store und seine Daten
const stopplanStore = useStopplanStore();
const stopplans = stopplanStore.stopplans; // Liste der Stoppläne
const stopplan = ref(null); // Aktuell ausgewählter Stopplan

// Wird ausgeführt, wenn die Komponente gemountet wird
onMounted(() => {
  stopplanStore.fetchStopplans(); // Stoppläne aus dem Store laden
});

// Funktion zum Löschen eines Stopplans
function deleteStopplan(currentStopplan) {
  // Warnung, wenn der Stopplan mit Fahrtdurchführungen verknüpft ist
  if (currentStopplan.rideExecutions.length > 0) {
    toast.add({
      severity: 'warn',
      summary: 'Löschen nicht möglich',
      detail: 'Halteplan bereits in Verwendung',
      life: 3000
    });
  } else {
    // Stopplan aus dem Store löschen und Erfolgsmeldung anzeigen
    stopplanStore.deleteStopplan(currentStopplan.id);
    toast.add({
      severity: 'success',
      summary: 'Erfolgreich',
      detail: 'Aktion wurde erfolgreich abgeschlossen',
      life: 3000
    });
  }
}

// Funktion, um den eindeutigen Schlüssel eines Stopplans abzurufen
function getStopplanKey(stopplan) {
  return stopplan.id;
}

// Funktion zum Umschalten des Erstellen-Dialogs
function toggleCreateDialog() {
  createDialogVisible.value = !createDialogVisible.value;
}

// Funktion zum Umschalten des Bearbeiten-Dialogs
function toggleEditDialog(currentStopplan) {
  // Warnung, wenn der Stopplan mit Fahrtdurchführungen verknüpft ist
  if (currentStopplan.rideExecutions.length > 0) {
    toast.add({
      severity: 'warn',
      summary: 'Bearbeiten nicht möglich',
      detail: 'Halteplan bereits in Verwendung',
      life: 3000
    });
  } else {
    // Setze den aktuellen Stopplan und öffne den Dialog
    stopplan.value = currentStopplan;
    editDialogVisible.value = !editDialogVisible.value;
  }
}
</script>

