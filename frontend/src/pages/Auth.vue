<template>
  <div class="auth-root">
    <div v-if="loadingStage" class="auth-loading">
      <div class="loader-spinner"></div>
      <div class="loader-stage">{{ loadingStage }}</div>
    </div>
    <form v-else @submit.prevent="mode === 'login' ? doLogin() : doRegister()">
      <h2>{{ mode === 'login' ? 'Login' : 'Register' }}</h2>
      <div class="input-group">
        <input v-model="email" placeholder="Email" @blur="validateEmail" :class="{invalid: emailError}" />
        <span v-if="emailError" class="input-error">{{ emailError }}</span>
      </div>
      <div class="input-group password-group">
        <input :type="showPassword ? 'text' : 'password'" v-model="password" placeholder="Password" @input="onPasswordInput" />
        <div type="button" class="eye-btn" @click="togglePassword">
          <span class="moon-emoji" :class="moonAnimClass('password')">{{ moonEmojiPassword }}</span>
        </div>
      </div>
      <div v-if="mode === 'register' && password.length > 0" class="input-group password-group">
        <input :type="showConfirm ? 'text' : 'password'" v-model="confirmPassword" placeholder="Confirm password" />
        <div type="button" class="eye-btn" @click="toggleConfirm">
          <span class="moon-emoji" :class="moonAnimClass('confirm')">{{ moonEmojiConfirm }}</span>
        </div>
      </div>
      <span v-if="mode === 'register' && confirmPassword && password !== confirmPassword" class="input-error">Passwords do not match</span>
      <button v-if="mode === 'login'" type="submit">Login</button>
      <button v-else type="submit" :disabled="!canRegister">Register</button>
      <p v-if="error" style="color:red;">{{ error }}</p>
      <button class="mode-switch" type="button" @click="switchMode">
        {{ mode === 'login' ? 'Do not have an account? Register ' : 'Already have an account? Login ' }}
      </button>
      <div class="oauth-section">
        <div class="oauth-divider">Or login with</div>
        <button class="oauth-btn google" type="button" @click="oauthGoogle">Google</button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useUserStore } from '../stores/user';
import { storeToRefs } from 'pinia';

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
const { loginStage } = storeToRefs(userStore);
const loadingStage = computed(() => loginStage.value);

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
  userStore.loginStage = 'Sending requests...';
  const result = await userStore.login(email.value, password.value);
  if (result.ok) {
    userStore.loginStage = '';
    router.push(`/${userStore.currentUser.nickname}/home`);
  } else {
    error.value = result.error || 'Invalid credentials or server unavailable';
    userStore.loginStage = '';
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
  loadingStage.value = 'Sending requests...';
  const result = await userStore.register(email.value, password.value);
  if (result.ok) {
    loadingStage.value = 'Response received. Loading...';
    router.push(`/${userStore.currentUser.nickname}/home`);
  } else {
    error.value = result.error || 'Registration failed or server unavailable';
    loadingStage.value = '';
  }
}

function oauthGoogle() {
  window.location.href = '/oauth/google/login';
}

const moonFramesOpen = ['🌑','🌘','🌗','🌖','🌕']
const moonFramesClose = ['🌕','🌔','🌓','🌒','🌑']
const moonEmojiPassword = ref('🌑')
const moonEmojiConfirm = ref('🌑')
const moonAnimPassword = ref('')
const moonAnimConfirm = ref('')

function animateMoon(isOpen, targetRef, animRef) {
  const frames = isOpen ? moonFramesOpen : moonFramesClose
  let i = 0
  animRef.value = 'animating'
  const interval = setInterval(() => {
    targetRef.value = frames[i]
    i++
    if (i >= frames.length) {
      clearInterval(interval)
      animRef.value = ''
    }
  }, 45)
}
function togglePassword() {
  showPassword.value = !showPassword.value
  animateMoon(showPassword.value, moonEmojiPassword, moonAnimPassword)
}
function toggleConfirm() {
  showConfirm.value = !showConfirm.value
  animateMoon(showConfirm.value, moonEmojiConfirm, moonAnimConfirm)
}
function moonAnimClass(type) {
  return type === 'password' ? moonAnimPassword.value : moonAnimConfirm.value
}
</script>

<style scoped>
.auth-root {
  min-width: 400px;
  min-height: 480px;
  position: absolute;
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
  justify-self: center;
  text-align: center;
  padding: 32px;
  color: #fff;
  background: rgba(255,255,255,0.18);
  border-radius: 18px;
  box-shadow: 0 2px 32px 0 rgba(0,0,0,0.18);
  display: flex;
  flex-direction: column;
  gap: 16px;
  backdrop-filter: blur(18px) saturate(1.5);
  -webkit-backdrop-filter: blur(18px) saturate(1.5);
  border: 1.5px solid rgba(255,255,255,0.25);
}
.auth-root h2 {
  font-size: 2.5em;
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
  background: rgba(255,255,255,0.18);
  border: 1px solid rgba(255,255,255,0.25);
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
  font-size: 1.5em;
  cursor: pointer;
  z-index: 2;
  width: 2.2em;
  height: 2.2em;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: color 0.2s;
}
@keyframes moon-open {
  0%   { content: '"🌑"'; }
  25%  { content: '"🌘"'; }
  50%  { content: '"🌗"'; }
  75%  { content: '"🌖"'; }
  100% { content: '"🌕"'; }
}
@keyframes moon-close {
  0%   { content: '"🌕"'; }
  25%  { content: '"🌔"'; }
  50%  { content: '"🌓"'; }
  75%  { content: '"🌒"'; }
  100% { content: '"🌑"'; }
}
.eye-btn .moon-emoji {
  display: inline-block;
  will-change: content;
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
  background: rgba(255,255,255,0.18);
  color: #fff;
  border: 1px solid rgba(255,255,255,0.25);
  box-shadow: 0 1px 4px rgba(66,133,244,0.08);
  font-weight: bold;
  transition: background 0.2s, color 0.2s;
}
.oauth-btn.google:hover {
  background: rgba(255,255,255,0.25);
  color: #5f99f5;
  border-color: #5f99f5;
}
.oauth-divider {
  margin-bottom: 8px;
}
.invalid {
  border: 1px solid #ff4444;
}
.auth-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 320px;
  gap: 24px;
}
.loader-spinner {
  width: 48px;
  height: 48px;
  border: 5px solid #fff;
  border-top: 5px solid #ff4444;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}
@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
.loader-stage {
  font-size: 1.2em;
  color: #fff;
  margin-top: 8px;
}
</style>
