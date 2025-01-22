<template>
  <!-- Stepper-Komponente zur Übersicht der Schritte -->
  <Stepper value="1" class="custom-stepper">
    <StepList style="gap: 10px; justify-content: space-between;">
      <Step value="1">Datum</Step>
      <Step value="2">Zeit</Step>
      <Step value="3">Daten</Step>
      <Step value="4">Mitarbeiter</Step>
    </StepList>

    <!-- Panels, die die Inhalte der einzelnen Schritte enthalten -->
    <StepPanels>
      <!-- Schritt 1: Auswahl von Datum und Intervall -->
      <StepPanel v-slot="{ activateCallback }" value="1">
        <div v-if="currentStep === 1">
          <div class="flex flex-col">
            <!-- Umschalter für einmaliges Datum -->
            <label class="font-semibold block mb-2 mt-2" for="datumIsEinmalig">Einmalig</label>
            <ToggleSwitch id="datumIsEinmalig" v-model="datumIsEinmalig" />
            <br>
            <!-- Auswahl für Intervalle -->
            <label class="font-semibold block mb-2 mt-2" for="intervall">Intervall</label>
            <SelectButton
              id="intervall"
              v-model="rideExecution.selectedDays"
              :options="options"
              optionLabel="name"
              multiple
              aria-labelledby="multiple"
              :disabled="datumIsEinmalig"
            />
          </div>
          <br>
          <!-- Eingabe von Start- und Enddatum -->
          <div class="flex flex-row gap-8 mt-2">
            <div class="flex flex-col">
              <label class="font-semibold block mb-2 mt-2" for="startdatum">Startdatum</label>
              <DatePicker
                id="startdatum"
                v-model="rideExecution.startdatum"
                showIcon
                fluid
                iconDisplay="input"
              />
            </div>
            <div class="flex flex-col">
              <label class="font-semibold block mb-2 mt-2" for="enddatum">Enddatum</label>
              <DatePicker
                id="enddatum"
                v-model="rideExecution.enddatum"
                showIcon
                fluid
                iconDisplay="input"
                :disabled="datumIsEinmalig"
              />
            </div>
          </div>
          <br>
          <!-- Navigation: Weiter-Button -->
          <div class="flex flex-row gap-2">
            <ScotButton
              label="Weiter"
              icon="pi pi-arrow-right"
              variant="blue"
              :disabled="datumIsEinmalig === false ? (!rideExecution.startdatum || !rideExecution.enddatum || rideExecution.selectedDays.length === 0) : (!rideExecution.startdatum && datumIsEinmalig === false)"
              @click="nextStep(); activateCallback('2')"
            />
          </div>
        </div>
      </StepPanel>

      <!-- Schritt 2: Auswahl von Zeit -->
      <StepPanel v-slot="{ activateCallback }" value="2">
        <div v-if="currentStep === 2">
          <div class="flex flex-row gap-8">
            <!-- Umschalter für einmalige Zeit -->
            <div class="flex flex-col">
              <label class="font-semibold block mb-2 mt-2" for="zeitIsEinmalig">Einmalig</label>
              <ToggleSwitch id="zeitIsEinmalig" v-model="zeitIsEinmalig" />
            </div>
          </div>

          <!-- Eingabe von Startzeit, Endzeit und Zeitintervall -->
          <div class="flex flex-row gap-8 mt-2">
            <div class="flex flex-col">
              <label class="font-semibold block my-2" for="startzeit">Startzeit</label>
              <DatePicker
                id="startzeit"
                v-model="rideExecution.startzeit"
                showIcon
                fluid
                iconDisplay="input"
                timeOnly
              >
                <template #inputicon="slotProps">
                  <i class="pi pi-clock" @click="slotProps.clickCallback" />
                </template>
              </DatePicker>
            </div>

            <div class="flex flex-col">
              <label class="font-semibold block my-2" for="endzeit">Endzeit</label>
              <DatePicker
                id="endzeit"
                v-model="rideExecution.endzeit"
                showIcon
                fluid
                iconDisplay="input"
                timeOnly
                :disabled="zeitIsEinmalig"
              >
                <template #inputicon="slotProps">
                  <i class="pi pi-clock" @click="slotProps.clickCallback" />
                </template>
              </DatePicker>
            </div>

            <div class="flex flex-col">
              <label class="font-semibold block my-2" for="zeitintervall">Intervall in Minuten</label>
              <InputNumber
                id="zeitintervall"
                v-model="rideExecution.zeitintervall"
                inputId="minmax-buttons"
                mode="decimal"
                :step="5"
                showButtons
                :min="0"
                :max="2880"
                fluid
                :disabled="zeitIsEinmalig"
              />
            </div>
          </div>
          <br>
          <!-- Navigation: Zurück- und Weiter-Buttons -->
          <div class="flex flex-row gap-2">
            <ScotButton
              label="Zurück"
              icon="pi pi-arrow-left"
              variant="gray"
              @click="prevStep(); activateCallback('1')"
            />
            <ScotButton
              label="Weiter"
              icon="pi pi-arrow-right"
              variant="blue"
              :disabled="zeitIsEinmalig === false ? (!rideExecution.startzeit || !rideExecution.endzeit || !rideExecution.zeitintervall) : (!rideExecution.startzeit && zeitIsEinmalig === false)"
              @click="getTrains(); nextStep(); activateCallback('3')"
            />
          </div>
        </div>
      </StepPanel>

      <!-- Schritt 3: Auswahl von Stopplan und Zug -->
      <StepPanel v-slot="{ activateCallback }" value="3">
        <div v-if="currentStep === 3">
          <div class="flex flex-col">
            <label for="stopplan" class="font-semibold block mb-2 mt-2">Halteplan</label>
            <Dropdown
              id="stopplan"
              v-model="rideExecution.stopplan"
              :options="stopplans"
              optionLabel="name"
              placeholder="Auswahl treffen..."
            />
            <br>
            <label for="train" class="font-semibold block mb-2 mt-2">Zug</label>
            <Dropdown
              id="train"
              v-model="rideExecution.train"
              :options="trains"
              optionLabel="name"
              placeholder="Auswahl treffen..."
            />
          </div>
          <br>
          <!-- Navigation: Zurück- und Weiter-Buttons -->
          <div class="flex" style="gap: 0.5rem;">
            <ScotButton
              label="Zurück"
              icon="pi pi-arrow-left"
              variant="gray"
              @click="prevStep(); activateCallback('2')"
            />
            <ScotButton
              label="Weiter"
              icon="pi pi-arrow-right"
              variant="blue"
              :disabled="!rideExecution.stopplan || !rideExecution.train"
              @click="nextStep(); getStopplanByID(); activateCallback('4')"
            />
          </div>
        </div>
      </StepPanel>

      <!-- Schritt 4: Auswahl von Mitarbeitern -->
      <StepPanel v-slot="{ activateCallback }" value="4">
        <div v-if="currentStep === 4">
          <div class="flex flex-col">
            <label for="employees" class="font-semibold block mb-2 mt-2">Mitarbeiter</label>
            <MultiSelect
              id="employees"
              v-model="rideExecution.employees"
              :options="employees"
              optionLabel="lastName"
              placeholder="Mitarbeiter hinzufügen..."
            >
              <template #option="slotProps">
                <div>
                  <span>{{ slotProps.option.firstName }} {{ slotProps.option.lastName }}</span>
                </div>
              </template>
            </MultiSelect>
            <br>
            <label for="minmaxfraction" class="font-semibold block mb-2 mt-2">Preis für Stoßzeiten</label>
            <InputNumber
              v-model="rideExecution.price"
              inputId="price"
              :minFractionDigits="1"
              :maxFractionDigits="2"
              :min="stopplan2.minPrice"
              fluid
              mode="currency"
              currency="EUR"
            />
          </div>
          <br>
          <!-- Navigation: Zurück- und Erstellen-Buttons -->
          <div class="flex" style="gap: 0.5rem;">
            <ScotButton
              label="Zurück"
              icon="pi pi-arrow-left"
              variant="gray"
              @click="prevStep(); activateCallback('3')"
            />
            <ScotButton
              label="Erstellen"
              icon="pi pi-plus"
              variant="blue"
              :disabled="rideExecution.employees.length === 0"
              @click="createRideExecution"
            />
          </div>
        </div>
      </StepPanel>
    </StepPanels>
  </Stepper>
