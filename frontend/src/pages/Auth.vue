<template>
  <div class="auth-root">
    <form @submit.prevent="mode === 'login' ? doLogin() : doRegister()">
      <h2>{{ mode === 'login' ? 'Login' : 'Register' }}</h2>
      <div class="input-group">
        <input v-model="email" placeholder="Email" @blur="validateEmail" :class="{invalid: emailError}" />
        <span v-if="emailError" class="input-error">{{ emailError }}</span>
      </div>
      <div class="input-group password-group">
        <input :type="showPassword ? 'text' : 'password'" v-model="password" placeholder="Password" @input="onPasswordInput" />
        <div type="button" class="eye-btn" @click="showPassword = !showPassword">
          <span v-if="showPassword">👁️</span>
          <span v-else>🙈</span>
        </div>
      </div>
      <div v-if="mode === 'register' && password.length > 0" class="input-group password-group">
        <input :type="showConfirm ? 'text' : 'password'" v-model="confirmPassword" placeholder="Confirm password" />
        <div type="button" class="eye-btn" @click="showConfirm = !showConfirm">
          <span v-if="showConfirm">👁️</span>
          <span v-else>🙈</span>
        </div>
      </div>
      <span v-if="mode === 'register' && confirmPassword && password !== confirmPassword" class="input-error">Passwords do not match</span>
      <button v-if="mode === 'login'" type="submit">Login</button>
      <button v-else type="submit" :disabled="!canRegister">Register</button>
      <p v-if="error" style="color:red;">{{ error }}</p>
      <button class="mode-switch" type="button" @click="switchMode">
        {{ mode === 'login' ? 'Нет аккаунта? Зарегистрироваться' : 'Уже есть аккаунт? Войти' }}
      </button>
      <div class="oauth-section">
        <div class="oauth-divider">или войти через</div>
        <button class="oauth-btn google" type="button" @click="oauthGoogle">Google</button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useUserStore } from '../stores/user';

const email = ref('');
const password = ref('');
const confirmPassword = ref('');
const error = ref('');
const emailError = ref('');
const mode = ref('login');
const showPassword = ref(false);
const showConfirm = ref(false);
const userStore = useUserStore();
const router = useRouter();
const route = useRoute();

onMounted(() => {
  if (route.query.mode === 'register') {
    mode.value = 'register';
  }
});

function switchMode() {
  mode.value = mode.value === 'login' ? 'register' : 'login';
  error.value = '';
  confirmPassword.value = '';
  emailError.value = '';
}

function validateEmail() {
  if (!email.value) {
    emailError.value = '';
    return;
  }
  // Простая валидация email
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!re.test(email.value)) {
    emailError.value = 'Invalid email format';
  } else {
    emailError.value = '';
  }
}

function onPasswordInput() {
  if (mode.value === 'register' && confirmPassword.value) {
    confirmPassword.value = '';
  }
}

const canRegister = computed(() => {
  return (
    email.value &&
    password.value &&
    confirmPassword.value &&
    password.value === confirmPassword.value &&
    !emailError.value
  );
});

async function doLogin() {
  error.value = '';
  if (!email.value || !password.value) {
    error.value = 'Email and password required';
    return;
  }
  if (emailError.value) {
    error.value = emailError.value;
    return;
  }
  console.log('[LOGIN] UI sending:', { email: email.value, password: password.value });
  const result = await userStore.login(email.value, password.value);
  if (result.ok) {
    router.push(`/${userStore.currentUser.nickname}/home`);
  } else {
    error.value = result.error || 'Invalid credentials or server unavailable';
  }
}

async function doRegister() {
  error.value = '';
  validateEmail();
  if (emailError.value) {
    error.value = emailError.value;
    return;
  }
  if (!canRegister.value) {
    error.value = 'Fill all fields correctly';
    return;
  }
  console.log('[REGISTER] UI sending:', { email: email.value, password: password.value });
  const result = await userStore.register(email.value, password.value);
  if (result.ok) {
    router.push(`/${userStore.currentUser.nickname}/home`);
  } else {
    error.value = result.error || 'Registration failed or server unavailable';
  }
}

function oauthGoogle() {
  window.location.href = '/oauth/google/login';
}
</script>

<style scoped>
.auth-root {
  max-width: 400px;
  margin: 60px auto;
  padding: 32px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 16px rgba(0,0,0,0.07);
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.input-group {
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 2px;
  margin-bottom: 8px;
}
.password-group {
  flex-direction: row;
  align-items: center;
}
input {
  padding: 10px 16px;
  border-radius: 8px;
  border: 1px solid #eee;
  font-size: 1em;
  flex: 1 1 auto;
}
button {
  padding: 10px 0;
  border-radius: 8px;
  border: none;
  background: #ff4444;
  color: #fff;
  font-weight: bold;
  font-size: 1em;
  cursor: pointer;
  width: 100%;
  margin-bottom: 8px;
}
button:disabled {
  background: #ccc;
  cursor: not-allowed;
}
.eye-btn {
  background: none;
  border: none;
  font-size: 1.2em;
  cursor: pointer;
  z-index: 2;
}
.input-error {
  color: #ff4444;
  font-size: 0.95em;
  margin-top: 2px;
  margin-bottom: 2px;
}
.mode-switch {
  background: none;
  color: #ff4444;
  border: none;
  font-size: 0.95em;
  margin-top: 8px;
  cursor: pointer;
  width: 100%;
  margin-bottom: 0;
  text-align: center;
}
.auth-root form {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.oauth-section {
  margin-top: 18px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  align-items: center;
}
.oauth-btn {
  width: 100%;
  margin-bottom: 8px;
}
.oauth-btn.google {
  background: #fff;
  color: #222;
  border: 1px solid #eee;
  box-shadow: 0 1px 4px rgba(66,133,244,0.08);
  font-weight: bold;
  transition: background 0.2s, color 0.2s;
}
.oauth-btn.google:hover {
  background: #f5f5f5;
  color: #174ea6;
  border-color: #4285f4;
}
.oauth-divider {
  margin-bottom: 8px;
}
.invalid {
  border: 1px solid #ff4444;
}
</style>
