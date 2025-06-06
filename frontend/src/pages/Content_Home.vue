<template>
  <div class="content-home">
    <div class="home-header">
      <h2>Home</h2>
    </div>
    <div class="home-content">
      <div class="nav-block listen">

      </div>
      <div class="nav-block share">

      </div>
      <div class="nav-block search">

      </div>
    </div>
  </div>
</template>

<script setup>
</script>

<style scoped>
.content-home {
  display: flex;
  flex-direction: column;
  position: relative;
  width: calc(100% - 80px);
  height: calc(100% - 54px);
  gap: 0;
  color: #fff;
  background: rgba(255, 255, 255, 0.15);
  border-radius: 18px;
  box-shadow: 0 2px 32px 0 rgba(0, 0, 0, 0.18);
  backdrop-filter: blur(8px) saturate(2);
  border: 1px solid rgba(255,255,255,0.33);
  min-height: 0;
  min-width: 0;
  padding: 22px 40px 32px 40px;
}
.home-header h2 {
  font-size: 3em;
  font-weight: 700;
  margin: 0;
  color: #fff;
}
.home-content {
  height: calc(100% - 42px);
}
</style>
