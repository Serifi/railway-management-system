<template>
  <div class="flex flex-col min-h-screen">
    <!-- Header -->
    <header class="flex items-center justify-between py-4 border-b">
      <!-- Left: Icon and Scotty -->
      <div class="flex items-center space-x-4 me-4">
        <img src="../assets/images/icon.png" alt="Icon" class="w-8 h-8">
        <span class="text-xl font-bold">Scotty</span>
      </div>

      <!-- Middle: Navigation -->
      <Navigation />

      <!-- Right: User -->
      <div class="flex items-center space-x-4 mx-4">
        <div class="w-px h-8 bg-gray-300"></div>
        <div class="flex items-center space-x-4 cursor-pointer" @click="showUserPanel">
          <i class="pi pi-user text-xl"/>
          <div>
            <div class="text-sm font-bold">{{ userFullName }}</div>
            <div class="text-xs text-gray-500 leading-3">{{ userRole }}</div>
          </div>
        </div>
      </div>

      <Popover ref="userPanel" appendTo="body">
        <div class="flex flex-col">
          <div class="flex items-center p-2 space-x-2 rounded hover:bg-gray-200 transition duration-300 cursor-pointer" @click="logout">
            <i class="pi pi-power-off text-red-400"/>
            <div>Abmelden</div>
          </div>
        </div>
      </Popover>
    </header>

    <!-- Page -->
    <main class="flex-grow p-8">
      <NuxtPage />
    </main>

    <Toast />
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useUserStore } from '@/stores/user'
import { useRouter } from "vue-router"
import Navigation from '~/components/ScotNavigation.vue'

const router = useRouter()
const userStore = useUserStore()
const userPanel = ref(null)

const userFullName = computed(() => userStore.getFullName)
const userRole = computed(() => userStore.user.role)

function showUserPanel() { userPanel.value.toggle(event) }
function logout(){
  router.push('/')
}

</script>