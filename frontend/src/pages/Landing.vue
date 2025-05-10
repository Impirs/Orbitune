<template>
  <div>
    <Navbar :user="user" />
    <main>
      <!-- Feature Slides -->
      <section class="feature-slides">
        <button class="slide-btn left" @click="prevSlide"></button>
        <div class="slide-content">
          <h2>{{ slides[currentSlide].title }}</h2>
          <p>{{ slides[currentSlide].text }}</p>
        </div>
        <button class="slide-btn right" @click="nextSlide"></button>
      </section>

      <!-- Application Article -->
      <section class="app-article">
        <div class="img-placeholder"></div>
        <div class="text-content">
          <h2>Orbitune Application</h2>
          <p>
            Добро пожаловать в Orbitune! Здесь будет описание приложения, его возможностей и преимуществ.
          </p>
        </div>
      </section>

      <!-- Welcome Section -->
      <section class="welcome-section">
        <h1>Welcome to Orbitune</h1>
        <router-link to="/auth" class="register-btn">Зарегистрироваться</router-link>
      </section>
    </main>
    <Footer />
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import Navbar from '../components/Navbar.vue'
import Footer from '../components/Footer.vue'

const slides = [
  { title: 'Слайд 1', text: 'Описание первого слайда Orbitune.' },
  { title: 'Слайд 2', text: 'Описание второго слайда Orbitune.' },
  { title: 'Слайд 3', text: 'Описание третьего слайда Orbitune.' },
]
const currentSlide = ref(0)
let interval = null

function nextSlide() {
  currentSlide.value = (currentSlide.value + 1) % slides.length
}
function prevSlide() {
  currentSlide.value = (currentSlide.value - 1 + slides.length) % slides.length
}

onMounted(() => {
  interval = setInterval(nextSlide, 10000)
})
onUnmounted(() => {
  clearInterval(interval)
})

// user: null если не залогинен, иначе объект пользователя
const user = ref(null) // для теста можно заменить на { name: 'User' }
</script>

<style scoped>
.feature-slides {
  position: relative;
  width: 100vw;
  height: 420px;
  display: flex;
  align-items: center;
  background: #f5f5f5;
  overflow: hidden;
}
.slide-btn {
  width: 180px;
  height: 100%;
  background: rgba(255,0,0,0.1);
  border: none;
  cursor: pointer;
  transition: background 0.2s;
  z-index: 2;
}
.slide-btn.left { position: absolute; left: 0; top: 0; }
.slide-btn.right { position: absolute; right: 0; top: 0; }
.slide-content {
  margin: 0 auto;
  text-align: center;
  width: 100%;
  z-index: 1;
}
.app-article {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 60px 0;
  gap: 40px;
}
.img-placeholder {
  width: 320px;
  height: 220px;
  background: #ff4444;
  border-radius: 16px;
}
.text-content {
  max-width: 500px;
}
.welcome-section {
  text-align: center;
  padding: 60px 0 40px 0;
}
.register-btn {
  display: inline-block;
  margin-top: 24px;
  padding: 12px 32px;
  background: #ff4444;
  color: #fff;
  border-radius: 8px;
  text-decoration: none;
  font-weight: bold;
  font-size: 1.2em;
}
</style>
