<template>
  <!-- Button with dynamic classes and click handling -->
  <button @click="handleClick" :class="buttonClasses" :disabled="disabled" type="button">
    <div class="flex items-center space-x-2">
      <i :class="icon" class="!text-[12px]"/>
      <span class="text-l font-bold">{{ label }}</span>
    </div>
  </button>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  // Label displayed on the button
  label: {
    type: String,
    required: true
  },
  // Icon displayed on the button
  icon: {
    type: String,
    required: true
  },
  // Flag to indicate whether the button is disabled.
  disabled: {
    type: Boolean,
    default: false,
  },
  // Visual variant of the button (accepted values: 'blue', 'green', 'red', 'yellow', 'gray')
  variant: {
    type: String,
    required: true,
    validator: (value) => [
      'blue',
      'green',
      'red',
      'yellow',
      'gray'
    ].includes(value)
  }
})

const emits = defineEmits(['click'])
const handleClick = (event) => emits('click', event)

const buttonClasses = computed(() => {
  switch (props.variant) {
    case 'blue':
      return 'blue-button'
    case 'green':
      return 'green-button'
    case 'red':
      return 'red-button'
    case 'yellow':
      return 'yellow-button'
    case 'gray':
      return 'gray-button'
    default:
      return ''
  }
})
</script>

<style>
button {
  font-family: Arial, sans-serif;
  font-size: 14px;
  font-weight: 600;
  padding: 8px 16px;
  border-radius: 4px;
  border: none;
  cursor: pointer;
  transition: background-color 0.3s, color 0.3s, border-color 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
}

button:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

.blue-button {
  background-color: #EFF6FF;
  color: #3076A7;
}

.blue-button:hover {
  background-color: #DCEFFB;
}

.yellow-button {
  background-color: #FFF4CC;
  color: #B8941C;
}

.yellow-button:hover {
  background-color: #FFEDB5;
}

.red-button {
  background-color: #FFEFF6;
  color: #C23B6E;
}

.red-button:hover {
  background-color: #FFDDE9;
}

.green-button {
  background-color: #F0F0F0;
  color: #7A7A7A;
}

.green-button:hover {
  background-color: #E0E0E0;
}

.gray-button {
  background-color: white;
  color: black;
  border: 1px solid black;
}

.gray-button:hover {
  background-color: #F3F3F3;
  border-color: black;
}

.dialog button {
  border: 1px solid currentColor;
}
</style>