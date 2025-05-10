<template>
  <div>
    <h1>Welcome, {{ currentUser }}</h1>
    <button @click="logout">Logout</button>
  </div>
</template>

<script setup>
import { useUserStore } from '../stores/user';
import { useRouter } from 'vue-router';

const userStore = useUserStore();
const router = useRouter();
const currentUser = userStore.currentUser;

function logout() {
  userStore.logout();
  router.push('/');
}
</script>
