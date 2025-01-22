<template>
  <!-- Oberer Bereich mit Suchfeld, Buttons und Rollen-spezifischen Elementen -->
  <div class="flex flex-row items-center justify-between mb-4">
    <!-- Suchfeld für die Suche nach Fahrtdurchführungen -->
    <div class="flex-none">
      <IconField>
        <InputIcon class="pi pi-search" />
        <InputText v-model="searchQuery" placeholder="Suchen..." />
      </IconField>
    </div>

    <!-- Button zum Erstellen einer neuen Fahrtdurchführung, nur für Admins sichtbar -->
    <div v-if="user.role === 'Admin'" class="ml-4">
      <ScotButton label="Erstellen" icon="pi pi-plus" variant="blue" @click="toggleCreateDialog" />
    </div>

    <!-- Auswahlfeld für Optionen, nur für Mitarbeiter sichtbar -->
    <div v-if="user.role === 'Employee'" class="absolute left-1/2 transform -translate-x-1/2">
      <SelectButton v-model="value" :options="options" />
    </div>
  </div>

  <!-- Anzeige der Fahrtdurchführungen basierend auf der ausgewählten Option -->
  <div v-if="value==='Alle'">
    <div v-for="stopplan in stopplans" :key="stopplan.id" class="border-b">
      <!-- Überschrift für jeden Halteplan -->
      <div class="text-2xl font-bold ml-3 mt-5">Fahrplan für Halteplan {{ stopplan.name }}</div>

      <!-- Nachricht bei fehlenden Fahrtdurchführungen -->
      <div v-if="stopplan.rideExecutions && stopplan.rideExecutions.length < 1">
        <div class="card flex flex-wrap gap-4 justify-start pl-5 py-6">
          <Message size="small" severity="warn">Keine Fahrtdurchführungen verfügbar!</Message>
        </div>
      </div>

      <!-- Liste der Fahrtdurchführungen -->
      <div v-for="rideExecution in stopplan.rideExecutions" :key="rideExecution.id"
           class="flex p-6 rounded transition-colors duration-200"
           @mouseover="hover = rideExecution.id" @mouseleave="hover = null">
        <!-- Informationen zur Fahrtdurchführung -->
        <div class="flex flex-col space-y-4 flex-grow">
          <div class="text-lg font-bold">
            Fahrtdurchführung<i class="fa-solid fa-calendar-days ml-3"></i> {{ rideExecution.date }}
            <i class="fa-regular fa-clock ml-3"></i> {{ rideExecution.time }}
            <!-- Anzeige von Verspätungen -->
            <span v-if="!rideExecution.isCanceled && rideExecution.delay > 0" style="color: #db3939; margin-left: 0.4rem;" >+{{rideExecution.delay}}</span>
          </div>
          <div class="text-sm text-gray-400 whitespace-pre-line">
            <i class="fa-solid fa-train mr-1"></i>Zug: {{ rideExecution.train.name }}<br/>
            <!-- Nachricht bei abgesagten Fahrten -->
            <div v-if="rideExecution.isCanceled">
              <CustomMessage />
            </div>
          </div>
        </div>

        <!-- Admin-spezifische Bearbeitungs- und Löschoptionen -->
        <div v-if="user.role==='Admin'">
          <div v-if="hover === rideExecution.id" class="flex flex-col justify-center space-y-2">
            <ScotButton label="Bearbeiten" icon="pi pi-pencil" variant="green" @click="toggleEditDialog(rideExecution.id, rideExecution.delay, rideExecution.isCanceled)" />
            <ScotButton label="Löschen" icon="pi pi-trash" variant="red" @click="confirmDeletion($event, rideExecution)" />
          </div>
        </div>
      </div>
      <!-- Popup-Bestätigung für Löschaktionen -->
      <ConfirmPopup/>
    </div>
  </div>

  <!-- Anzeige der Fahrtdurchführungen, die dem Benutzer zugeordnet sind -->
  <div v-if="value==='Meine'">
    <List :items="user.rideExecutions" :getKey="getRideExecutionKey" :rowsPerPage="5" :toggleValue="value">
      <!-- Titel für die Listelemente -->
      <template #title="{ item }">
        Fahrtdurchführung<i class="fa-solid fa-calendar-days ml-3"></i> {{ item.date }}
        <i class="fa-regular fa-clock ml-3"></i> {{ item.time }}
        <span v-if="!item.isCanceled && item.delay > 0" style="color: #db3939; margin-left: 0.4rem;" >+{{item.delay}}</span>
      </template>
      <!-- Beschreibung für die Listelemente -->
      <template #description="{ item }">
        {{`Halteplan: ${item.stopplan.name}`}} <br>
        {{`Zug: ${item.train.name}`}}
        <div v-if="item.isCanceled">
          <CustomMessage />
        </div>
      </template>
    </List>
  </div>

  <!-- Dialog zum Erstellen einer neuen Fahrtdurchführung -->
  <Dialog v-model:visible="createDialogVisible" header="Fahrtdurchführung erstellen" class="w-2/3">
    <ScotRideExecution @stopplan-created="toggleCreateDialog" />
    <template #footer>
      <ScotButton label="Abbrechen" icon="pi pi-times" variant="gray" @click="toggleCreateDialog"/>
    </template>
  </Dialog>

  <!-- Dialog zum Bearbeiten einer bestehenden Fahrtdurchführung -->
  <Dialog v-model:visible="editDialogVisible" header="Fahrtdurchführung bearbeiten" class="w-2/3">
    <ScotEditRideExecution
        @stopplan-created="toggleEditDialog"
        :rideExecutionID="selectedRideExecution"
        :rideExecutionDelay="delay"
        :rideExecutionIsCanceled="isCanceled"
    />
    <template #footer>
      <ScotButton label="Abbrechen" icon="pi pi-times" variant="gray" @click="toggleEditDialog"/>
    </template>
  </Dialog>
