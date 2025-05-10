<template>
  <div>
    <h2>Login</h2>
    <input v-model="username" placeholder="Username" />
    <input v-model="password" type="password" placeholder="Password" />
    <button @click="login">Login</button>
    <p v-if="error" style="color:red;">{{ error }}</p>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useUserStore } from '../stores/user';

const username = ref('');
const password = ref('');
const error = ref('');
const userStore = useUserStore();
const router = useRouter();

function login() {
  if (userStore.login(username.value, password.value)) {
    router.push(`/${userStore.currentUser}/home`);
  } else {
    error.value = 'Invalid credentials';
  }
}
</script>
