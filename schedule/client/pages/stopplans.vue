<template>
  <List :items="stopplans" :getKey="getStopplanKey" :rowsPerPage="5"  @create="toggleCreateDialog" @edit="toggleEditDialog" @delete="deleteStopplan">
    <template #title="{ item }">
      {{ `Halteplan ${item.name}` }} <span v-if="item.rideExecutions && item.rideExecutions.length > 0"><Tag  severity="success" value="Aktiv"></Tag></span>
    </template>
    <template #description="{ item }">
      Mindestpreis zwischen 2 Haltestellen: {{ item.minPrice }}€<br/>

      Stationen: <span v-for="(station, index) in item.trainStations" :key="station.id">
    {{ station.name }}<span v-if="index < item.trainStations.length - 1">, </span>
  </span>

    </template>

  </List>


  <Dialog v-model:visible="createDialogVisible" header="Halteplan erstellen" class="w-2/3">
    <ScotStopplan @stopplan-created="toggleCreateDialog" />
    <template #footer>
      <ScotButton label="Abbrechen" icon="pi pi-times" variant="gray" @click="toggleCreateDialog"/>
    </template>
  </Dialog>

  <Dialog v-model:visible="editDialogVisible" header="Halteplan bearbeiten" class="w-2/3">
    <ScotEditStopplan @stopplan-created="toggleEditDialog" :stopplanID="stopplan?.id" :stopplanName="stopplan?.name" :stopplanTrackID="stopplan?.trackID" :stopplanTrainstations="stopplan?.trainStations" /> <!--neu hinzugefügt-->
    <template #footer>
      <ScotButton label="Abbrechen" icon="pi pi-times" variant="gray" @click="toggleEditDialog"/>
<!--      <ScotButton label="Bearbeiten" icon="pi pi-pencil" variant="green" @click="editEmployee"/>-->
    </template>
  </Dialog>
</template>

<script setup>
import {ref, computed} from 'vue'
import { useEmployeeStore } from '@/stores/employee'
import { useToast } from 'primevue/usetoast'
import List from '~/components/ScotList.vue'
import ScotStopplan from "~/components/ScotStopplan.vue";
import {useStopplanStore} from "~/stores/stopplan.js";

const toast = useToast()
const createDialogVisible = ref(false)
const editDialogVisible = ref(false)
const stopplanStore = useStopplanStore()
const stopplans = stopplanStore.stopplans
const stopplan = ref(null)


onMounted(() => {
  stopplanStore.fetchStopplans();
});

function deleteStopplan(currentStopplan) {
  if(currentStopplan.rideExecutions.length > 0) {
    toast.add({ severity: 'warn', summary: 'Löschen nicht möglich', detail: 'Halteplan bereits in Verwendung', life: 3000 })
  }
  else {
    stopplanStore.deleteStopplan(currentStopplan.id)
    toast.add({ severity: 'success', summary: 'Erfolgreich', detail: 'Aktion wurde erfolgreich abgeschlossen', life: 3000 })
  }
}


function getStopplanKey(stopplan) {
  return stopplan.id
}


function toggleCreateDialog() {
  createDialogVisible.value = !createDialogVisible.value;
}

function toggleEditDialog(currentStopplan) {
  if(currentStopplan.rideExecutions.length > 0) {
    toast.add({ severity: 'warn', summary: 'Bearbeiten nicht möglich', detail: 'Halteplan bereits in Verwendung', life: 3000 })
  }
  else {
    stopplan.value = currentStopplan; // Setze den aktuellen Stopplan
    editDialogVisible.value = !editDialogVisible.value;
  }
}

</script>

