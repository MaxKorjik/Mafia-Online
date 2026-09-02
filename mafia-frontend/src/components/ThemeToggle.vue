<template>
  <button class="theme-toggle-btn" @click="toggleTheme">
    {{ isDark ? 'Денний випуск' : 'Нічний випуск' }}
  </button>
</template>

<script setup>
import { ref, onMounted } from 'vue'

// Инициализируем значение сразу на основе localStorage, чтобы избежать рассинхрона шаблона
const getSavedTheme = () => {
  return localStorage.getItem('theme') === 'dark'
}

const isDark = ref(getSavedTheme())

const toggleTheme = () => {
  isDark.value = !isDark.value
  if (isDark.value) {
    document.body.classList.add('dark-theme')
    localStorage.setItem('theme', 'dark')
  } else {
    document.body.classList.remove('dark-theme')
    localStorage.setItem('theme', 'light')
  }
}

onMounted(() => {
  // На всякий случай дублируем класс на body при монтировании, если тема темная
  if (isDark.value) {
    document.body.classList.add('dark-theme')
  } else {
    document.body.classList.remove('dark-theme')
  }
})
</script>

<style scoped>
.theme-toggle-btn {
  background: transparent;
  border: 1px dashed var(--ink-color);
  color: var(--ink-color);
  padding: 6px 12px;
  font-family: var(--font-text);
  font-size: 0.85rem;
  cursor: pointer;
  text-transform: uppercase;
  font-weight: bold;
  transition: all 0.3s ease;
}

.theme-toggle-btn:hover {
  background-color: var(--ink-color);
  color: var(--paper-color);
}
</style>