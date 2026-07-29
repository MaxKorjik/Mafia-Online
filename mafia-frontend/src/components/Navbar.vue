<template>
  <header class="newspaper-header">
    <div class="logo-block">
      <router-link to="/" class="logo-link">
        <h1 class="logo-title">THE MAFIA NEWS</h1>
      </router-link>
      <p class="logo-subtitle">Щоденна хроніка Чикаго — Випуск №1932</p>
    </div>
    
    <nav class="main-nav">
      <ul :class="{ 'open': menuOpen }">
        <li><router-link to="/" @click="closeMenu">Головна</router-link></li>
        <li><router-link to="/rooms" @click="closeMenu">Кімнати</router-link></li>
        <li><router-link to="/leaderboard" @click="closeMenu">Рейтинг</router-link></li>
      </ul>
    </nav>

    <div class="header-right">
      <ThemeToggle />
      
      <template v-if="isLoggedIn">
        <div class="user-profile">
          <div class="avatar">
            <span v-if="username">{{ username[0].toUpperCase() }}</span>
          </div>
          <router-link to="/profile" class="user-name" @click="closeMenu">
            {{ username }}
          </router-link>
          <button @click="logout" class="btn-logout" title="Вийти">✖</button>
        </div>
      </template>
      <template v-else>
        <div class="auth-links">
          <!-- Добавлен @click="closeMenu" для закрытия шторки на мобилках -->
          <router-link to="/login" class="btn-enter" @click="closeMenu">Увійти</router-link>
          <router-link to="/register" class="btn-enter" @click="closeMenu">Реєстрація</router-link>
        </div>
      </template>

      <button class="burger" @click="toggleMenu">☰</button>
    </div>
  </header>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useToast } from 'vue-toastification'
import ThemeToggle from './ThemeToggle.vue'

const router = useRouter()
const authStore = useAuthStore()
const toast = useToast()

const isLoggedIn = computed(() => authStore.isLoggedIn)
const username = computed(() => authStore.getUser?.username)

const menuOpen = ref(false)
const toggleMenu = () => { menuOpen.value = !menuOpen.value }
const closeMenu = () => { menuOpen.value = false }

const logout = async () => {
  try {
    await authStore.logout()
    toast.success('Ви успішно вийшли з системи')
    router.push('/login')
  } catch (error) {
    toast.error('Помилка при виході з системи')
  }
}
</script>

<style scoped>
.newspaper-header {
  position: relative; /* Добавлено для корректного абсолютного позиционирования меню */
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-top: 5px double var(--ink-color);
  border-bottom: 2px solid var(--ink-color);
  padding: 20px 0;
  margin-bottom: 35px;
  flex-wrap: wrap;
  gap: 20px;
}

.logo-block { text-align: left; }
.logo-link { text-decoration: none; color: inherit; }
.logo-title {
  font-family: var(--font-heading);
  font-size: 3.2rem;
  font-weight: 900;
  text-transform: uppercase;
  letter-spacing: 1px;
  line-height: 0.95;
}
.logo-subtitle {
  font-family: var(--font-text);
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 1px;
  margin-top: 8px;
  opacity: 0.8;
}

.main-nav ul {
  display: flex;
  list-style: none;
  gap: 25px;
}
.main-nav a {
  color: var(--ink-color);
  text-decoration: none;
  font-family: var(--font-heading);
  font-weight: 700;
  font-size: 1.1rem;
  text-transform: uppercase;
  transition: color 0.2s;
}
.main-nav a:hover, .main-nav a.router-link-active { color: var(--accent-color); }

.header-right {
  display: flex;
  align-items: center;
  gap: 20px;
}

.auth-links { display: flex; gap: 10px; }
.btn-enter {
  padding: 6px 12px; background: transparent; border: 1px solid var(--ink-color);
  color: var(--ink-color); font-family: var(--font-text); font-weight: bold;
  text-transform: uppercase; font-size: 0.85rem; cursor: pointer; text-decoration: none;
}
.btn-enter:hover { background: var(--ink-color); color: var(--paper-color); }

.user-profile {
  display: flex;
  align-items: center;
  gap: 12px;
  border-left: 1px solid var(--stamp-border);
  padding-left: 20px;
}
.avatar {
  width: 42px; height: 42px; border-radius: 50%; border: 2px solid var(--ink-color);
  background-color: var(--paper-shadow);
  display: flex; justify-content: center; align-items: center;
  font-family: var(--font-heading); font-weight: bold; font-size: 1.2rem;
}
.user-name { font-family: var(--font-text); font-weight: 700; font-size: 0.9rem; text-decoration: none; color: var(--ink-color); }
.btn-logout {
  background: none; border: none; color: var(--accent-color); font-weight: bold; cursor: pointer; font-size: 1rem;
}

.burger { display: none; background: none; border: none; font-size: 1.5rem; color: var(--ink-color); cursor: pointer; }

@media (max-width: 950px) {
  .burger { display: block; }
  .main-nav ul { 
    display: none; 
    flex-direction: column; 
    width: 100%; 
    position: absolute; 
    background: var(--paper-color); 
    padding: 20px; 
    z-index: 10; 
    border: 2px solid var(--ink-color); 
    left: 0; 
    top: 100%; /* Гарантирует, что меню откроется ровно под хедером */
  }
  .main-nav ul.open { display: flex; }
}
@media (max-width: 680px) {
  .newspaper-header { flex-direction: column; text-align: center; }
  .header-right { flex-direction: column; width: 100%; gap: 15px; }
  .user-profile { border-left: none; border-top: 1px solid var(--stamp-border); padding-left: 0; padding-top: 15px; width: 100%; justify-content: center; }
  .logo-title { font-size: 2.3rem; }
}
</style>