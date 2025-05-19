<template>
  <div class="content-settings">
    <h2>Settings</h2>
    <p>Manage your connected services:</p>
    <div v-if="userStore.loading" class="loader">Loading services...</div>
    <div v-else-if="userStore.error" class="error-block">{{ userStore.error }}</div>
    <div class="services-list" v-else>
      <div v-for="service in userStore.connectedServices" :key="service.platform" class="service-item">
        <span class="service-name">{{ service.platform }}</span>
        <button v-if="!service.is_connected" @click="connect(service.platform)">Connect</button>
        <button v-else @click="disconnect(service.platform)">Disconnect</button>
      </div>
    </div>
    <div class="oauth-auth-block">
      <h3>Authorize new service</h3>
      <button class="oauth-btn google" @click="connect('google')">Connect Google</button>
      <button class="oauth-btn spotify" @click="connect('spotify')">Connect Spotify</button>
      <!-- <div class="yandex-auth-collapsible">
        <button class="oauth-btn yandex" @click="toggleYandex">Connect Yandex</button>
        <div v-if="showYandex" class="yandex-instructions">
          <ol>
            <li>Перейдите на <a href="https://music.yandex.ru" target="_blank">music.yandex.ru</a> и войдите в свой аккаунт.</li>
            <li>Откройте инструменты разработчика (F12), вкладка <b>Application</b> → <b>Cookies</b> → <b>music.yandex.ru</b> или <b>localStorage</b>.</li>
            <li>Найдите токен <b>"yandex_gid"</b>, <b>"Session_id"</b> или <b>"access-token"/"xtoken"</b> (обычно в localStorage или cookies).</li>
            <li>Скопируйте значение токена и вставьте в поле ниже.</li>
          </ol>
          <input v-model="manualXToken" placeholder="Вставьте ваш xtoken" style="width: 100%; margin-bottom: 8px;" />
          <button @click="saveManualXToken" :disabled="savingXToken || !manualXToken">Сохранить токен</button>
          <div v-if="xTokenError" class="error-block">{{ xTokenError }}</div>
          <div v-if="xTokenSuccess" class="success-block">Токен сохранён!</div>
        </div>
      </div> -->
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useUserStore } from '../stores/user';
import axios from 'axios';
import { useRouter } from 'vue-router';

const userStore = useUserStore();
const router = useRouter();
const showYandex = ref(false);
const manualXToken = ref('');
const savingXToken = ref(false);
const xTokenError = ref('');
const xTokenSuccess = ref(false);

onMounted(() => {
  userStore.fetchConnectedServices();
});

function connect(platform) {
  if (platform === 'google') {
    window.location.href = '/oauth/google/login';
  } else if (platform === 'spotify') {
    window.location.href = '/oauth/spotify/login';
  } else if (platform === 'yandex') {
    toggleYandex();
  }
}

function toggleYandex() {
  showYandex.value = !showYandex.value;
  xTokenError.value = '';
  xTokenSuccess.value = false;
}
// No need in case of Yandex music politics rn
async function saveManualXToken() {
  xTokenError.value = '';
  xTokenSuccess.value = false;
  savingXToken.value = true;
  try {
    const user_id = userStore.currentUser?.id;
    if (!user_id) {
      xTokenError.value = 'Сначала выполните вход в Orbitune.';
      savingXToken.value = false;
      return;
    }
    const res = await axios.post('/yandex_music/xtoken', {
      user_id,
      xtoken: manualXToken.value
    });
    if (res.data && res.data.ok) {
      xTokenSuccess.value = true;
      setTimeout(() => {
        xTokenSuccess.value = false;
        showYandex.value = false;
        userStore.fetchConnectedServices();
      }, 1200);
    } else {
      xTokenError.value = res.data?.detail || 'Ошибка сохранения токена';
    }
  } catch (e) {
    xTokenError.value = e?.response?.data?.detail || e?.message || 'Ошибка сохранения токена';
  } finally {
    savingXToken.value = false;
  }
}

function disconnect(platform) {
  if (!platform) return;
  if (!confirm('Disconnect ' + platform + '?')) return;
  userStore.loading = true;
  userStore.error = '';
  axios.delete('/connected_services', {
    params: { user_id: userStore.currentUser.id, platform },
    withCredentials: true
  })
    .then(() => {
      userStore.fetchConnectedServices();
      userStore.fetchPlaylists();
      userStore.fetchFavoritesFull();
      userStore.error = '';
      setTimeout(() => {}, 0);
    })
    .catch(e => {
      userStore.error = e?.response?.data?.detail || e?.message || 'Failed to disconnect';
    })
    .finally(() => {
      userStore.loading = false;
    });
}
</script>

<style scoped>
.content-settings {
  padding: 32px;
}
.loader {
  color: #888;
  margin: 24px 0;
}
.error-block {
  color: #ff4444;
  margin: 24px 0;
  font-weight: bold;
}
.services-list {
  margin-top: 24px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.service-item {
  display: flex;
  align-items: center;
  gap: 16px;
}
.service-name {
  font-weight: bold;
  text-transform: capitalize;
}
button {
  padding: 6px 18px;
  border-radius: 8px;
  border: none;
  background: #ff4444;
  color: #fff;
  font-weight: bold;
  cursor: pointer;
}
.oauth-auth-block {
  margin-top: 32px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.oauth-btn.google {
  background: #fff;
  color: #222;
  border: 1px solid #eee;
}
.oauth-btn.spotify {
  background: #1db954;
  color: #fff;
}
.oauth-btn.yandex {
  background: #f2412e;
  color: #222;
  border: 1px solid #eee;
}
.yandex-auth-collapsible {
  margin-top: 12px;
}
.yandex-instructions {
  background: #fffbe6;
  border: 1px solid #ffe58f;
  border-radius: 6px;
  padding: 16px;
  margin-top: 8px;
}
.success-block {
  color: #389e0d;
  margin-top: 8px;
}
.error-block {
  color: #cf1322;
  margin-top: 8px;
}
</style>