</template>




<script setup>
import {ref, computed} from 'vue'
import { useToast } from 'primevue/usetoast'
import List from '~/components/ScotList.vue'
import {useStopplanStore} from "~/stores/stopplan.js";
import {useRideExecutionStore} from "~/stores/rideExecution.js";
import ScotRideExecution from "~/components/ScotRideExecution.vue";
import { useConfirm } from "primevue/useconfirm"
import {useUserStore} from "~/stores/user.js";
import CustomMessage from "~/components/CustomMessage.vue";
import {FontAwesomeIcon} from "@fortawesome/vue-fontawesome";


// Reaktiver Zustand für die Auswahloptionen "Alle" oder "Meine"
const value = ref('Alle');
const options = ref(['Alle', 'Meine']);

// Zugriff auf den User-Store, um Benutzerdaten zu erhalten
const userStore = useUserStore();
// Computed-Wert, der den aktuellen Benutzer aus dem Store zurückgibt
const user = computed(() => userStore.user);

// Toast-Benachrichtigungen für Benutzeraktionen
const toast = useToast();

// Zustände für die Sichtbarkeit der Dialoge (Erstellen und Bearbeiten)
const createDialogVisible = ref(false);
const editDialogVisible = ref(false);

// Zugriff auf den RideExecution- und Stopplan-Store
const rideExecutionStore = useRideExecutionStore();
const stopplanStore = useStopplanStore();
// Zugriff auf die Liste der Stoppläne aus dem Store
const stopplans = stopplanStore.stopplans;

// Zustände für die aktuell ausgewählte Fahrtdurchführung
const selectedRideExecution = ref(null);
const delay = ref(0); // Verspätung
const isCanceled = ref(false); // Storniert-Status

// Wird ausgeführt, sobald die Komponente gemountet wird
onMounted(() => {
  stopplanStore.fetchStopplans(); // Stoppläne abrufen
  userStore.fetchEmployees(); // Mitarbeiterdaten abrufen
});

// Hilfsfunktion, um den Schlüssel einer Fahrtdurchführung zu erhalten
function getRideExecutionKey(rideExecution) {
  return rideExecution.id;
}

// Funktion zum Umschalten des Erstellen-Dialogs
function toggleCreateDialog(rideExecutionID) {
  createDialogVisible.value = !createDialogVisible.value;
}

