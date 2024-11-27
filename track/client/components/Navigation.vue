<template>
  <!-- Desktop -->
  <nav class="hidden lg:flex space-x-8">
    <NuxtLink
        v-for="item in navItems"
        :key="item.page"
        :to="`/${item.page}`"
        :class="[
        'flex items-center px-4 py-2 rounded transition-colors duration-200',
        isActive(item.page)
          ? 'bg-[#EFF6FF] text-[#1769aa]'
          : 'hover:bg-[#EFF6FF] hover:text-[#1769aa]'
      ]"
    >
      <span>{{ item.name }}</span>
    </NuxtLink>
  </nav>

  <!-- Mobile -->
  <nav class="fixed bottom-0 left-0 right-0 h-12 border-t lg:hidden">
    <div class="flex justify-around">
      <NuxtLink
          v-for="item in navItems"
          :key="item.page"
          :to="`/${item.page}`"
          class="flex-1 flex flex-col items-center py-2 text-gray-700 hover:text-[#1769aa] transition-colors duration-200"
          :class="isActive(item.page) ? 'text-[#1769aa]' : ''"
      >
        <FontAwesomeIcon :icon="item.icon" :class="isActive(item.page) ? 'text-[#1769aa]' : null"/>
      </NuxtLink>
    </div>
  </nav>
</template>

<script setup>
import { useRoute } from 'vue-router'
import { useNavigationStore } from '@/stores/navigation'
import { computed } from 'vue'

const navigationStore = useNavigationStore()
const route = useRoute()

const navItems = computed(() => navigationStore.getNavItems)
const isActive = (page) => route.path === `/${page}`
</script>