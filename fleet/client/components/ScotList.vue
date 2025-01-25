<template>
  <!-- Top with search, filter, and create button -->
  <div class="flex justify-between mb-4">
    <!-- Search input -->
    <IconField>
      <InputIcon class="pi pi-search" />
      <InputText v-model="searchQuery" :placeholder="$t('search')" />
    </IconField>
    <div class="flex space-x-4 items-center cursor-pointer">
      <!-- Filter toggle button -->
      <i class="pi pi-filter" @click="toggleFilter" />
      <!-- Create button, visible only to admins -->
      <ScotButton v-if="isAdmin" :label="$t('create')" icon="pi pi-plus" variant="blue" @click="emitCreate" />
    </div>

    <!-- Drawer for filter options -->
    <Drawer v-model:visible="filterVisible" header="Filter" position="right">
      <!-- Slot for custom filters -->
      <slot name="filters" :filters="filters" />
    </Drawer>
  </div>

  <!-- List of items with hover-based actions for admins -->
  <div v-for="item in paginatedItems" :key="getKey(item)" class="flex p-6 rounded transition-colors duration-200 border-b"
       @mouseover="hover = getKey(item)" @mouseleave="hover = null">
    <div class="flex flex-col space-y-4 flex-grow">
      <!-- Title -->
      <div class="text-lg font-bold">
        <slot name="title" :item="item">{{ item.title }}</slot>
      </div>
      <!-- Description -->
      <div class="text-sm text-gray-400 whitespace-pre-line">
        <slot name="description" :item="item">{{ item.description }}</slot>
      </div>
    </div>

    <!-- Action buttons for admins, visible only on hover -->
    <div v-if="isAdmin && hover === getKey(item)" class="flex flex-col justify-center space-y-2">
      <ScotButton :label="$t('edit')" icon="pi pi-pencil" variant="green" @click="emitEdit(item)" :disabled="disableOnActive && item.active" />
      <ScotButton :label="$t('delete')" icon="pi pi-trash" variant="red" @click="confirmDeletion($event, item)" :disabled="disableOnActive && item.active" />
    </div>
  </div>
  <ConfirmPopup />

  <!-- Paginator for navigating items -->
  <Paginator :rows="rowsPerPage" :rowsPerPageOptions="[2, 5, 10, 25]" :totalRecords="filteredItems.length"
             :first="firstRecord" @page="onPageChange" class="mt-4"/>
</template>

<script setup>
import { ref, computed, reactive, createApp, watch } from 'vue'
import { useConfirm } from "primevue/useconfirm"
import {useI18n} from "vue-i18n"

const { t } = useI18n()
const hover = ref(null)
const emits = defineEmits(['create', 'edit', 'delete'])
const props = defineProps({
  items: {
    type: Array,
    required: true
  },
  rowsPerPage: {
    type: Number,
    default: 5
  },
  getKey: {
    type: Function,
    required: true
  },
  disableOnActive: {
    type: Boolean,
    default: false
  }
})

const userStore = useUserStore()
const isAdmin = computed(() => userStore.getUserRole === 'Admin')

const slots = useSlots()
const rowsPerPage = ref(props.rowsPerPage)
const searchQuery = ref('')
const currentPage = ref(0)
const filterVisible = ref(false)
const filters = reactive({});
function toggleFilter() {
  filterVisible.value = !filterVisible.value
}

const getTitle = (item) => {
  const container = document.createElement('div')
  const app = createApp({ render: () => slots.title?.({ item }) })
  app.mount(container)
  const title = container.textContent.trim()
  app.unmount()
  return title
}

const filteredItems = computed(() =>
    // Check if the item matches the search query
    props.items.filter(item => {
      const matchesSearch = !searchQuery.value ||
          Object.values(item).some(val => String(val).toLowerCase().includes(searchQuery.value.toLowerCase()))

      let matchesFilter = true;
      for (const key in filters) {
        const filter = filters[key];
        // Filter by boolean status
        if (key === 'status') {
          if (typeof filter === 'boolean' && item.active !== filter) {
            matchesFilter = false;
            break;
          }
        // Filter by IDs in an array of passenger cars
        } else if (Array.isArray(filter)) {
          if (!filter.every(id => item.passenger_cars.some(car => car.carriageID === id))) {
            matchesFilter = false;
            break;
          }
        // Filter by string or number values
        } else if (typeof filter === 'string' || typeof filter === 'number') {
          if (filter && item[key] !== filter) {
            matchesFilter = false;
            break;
          }
        // Filter by a range (from/to)
        } else if (typeof filter === 'object' && filter !== null) {
          const from = filter.from !== null && filter.from !== undefined ? filter.from : -Infinity
          const to = filter.to !== null && filter.to !== undefined ? filter.to : Infinity
          if (item[key] < from || item[key] > to) {
            matchesFilter = false
            break;
          }
        }
      }

      // Return item if it matches the search and all filters
      return matchesSearch && matchesFilter
    // Sort items alphabetically by title
    }).sort((a, b) => getTitle(a).localeCompare(getTitle(b), undefined, { sensitivity: 'base' }))
)

// Pagination
watch([searchQuery, rowsPerPage], () => currentPage.value = 0)
const firstRecord = computed(() => currentPage.value * rowsPerPage.value)
const paginatedItems = computed(() => filteredItems.value.slice(firstRecord.value, firstRecord.value + rowsPerPage.value))
const onPageChange = (event) => {
  if (event.rows !== rowsPerPage.value) {
    rowsPerPage.value = event.rows
    currentPage.value = 0
  } else {
    currentPage.value = event.page
  }
}

// Emits
const emitCreate = () => emits('create')
const emitEdit = (item) => emits('edit', item)
const confirm = useConfirm();
const confirmDeletion = (event, item) => {
  confirm.require({
    target: event.currentTarget,
    message: t('deleteMessage'),
    icon: 'pi pi-info-circle',
    rejectProps: {
      label: t('cancel'),
      severity: 'secondary',
      outlined: true
    },
    acceptProps: {
      label: t('delete'),
      severity: 'danger'
    },
    accept: () => {
      emits('delete', item)
    }
  })
}
</script>