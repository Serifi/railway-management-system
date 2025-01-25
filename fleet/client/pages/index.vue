<template>
  <div class="flex items-center justify-center min-h-screen">
    <!-- Left half of the screen -->
    <img src="@/assets/images/login.png" class="min-h-screen w-1/2 object-cover hidden lg:block brightness-75" alt="Scotty">

    <!-- Right half of the screen -->
    <div class="flex flex-col items-center space-y-8 lg:w-1/2">
      <!-- Icon with title -->
      <div class="flex items-center text-3xl font-bold text-center">
        <img src="@/assets/images/icon.png" class="me-4 w-16 h-16" alt="Icon"> Scotty
      </div>
      <div class="w-full lg:w-1/2">
        <div class="flex-col space-y-8">
          <!-- Login form -->
          <div class="flex flex-col space-y-2">
            <label for="username" class="font-bold">{{ $t('username') }}</label>
            <InputText id="username" v-model="username" :placeholder="$t('textPlaceholder')"/>
          </div>
          <div class="flex flex-col space-y-2">
            <label for="password" class="font-bold">{{ $t('password') }}</label>
            <Password id="password" v-model="password" :placeholder="$t('textPlaceholder')" toggleMask :feedback="false"/>
          </div>
          <Message v-if="wrongCredentials" severity="error" :closable="false">
            <div class="text-sm">{{ $t('wrongCredentials') }}</div>
          </Message>
          <ScotButton :label="$t('login')" icon="pi pi-user" variant="blue" @click="login" class="w-full"/>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from "vue"
import { useUserStore } from '@/stores/user'
import { useRouter } from "vue-router"

const userStore = useUserStore()
const router = useRouter()
const username = ref("")
const password = ref("")
const wrongCredentials = ref(false)
const disableButton = ref(true)

async function login() {
  const success = await userStore.login(username.value, password.value)
  if (success) {
    await router.push("/trains")
  } else {
    wrongCredentials.value = true
    setTimeout(() => (wrongCredentials.value = false), 3000)
  }
}
watch([username, password], () => disableButton.value = !username.value || !password.value)
</script>

<style>
.p-password .p-password-input {
  width: 100% !important;
}
</style>