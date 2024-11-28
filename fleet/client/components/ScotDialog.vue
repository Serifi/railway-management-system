<template>
  <Dialog v-model:visible="props.visible" :closable="false" :modal="true" :draggable="false" :header="header" class="dialog w-2/3">
    <slot />

    <template #footer>
      <ScotButton label="Abbrechen" icon="pi pi-times" variant="gray" @click="emitCancel"/>
      <ScotButton v-if="type === 'create'" :label="header" icon="pi pi-plus" variant="blue" @click="emitAction"/>
      <ScotButton v-else-if="type === 'edit'" :label="header" icon="pi pi-pencil" variant="green" @click="emitAction"/>
    </template>
  </Dialog>
</template>

<script setup>
const props = defineProps({
  visible: {
    type: Boolean,
    required: true,
  },
  type: {
    type: String,
    required: true,
    validator: (value) => ["create", "edit", "show"].includes(value),
  },
  header: {
    type: String,
    required: true,
  },
})

const emits = defineEmits(["update:visible", "action", "cancel"]);
const emitAction = () => emits("action");
const emitCancel = () => emits("cancel");
</script>