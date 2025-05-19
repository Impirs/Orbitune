<template>
  <div class="yandex-auth-bg">
    <div class="yandex-auth-container">
      <img src="" alt="Yandex" class="yandex-logo" />
      <h2>Вход в Яндекс.Музыку</h2>
      <form @submit.prevent="onSubmit">
        <div class="form-group">
          <label for="login">Логин Яндекса</label>
          <input v-model="login" id="login" type="text" required autocomplete="username" />
        </div>
        <div class="form-group">
          <label for="password">Пароль</label>
          <input v-model="password" id="password" type="password" required autocomplete="current-password" />
        </div>
        <button type="submit" :disabled="loading">Войти</button>
        <div v-if="error" class="error-block">{{ error }}</div>
        <div v-if="success" class="success-block">Авторизация успешна! XToken сохранён.</div>
      </form>
      <div class="yandex-auth-hint">
        <small>Данные используются только для получения XToken Яндекс.Музыки и не сохраняются.</small>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import axios from 'axios';
import { useUserStore } from '../../stores/user';
import { useRouter } from 'vue-router';

const login = ref('');
const password = ref('');
const loading = ref(false);
const error = ref('');
const success = ref(false);
const userStore = useUserStore();
const router = useRouter();

async function onSubmit() {
  error.value = '';
  success.value = false;
  loading.value = true;
  try {
    const user_id = userStore.currentUser?.id;
    if (!user_id) {
      error.value = 'Сначала выполните вход в Orbitune.';
      loading.value = false;
      return;
    }
    const res = await axios.post('/yandex_music/xtoken', {
      user_id,
      login: login.value,
      password: password.value
    });
    if (res.data && res.data.ok) {
      success.value = true;
      setTimeout(() => router.replace({ name: 'UserHome' }), 1500);
    } else {
      error.value = res.data?.detail || 'Ошибка авторизации';
    }
  } catch (e) {
    error.value = e?.response?.data?.detail || e?.message || 'Ошибка авторизации';
  } finally {
    loading.value = false;
  }
}
</script>

<style scoped>
.yandex-auth-bg {
  min-height: 100vh;
  background: #191919 url('https://yastatic.net/s3/passport-auth-customs/customs/_/b/2/b2e2b7b2-7e2e-4e2e-8e2e-2e2e2e2e2e2e.svg') no-repeat center 80px;
  background-size: 120px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.yandex-auth-container {
  background: #232323;
  border-radius: 18px;
  box-shadow: 0 4px 32px rgba(0,0,0,0.18);
  padding: 40px 32px 28px 32px;
  min-width: 340px;
  display: flex;
  flex-direction: column;
  align-items: center;
}
.yandex-logo {
  width: 64px;
  margin-bottom: 18px;
}
h2 {
  color: #fff;
  margin-bottom: 24px;
}
.form-group {
  margin-bottom: 18px;
  width: 100%;
}
label {
  color: #bbb;
  font-size: 1em;
  margin-bottom: 6px;
  display: block;
}
input {
  width: 100%;
  padding: 10px 12px;
  border-radius: 8px;
  border: 1px solid #444;
  background: #181818;
  color: #fff;
  font-size: 1.1em;
}
button {
  width: 100%;
  padding: 12px;
  background: #ffdb4d;
  color: #222;
  border: none;
  border-radius: 8px;
  font-size: 1.1em;
  font-weight: bold;
  cursor: pointer;
  margin-top: 8px;
  transition: background 0.15s;
}
button:disabled {
  background: #ffe9a7;
  color: #888;
  cursor: not-allowed;
}
.error-block {
  color: #ff4444;
  margin-top: 16px;
  font-weight: bold;
}
.success-block {
  color: #1db954;
  margin-top: 16px;
  font-weight: bold;
}
.yandex-auth-hint {
  margin-top: 18px;
  color: #888;
  font-size: 0.95em;
  text-align: center;
}
</style>
