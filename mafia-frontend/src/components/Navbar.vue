<template>
  <nav class="navbar" aria-label="Головна навігація">
    <div class="navbar-container">
      <router-link to="/" class="navbar-brand">
        Mafia Online
      </router-link>

      <button class="burger" @click="toggleMenu" :aria-expanded="menuOpen.toString()" aria-label="Відкрити меню">
        <span :class="{ 'open': menuOpen }"></span>
        <span :class="{ 'open': menuOpen }"></span>
        <span :class="{ 'open': menuOpen }"></span>
      </button>

      <div class="navbar-menu" :class="{ open: menuOpen }">
        <router-link to="/" class="navbar-link" @click="closeMenu">Головна</router-link>
        <router-link to="/rooms" class="navbar-link" @click="closeMenu">Кімнати</router-link>
        <router-link to="/leaderboard" class="navbar-link" @click="closeMenu">Таблиця лідерів</router-link>
      </div>

      <div class="navbar-actions">
        <ThemeToggle />
        <template v-if="isLoggedIn">
          <router-link to="/profile" class="navbar-link" @click="closeMenu">
            {{ username }}
          </router-link>
          <button @click="logout" class="btn btn-danger">Вийти</button>
        </template>
        <template v-else>
          <router-link to="/login" class="btn" @click="closeMenu">Увійти</router-link>
          <router-link to="/register" class="btn btn-secondary" @click="closeMenu">Реєстрація</router-link>
        </template>
      </div>
    </div>
  </nav>
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
.navbar {
  background-color: var(--bg-secondary);
  box-shadow: var(--shadow-sm);
  padding: var(--spacing-md) var(--spacing-lg);
  width: 100%;
  position: relative;
  z-index: 10;
  box-sizing: border-box;
}

.navbar-container {
  display: flex;
  align-items: center;
  justify-content: space-between; /* Лого зліва, Кнопки справа */
  width: 100%;
  max-width: 1200px; /* Обмежуємо ширину шапки разом із сайтом */
  margin: 0 auto;
  box-sizing: border-box;
}

.navbar-brand {
  font-size: var(--font-size-xl);
  font-weight: bold;
  color: var(--primary-color);
  text-decoration: none;
  transition: color 0.2s;
}

.navbar-brand:hover {
  color: var(--accent-color);
}

.navbar-menu {
  display: flex;
  gap: var(--spacing-lg);
}

.navbar-link {
  color: var(--text-primary);
  text-decoration: none;
  transition: all 0.2s;
  border-radius: 6px;
  padding: 0.4rem 1rem;
  font-weight: 500;
}

.navbar-link:hover, .navbar-link:focus {
  color: var(--primary-color);
  background: var(--bg-tertiary);
}

.navbar-actions {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
}

.burger {
  display: none; /* Заховано на ПК */
  flex-direction: column;
  gap: 4px;
  background: none;
  border: none;
  cursor: pointer;
}

/* 📱 МОБІЛЬНА ВЕРСІЯ НАВІГАЦІЇ (для телефонів) */
@media (max-width: 768px) {
  .burger {
    display: flex;
  }

  .navbar-menu {
    display: none; /* Перетворюємо на випадайку, якщо потрібно */
    flex-direction: column;
    position: absolute;
    top: 100%;
    left: 0;
    width: 100%;
    background: var(--bg-secondary);
    padding: var(--spacing-md);
    box-shadow: var(--shadow-md);
  }

  .navbar-menu.open {
    display: flex;
  }
}
</style>