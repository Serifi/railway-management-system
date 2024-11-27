<!-- layouts/default.vue -->
<template>
  <div class="flex flex-col min-h-screen">
    <!-- Header -->
    <header class="flex items-center justify-between px-8 py-4 border-b">
      <!-- Left: Icon and Scotty -->
      <div class="flex items-center">
        <img src="../assets/images/icon.png" alt="Icon" class="w-8 h-8 me-2">
        <span class="text-2xl font-bold">Scotty</span>
      </div>

      <!-- Middle: Navigation -->
      <Navigation />

      <!-- Right: User -->
      <div class="flex items-center space-x-4">
        <div class="w-px h-8 bg-gray-300"></div>
        <div class="flex items-center space-x-4">
          <i class="pi pi-user text-xl"></i>
          <div>
            <div class="text-l">{{ userFullName }}</div>
            <div class="text-sm text-gray-500 leading-3">{{ userRole }}</div>
          </div>
        </div>
      </div>
    </header>

    <!-- Page -->
    <main class="flex-grow">
      <NuxtPage />
    </main>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useUserStore } from '@/stores/user'
import Navigation from '@/components/Navigation.vue'

const userStore = useUserStore()

const userFullName = computed(() => userStore.getFullName)
const userRole = computed(() => userStore.user.role)
</script>