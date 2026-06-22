<template>
  <div class="app">
    <Navbar />
    <main class="main-content">
      <div class="content-wrapper">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </div>
    </main>
  </div>
</template>

<script setup>
import Navbar from '@/components/Navbar.vue'
</script>

<style>
@import '@/assets/theme.css';

.app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.main-content {
  flex: 1;
  padding: var(--spacing-xl) 0;
  width: 100%;
}

/* Оновлений контейнер-обгортка для всього сайту */
.content-wrapper {
  width: 100%;
  max-width: 1200px; /* На ПК контент не розповзеться ширше ніж 1200px */
  margin: 0 auto;    /* Центрує весь контент сторінок по центру екрану */
  padding: 0 1.5rem; /* Безпечні відступи з боків для планшетів та мобілок */
  box-sizing: border-box;
}

/* Анімації переходів */
.fade-enter-active,
.fade-leave-active {
  transition: opacity var(--transition-normal);
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>