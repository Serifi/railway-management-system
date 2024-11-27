<template>
  <button @click="handleClick" :class="buttonClasses" type="button">
    <div class="flex items-center space-x-2">
      <i :class="icon" class="!text-[12px]"/>
      <span class="text-l font-bold">{{ label }}</span>
    </div>
  </button>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  label: {
    type: String,
    required: true
  },
  icon: {
    type: String,
    required: true
  },
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

.blue-button {
  background-color: #EFF6FF;
  color: #3076A7;
  border: 1px solid transparent;
}

.blue-button:hover {
  background-color: #DCEFFB;
}

.yellow-button {
  background-color: #FFF4CC;
  color: #B8941C;
  border: 1px solid transparent;
}

.yellow-button:hover {
  background-color: #FFEDB5;
}

.red-button {
  background-color: #FFEFF6;
  color: #C23B6E;
  border: 1px solid transparent;
}

.red-button:hover {
  background-color: #FFDDE9;
}

.green-button {
  background-color: #F0F0F0;
  color: #7A7A7A; /* Gray text */
  border: 1px solid transparent;
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
  color: black;
  border-color: black;
}
</style>