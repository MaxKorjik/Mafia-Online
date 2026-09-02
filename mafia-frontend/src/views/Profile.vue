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
  color: var(--ink-color);
  font-family: var(--font-text);
}

.profile-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  margin-bottom: 2rem;
  padding: 1.5rem 2rem;
  background: var(--card-bg);
  border: 1px solid var(--stamp-border);
  border-radius: 0;
  box-shadow: 8px 10px 18px rgba(0, 0, 0, 0.08);
}

.profile-header h1 {
  margin: 0;
  font-size: 2.4rem;
  color: var(--accent-color);
  letter-spacing: 0.02em;
}

.profile-header .btn-danger {
  background-color: var(--error-color);
  color: white;
  padding: 0.95rem 1.6rem;
  border: 2px solid var(--error-color-dark);
  border-radius: 0;
  font-weight: 700;
  letter-spacing: 0.04em;
  box-shadow: 0 0 0 3px rgba(229, 57, 53, 0.12);
  transition: transform 0.2s ease, box-shadow 0.2s ease, background-color 0.2s ease;
}

.profile-header .btn-danger:hover {
  transform: translateY(-1px);
  background-color: var(--error-color-dark);
}

.profile-content {
  background-color: var(--paper-color);
  border: 1px solid rgba(43, 43, 43, 0.14);
  border-radius: 0;
  padding: 2rem;
  box-shadow: 12px 14px 28px rgba(0, 0, 0, 0.08);
}

.profile-info {
  margin-bottom: 2rem;
}

.info-group {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  margin-bottom: 1rem;
  padding: 1rem;
  background: var(--card-bg);
  border-radius: 0;
  border: 1px solid var(--stamp-border);
}

.info-group label {
  font-weight: 700;
  width: 220px;
  color: var(--text-secondary);
}

.info-group span {
  flex: 1;
  color: var(--ink-color);
}

.stats-section h2 {
  margin-bottom: 1.5rem;
  color: var(--accent-color);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
}

.stat-card {
  background-color: var(--card-bg);
  padding: 1.6rem;
  border-radius: 0;
  text-align: center;
  box-shadow: 6px 6px 0 rgba(0, 0, 0, 0.05);
  border: 1px solid var(--stamp-border);
}

.stat-card h3 {
  font-size: 1rem;
  margin-bottom: 0.75rem;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.stat-value {
  font-size: 2.2rem;
  font-weight: 800;
  color: var(--accent-primary);
  margin: 0;
}

.loading,
.error {
  text-align: center;
  padding: 2rem;
  border-radius: 0;
  background: var(--card-bg);
  border: 1px solid var(--stamp-border);
}

.error {
  color: var(--error-color);
}

@media (max-width: 820px) {
  .profile {
    padding: 1rem;
  }

  .profile-header {
    flex-direction: column;
    align-items: stretch;
    text-align: center;
  }

  .info-group {
    flex-direction: column;
    align-items: flex-start;
  }

  .info-group label {
    width: 100%;
  }
}
</style> 