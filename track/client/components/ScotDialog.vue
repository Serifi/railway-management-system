<!-- Komponente für Dialoge mit Aktionen "Erstellen" oder "Bearbeiten" unterstützt. -->
<template>
  <Dialog
    v-model:visible="props.visible"
    :closable="false"
    :modal="true"
    :draggable="false"
    :header="header"
    class="dialog w-2/3"
  >
    <!-- Slot für den Hauptinhalt des Dialogs -->
    <slot />

    <!-- Footer-Slot mit Aktionen -->
    <template #footer>
      <!-- Abbrechen-Button -->
      <ScotButton
        label="Abbrechen"
        icon="pi pi-times"
        variant="gray"
        @click="emitCancel"
      />
      <!-- Button für "Erstellen" -->
      <ScotButton
        v-if="type === 'create'"
        :label="header"
        icon="pi pi-plus"
        variant="blue"
        :disabled="disableAction"
        @click="emitAction"
      />
      <!-- Button für "Bearbeiten" -->
      <ScotButton
        v-else-if="type === 'edit'"
        :label="header"
        icon="pi pi-pencil"
        variant="green"
        :disabled="disableAction"
        @click="emitAction"
      />
    </template>
  </Dialog>
</template>

<script setup>
/* Props für die Steuerung der Dialogeigenschaften */
const props = defineProps({
  visible: {
    type: Boolean,
    required: true,
  },
  type: {
    type: String,
    required: true, // Typ der Aktion ("create", "edit" oder "show")
    validator: (value) => ["create", "edit", "show"].includes(value),
  },
  header: {
    type: String,
    required: true,
  },
  disableAction: {
    type: Boolean,
    default: false,
  },
});

/* Ereignisse, die vom Dialog ausgelöst werden */
const emits = defineEmits(["update:visible", "action", "cancel"]);
const emitAction = () => emits("action");
const emitCancel = () => emits("cancel");
</script>