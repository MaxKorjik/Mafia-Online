<template>
  <div class="register-container">
    <div class="card register-card">
      <h1>Реєстрація</h1>
      <form @submit.prevent="handleRegister" class="register-form">
        <div class="form-group">
          <label for="username">Логін</label>
          <input
            type="text"
            id="username"
            v-model="username"
            class="input"
            required
            placeholder="Введіть логін"
          />
        </div>

        <div class="form-group">
          <label for="email">Email</label>
          <input
            type="email"
            id="email"
            v-model="email"
            class="input"
            required
            placeholder="Введіть email"
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

        <div class="form-group">
          <label for="confirmPassword">Підтвердження паролю</label>
          <input
            type="password"
            id="confirmPassword"
            v-model="confirmPassword"
            class="input"
            required
            placeholder="Повторіть пароль"
          />
        </div>

        <div v-if="error" class="error-message">
          {{ error }}
        </div>

        <button type="submit" class="button" :disabled="loading">
          {{ loading ? 'Завантаження...' : 'Зареєструватися' }}
        </button>

        <div class="login-link">
          Вже маєте акаунт? 
          <router-link to="/login">Увійти</router-link>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const username = ref('')
const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const error = ref('')
const loading = ref(false)

const handleRegister = async () => {
  if (password.value !== confirmPassword.value) {
    error.value = 'Паролі не співпадають'
    return
  }

  try {
    loading.value = true
    error.value = ''
    
    await axios.post(`${import.meta.env.VITE_API_URL}/auth/register`, {
      username: username.value,
      email: email.value,
      password: password.value
    })

    router.push('/login')
  } catch (err) {
    error.value = err.response?.data?.detail || 'Помилка реєстрації'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.register-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: calc(100vh - 200px);
}

.register-card {
  width: 100%;
  max-width: 400px;
  padding: 2rem;
}

.register-form {
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

.login-link {
  text-align: center;
  color: var(--text-secondary);
}

.login-link a {
  color: var(--accent-primary);
  text-decoration: none;
}

.login-link a:hover {
  text-decoration: underline;
}
</style> 