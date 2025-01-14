<template>
  <!-- Popover container for displaying items -->
  <Popover ref="popoverRef">
    <div v-for="item in props.items" :key="item.name" @click="handleClick(item)" class="flex items-center space-x-2 p-2 rounded cursor-pointer">
      <component :is="item.iconComponent" v-bind="item.iconProps" class="text-xs"/>
      <span class="me-2">{{ item.name }}</span>
    </div>
  </Popover>
</template>

<script setup>
import {ref} from 'vue'

const emit = defineEmits(['item-click'])
const props = defineProps({
  // Array of items to display in the popover
  items: {
    type: Array,
    required: true
  }
})

const popoverRef = ref(null)
const handleClick = (item) => emit('item-click', item);
const toggle = (event) => popoverRef.value.toggle(event);

// Expose the toggle method to allow parent components to call it
defineExpose({toggle})
</script>