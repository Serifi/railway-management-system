<template>
  <Stepper value="1" class="custom-stepper">
    <StepList style="gap: 10px; justify-content: space-between;">
      <Step value="1">Datum</Step>
      <Step value="2">Zeit</Step>
      <Step value="3">Daten</Step>
      <Step value="4">Mitarbeiter</Step>
    </StepList>
  </Stepper>
  <div>

    <div v-if="currentStep === 1">
      <div class="flex flex-col">
        <label class="font-semibold block mb-2 mt-2" for="datumIsEinmalig" >Einmalig</label>
        <ToggleSwitch id="datumIsEinmalig" v-model="datumIsEinmalig"/>
        <br>
        <label class="font-semibold block mb-2 mt-2" for="intervall">Intervall</label>
        <SelectButton
            id="intervall"
            v-model="rideExecution.selectedDays"
            :options="options"
            optionLabel="name"
            multiple aria-labelledby="multiple"
            :disabled="datumIsEinmalig"
        />
      </div>
      <br>
    <div class="flex flex-row gap-8 mt-2">
      <div class="flex flex-col">
        <label class="font-semibold block mb-2 mt-2" for="startdatum">Startdatum</label>
        <DatePicker id="startdatum" v-model="rideExecution.startdatum" showIcon fluid iconDisplay="input" />
      </div>
      <div class="flex flex-col">
        <label class="font-semibold block mb-2 mt-2" for="enddatum">Enddatum</label>
        <DatePicker
            id="enddatum"
            v-model="rideExecution.enddatum"
            showIcon fluid iconDisplay="input"
            :disabled="datumIsEinmalig"
        />
      </div>
    </div>
      <br>
      <div class="flex flex-row gap-2">
        <ScotButton
            label="Weiter"
            icon="pi pi-arrow-right"
            variant="blue"
            :disabled="datumIsEinmalig===false ? (!rideExecution.startdatum || !rideExecution.enddatum || rideExecution.selectedDays.length===0) : (!rideExecution.startdatum && datumIsEinmalig===false)"
            @click="nextStep"
        />
      </div>
    </div>


    <div v-if="currentStep === 2">
    <div class="flex flex-row gap-8">
      <div class="flex flex-col">
        <label class="font-semibold block mb-2 mt-2" for="zeitIsEinmalig" >Einmalig</label>
        <ToggleSwitch id="zeitIsEinmalig" v-model="zeitIsEinmalig" />
      </div>


    </div>

      <div class="flex flex-row gap-8 mt-2">
        <div class="flex flex-col">
          <label class="font-semibold block my-2" for="startzeit">Startzeit</label>
          <DatePicker id="startzeit" v-model="rideExecution.startzeit" showIcon fluid iconDisplay="input" timeOnly>
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
              showIcon fluid iconDisplay="input" timeOnly
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
              :max="2880" fluid
              :disabled="zeitIsEinmalig"
          />
        </div>
      </div>
      <br>
      <div class="flex flex-row gap-2">
        <ScotButton
            label="Zurück"
            icon="pi pi-arrow-left"
            variant="gray"
            @click="prevStep"
        />
        <ScotButton
            label="Weiter"
            icon="pi pi-arrow-right"
            variant="blue"
            :disabled="zeitIsEinmalig===false ? (!rideExecution.startzeit || !rideExecution.endzeit || !rideExecution.zeitintervall) : (!rideExecution.startzeit && zeitIsEinmalig===false)"
            @click="getTrains(); nextStep()"
        />
      </div>

    </div>
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
      <div class="flex" style="gap: 0.5rem;">
        <ScotButton
            label="Zurück"
            icon="pi pi-arrow-left"
            variant="gray"
            @click="prevStep"
        />
        <ScotButton
            label="Weiter"
            icon="pi pi-arrow-right"
            variant="blue"
            :disabled="!rideExecution.stopplan||!rideExecution.train"
            @click="nextStep(); getStopplanByID()"
        />
      </div>

    </div>

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
        <label for="minmaxfraction" class="font-semibold block mb-2 mt-2"> Preis für Stoßzeiten</label>
        <InputNumber
            v-model="rideExecution.price"
            inputId="price"
            :minFractionDigits="1"
            :maxFractionDigits="2"
            :min="stopplan2.minPrice"
            fluid mode="currency"
            currency="EUR"
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
            label="Erstellen"
            icon="pi pi-plus"
            variant="blue"
            :disabled="rideExecution.employees.length === 0"
            @click="createRideExecution"
        />
      </div>
    </div>

  </div>
</template>

<script setup>




