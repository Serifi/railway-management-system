<template>
  <div class="flex p-6 rounded transition-colors duration-200 border-b" :class="{ 'bg-gray-100': hover }"
       @mouseover="hover = true" @mouseleave="hover = false">

    <div class="flex flex-col space-y-4 flex-grow">
      <!-- Title -->
      <div class="text-lg font-bold" :class="titleClass">{{ title }}</div>

      <!-- Description -->
      <div class="text-sm text-gray-400 whitespace-pre-line">{{ description }}</div>
    </div>

    <!-- Buttons -->
    <div v-if="hover" class="flex flex-col justify-center space-y-4">
      <Button label="Bearbeiten" icon="pi pi-pencil" class="p-button-text text-gray-700" @click="onEdit" />
      <Button label="Löschen" icon="pi pi-trash" class="p-button-text text-red-500" @click="onDelete" />
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const hover = ref(false)
const emits = defineEmits(['edit', 'delete'])
const props = defineProps({
  title: String,
  description: String,
  titleClass: String
})

const onEdit = () => {
  emits('edit')
}

const onDelete = () => {
  emits('delete')
}
</script>