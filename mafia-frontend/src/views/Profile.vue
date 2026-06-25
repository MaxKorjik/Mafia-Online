<template>
  <div class="profile">
    <div class="profile-header">
      <h1>Профіль користувача</h1>
      <button @click="logout" class="btn btn-danger">Вийти</button>
    </div>

    <div v-if="loading" class="loading">
      Завантаження...
    </div>

    <div v-else-if="error" class="error">
      {{ error }}
    </div>

    <div v-else class="profile-content">
      <div class="profile-info">
        <div class="info-group">
          <label>Ім'я користувача:</label>
          <span>{{ user?.username }}</span>
        </div>
        <div class="info-group">
          <label>Email:</label>
          <span>{{ user?.email }}</span>
        </div>
        <div class="info-group">
          <label>Дата реєстрації:</label>
          <span>{{ formatDate(user?.created_at) }}</span>
        </div>
      </div>

      <div class="stats-section">
        <h2>Статистика гри</h2>
        <div class="stats-grid">
          <div class="stat-card">
            <h3>Всього ігор</h3>
            <p class="stat-value">{{ user?.total_games || 0 }}</p>
          </div>
          <div class="stat-card">
            <h3>Перемог як мафія</h3>
            <p class="stat-value">{{ user?.mafia_matches || 0 }}</p>
          </div>
          <div class="stat-card">
            <h3>Перемог як мирний</h3>
            <p class="stat-value">{{ user?.survivor_matches || 0 }}</p>
          </div>
          <div class="stat-card">
            <h3>Відсоток перемог</h3>
            <p class="stat-value">{{ winPercentage }}%</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useToast } from 'vue-toastification'

const router = useRouter()
const authStore = useAuthStore()
const toast = useToast()

const loading = ref(true)
const error = ref(null)
const user = ref(null)

const winPercentage = computed(() => {
  if (!user.value?.total_games) return 0
  const totalWins = (user.value.mafia_matches || 0) + (user.value.survivor_matches || 0)
  return Math.round((totalWins / user.value.total_games) * 100)
})

const formatDate = (dateString) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleDateString('uk-UA', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

const loadUserProfile = async () => {
  try {
    loading.value = true
    error.value = null
    user.value = await authStore.fetchUserProfile()
  } catch (err) {
    error.value = 'Помилка завантаження профілю'
    toast.error('Не вдалося завантажити профіль')
  } finally {
    loading.value = false
  }
}

const logout = async () => {
  try {
    await authStore.logout()
    toast.success('Ви успішно вийшли з системи')
    router.push('/login')
  } catch (err) {
    toast.error('Помилка при виході з системи')
  }
}

onMounted(() => {
  loadUserProfile()
})
</script>

<style scoped>
.profile {
  margin: 0;
  padding: 2rem;
}

.profile-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.profile-content {
  background-color: var(--bg-secondary);
  border-radius: 8px;
  padding: 2rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.profile-info {
  margin-bottom: 2rem;
}

.info-group {
  display: flex;
  margin-bottom: 1rem;
  padding: 0.5rem 0;
  border-bottom: 1px solid var(--border-color);
}

.info-group label {
  font-weight: bold;
  width: 200px;
  color: var(--text-secondary);
}

.stats-section h2 {
  margin-bottom: 1.5rem;
  color: var(--text-primary);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
}

.stat-card {
  background-color: var(--bg-primary);
  padding: 1.5rem;
  border-radius: 8px;
  text-align: center;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.stat-card h3 {
  font-size: 1rem;
  margin-bottom: 0.5rem;
  color: var(--text-secondary);
}

.stat-value {
  font-size: 2rem;
  font-weight: bold;
  color: var(--primary-color);
  margin: 0;
}

.loading {
  text-align: center;
  padding: 2rem;
  color: var(--text-secondary);
}

.error {
  text-align: center;
  padding: 2rem;
  color: var(--error-color);
}

.btn-danger {
  background-color: var(--error-color);
}

.btn-danger:hover {
  background-color: var(--error-color-dark);
}

@media (max-width: 600px) {
  .profile {
    padding: 1rem;
  }

  .profile-header {
    flex-direction: column;
    gap: 1rem;
    text-align: center;
  }

  .info-group {
    flex-direction: column;
  }

  .info-group label {
    width: 100%;
    margin-bottom: 0.5rem;
  }
}
</style> 