<template>
  <div class="rooms-container">
    <div class="rooms-header">
      <h1>Кімнати</h1>
      <button @click="showCreateRoomModal = true" class="button create-room-btn">
        Створити кімнату
      </button>
    </div>

    <div class="rooms-grid">
      <div v-for="room in rooms" :key="room.id" class="card room-card">
        <div class="room-card-header">
          <h3>{{ room.name }}</h3>
          <span class="room-players-count">Гравців: {{ room.players_number }}/{{ room.max_players_number }}</span>
        </div>
        <div class="room-info">
          <p>Мін. гравців: {{ room.min_players_number }}</p>
          <p v-if="room.is_private" class="private-badge">Приватна</p>
        </div>
        <div class="room-players-list">
          <h4>Гравці</h4>
          <div class="players-avatars">
            <template v-if="room.players && room.players.length">
              <div v-for="player in room.players" :key="player.id" class="player-avatar">
                {{ player.username[0].toUpperCase() }}
              </div>
            </template>
            <span v-else class="no-players">Немає гравців</span>
          </div>
        </div>
        <button 
          @click="joinRoom(room)" 
          class="button join-btn"
          :disabled="room.players_number >= room.max_players_number"
        >
          Приєднатися
        </button>
      </div>
    </div>

    <!-- Модальне вікно створення кімнати -->
    <div v-if="showCreateRoomModal" class="modal">
      <div class="modal-content card">
        <h2>Створити кімнату</h2>
        <form @submit.prevent="createRoom" class="create-room-form">
          <div class="form-group">
            <label for="roomName">Назва кімнати</label>
            <input
              type="text"
              id="roomName"
              v-model="newRoom.name"
              class="input"
              required
              placeholder="Введіть назву кімнати"
            />
          </div>

          <div class="form-group">
            <label for="minPlayers">Мінімальна кількість гравців</label>
            <input
              type="number"
              id="minPlayers"
              v-model="newRoom.min_players_number"
              class="input"
              required
              min="4"
              max="12"
            />
          </div>

          <div class="form-group">
            <label for="maxPlayers">Максимальна кількість гравців</label>
            <input
              type="number"
              id="maxPlayers"
              v-model="newRoom.max_players_number"
              class="input"
              required
              min="4"
              max="12"
            />
          </div>

          <div class="form-group checkbox-group">
            <label>
              <input
                type="checkbox"
                v-model="newRoom.is_private"
              />
              Приватна кімната
            </label>
          </div>

          <div v-if="newRoom.is_private" class="form-group">
            <label for="password">Пароль</label>
            <input
              type="password"
              id="password"
              v-model="newRoom.password"
              class="input"
              required
              placeholder="Введіть пароль"
            />
          </div>

          <div class="modal-buttons">
            <button type="button" @click="showCreateRoomModal = false" class="button secondary">
              Скасувати
            </button>
            <button type="submit" class="button" :disabled="loading">
              {{ loading ? 'Створення...' : 'Створити' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/services/api'

const router = useRouter()
const rooms = ref([])
const showCreateRoomModal = ref(false)
const loading = ref(false)

const newRoom = ref({
  name: '',
  min_players_number: 6,
  max_players_number: 6,
  is_private: false,
  password: ''
})

const fetchRooms = async () => {
  try {
    const response = await api.get('/api/rooms')
    rooms.value = response.data
  } catch (error) {
    console.error('Помилка отримання кімнат:', error)
  }
}

const createRoom = async () => {
  try {
    loading.value = true
    
    // Валідація даних
    if (newRoom.value.min_players_number < 4) {
      throw new Error('Мінімальна кількість гравців має бути не менше 4')
    }
    if (newRoom.value.max_players_number > 12) {
      throw new Error('Максимальна кількість гравців не може перевищувати 12')
    }
    if (newRoom.value.max_players_number < newRoom.value.min_players_number) {
      throw new Error('Максимальна кількість гравців має бути не менше мінімальної')
    }
    if (newRoom.value.is_private && !newRoom.value.password) {
      throw new Error('Для приватної кімнати потрібен пароль')
    }

    const response = await api.post('/api/rooms', {
      name: newRoom.value.name,
      min_players_number: newRoom.value.min_players_number,
      max_players_number: newRoom.value.max_players_number,
      is_private: newRoom.value.is_private,
      password: newRoom.value.is_private ? newRoom.value.password : null
    })

    showCreateRoomModal.value = false
    
    // ❌ ПРИБРАЛИ await fetchRooms(), щоб не спамити запитами перед редіректом
    // fetchRooms() Можна запустити без await у фоні, якщо дуже треба:
    fetchRooms() 

    // Додаємо мікро-паузу на 150 мілісекунд (залізобетонний буфер для бекенду, щоб він встиг записати сесію)
    await new Promise(resolve => setTimeout(resolve, 150))

    // Тепер спокійно переходимо в кімнату
    router.push(`/room/${response.data.id}`)
  } catch (error) {
    console.error('Помилка створення кімнати:', error)
  } finally {
    loading.value = false
  }
}

const joinRoom = async (room) => {
  if (room.is_private) {
    const password = prompt('Введіть пароль для кімнати:')
    if (!password) return
    // Тут можна додати перевірку пароля
  }
  router.push(`/room/${room.id}`)
}

onMounted(fetchRooms)
</script>

<style scoped>
.rooms-container {
  margin: 0;
  padding: 2rem;
  min-height: 80vh;
}

.rooms-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.create-room-btn {
  background-color: var(--primary-color);
  color: var(--text-light);
  font-weight: 500;
  font-size: 1rem;
  padding: 0.7rem 2rem;
  border-radius: 8px;
  transition: background 0.2s;
}
.create-room-btn:hover {
  background-color: var(--primary-color-dark);
}

.rooms-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 2rem;
  justify-items: center;
}

.room-card {
  width: 100%;
  max-width: 400px;
  min-height: 320px;
  display: flex;
  flex-direction: column;
  gap: 1.2rem;
  align-items: stretch;
  background: var(--bg-secondary);
  box-shadow: var(--shadow-md);
  border-radius: 12px;
  padding: 2rem 1.5rem 1.5rem 1.5rem;
}

.room-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.room-players-count {
  color: var(--text-secondary);
  font-size: 1rem;
}

.room-info {
  color: var(--text-secondary);
  font-size: 1rem;
  margin-bottom: 0.5rem;
}

.private-badge {
  color: var(--accent-primary);
  font-weight: bold;
}

.room-players-list {
  margin: 0.5rem 0 1rem 0;
}
.room-players-list h4 {
  margin-bottom: 0.5rem;
  color: var(--text-primary);
  font-size: 1.1rem;
}
.players-avatars {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
  min-height: 32px;
}
.player-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background-color: var(--accent-primary);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 1.1rem;
}
.no-players {
  color: var(--text-secondary);
  font-size: 0.95rem;
  margin-left: 0.5rem;
}

.join-btn {
  margin-top: auto;
  background-color: var(--accent-primary);
  color: #fff;
  font-weight: 500;
  font-size: 1rem;
  padding: 0.7rem 2rem;
  border-radius: 8px;
  transition: background 0.2s;
}
.join-btn:hover {
  background-color: var(--accent-secondary);
}

@media (max-width: 700px) {
  .rooms-header {
    flex-direction: column;
    gap: 1rem;
    align-items: flex-start;
  }
  .rooms-grid {
    grid-template-columns: 1fr;
  }
  .room-card {
    max-width: 100%;
    padding: 1.2rem 0.7rem;
  }
}
</style> 