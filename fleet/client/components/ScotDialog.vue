<template>
  <Dialog v-model:visible="props.visible" :closable="false" :modal="true" :draggable="false" :header="header" class="dialog w-2/3">
    <slot /> <!-- Slot for custom content -->

    <template #footer> <!-- Footer with action buttons -->
      <!-- Cancel button, always shown -->
      <ScotButton :label="$t('cancel')" icon="pi pi-times" variant="gray" @click="emitCancel"/>
      <!-- Create button, shown when type is 'create' -->
      <ScotButton v-if="type === 'create'" :label="header" icon="pi pi-plus" variant="blue" :disabled="disableAction" @click="emitAction"/>
      <!-- Edit button, shown when type is 'edit' -->
      <ScotButton v-else-if="type === 'edit'" :label="header" icon="pi pi-pencil" variant="green" :disabled="disableAction" @click="emitAction"/>
    </template>
  </Dialog>
</template>

<script setup>
const props = defineProps({
  // Controls the visibility of the dialog
  visible: {
    type: Boolean,
    required: true,
  },
  // Specifies the dialog type, either 'create' or 'edit'
  type: {
    type: String,
    required: true,
    validator: (value) => ["create", "edit", "show"].includes(value),
  },
  // Sets the title of the dialog
  header: {
    type: String,
    required: true,
  },
  // Disables the action buttons when true
  disableAction: {
    type: Boolean,
    default: false
  }
})

// Fired when the dialog visibility changes
const emits = defineEmits(["update:visible", "action", "cancel"])
// Fired when an action button (create/edit) is clicked
const emitAction = () => emits("action")
// Fired when the cancel button is clicked
const emitCancel = () => emits("cancel")
</script>