</template>


<script setup>
// Optionen für die Auswahl der Wochentage
const options = ref([
  { name: 'Mo', value: 1 },
  { name: 'Di', value: 2 },
  { name: 'Mi', value: 3 },
  { name: 'Do', value: 4 },
  { name: 'Fr', value: 5 },
  { name: 'Sa', value: 6 },
  { name: 'So', value: 7 }
]);

// State-Variablen für einmalige Auswahl
const datumIsEinmalig = ref(false); // Ob das Datum einmalig ist
const zeitIsEinmalig = ref(false); // Ob die Zeit einmalig ist


const toast = useToast(); // Toast für Benachrichtigungen
const emit = defineEmits(['stopplanCreated']);
// Stores für Daten
const rideExecutionStore = useRideExecutionStore(); // Store für Fahrtdurchführungen
const stopplanStore = useStopplanStore(); // Store für Stoppläne

// Aktueller Schritt im Stepper
const currentStep = ref(1);

// Initiales Datenobjekt für die Fahrtdurchführung
const rideExecution = ref({
  stopplan: null,
  train: null,
  employees: [],
  startdatum: '',
  enddatum: '',
  startzeit: '',
  endzeit: '',
  selectedDays: [],
  zeitintervall: '',
  price: 0
});

// Validierungsstatus für Datumsfelder
const dateError = ref(false);

