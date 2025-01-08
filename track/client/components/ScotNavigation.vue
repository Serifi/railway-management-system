<template>
  <!-- Desktop -->
  <nav class="hidden lg:flex space-x-8">
    <NuxtLink  v-for="item in navItems"  :key="item.page"  :to="`/${item.page}`"
        class="nav-link desktop"  :class="{ 'nav-active': isActive(item.page), 'nav-hover': !isActive(item.page) }">
      <span>{{ item.name }}</span>
    </NuxtLink>
  </nav>

  <nav class="fixed bottom-0 left-0 right-0 h-12 border-t lg:hidden">
    <div class="flex justify-around">
      <NuxtLink v-for="item in navItems"  :key="item.page"  :to="`/${item.page}`"
          class="nav-link mobile" :class="{ 'text-color': isActive(item.page) }">
        <FontAwesomeIcon :icon="item.icon" />
      </NuxtLink>
    </div>
  </nav>
</template>

<script setup>
import {useRoute} from 'vue-router'
import {useNavigationStore} from '@/stores/navigation'
import {computed} from 'vue'

const navigationStore = useNavigationStore()
const route = useRoute()

const navItems = computed(() => navigationStore.getNavItems)
const isActive = (page) => route.path === `/${page}`
</script>

<style>
.nav-link {
  font-weight: bold;
  transition: color 0.2s, background-color 0.2s;
}

.nav-link.desktop {
  display: flex;
  align-items: center;
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
}

.nav-link.mobile {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 0.5rem 0;
}

.nav-active {
  background-color: #EFF6FF;
  color: #1769AA;
}

.nav-hover:hover {
  background-color: #EFF6FF;
  color: #1769AA;
}

.text-color {
  color: #1769AA;
}

[data-theme="dark"] .nav-active {
  background-color: #1A283A;
  color: #7FB3D4;
}

[data-theme="dark"] .nav-hover:hover {
  background-color: #223A50;
  color: #A4D0F0;
}

[data-theme="dark"] .text-color {
  color: #A4D0F0;
}
</style>