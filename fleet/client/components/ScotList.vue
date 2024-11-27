<!-- ScotList.vue -->
<template>
  <div class="flex justify-between mb-4">
    <IconField>
      <InputIcon class="pi pi-search"/>
      <InputText v-model="searchQuery" placeholder="Suchen..." />
    </IconField>
    <ScotButton label="Erstellen" icon="pi pi-plus" variant="blue" @click="emitCreate"/>
  </div>

  <div v-for="item in paginatedItems" :key="getKey(item)"
      class="flex p-6 rounded transition-colors duration-200 border-b"
      @mouseover="hover = getKey(item)" @mouseleave="hover = null">
    <div class="flex flex-col space-y-4 flex-grow">
      <div class="text-lg font-bold">
        <slot name="title" :item="item">{{ item.title }}</slot>
      </div>
      <div class="text-sm text-gray-400 whitespace-pre-line">
        <slot name="description" :item="item">{{ item.description }}</slot>
      </div>
    </div>

    <div v-if="hover === getKey(item)" class="flex flex-col justify-center space-y-2">
      <ScotButton label="Bearbeiten" icon="pi pi-pencil" variant="green" @click="emitEdit(item)"/>
      <ScotButton label="Löschen" icon="pi pi-trash" variant="red" @click="confirmDeletion($event, item)"/>
    </div>
  </div>
  <ConfirmPopup/>

  <Paginator :rows="rowsPerPage" :totalRecords="filteredItems.length" :first="firstRecord" @page="onPageChange" class="mt-4"/>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useConfirm } from "primevue/useconfirm"

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
      console.log(item)
      emits('delete', item)
    }
  })
}
</script>

<style>
.p-confirm-popup-accept,
.p-confirm-popup-reject {
  padding: 4px;
  margin: 4px;
}

.p-confirm-popup-accept{
  background-color: #FF9999 !important;
}
</style>