// Computed-Properties, um auf Daten aus den Stores zuzugreifen
const stopplan2 = computed(() => stopplanStore.stopplan); // Aktueller Stopplan
const stopplans = computed(() => stopplanStore.stopplans); // Liste aller Stoppläne
const trains = computed(() => rideExecutionStore.trains); // Verfügbare Züge
const employees = computed(() => rideExecutionStore.employees); // Verfügbare Mitarbeiter

// Lifecycle-Hook: Daten beim Laden der Komponente abrufen
onMounted(() => {
  stopplanStore.fetchStopplans(); // Stoppläne laden
  rideExecutionStore.fetchEmployees(); // Mitarbeiter laden
});

// Funktion, um zum nächsten Schritt zu wechseln
function nextStep() {
  if (currentStep.value === 1) {
    validateDates(); // Validierung der Datumsfelder
    if (!dateError.value) {
      currentStep.value++; // Schritt erhöhen, wenn keine Fehler vorliegen
    }
  } else if (currentStep.value === 2) {
    if ( //Überprüfung ob Enddatum später ist als Startdatum
      new Date(rideExecution.value.endzeit).getTime() <=
        new Date(rideExecution.value.startzeit).getTime() &&
      !zeitIsEinmalig.value
    ) {
      toast.add({  //Fehlermeldung
        severity: 'error',
        summary: 'Fehler',
        detail: 'Endzeit muss nach Startzeit sein!',
        life: 3000
      });
    } else {
      currentStep.value++;
    }
  } else {
    currentStep.value++;
  }
}

// Funktion, um zum vorherigen Schritt zu wechseln
function prevStep() {
  currentStep.value--;
}

// Funktion, um Züge basierend auf der eingegebenen Datum und Zeit zu laden
async function getTrains() {
  const dateAndTimeData = {
    startDate: rideExecution.value.startdatum,
    startTime: rideExecution.value.startzeit,
    endDate: rideExecution.value.enddatum,
    endTime: rideExecution.value.endzeit,
    selectedDays: rideExecution.value.selectedDays,
    zeitIntervall: rideExecution.value.zeitintervall,
    datumIsEinmalig: datumIsEinmalig.value,
    zeitIsEinmalig: zeitIsEinmalig.value
  };
  await rideExecutionStore.fetchTrains(dateAndTimeData);
}

// Funktion, um einen spezifischen Stopplan anhand der ID zu laden
function getStopplanByID() {
  stopplanStore.fetchStopplanByID(rideExecution.value.stopplan.id);
}

// Validierung der eingegebenen Datumswerte
const validateDates = () => {
  if (
    new Date(rideExecution.value.enddatum) <=
      new Date(rideExecution.value.startdatum) &&
    !datumIsEinmalig.value
  ) {
    dateError.value = true;
    toast.add({
      severity: 'error',
      summary: 'Fehler',
      detail: 'Enddatum muss nach Startdatum sein!',
      life: 3000
    });
  } else {
    dateError.value = false;
  }
};

// Funktion, um die Fahrtdurchführung zu erstellen
async function createRideExecution() {
  const rideExecutionData = {
    stopplanID: rideExecution.value.stopplan.id,
    trainID: rideExecution.value.train.id,
    employeeSSN_list: rideExecution.value.employees.map(employee => ({
      ssn: employee.ssn
    })),
    startDate: rideExecution.value.startdatum,
    startTime: rideExecution.value.startzeit,
    endDate: rideExecution.value.enddatum,
    endTime: rideExecution.value.endzeit,
    selectedDays: rideExecution.value.selectedDays,
    zeitIntervall: rideExecution.value.zeitintervall,
    datumIsEinmalig: datumIsEinmalig.value,
    zeitIsEinmalig: zeitIsEinmalig.value,
    price: rideExecution.value.price
  };

  await rideExecutionStore.createRideExecution(rideExecutionData);

  toast.add({
    severity: 'success',
    summary: 'Erfolg',
    detail: 'Fahrtdurchführung wurde erfolgreich erstellt',
    life: 3000
  });

  emit('stopplanCreated'); // Event senden, um den Erfolg zu signalisieren

  // Daten zurücksetzen
  rideExecution.value = {
    stopplan: null,
    train: null,
    employees: [],
    startdatum: '',
    enddatum: '',
    startzeit: '',
    endzeit: '',
    selectedDays: [],
    zeitintervall: ''
  };
  currentStep.value = 1; // Zurück zum ersten Schritt
}

// Externe Props definieren
defineProps(['close']);
</script>



.

