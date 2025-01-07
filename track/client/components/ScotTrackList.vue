<template>
  <div class="flex justify-between mb-4">
    <IconField>
      <InputIcon class="pi pi-search" />
      <InputText
        v-model="searchQuery"
        :placeholder="`${pagePlaceholder} suchen...`"
      />
    </IconField>

    <div v-if="isAdmin" class="flex space-x-2">
      <ScotButton
        v-if="showWarningButton"
        label="Warnung erstellen"
        icon="pi pi-plus"
        variant="yellow"
        @click="emitCreateWarning"
      />
      <ScotButton
        :label="`${pagePlaceholder} erstellen`"
        icon="pi pi-plus"
        variant="blue"
        @click="emitCreate"
      />
    </div>
  </div>

  <div
    v-for="item in paginatedItems"
    :key="getKey(item)"
    class="relative flex flex-col p-6 rounded transition-colors duration-200 border-b"
    @mouseover="hover = getKey(item)"
    @mouseleave="hover = null"
  >
    <div
      class="flex justify-between items-center cursor-pointer"
      @click="toggleExpanded(item)"
    >
      <div class="text-lg font-bold">
        <slot name="title" :item="item">{{ item.title }}</slot>
      </div>
      <i
        class="pi"
        :class="{
          'pi-chevron-down': expandedItem === getKey(item),
          'pi-chevron-right': expandedItem !== getKey(item),
        }"
      ></i>
    </div>

    <div v-if="expandedItem === getKey(item)" class="mt-4 relative">
      <div class="text-sm text-gray-400 whitespace-pre-line">
        <slot name="description" :item="item">{{ item.description }}</slot>
      </div>

      <div
        v-if="hover === getKey(item) && isAdmin"
        class="absolute inset-0 flex flex-col justify-center items-end space-y-2 pr-4 pointer-events-none"
      >
        <div class="pointer-events-auto flex flex-col space-y-2">
          <ScotButton
            label="Bearbeiten"
            icon="pi pi-pencil"
            variant="green"
            @click="emitEdit(item)"
          />
          <ScotButton
            label="Löschen"
            icon="pi pi-trash"
            variant="red"
            @click="confirmDeletion($event, item)"
          />
        </div>
      </div>
    </div>
  </div>

  <ConfirmPopup />

  <Paginator
    :rows="rowsPerPage"
    :totalRecords="filteredItems.length"
    :first="firstRecord"
    @page="onPageChange"
    class="mt-4"
  />
</template>

<script setup>
import { ref, computed } from "vue";
import { useConfirm } from "primevue/useconfirm";
import { useUserStore } from "@/stores/user";

const userStore = useUserStore();
const isAdmin = computed(() => userStore.getUserRole === "Admin");

const hover = ref(null);
const expandedItem = ref(null);

const emits = defineEmits(["create", "createWarning", "edit", "delete"]);
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
  pageType: {
    type: String,
    required: true,
    validator: (value) =>
      ["Abschnitt", "Strecke", "Bahnhof", "Mitarbeiter"].includes(value),
  },
  showWarningButton: {
    type: Boolean,
    default: false,
  },
});

const pagePlaceholder = computed(() => props.pageType);

const searchQuery = ref("");
const filteredItems = computed(() => {
  if (!searchQuery.value) return props.items;
  return props.items.filter((item) =>
    Object.values(item).some((val) =>
      String(val).toLowerCase().includes(searchQuery.value.toLowerCase())
    )
  );
});

const currentPage = ref(0);
const firstRecord = computed(() => currentPage.value * props.rowsPerPage);
const paginatedItems = computed(() => {
  const start = firstRecord.value;
  const end = start + props.rowsPerPage;
  return filteredItems.value.slice(start, end);
});

const emitCreate = () => emits("create");
const emitCreateWarning = () => emits("createWarning");
const emitEdit = (item) => emits("edit", item);

const confirm = useConfirm();
const confirmDeletion = (event, item) => {
  confirm.require({
    target: event.currentTarget,
    message: "Sicher, dass Sie dieses Element löschen möchten?",
    icon: "pi pi-info-circle",
    rejectProps: {
      label: "Abbrechen",
      severity: "secondary",
      outlined: true,
    },
    acceptProps: {
      label: "Löschen",
      severity: "danger",
    },
    accept: () => emits("delete", item),
  });
};

const toggleExpanded = (item) => {
  const itemKey = props.getKey(item);
  expandedItem.value = expandedItem.value === itemKey ? null : itemKey;
};

const onPageChange = (event) => (currentPage.value = event.page);
</script>

<style>
.p-confirm-popup-accept,
.p-confirm-popup-reject {
  padding: 4px;
  margin: 4px;
}

.p-confirm-popup-accept {
  background-color: #ff9999 !important;
}
</style>