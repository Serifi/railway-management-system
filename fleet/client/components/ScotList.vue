<template>
  <div class="flex justify-between mb-4">
    <IconField>
      <InputIcon class="pi pi-search" />
      <InputText v-model="searchQuery" :placeholder="$t('search')" />
    </IconField>
    <div class="flex space-x-4 items-center cursor-pointer">
      <i class="pi pi-filter" @click="toggleFilter" />
      <ScotButton v-if="isAdmin" :label="$t('create')" icon="pi pi-plus" variant="blue" @click="emitCreate" />
    </div>
    <Drawer v-model:visible="filterVisible" header="Filter" position="right">
      <slot name="filters" :filters="filters" />
    </Drawer>
  </div>

  <div v-for="item in paginatedItems" :key="getKey(item)" class="flex p-6 rounded transition-colors duration-200 border-b"
       @mouseover="hover = getKey(item)" @mouseleave="hover = null">
    <div class="flex flex-col space-y-4 flex-grow">
      <div class="text-lg font-bold">
        <slot name="title" :item="item">{{ item.title }}</slot>
      </div>
      <div class="text-sm text-gray-400 whitespace-pre-line">
        <slot name="description" :item="item">{{ item.description }}</slot>
      </div>
    </div>

    <div v-if="isAdmin && hover === getKey(item)" class="flex flex-col justify-center space-y-2">
      <ScotButton :label="$t('edit')" icon="pi pi-pencil" variant="green" @click="emitEdit(item)" :disabled="item.active" />
      <ScotButton :label="$t('delete')" icon="pi pi-trash" variant="red" @click="confirmDeletion($event, item)" :disabled="item.active" />
    </div>
  </div>
  <ConfirmPopup />

  <Paginator :rows="rowsPerPage" :rowsPerPageOptions="[2, 5, 10, 25]" :totalRecords="filteredItems.length"
             :first="firstRecord" @page="onPageChange" class="mt-4"/>
</template>

<script setup>
import { ref, computed, reactive, createApp, watch } from 'vue';
import { useConfirm } from "primevue/useconfirm";

const hover = ref(null);
const emits = defineEmits(['create', 'edit', 'delete']);
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
  }
});

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
};

const filteredItems = computed(() =>
    props.items.filter(item => {
          const matchesSearch = !searchQuery.value ||
              Object.values(item).some(val => String(val).toLowerCase().includes(searchQuery.value.toLowerCase()))

          let matchesFilter = true;
          for (const key in filters) {
            const filter = filters[key];
            if (key === 'status') {
              if (typeof filter === 'boolean' && item.active !== filter) {
                matchesFilter = false
                break
              }
            } else if (typeof filter === 'string' || typeof filter === 'number') {
              if (filter && item[key] !== filter) {
                matchesFilter = false
                break;
              }
            } else if (typeof filter === 'object' && filter !== null) {
              const from = filter.from !== null && filter.from !== undefined ? filter.from : -Infinity
              const to = filter.to !== null && filter.to !== undefined ? filter.to : Infinity
              if (item[key] < from || item[key] > to) {
                matchesFilter = false
                break
              }
            }
          }

          return matchesSearch && matchesFilter
        }).sort((a, b) => getTitle(a).localeCompare(getTitle(b), undefined, { sensitivity: 'base' }))
)

const firstRecord = computed(() => currentPage.value * rowsPerPage.value);
const paginatedItems = computed(() =>
    filteredItems.value.slice(firstRecord.value, firstRecord.value + rowsPerPage.value)
);

const onPageChange = (event) => {
  if (event.rows !== rowsPerPage.value) {
    rowsPerPage.value = event.rows;
    currentPage.value = 0;
  } else {
    currentPage.value = event.page;
  }
};

const emitCreate = () => emits('create');
const emitEdit = (item) => emits('edit', item);

const confirm = useConfirm();
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
      emits('delete', item);
    }
  });
};

watch([searchQuery, rowsPerPage], () => {
  currentPage.value = 0;
});

const userStore = useUserStore();
const isAdmin = computed(() => userStore.getUserRole === 'Admin');
</script>