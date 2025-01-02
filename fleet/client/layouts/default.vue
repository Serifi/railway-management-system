<template>
  <div class="flex flex-col min-h-screen">
    <!-- Header -->
    <header class="flex items-center justify-between py-4 border-b">
      <!-- Left: Icon and Scotty -->
      <div class="flex items-center space-x-4 me-4">
        <img src="../assets/images/icon.png" alt="Icon" class="w-12 h-12">
        <span class="text-xl font-bold">Scotty</span>
      </div>

      <!-- Middle: Navigation -->
      <Navigation />

      <!-- Right: User -->
      <div class="flex items-center space-x-4 mx-4">
        <ScotIcon icon="pi pi-language" @click="toggleLanguagePopover" />
        <ScotPopover ref="languagePopover" :items="languageItems" @item-click="setLanguage" class="rounded shadow"/>

        <ScotIcon icon="fa-solid fa-circle-half-stroke" @click="toggleThemePopover" />
        <ScotPopover ref="themePopover" :items="themeItems" @item-click="setTheme" class="rounded shadow"/>

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
            <div>{{ $t('logout') }}</div>
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
import { useI18n } from 'vue-i18n'
import Navigation from '~/components/ScotNavigation.vue'

const router = useRouter()
const userStore = useUserStore()
const userPanel = ref(null)
const { t, locale } = useI18n({ useScope: 'global' })

const userFullName = computed(() => userStore.getFullName)
const userRole = computed(() => userStore.getUserRole)

function showUserPanel() { userPanel.value.toggle(event) }
function logout(){
  userStore.logout()
  router.push('/')
}

const languagePopover = ref(null);
function toggleLanguagePopover(event) {
  languagePopover.value.toggle(event);
}

const languages = [
  { code: 'de', name: 'German', locale: 'de' },
  { code: 'gb', name: 'English', locale: 'en' }
];

const languageItems = languages.map(language => ({
  name: language.name,
  locale: language.locale,
  iconComponent: 'country-flag',
  iconProps: { country: language.code, size: 'small' }
}));

function setLanguage(language) {
  locale.value = language.locale;
}

const themePopover = ref(null);
function toggleThemePopover(event) {
  themePopover.value.toggle(event);
}

const themes = [
  { name: 'Light', iconComponent: 'i', iconProps: { class: 'pi pi-sun text-xs' } },
  { name: 'Dark', iconComponent: 'i', iconProps: { class: 'pi pi-moon text-xs' } },
  { name: 'System', iconComponent: 'i', iconProps: { class: 'pi pi-sync text-xs' } }
];

const themeItems = themes.map(theme => ({
  key: theme.key,
  name: theme.name,
  iconComponent: theme.iconComponent,
  iconProps: theme.iconProps
}));

function setTheme(theme) {
  if (theme.name === 'Dark') {
    document.documentElement.classList.add('dark');
    document.documentElement.setAttribute('data-theme', 'dark');
    localStorage.setItem('theme', 'dark');
  } else if (theme.name === 'Light') {
    document.documentElement.classList.remove('dark');
    document.documentElement.setAttribute('data-theme', 'light');
    localStorage.setItem('theme', 'light');
  } else if (theme.name === 'System') {
    const systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    document.documentElement.classList.toggle('dark', systemTheme === 'dark');
    document.documentElement.setAttribute('data-theme', systemTheme);
    localStorage.setItem('theme', systemTheme);
  }
}

onMounted(() => {
  const savedTheme = localStorage.getItem('theme');
  if (savedTheme) {
    setTheme({name: savedTheme.charAt(0).toUpperCase() + savedTheme.slice(1)});
  } else {
    const systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    setTheme({name: systemTheme.charAt(0).toUpperCase() + systemTheme.slice(1)});
  }

  const savedLanguage = localStorage.getItem('language');
  if (savedLanguage) setLanguage({locale: savedLanguage});
});
</script>