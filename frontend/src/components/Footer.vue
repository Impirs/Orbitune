<template>
  <footer class="footer">
    <div class="footer-content">
      <div class="footer-col">Колонка 1</div>
      <div class="footer-col">Колонка 2</div>
      <div class="footer-col">Колонка 3</div>
    </div>
  </footer>
</template>

<style scoped>
.footer {
  width: 100vw;
  min-height: 400px;
  background: #222;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px 0;
}
.footer-content {
  display: flex;
  gap: 80px;
  justify-content: center;
  width: 100%;
  max-width: 1200px;
}
.footer-col {
  flex: 1;
  min-width: 200px;
  text-align: center;
  padding: 20px;
  background: rgba(255,255,255,0.04);
  border-radius: 12px;
}
</style>