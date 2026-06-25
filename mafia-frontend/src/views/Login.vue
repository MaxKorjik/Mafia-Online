<template>
  <div class="login-container">
    <div class="card login-card">
      <h1>Вхід</h1>
      <form @submit.prevent="handleLogin" class="login-form">
        <div class="form-group">
          <label for="username">Логін або Email</label>
          <input
            type="text"
            id="username"
            v-model="username"
            class="input"
            required
            placeholder="Введіть логін або email"
          />
        </div>
        
        <div class="form-group">
          <label for="password">Пароль</label>
          <input
            type="password"
            id="password"
            v-model="password"
            class="input"
            required
            placeholder="Введіть пароль"
          />
        </div>

        <div v-if="error" class="error-message">
          {{ error }}
        </div>

        <button type="submit" class="button" :disabled="loading">
          {{ loading ? 'Завантаження...' : 'Увійти' }}
        </button>

        <div class="register-link">
          Немає акаунту? 
          <router-link to="/register">Зареєструватися</router-link>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const username = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

const handleLogin = async () => {
  try {
    loading.value = true
    error.value = ''
    
    await authStore.login(username.value, password.value)
    router.push('/rooms')
  } catch (err) {
    error.value = err.response?.data?.detail || 'Помилка входу'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: calc(100vh - 200px);
}

.login-card {
  width: 100%;
  max-width: 400px;
  padding: 2rem;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  color: var(--text-secondary);
}

.error-message {
  color: var(--error-color);
  text-align: center;
}

.register-link {
  text-align: center;
  color: var(--text-secondary);
}

.register-link a {
  color: var(--accent-primary);
  text-decoration: none;
}

.register-link a:hover {
  text-decoration: underline;
}
</style> 