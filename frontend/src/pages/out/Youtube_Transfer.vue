<template>
    <div class="youtube-transfer">
        <div class="transfer-header">
            <h2>Select playlists to import from YouTube</h2>
        </div>
        <div class="transfer-content">
            <div v-if="loading" class="loader">Loading playlists...</div>
            <div v-else-if="error" class="error-block">{{ error }}</div>
            <div v-else class="playlist-list">
                <div v-for="pl in playlists" :key="pl.id" class="playlist-row">
                    <input type="checkbox"
                        :checked="isChecked(pl.id)"
                        @change="() => toggleCheckbox(pl.id)"
                        :style="checkboxStyle(pl.id)"
                    />
                    <img :src="pl.cover_url || fallbackCover" class="playlist-cover" />
                    <div class="playlist-info">
                        <h3 class="playlist-title">{{ pl.title }}</h3>
                        <span v-if="importedIds.includes(pl.id)" :style="importedLabelStyle(pl.id)">
                            {{ importedLabel(pl.id) }}
                        </span>
                    </div>
                    <span class="playlist-count">{{ pl.tracks_count }} tracks</span>
                </div>
            </div>
            <div class="transfer-contoller">
                <button v-if="showCancel" class="cancel-btn" @click="goBack">Cancel</button>
                <button class="import-btn" :disabled="importing || (((toImport?.value?.length || 0) === 0) && ((toDelete?.value?.length || 0) === 0))" @click="importSelected">
                    Apply Changes
                </button>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import axios from 'axios';

const playlists = ref([]);
const importedIds = ref([]); // store already imported external_ids
const loading = ref(true);
const error = ref('');
const importing = ref(false);
const fallbackCover = new URL('../../assets/music_universe.png', import.meta.url).href;
const route = useRoute();
const router = useRouter();

// --- определяем источник перехода ---
const from = ref(route.query.from || 'settings');
const showCancel = computed(() => from.value === 'settings');

// --- состояние чекбоксов ---
// { [id]: 'import' | 'ignore' | 'keep' | 'delete' }
const checkboxState = ref({});

onMounted(async () => {
    loading.value = true;
    error.value = '';
    try {
        const user = JSON.parse(localStorage.getItem('currentUser'));
        const userId = user?.id;
        if (!userId) throw new Error('User not found');
        // 1. Fetch imported playlists from DB
        const importedRes = await axios.get('/playlists', { params: { user_id: userId, platform: 'youtube' }, withCredentials: true });
        importedIds.value = (importedRes.data.playlists || []).map(pl => pl.external_id);
        // 2. Fetch YouTube playlists from API
        const res = await axios.get(`/youtube/fetch_temp_data?user_id=${userId}`, { withCredentials: true });
        playlists.value = res.data.playlists || [];
        // 3. Инициализация состояния чекбоксов
        playlists.value.forEach(pl => {
            if (importedIds.value.includes(pl.id)) {
                checkboxState.value[pl.id] = 'keep'; // уже импортирован — оставить
            } else {
                checkboxState.value[pl.id] = 'ignore'; // не импортирован — не импортировать
            }
        });
    } catch (e) {
        error.value = e?.response?.data?.detail || e?.message || 'Failed to load playlists';
    } finally {
        loading.value = false;
    }
});

function isChecked(id) {
    // Для новых: import — true, ignore — false
    // Для импортированных: keep — true, delete — false
    return checkboxState.value[id] === 'import' || checkboxState.value[id] === 'keep';
}
function checkboxStyle(id) {
    if (importedIds.value.includes(id)) {
        // Импортированные: зелёный если keep, красный если delete
        return checkboxState.value[id] === 'keep' ? 'accent-color:#3fb758;' : 'accent-color:#ea1644;';
    } else {
        // Новые: зелёный если import, прозрачный если ignore
        return checkboxState.value[id] === 'import' ? 'accent-color:#3fb758;' : 'accent-color:transparent;';
    }
}
function importedLabel(id) {
    if (!importedIds.value.includes(id)) return '';
    return checkboxState.value[id] === 'keep' ? 'Already imported' : 'Will be deleted';
}
function importedLabelStyle(id) {
    if (!importedIds.value.includes(id)) return '';
    return checkboxState.value[id] === 'keep' ? 'color:#1db954;' : 'color:#ea1644;';
}
function toggleCheckbox(id) {
    if (importedIds.value.includes(id)) {
        // Импортированные: keep <-> delete
        checkboxState.value[id] = checkboxState.value[id] === 'keep' ? 'delete' : 'keep';
    } else {
        // Новые: import <-> ignore
        checkboxState.value[id] = checkboxState.value[id] === 'import' ? 'ignore' : 'import';
    }
}
function goBack() {
    router.back();
}

