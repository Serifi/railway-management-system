<template>
  <div>

    <div>
      <div class="flex flex-col">
        <label for="name" class="mb-1">Verspätung in min</label>
        <InputText
            id="delay"
            v-model="rideExecution.delay"
            placeholder="Verspätung eingeben..."
        />
      </div>
      <br>
      <div class="flex flex-col mb-4">
        <label for="ausfall" class="mb-1">Ausfall</label>
        <SelectButton id="ausfall" v-model="optionsValue" :options="options" />
      </div>
    </div>

    <div class="mt-7">
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




import Stepper from 'primevue/stepper';
import StepList from 'primevue/steplist';
import StepPanels from 'primevue/steppanels';
import StepItem from 'primevue/stepitem';
import Step from 'primevue/step';
import StepPanel from 'primevue/steppanel';



import { ref, computed, onMounted } from 'vue';
import { useRideExecutionStore } from '~/stores/rideExecution.js';
import { useToast } from 'primevue/usetoast'


const toast = useToast()
const emit = defineEmits(['rideExecution-created']);
const rideExecutionStore = useRideExecutionStore();



const props = defineProps({
  rideExecutionID: {
    type: Number,
    required: true,
  },
  rideExecutionDelay: {
    type: Number,
    required: true,
  },
  rideExecutionIsCanceled: {
    type: Boolean,
    required: true,
  }
});
/*defineProps(['close']);*/

const optionsValue = ref(props.rideExecutionIsCanceled ? 'Ja' : 'Nein');
const options = ref(['Nein', 'Ja']);

const rideExecution = ref({
  delay: props.rideExecutionIsCanceled ? 0 : props.rideExecutionDelay
});



onMounted(() => {
  console.log(props.rideExecutionID);
})



async function editRideExecution() {

  const rideExecutionData = {
    delay: rideExecution.value.delay,
    isCanceled: optionsValue.value
  };

  console.log(rideExecutionData);

  await rideExecutionStore.editRideExecution(rideExecutionData, props.rideExecutionID);

  toast.add({
    severity: 'success',
    summary: 'Erfolg',
    detail: "Fahrtdurchführung wurde erfolgreich bearbeitet",
    life: 3000
  });

  emit('stopplanCreated'); //sorgt für schließen von fenster aber wieso?

  //rideExecution.value = { name: '', stopplan: null, train: null };

}



</script>