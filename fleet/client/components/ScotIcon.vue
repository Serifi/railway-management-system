<template>
  <i :class="iconClasses" @click="handleClick" class="text-md cursor-pointer"/>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  icon: {
    type: String,
    required: true
  }
})

const emit = defineEmits(['click'])

function handleClick(event) {
  emit('click', event)
}

const iconClasses = computed(() => props.icon)
</script>