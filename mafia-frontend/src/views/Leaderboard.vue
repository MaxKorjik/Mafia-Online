<template>
  <div class="leaderboard-container">
    <h1>Таблиця лідерів</h1>
    
    <div class="leaderboard-filters">
      <button 
        v-for="filter in filters" 
        :key="filter.value"
        @click="currentFilter = filter.value"
        class="button"
        :class="{ active: currentFilter === filter.value }"
      >
        {{ filter.label }}
      </button>
    </div>

    <div class="leaderboard-table card">
      <div class="table-header">
        <div class="rank">#</div>
        <div class="player">Гравець</div>
        <div class="stats">
          <div class="stat">Всього ігор</div>
          <div class="stat">Як вижив</div>
          <div class="stat">Як мафія</div>
        </div>
      </div>

      <div class="table-body">
        <div 
          v-for="(player, index) in sortedPlayers" 
          :key="player.id"
          class="table-row"
          :class="{ 'top-3': index < 3 }"
        >
          <div class="rank">{{ index + 1 }}</div>
          <div class="player">
            <div class="player-avatar">
              {{ player.username[0].toUpperCase() }}
            </div>
            <span class="player-name">{{ player.username }}</span>
          </div>
          <div class="stats">
            <div class="stat">{{ player.matches }}</div>
            <div class="stat">{{ player.survivor_matches }}</div>
            <div class="stat">{{ player.mafia_matches }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '@/services/api'

const players = ref([])
const currentFilter = ref('matches')

const filters = [
  { label: 'Всього ігор', value: 'matches' },
  { label: 'Як вижив', value: 'survivor_matches' },
  { label: 'Як мафія', value: 'mafia_matches' }
]

const sortedPlayers = computed(() => {
  return [...players.value].sort((a, b) => b[currentFilter.value] - a[currentFilter.value])
})

const fetchLeaderboard = async () => {
  try {
    const response = await api.get('/api/leaderboard')
    players.value = response.data
  } catch (error) {
    console.error('Помилка отримання таблиці лідерів:', error)
  }
}

onMounted(fetchLeaderboard)
</script>

<style scoped>
.leaderboard-container {
  margin: 0;
  padding: 2rem;
}

.leaderboard-filters {
  display: flex;
  justify-content: center;
  gap: 1rem;
  margin-bottom: 2rem;
}

.button.active {
  background-color: var(--accent-secondary);
}

.leaderboard-table {
  padding: 0;
  overflow: hidden;
}

.table-header {
  display: grid;
  grid-template-columns: 80px 1fr 3fr;
  padding: 1rem;
  background-color: var(--bg-secondary);
  font-weight: bold;
}

.stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  text-align: center;
}

.table-body {
  display: flex;
  flex-direction: column;
}

.table-row {
  display: grid;
  grid-template-columns: 80px 1fr 3fr;
  padding: 1rem;
  align-items: center;
  border-bottom: 1px solid var(--border-color);
}

.table-row:last-child {
  border-bottom: none;
}

.table-row.top-3 {
  background-color: var(--bg-secondary);
}

.rank {
  text-align: center;
  font-weight: bold;
  color: var(--text-secondary);
}

.player {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.player-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: var(--accent-primary);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
}

.player-name {
  font-weight: 500;
}

.stat {
  text-align: center;
  color: var(--text-secondary);
}
</style> 