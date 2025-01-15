<!-- Komponente für durchsuchbare Liste mit Paginierung und Bearbeiten, Löschen sowie optional Warnungen erstellen -->
<template>
  <!-- Suchleiste und Aktionen -->
  <div class="flex justify-between mb-4">
    <!-- Suchfeld -->
    <IconField>
      <InputIcon class="pi pi-search" />
      <InputText
        v-model="searchQuery"
        :placeholder="`${pagePlaceholder} suchen...`"
      />
    </IconField>

    <!-- Admin-spezifische Buttons -->
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

  <!-- Listenelemente -->
  <div
    v-for="item in paginatedItems"
    :key="getKey(item)"
    class="flex p-6 rounded transition-colors duration-200 border-b"
    @mouseover="hover = getKey(item)"
    @mouseleave="hover = null"
  >
    <div class="flex flex-col space-y-4 flex-grow">
      <!-- Titel und Beschreibung der Elemente -->
      <div class="text-lg font-bold">
        <slot name="title" :item="item">{{ item.title }}</slot>
      </div>
      <div class="text-sm text-gray-400 whitespace-pre-line">
        <slot name="description" :item="item">{{ item.description }}</slot>
      </div>
    </div>

    <!-- Admin-Aktionen beim Hover -->
    <div v-if="hover === getKey(item) && isAdmin" class="flex flex-col justify-center space-y-2">
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

  <!-- Bestätigungsdialog -->
  <ConfirmPopup />

  <!-- Paginierung -->
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

const hover = ref(null); // Aktives Listenelement
const searchQuery = ref(""); // Suchbegriff
const currentPage = ref(0); // Aktuelle Seite

const emits = defineEmits(["create", "createWarning", "edit", "delete"]);
const props = defineProps({
  items: { type: Array, required: true }, // Liste der Elemente
  rowsPerPage: { type: Number, default: 10 }, // Anzahl der Elemente pro Seite
  getKey: { type: Function, required: true },
  pageType: {
    type: String,
    required: true,
    validator: (value) =>
      ["Abschnitt", "Strecke", "Bahnhof", "Mitarbeiter"].includes(value),
  },
  showWarningButton: { type: Boolean, default: false }, // Steuerung des Warnung-Buttons
});

const pagePlaceholder = computed(() => props.pageType);
const filteredItems = computed(() => {
  // Filterung der Elemente basierend auf dem Suchbegriff
  if (!searchQuery.value) return props.items;
  return props.items.filter((item) =>
    Object.values(item).some((val) =>
      String(val).toLowerCase().includes(searchQuery.value.toLowerCase())
    )
  );
});
const firstRecord = computed(() => currentPage.value * props.rowsPerPage);
const paginatedItems = computed(() => {
  // Elemente der aktuellen Seite
  const start = firstRecord.value;
  const end = start + props.rowsPerPage;
  return filteredItems.value.slice(start, end);
});

/* Aktionen */
const emitCreate = () => emits("create"); // Neues Element erstellen
const emitCreateWarning = () => emits("createWarning"); // Warnung erstellen
const emitEdit = (item) => emits("edit", item); // Element bearbeiten

/* Bestätigungsdialog für das Löschen */
const confirm = useConfirm();
const confirmDeletion = (event, item) => {
  confirm.require({
    target: event.currentTarget,
    message: "Sicher, dass Sie dieses Element löschen möchten?",
    icon: "pi pi-info-circle",
    rejectProps: { label: "Abbrechen", severity: "secondary", outlined: true },
    acceptProps: { label: "Löschen", severity: "danger" },
    accept: () => emits("delete", item),
  });
};

/* Paginierungs-Handler */
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