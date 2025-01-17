<template>
  <div class="flex items-center justify-center min-h-screen">
    <img src="@/assets/images/login.png" class="min-h-screen w-1/2 object-cover hidden lg:block brightness-75" alt="Scotty">
    <div class="flex flex-col items-center space-y-8 lg:w-1/2">
      <div class="flex items-center text-3xl font-bold text-center">
        <img src="@/assets/images/icon.png" class="me-4" alt="Icon"> Scotty
      </div>
      <div class="w-full lg:w-1/2">
        <div class="flex-col space-y-8">
          <div class="flex flex-col space-y-2">
            <label for="username" class="font-bold">Benutzername</label>
            <InputText id="username" v-model="username" placeholder="Text einfügen..."/>
          </div>
          <div class="flex flex-col space-y-2">
            <label for="password" class="font-bold">Passwort</label>
            <Password id="password" v-model="password" placeholder="Text einfügen..." toggleMask :feedback="false"/>
          </div>
          <Message v-if="wrongCredentials" severity="error" :closable="false">
            <div class="text-sm">Oops! Es scheint, dass Benutzername / Passwort falsch ist.</div>
          </Message>
          <ScotButton label="Anmelden" icon="pi pi-user" variant="blue" @click="login" class="w-full"/>
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

function login() {
  if (userStore.authenticate(username.value, password.value)) {
    router.push("/rideExecutions")
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