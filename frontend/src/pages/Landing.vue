<template>
  <div>
    <Navbar :user="userStore.currentUser" />
    <main>
      <!-- Feature Slides -->
      <section class="feature-slides">
        <button class="slide-btn left" @click="prevSlide"></button>
        <div class="slide-content">
          <h2>{{ slides[currentSlide].title }}</h2>
          <p>{{ slides[currentSlide].text }}</p>
        </div>
        <button class="slide-btn right" @click="nextSlide"></button>
        <div class="slide-progress-bar">
          <div class="slide-progress-bar__fill" :style="{ width: progress + '%' }"></div>
        </div>
      </section>

      <div class="content-divider"></div>
      <!-- Application Article -->
      <section class="app-article">
        <img class="img-placeholder" src="../assets/music_universe.png" alt="music_universe">
        <div class="text-content">
          <h2>Orbitune</h2>
          <blockquote class="app-quote">
            «<span v-html="quoteHtml"></span>»
          </blockquote>
        </div>
      </section>

      <!-- Welcome Section -->
      <section class="welcome-section">
        <h1>Welcome to Orbitune</h1>
        <router-link to="/auth?mode=register" class="register-btn"
          >Join Us</router-link
        >
      </section>
    </main>
    <Footer />
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import Navbar from '../components/Navbar.vue'
import Footer from '../components/Footer.vue'
import { useUserStore } from '../stores/user'

const userStore = useUserStore()

const slides = [
  {
    title: 'One link. Every platform.',
    text: 'Mix and listen music from different platforms.'
  },
  {
    title: 'Transfer. Discover. Repeat.',
    text: 'Transfer playlists to your favorite service.\nSearch for music through all platforms.'
  },
  {
    title: 'Your sound. Everywhere.',
    text: 'Share your music with your friends regardless of the restrictions.'
  }
]
const currentSlide = ref(0)
const progress = ref(0)
const SLIDE_DURATION = 5000
let interval = null
let progressInterval = null

function startProgress() {
  progress.value = 0
  if (progressInterval) clearInterval(progressInterval)
  const start = Date.now()
  progressInterval = setInterval(() => {
    const elapsed = Date.now() - start
    progress.value = Math.min(100, (elapsed / SLIDE_DURATION) * 100)
    if (progress.value >= 100) {
      clearInterval(progressInterval)
    }
  }, 16)
}

function resetSlideTimer() {
  if (interval) clearInterval(interval)
  if (progressInterval) clearInterval(progressInterval)
  startProgress()
  interval = setInterval(() => {
    nextSlide()
  }, SLIDE_DURATION)
}

function nextSlide() {
  currentSlide.value = (currentSlide.value + 1) % slides.length
  resetSlideTimer()
}
function prevSlide() {
  currentSlide.value = (currentSlide.value - 1 + slides.length) % slides.length
  resetSlideTimer()
}

onMounted(() => {
  resetSlideTimer()
})
onUnmounted(() => {
  clearInterval(interval)
  clearInterval(progressInterval)
})

// user: null если не залогинен, иначе объект пользователя
const user = ref(null) // для теста можно заменить на { name: 'User' }
const quote = ` Your music universe\nBe on your own orbite `
const quoteHtml = quote.replace(/\n/g, '<br>')
</script>

<style scoped>
.feature-slides {
  position: relative;
  height: 720px;
  display: flex;
  align-items: center;
  background: #090b17;
  color: #d0e7ef;
  border-bottom: 1px solid #162036bf;
  overflow: hidden;
}
.slide-btn {
  width: 280px;
  height: 100%;
  background: #16203640;
  border: none;
  cursor: pointer;
  transition: background 0.2s;
  z-index: 2;
}
.slide-btn.left {
  position: absolute;
  left: 0;
  top: 0;
}
.slide-btn.right {
  position: absolute;
  right: 0;
  top: 0;
}
.slide-content {
  margin: 0 auto;
  text-align: center;
  width: 100%;
  z-index: 1;
}

.slide-progress-bar {
  position: absolute;
  left: 0;
  bottom: 0;
  width: 100%;
  height: 1px;
  background: transparent;
  z-index: 3;
}
.slide-progress-bar__fill {
  height: 100%;
  background: #d0e7ef40;
  width: 0%;
  transition: width 0.1s linear;
}

.content-divider {
  display: flexbox;
  background: #090b17;
  content: '';
  height: 120px;
  padding: 23px 0;
}

.app-article {
  display: flex;
  color: #fff;
  background: #090b17;
  align-items: center;
  justify-content: center;
  padding: 0;
  gap: 40px;
}
.img-placeholder {
  width: 540px;
  height: 400px;
  border-radius: 16px;
}
.text-content {
  max-width: 500px;
}
.app-quote {
  font-style: italic;
  font-size: 1.3em;
  color: #d0e7ef;
  background: #16203640;
  border-left: 4px solid #162036;
  padding: 18px 24px;
  margin: 24px 0 0 0;
  border-radius: 8px;
  position: relative;
}
.app-quote:before,
.app-quote:after {
  display: none;
}

.welcome-section {
  background: #090b17;
  color: #fff;
  text-align: center;
  padding: 30px 0 50px 0;
}
.register-btn {
  display: inline-block;
  margin-top: 18px;
  padding: 16px 124px;
  background: #f2412ebf;
  color: #d0e7ef;
  border-radius: 8px;
  text-decoration: none;
  font-weight: bold;
  font-size: 1.4em;
}
</style>
