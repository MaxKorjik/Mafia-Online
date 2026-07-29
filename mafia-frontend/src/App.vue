<template>
  <div class="newspaper-wrapper">
    <div class="newspaper-main">
      
      <Navbar />
      
      <router-view :key="$route.fullPath" />
      
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import Navbar from '@/components/Navbar.vue'
import { useAuthStore } from '@/stores/auth' // Убедись, что путь к store правильный

const authStore = useAuthStore()

// При монтировании главного компонента (F5 / первый запуск)
onMounted(async () => {
  // Если токен есть в localStorage, восстанавливаем данные профиля
  if (authStore.token) {
    try {
      await authStore.fetchUserProfile()
    } catch (error) {
      console.error('Ошибка автоматического входа:', error)
    }
  }
})
</script>

<style>
/* Переходы между маршрутами отключены, чтобы не мешать рендеру страниц */
</style>