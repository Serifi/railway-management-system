<template>
  <!-- Icon element with dynamic classes and click event -->
  <i :class="iconClasses" @click="handleClick" class="text-md cursor-pointer"/>
</template>

<script setup>
import { computed } from 'vue'

const emit = defineEmits(['click'])
const props = defineProps({
  // String representing the CSS class for the icon
  icon: {
    type: String,
    required: true
  }
})

const handleClick = (event) => emit('click', event)
const iconClasses = computed(() => props.icon)
</script>