import Stepper from 'primevue/stepper';
import StepList from 'primevue/steplist';
import StepPanels from 'primevue/steppanels';
import StepItem from 'primevue/stepitem';
import Step from 'primevue/step';
import StepPanel from 'primevue/steppanel';



import { ref, computed, onMounted } from 'vue';
import { useRideExecutionStore } from '~/stores/rideExecution.js';
import { useStopplanStore } from "~/stores/stopplan.js";
import { useToast } from 'primevue/usetoast'

const options = ref([
  { name: 'Mo', value: 1 },
  { name: 'Di', value: 2 },
  { name: 'Mi', value: 3 },
  { name: 'Do', value: 4 },
  { name: 'Fr', value: 5 },
  { name: 'Sa', value: 6 },
  { name: 'So', value: 7 }
]);

const datumIsEinmalig = ref(false);
const zeitIsEinmalig = ref(false);

const toast = useToast()
const emit = defineEmits(['stopplanCreated']);
const rideExecutionStore = useRideExecutionStore();
const stopplanStore = useStopplanStore();

const currentStep = ref(1); // Track den aktuellen Schritt
const rideExecution = ref({
  stopplan: null,
  train: null,
  employees: [],
  startdatum: '',
  enddatum: '',
  startzeit: '',
  endzeit: '',
  selectedDays: [], //brauche ich das? es gibt schon options ref
  zeitintervall: '',
  price: 0
});



const dateError = ref(false);

const stopplan2 = computed(() => stopplanStore.stopplan)
const stopplans = computed(() => stopplanStore.stopplans);
const trains = computed(() => rideExecutionStore.trains);
const employees = computed(() => rideExecutionStore.employees);

onMounted(() => {
  stopplanStore.fetchStopplans();

  rideExecutionStore.fetchEmployees();
});
  // Schritt wechseln
function nextStep() {
  if (currentStep.value === 1){
    validateDates();
    if (dateError.value==false) {
      currentStep.value = currentStep.value+1;
    }
  }
  else if (currentStep.value === 2) {
    if (new Date(rideExecution.value.endzeit).getTime() <= new Date(rideExecution.value.startzeit).getTime() && zeitIsEinmalig.value===false) {
      toast.add({
        severity: 'error',
        summary: 'Fehler',
        detail: 'Endzeit muss nach Startzeit sein!',
        life: 3000
      });
    }
    else {
      currentStep.value = currentStep.value+1;
    }
  }
  else {
    currentStep.value = currentStep.value+1;
  }
}

function prevStep() {
  currentStep.value = currentStep.value-1;
}

async function getTrains() {
  const dateAndTimeData = {
    startDate: rideExecution.value.startdatum,
    startTime: rideExecution.value.startzeit,
    endDate: rideExecution.value.enddatum,
    endTime: rideExecution.value.endzeit,
    selectedDays: rideExecution.value.selectedDays,
    zeitIntervall: rideExecution.value.zeitintervall,
    datumIsEinmalig: datumIsEinmalig.value,
    zeitIsEinmalig: zeitIsEinmalig.value,
  };
  await rideExecutionStore.fetchTrains(dateAndTimeData);

}




function getStopplanByID() {
  stopplanStore.fetchStopplanByID(rideExecution.value.stopplan.id);
}

defineProps(['close']);

const validateDates = () => {
  if (new Date(rideExecution.value.enddatum) <= new Date(rideExecution.value.startdatum) && datumIsEinmalig.value===false) {
    dateError.value = true;
    toast.add({
      severity: 'error',
      summary: 'Fehler',
      detail: 'Enddatum muss nach Startdatum sein!',
      life: 3000
    });
  }
  else {
    dateError.value = false;
  }
}
async function createRideExecution() {


  const rideExecutionData = {
    stopplanID: rideExecution.value.stopplan.id,
    trainID: rideExecution.value.train.id,
    employeeSSN_list: rideExecution.value.employees.map((employee) => ({ssn: employee.ssn})),
    startDate: rideExecution.value.startdatum,
    startTime: rideExecution.value.startzeit,
    endDate: rideExecution.value.enddatum,
    endTime: rideExecution.value.endzeit,
    selectedDays: rideExecution.value.selectedDays,
    zeitIntervall: rideExecution.value.zeitintervall,
    datumIsEinmalig: datumIsEinmalig.value,
    zeitIsEinmalig: zeitIsEinmalig.value,
    price: rideExecution.value.price,
  };

  await rideExecutionStore.createRideExecution(rideExecutionData);

  toast.add({
    severity: 'success',
    summary: 'Erfolg',
    detail: 'Fahrtdurchführung wurde erfolgreich erstellt',
    life: 3000
  });

  emit('stopplanCreated');

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
  currentStep.value = 1;

}

</script>

