<template>
  <div class="flex items-center justify-center min-h-screen">
    <!-- Linkes Bild für größere Bildschirme -->
    <img src="@/assets/images/login.png" class="min-h-screen w-1/2 object-cover hidden lg:block brightness-75" alt="Scotty">

    <!-- Login-Bereich -->
    <div class="flex flex-col items-center space-y-8 lg:w-1/2">
      <!-- Logo und Titel -->
      <div class="flex items-center text-3xl font-bold text-center">
        <img src="@/assets/images/icon.png" class="me-4 w-16 h-16" alt="Icon"> Scotty
      </div>

      <!-- Eingabefelder und Anmeldebutton -->
      <div class="w-full lg:w-1/2">
        <div class="flex-col space-y-8">
          <!-- Benutzername -->
          <div class="flex flex-col space-y-2">
            <label for="username" class="font-bold">Benutzername</label>
            <InputText id="username" v-model="username" placeholder="Text eingeben..."/>
          </div>

          <!-- Passwort -->
          <div class="flex flex-col space-y-2">
            <label for="password" class="font-bold">Passwort</label>
            <Password id="password" v-model="password" placeholder="Text eingeben..." toggleMask :feedback="false"/>
          </div>

          <!-- Fehlernachricht bei falschen Anmeldedaten -->
          <Message v-if="wrongCredentials" severity="error" :closable="false">
            <div class="text-sm">Oops! Es scheint, dass Benutzername / Passwort falsch ist.</div>
          </Message>

          <!-- Anmeldebutton -->
          <ScotButton label="Anmelden" icon="pi pi-user" variant="blue" @click="login" class="w-full"/>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from "vue";
import { useUserStore } from '@/stores/user';
import { useRouter } from "vue-router";

const userStore = useUserStore();
const router = useRouter();
const username = ref("");
const password = ref("");
const wrongCredentials = ref(false);
const disableButton = ref(true);

// Login
async function login() {
  const success = await userStore.login(username.value, password.value);
  if (success) {
    // Bei erfolgreicher Anmeldung Weiterleitung zur Hauptseite
    await router.push("/train-stations");
  } else {
    // Bei fehlerhaften Anmeldedaten Anzeige einer Fehlermeldung
    wrongCredentials.value = true;
    setTimeout(() => (wrongCredentials.value = false), 3000);
  }
}

// Beobachtung der Eingabefelder zur Aktivierung/Deaktivierung des Buttons
watch([username, password], () => disableButton.value = !username.value || !password.value);
</script>

<style>
.p-password .p-password-input {
  width: 100% !important;
}
</style>