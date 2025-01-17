<template>

  <div class="flex flex-row items-center justify-between mb-4">
    <!-- IconField: Links ausgerichtet -->
    <div class="flex-none">
      <IconField>
        <InputIcon class="pi pi-search" />
        <InputText v-model="searchQuery" placeholder="Suchen..." />
      </IconField>
    </div>

    <!-- ScotButton: Nur für Admins sichtbar -->
    <div v-if="user.role === 'Admin'" class="ml-4">
      <ScotButton label="Erstellen" icon="pi pi-plus" variant="blue" @click="toggleCreateDialog" />
    </div>

    <!-- SelectButton: Nur für Employee sichtbar -->
    <div v-if="user.role === 'Employee'" class="absolute left-1/2 transform -translate-x-1/2">
      <SelectButton v-model="value" :options="options" />
    </div>

  </div>


  <div v-if="value==='Alle'">
    <div v-for="stopplan in stopplans" :key="stopplan.id" class="border-b">
      <div class="text-2xl font-bold ml-3 mt-5">Fahrplan für Halteplan {{ stopplan.name }}</div>
      <div v-if="stopplan.rideExecutions && stopplan.rideExecutions.length < 1">
        <div class="card flex flex-wrap gap-4 justify-start pl-5 py-6">
          <Message size="small" severity="warn">Keine Fahrtdurchführungen verfügbar!</Message>
        </div>
      </div>
      <div v-for="rideExecution in stopplan.rideExecutions" :key="rideExecution.id"
           class="flex p-6 rounded transition-colors duration-200"
           @mouseover="hover = rideExecution.id" @mouseleave="hover = null">
        <div class="flex flex-col space-y-4 flex-grow">
          <div class="text-lg font-bold">
            Fahrtdurchführung<i class="fa-solid fa-calendar-days ml-3"></i> {{ rideExecution.date }} <i class="fa-regular fa-clock ml-3"></i> {{ rideExecution.time }}

            <span v-if="!rideExecution.isCanceled && rideExecution.delay > 0" style="color: #db3939; margin-left: 0.4rem;" >+{{rideExecution.delay}}</span>
          </div>
          <div class="text-sm text-gray-400 whitespace-pre-line">
            <i class="fa-solid fa-train mr-1"></i>Zug: {{ rideExecution.train.name }}<br/>
            <div v-if="rideExecution.isCanceled">
              <CustomMessage />
            </div>
          </div>
        </div>
        <div v-if="user.role==='Admin'">
          <div v-if="hover === rideExecution.id" class="flex flex-col justify-center space-y-2">
            <ScotButton label="Bearbeiten" icon="pi pi-pencil" variant="green" @click="toggleEditDialog(rideExecution.id, rideExecution.delay, rideExecution.isCanceled)" />
            <ScotButton label="Löschen" icon="pi pi-trash" variant="red" @click="confirmDeletion($event, rideExecution)" />
          </div>
        </div>
      </div>
      <ConfirmPopup/>
    </div>
  </div>

  <div v-if="value==='Meine'">
    <List :items="user.rideExecutions" :getKey="getRideExecutionKey" :rowsPerPage="5" :toggleValue="value">
      <template #title="{ item }">
        Fahrtdurchführung<i class="fa-solid fa-calendar-days ml-3"></i> {{ item.date }} <i class="fa-regular fa-clock ml-3"></i> {{ item.time }}
        <span v-if="!item.isCanceled && item.delay > 0" style="color: #db3939; margin-left: 0.4rem;" >+{{item.delay}}</span>
      </template>
      <template #description="{ item }">
        {{`Halteplan: ${item.stopplan.name}`}} <br>
        {{`Zug: ${item.train.name}`}}
        <div v-if="item.isCanceled">
          <CustomMessage />
        </div>
      </template>
    </List>
  </div>


<Dialog v-model:visible="createDialogVisible" header="Fahrtdurchführung erstellen" class="w-2/3">
    <ScotRideExecution @stopplan-created="toggleCreateDialog" />

    <template #footer>
      <ScotButton label="Abbrechen" icon="pi pi-times" variant="gray" @click="toggleCreateDialog"/>
    </template>
  </Dialog>

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





const value = ref('Alle');
const options = ref(['Alle', 'Meine']);

const userStore = useUserStore();
const user = computed(() => userStore.user);
const toast = useToast()
const createDialogVisible = ref(false)
const editDialogVisible = ref(false)
const rideExecutionStore = useRideExecutionStore()
const stopplanStore = useStopplanStore()
const stopplans = stopplanStore.stopplans

const selectedRideExecution = ref(null)
const delay = ref(0)
const isCanceled = ref(false)

onMounted(() => {
  stopplanStore.fetchStopplans();
  userStore.fetchEmployees();
});

function getRideExecutionKey(rideExecution) {
  return rideExecution.id
}
function getStopplanKey(stopplan) {
  return stopplan.id
}

function toggleCreateDialog(rideExecutionID) {
  createDialogVisible.value = !createDialogVisible.value;
}


function toggleEditDialog(rideExecutionID, rideExecutionDelay, rideExecutionIsCanceled) {
  selectedRideExecution.value = rideExecutionID;
  delay.value = rideExecutionDelay;
  isCanceled.value = rideExecutionIsCanceled;
  editDialogVisible.value = !editDialogVisible.value
}


function editEmployee() {
  employeeStore.editEmployee(employee)
  toggleEditDialog(null)
}


function deleteRideExecution(currentRideExecution) {
  console.log('Deleting Ride Execution:', currentRideExecution.id); // Debug-Log
  rideExecutionStore.deleteRideExecution(currentRideExecution.id)
  toast.add({ severity: 'success', summary: 'Erfolgreich', detail: 'Aktion wurde erfolgreich abgeschlossen', life: 3000 })
}





const hover = ref(null)
const emits = defineEmits(['create', 'edit', 'delete'])
const props = defineProps({
  items: {
    type: Array,
    required: true
  },
  rowsPerPage: {
    type: Number,
    default: 10
  },
  getKey: {
    type: Function,
    required: true
  }
})

const searchQuery = ref('')
watch(searchQuery, () => currentPage.value = 0)

const filteredItems = computed(() => {
  if (!searchQuery.value) return props.items
  return props.items.filter(item =>
      Object.values(item).some(val =>
          String(val).toLowerCase().includes(searchQuery.value.toLowerCase())
      )
  )
})

const currentPage = ref(0)
const onPageChange = (event) => currentPage.value = event.page
const firstRecord = computed(() => currentPage.value * props.rowsPerPage)
const paginatedItems = computed(() => {
  const start = firstRecord.value
  const end = start + props.rowsPerPage
  return filteredItems.value.slice(start, end)
})

const emitCreate = () => emits('create')
const emitEdit = (item) => emits('edit', item)

const confirm = useConfirm()
const confirmDeletion = (event, item) => {
  console.log('Confirm Deletion Triggered', item); // Debug-Log
  confirm.require({
    target: event.currentTarget,
    message: 'Sicher, dass Sie dieses Element löschen möchten?',
    icon: 'pi pi-info-circle',
    rejectProps: {
      label: 'Abbrechen',
      severity: 'secondary',
      outlined: true
    },
    acceptProps: {
      label: 'Löschen',
      severity: 'danger'
    },
    accept: () => {
      console.log('Item accepted for deletion:', item); // Debug-Log
      deleteRideExecution(item);
    }
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