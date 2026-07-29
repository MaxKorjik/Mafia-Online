<template>
  <div class="vintage-auth-container">
    <div class="vintage-card register-card">
      <div class="modal-case-badge">ФОРМА №02</div>
      
      <h2 class="modal-title">РЕЄСТРАЦІЯ У КАРТОТЕЦІ</h2>
      <p class="modal-subtitle">Внесіть свої дані до офіційного реєстру мешканців Чикаго</p>
      
      <form @submit.prevent="handleRegister" class="vintage-form">
        <div class="form-group-vintage">
          <label for="username">Логін (Позивний)</label>
          <input
            type="text"
            id="username"
            v-model="username"
            class="input-vintage"
            required
            placeholder="Введіть унікальне ім'я"
          />
        </div>

        <div class="form-group-vintage">
          <label for="email">Електронна пошта (Email)</label>
          <input
            type="email"
            id="email"
            v-model="email"
            class="input-vintage"
            required
            placeholder="Введіть вашу пошту"
          />
        </div>
        
        <div class="form-group-vintage">
          <label for="password">Пароль / Шифр доступу</label>
          <input
            type="password"
            id="password"
            v-model="password"
            class="input-vintage code-font"
            required
            placeholder="Придумайте надійний пароль"
          />
        </div>

        <div class="form-group-vintage">
          <label for="confirmPassword">Підтвердження шифру</label>
          <input
            type="password"
            id="confirmPassword"
            v-model="confirmPassword"
            class="input-vintage code-font"
            required
            placeholder="Повторіть пароль"
          />
        </div>

        <div v-if="error" class="error-message-vintage">
          🚨 УВАГА: {{ error }}
        </div>

        <button type="submit" class="btn-vintage-primary" :disabled="loading">
          {{ loading ? 'Занесення в базу...' : 'Завірити досьє печаткою →' }}
        </button>

        <div class="auth-link-section">
          Вже є картка в архіві? 
          <router-link to="/login">Перейти до авторизації</router-link>
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
    error.value = 'Шифри не співпадають. Перевірте написання.'
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
    error.value = err.response?.data?.detail || 'Помилка реєстрації. Можливо, цей логін вже зайнятий.'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.vintage-auth-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: calc(100vh - 200px);
  padding: 20px;
}

.vintage-card {
  background-color: var(--paper-color);
  color: var(--ink-color);
  border: 3px solid var(--ink-color);
  box-shadow: 10px 10px 0px rgba(0, 0, 0, 0.15);
  padding: 35px 30px;
  width: 100%;
  max-width: 450px;
  position: relative;
  box-sizing: border-box;
}

.modal-case-badge {
  position: absolute;
  top: 15px;
  right: 15px;
  border: 1px dashed var(--ink-color);
  padding: 3px 8px;
  font-family: var(--font-ui);
  font-size: 0.7rem;
  font-weight: bold;
  opacity: 0.7;
}

.modal-title {
  font-family: var(--font-heading);
  font-size: 1.4rem;
  font-weight: 900;
  text-transform: uppercase;
  margin-bottom: 5px;
  letter-spacing: 0.5px;
  text-align: center;
  border-bottom: 1px solid var(--ink-color);
  padding-bottom: 10px;
}

.modal-subtitle {
  font-family: var(--font-text);
  font-size: 0.85rem;
  text-align: center;
  font-style: italic;
  margin-bottom: 25px;
  opacity: 0.8;
}

.vintage-form {
  display: flex;
  flex-direction: column;
}

.form-group-vintage {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-bottom: 20px;
}

.form-group-vintage label {
  font-family: var(--font-ui);
  font-size: 0.85rem;
  text-transform: uppercase;
  font-weight: bold;
}

.input-vintage {
  background: transparent;
  border: none;
  border-bottom: 1px dashed var(--ink-color);
  color: var(--ink-color);
  font-family: var(--font-text);
  font-size: 1rem;
  padding: 8px 4px;
  outline: none;
  box-sizing: border-box;
  width: 100%;
}

.input-vintage:focus {
  border-bottom-style: solid;
  border-bottom-width: 2px;
}

.input-vintage::placeholder {
  opacity: 0.4;
  font-style: italic;
}

.code-font {
  font-family: 'Courier Prime', monospace;
  letter-spacing: 2px;
}

.error-message-vintage {
  color: var(--accent-color);
  font-family: var(--font-text);
  font-size: 0.9rem;
  text-align: center;
  border: 1px dashed var(--accent-color);
  padding: 8px;
  background-color: rgba(107, 33, 33, 0.03);
  margin-bottom: 20px;
}

.btn-vintage-primary {
  background: var(--ink-color);
  color: var(--paper-color);
  border: 1px solid var(--ink-color);
  font-family: var(--font-heading);
  font-weight: bold;
  padding: 10px 20px;
  font-size: 0.95rem;
  cursor: pointer;
  text-transform: uppercase;
  transition: all 0.2s ease;
  width: 100%;
}

.btn-vintage-primary:hover:not(:disabled) {
  background-color: var(--accent-color);
  border-color: var(--accent-color);
}

.btn-vintage-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.auth-link-section {
  text-align: center;
  margin-top: 20px;
  font-family: var(--font-text);
  font-size: 0.9rem;
  color: var(--ink-color);
  opacity: 0.9;
}

.auth-link-section a {
  color: var(--accent-color);
  text-decoration: none;
  font-weight: bold;
  border-bottom: 1px dashed var(--accent-color);
}

.auth-link-section a:hover {
  border-bottom-style: solid;
}
</style>