// Funktion zum Umschalten des Bearbeiten-Dialogs
function toggleEditDialog(rideExecutionID, rideExecutionDelay, rideExecutionIsCanceled) {
  selectedRideExecution.value = rideExecutionID; // Ausgewählte Fahrtdurchführung
  delay.value = rideExecutionDelay; // Verspätung setzen
  isCanceled.value = rideExecutionIsCanceled; // Storniert-Status setzen
  editDialogVisible.value = !editDialogVisible.value;
}

// Funktion zum Löschen einer Fahrtdurchführung
function deleteRideExecution(currentRideExecution) {
  console.log('Deleting Ride Execution:', currentRideExecution.id); // Debug-Log
  rideExecutionStore.deleteRideExecution(currentRideExecution.id); // Löschen aus dem Store
  // Erfolgsmeldung anzeigen
  toast.add({ severity: 'success', summary: 'Erfolgreich', detail: 'Aktion wurde erfolgreich abgeschlossen', life: 3000 });
}

// Zustand für das Hovering über einer Fahrtdurchführung
const hover = ref(null);

// Definierte Emit-Ereignisse für die Komponente
const emits = defineEmits(['create', 'edit', 'delete']);

// Definierte Eigenschaften (Props) für die Komponente
const props = defineProps({
  items: {
    type: Array,
    required: true,
  },
  rowsPerPage: {
    type: Number,
    default: 10,
  },
  getKey: {
    type: Function,
    required: true,
  },
});

// Suchbegriff für die Filterung
const searchQuery = ref('');
// Watcher, der den aktuellen Seitenindex zurücksetzt, wenn sich der Suchbegriff ändert
watch(searchQuery, () => (currentPage.value = 0));

// Berechnung der gefilterten Elemente basierend auf dem Suchbegriff
const filteredItems = computed(() => {
  if (!searchQuery.value) return props.items;
  return props.items.filter(item =>
    Object.values(item).some(val =>
      String(val).toLowerCase().includes(searchQuery.value.toLowerCase())
    )
  );
});

// Zustand für die aktuelle Seite
const currentPage = ref(0);
// Handler für Seitenwechsel
const onPageChange = (event) => (currentPage.value = event.page);

// Berechnung des ersten Elements auf der aktuellen Seite
const firstRecord = computed(() => currentPage.value * props.rowsPerPage);
// Berechnung der Elemente, die auf der aktuellen Seite angezeigt werden sollen
const paginatedItems = computed(() => {
  const start = firstRecord.value;
  const end = start + props.rowsPerPage;
  return filteredItems.value.slice(start, end);
});

// Emit-Ereignisse auslösen
const emitCreate = () => emits('create');
const emitEdit = (item) => emits('edit', item);

// Bestätigungsdialog für das Löschen einer Fahrtdurchführung
const confirm = useConfirm();
const confirmDeletion = (event, item) => {
  console.log('Confirm Deletion Triggered', item); // Debug-Log
  confirm.require({
    target: event.currentTarget, // Ziel-Element des Ereignisses
    message: 'Sicher, dass Sie dieses Element löschen möchten?', // Nachricht
    icon: 'pi pi-info-circle', // Symbol
    rejectProps: {
      label: 'Abbrechen',
      severity: 'secondary',
      outlined: true,
    },
    acceptProps: {
      label: 'Löschen',
      severity: 'danger',
    },
    accept: () => {
      console.log('Item accepted for deletion:', item); // Debug-Log
      deleteRideExecution(item); // Fahrtdurchführung löschen
    },
  });
};



</script>
<style>

.custom-message {
  display: flex;
  align-items: center;
  margin-top: 0.5rem;
  padding: 0.25rem 0.5rem;
  font-size: 0.75rem;
  color: #dc2625;
  background-color: #fef3f3;
  border-radius: 4px;
  border: solid 1px #fecaca;
  box-shadow: 0px 2px 4px rgba(0, 0, 0, 0.1);
  line-height: 1.2;
  max-width: fit-content;
}


.p-confirm-popup-accept,
.p-confirm-popup-reject {
  padding: 4px;
  margin: 4px;
}

.p-confirm-popup-accept{
  background-color: #FF9999 !important;
}
</style>