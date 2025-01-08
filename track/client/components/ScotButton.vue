<template>
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
  },
  disabled: {
    type: Boolean,
    default: false,
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

[data-theme="dark"] .blue-button {
  background-color: #1A283A;
  color: #7FB3D4;
}

[data-theme="dark"] .blue-button:hover {
  background-color: #223A50;
}

[data-theme="dark"] .yellow-button {
  background-color: #3A3020;
  color: #D3B76F;
}

[data-theme="dark"] .yellow-button:hover {
  background-color: #4A3E28;
}

[data-theme="dark"] .red-button {
  background-color: #36232A;
  color: #D28A99;
}

[data-theme="dark"] .red-button:hover {
  background-color: #432D37;
}

[data-theme="dark"] .green-button {
  background-color: #333333;
  color: #C0C0C0;
}

[data-theme="dark"] .green-button:hover {
  background-color: #3C3C3C;
}

[data-theme="dark"] .gray-button {
  background-color: #2A2A2A;
  color: #B0B0B0;
  border: 1px solid #3A3A3A;
}

[data-theme="dark"] .gray-button:hover {
  background-color: #3A3A3A;
  border-color: #4A4A4A;
}

.dialog button {
  border: 1px solid currentColor;
}
</style>