<template>
  <Popover ref="popoverRef">
    <div
        v-for="item in props.items"
        :key="item.name"
        @click="handleClick(item)"
        class="flex items-center space-x-2 p-2 rounded hover:bg-gray-200 dark:hover:bg-gray-700 transition duration-300 cursor-pointer bg-white dark:bg-gray-800 text-black dark:text-white"
    >
      <component :is="item.iconComponent" v-bind="item.iconProps" class="text-xs"/>
      <span class="me-2">{{ item.name }}</span>
    </div>
  </Popover>
</template>

<script setup>
import {ref} from 'vue'

const props = defineProps({
  items: {
    type: Array,
    required: true
  }
})

const emit = defineEmits(['item-click'])

const popoverRef = ref(null)

function handleClick(item) {
  emit('item-click', item)
}

function toggle(event) {
  popoverRef.value.toggle(event)
}

defineExpose({toggle})
</script>