const toImport = computed(() => Array.isArray(playlists.value)
    ? playlists.value.filter(pl => !importedIds.value.includes(pl.id) && checkboxState.value[pl.id] === 'import')
    : []);
const toDelete = computed(() => Array.isArray(playlists.value)
    ? playlists.value.filter(pl => importedIds.value.includes(pl.id) && checkboxState.value[pl.id] === 'delete')
    : []);

async function importSelected() {
    if (importing.value) return;
    importing.value = true;
    try {
        const user = JSON.parse(localStorage.getItem('currentUser'));
        const userId = user?.id;
        if (!userId) throw new Error('User not found');
        // Удаление отмеченных на удаление
        for (const pl of toDelete.value) {
            await axios.post('/youtube/delete_playlist', { user_id: userId, external_id: pl.id }, { withCredentials: true });
        }
        // Импорт отмеченных
        if (toImport.value.length > 0) {
            await axios.post('/youtube/import_playlists', { user_id: userId, playlists: toImport.value }, { withCredentials: true });
        }
        window.location.href = `/${user?.nickname || 'user'}/home`;
    } catch (e) {
        error.value = e?.response?.data?.detail || e?.message || 'Import failed';
    } finally {
        importing.value = false;
    }
}
</script>

<style scoped>
.youtube-transfer {
    position: absolute;
    left: 50%;
    top: 50%;
    transform: translate(-50%, -50%);
    height: 760px;
    width: 720px;
    justify-self: center;
    text-align: center;
    padding: 16px 20px 16px 32px;
    color: #fff;
    background: rgba(255,255,255,0.18);
    border-radius: 18px;
    box-shadow: 0 2px 32px 0 rgba(0,0,0,0.18);
    display: flex;
    flex-direction: column;
    backdrop-filter: blur(18px) saturate(1.5);
    border: 1.5px solid rgba(255,255,255,0.25);
}
.transfer-header {
    padding-right: 12px;
}
.transfer-header h2 {
    margin-bottom: 16px;
    font-size: 2em;
}
.transfer-content {
    position: relative;
    height: calc(100% - 64px);
}
/* --- playlists --- */
.playlist-list {
    display: flex;
    position: relative;
    flex-direction: column;
    overflow-y: auto;
    padding-right: 4px;
    gap: 8px;
    height: calc(100% - 52px);
}
.playlist-row {
  display: flex;
  align-items: center;
  gap: 16px;
  background: rgba(255,255,255,0.06);
  border-radius: 10px;
  padding: 10px 32px 10px 16px;
}
.playlist-cover {
  width: 64px;
  height: 64px;
  border-radius: 8px;
  object-fit: cover;
  background: #222;
}
.playlist-info {
    flex-direction: column;
    flex: 1;
    padding-left: 8px;
    text-align: left;
}
.playlist-title {
    margin: 0;
    font-size: 1.3em;
    font-weight: 600;
}
.playlist-count {
  font-size: 0.98em;
  color: #bbb;
}
/* --- buttons --- */
.transfer-contoller{
    display: flex;
    justify-content: space-between;
    align-items: center;
    height: 48px;
}
.cancel-btn{
    height: 32px;
    width: 160px;
    padding: 10px auto;
    border-radius: 12px;
    background: #1db954;
    color: #fff;
    font-weight: bold;
    border: none;
    font-size: 1.1em;
    cursor: pointer;
    transition: background 0.18s;
}
.import-btn {
    height: 32px;
    width: 160px;
    padding: 10px auto;
    border-radius: 12px;
    background: #1db954;
    color: #fff;
    font-weight: bold;
    border: none;
    font-size: 1.1em;
    cursor: pointer;
    transition: background 0.18s;
}
.import-btn:disabled {
    background: #444;
    cursor: not-allowed;
}
.loader, .error-block {
    display: flex;
    height: calc(100% - 52px);
    align-items: center;
    justify-content: center;
    color: #bbb;
}
.error-block {
    color: #ff4444;
}
</style>
