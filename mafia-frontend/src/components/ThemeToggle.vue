<template>
  <button class="theme-toggle" @click="toggleTheme" :title="theme === 'dark' ? 'Світла тема' : 'Темна тема'">
    <svg v-if="theme === 'dark'" width="24" height="24" fill="none"><circle cx="12" cy="12" r="10" fill="#fff"/><path d="M12 2a10 10 0 0 0 0 20c5.523 0 10-4.477 10-10S17.523 2 12 2Z" fill="#d32f2f"/></svg>
    <svg v-else width="24" height="24" fill="none"><circle cx="12" cy="12" r="10" fill="#1976d2"/><path d="M12 2a10 10 0 0 0 0 20c5.523 0 10-4.477 10-10S17.523 2 12 2Z" fill="#fff"/></svg>
  </button>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const theme = ref(localStorage.getItem('theme') || 'dark')

const toggleTheme = () => {
  theme.value = theme.value === 'dark' ? 'light' : 'dark'
  document.documentElement.setAttribute('data-theme', theme.value)
  localStorage.setItem('theme', theme.value)
}

onMounted(() => {
  document.documentElement.setAttribute('data-theme', theme.value)
})
</script>

<style scoped>
.theme-toggle {
  background: none;
  border: none;
  cursor: pointer;
  margin-left: 1rem;
  transition: filter .2s;
  filter: drop-shadow(0 0 4px var(--color-accent-glow));
}
.theme-toggle svg {
  width: 2rem;
  height: 2rem;
}
</style> 