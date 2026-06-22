<!-- <template>
  <div class="game-room">
    <div class="game-header">
      <h1>
        {{ room.name }}
      </h1>
      <ThemeToggle />
      <div class="room-status">
        <span>Гравців: {{ room.players_number }}/{{ room.max_players_number }}</span>
        <span v-if="isOwner" class="owner-badge">Ви власник</span>
      </div>
      <div class="game-phase">
        <span>Фаза: {{ gamePhase === 'day' ? 'День' : gamePhase === 'night' ? 'Ніч' : 'Очікування' }}</span>
        <span v-if="currentRound > 0">Раунд: {{ currentRound }}</span>
      </div>
    </div>

    <div class="game-content">
      <div class="players-list card">
        <h2>Гравці</h2>
        <div class="players-grid">
          <div v-for="player in players" :key="player.id || player.username" class="player-card" :class="{ 'dead': !player.is_alive }">
            <div class="player-avatar">
              {{ player.id }}
            </div>
            <div class="player-info">
              <span class="player-name">{{ player.username || 'Unknown' }}</span>
              <div class="player-status">
                <span v-if="player.is_owner" class="owner-badge" title="Власник">
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none"><path d="M2 19h20M4 19l2-8h12l2 8M7 11V7a5 5 0 0 1 10 0v4" stroke="#ff1744" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><ellipse cx="12" cy="7" rx="3" ry="2" fill="#ffd600"/></svg>
                  Власник
                </span>
                <span v-if="player.is_ready" class="ready-badge" title="Готовий">
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="10" fill="#43a047"/><path d="M8 12l2 2l4-4" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
                  Готовий
                </span>
                <span v-if="!player.is_alive" class="dead-badge" title="Мертвий">
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="10" fill="#e53935"/><path d="M9 9l6 6M15 9l-6 6" stroke="#fff" stroke-width="2" stroke-linecap="round"/></svg>
                  Мертвий
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="game-chat card">
        <div class="chat-messages" ref="chatMessages">
          <div v-for="message in messages" :key="message.id" class="message" :class="{
            'isPersonal': message.type === 'personal',
            'isSystem': message.type === 'system',
            'isError': message.type === 'error'
          }">
            <template v-if="message.type === 'chat'">
            <span class="message-sender">{{ message.username }}:</span>
              <span class="message-text">{{ message.message }}</span>
            </template>
            <template v-else-if="message.type === 'system'">
              <span class="message-text system-message">{{ message.message }}</span>
            </template>
            <template v-else-if="message.type === 'error'">
              <span class="message-text error-message">{{ message.message }}</span>
            </template>
            <template v-else>
              <span class="message-text">{{ message.message }}</span>
            </template>
          </div>
        </div>
        <div class="chat-input">
          <input
            type="text"
            v-model="newMessage"
            @keyup.enter="sendMessage"
            placeholder="Введіть повідомлення..."
            class="input"
          />
          <button @click="sendMessage" class="button">Надіслати</button>
        </div>
      </div>
    </div>

    <div class="game-controls">
      <button 
        v-if="!isGameStarted"
        @click="toggleReady" 
        class="button"
        :class="{ 'ready': isReady }"
      >
        {{ isReady ? 'Готовий' : 'Готуватися' }}
      </button>
      <button 
        v-if="isOwner && canStartGame" 
        @click="startGame" 
        class="start-game-button"
      >
        Почати гру
      </button>
      <div v-else-if="isOwner" class="start-game-info">
        <template v-if="players.length < room.min_players_number">
          Очікування гравців ({{ players.length }}/{{ room.min_players_number }})
        </template>
        <template v-else-if="!players.every(p => p.is_ready)">
          Очікування готовності гравців
        </template>
      </div>
      <button
        v-if="canVote && gamePhase === 'day'"
        @click="showVoteModal = true"
        class="button vote-button"
      >
        Голосувати
      </button>
    </div>

    <!-- Модальне вікно ролі -->
    <div v-if="showRoleModal" class="modal">
      <div class="modal-content">
        <h3>Ваша роль</h3>
        <p class="role-name">{{ 
          myRole === 'mafia' ? 'Мафія' : 
          myRole === 'doctor' ? 'Лікар' : 
          myRole === 'detective' ? 'Детектив' : 
          'Мирний житель' 
        }}</p>
        
        <div v-if="myRole === 'mafia' && otherMafia.length > 0" class="other-mafia">
          <h4>Інші мафійники:</h4>
          <ul>
            <li v-for="mafia in otherMafia" :key="mafia.id">
              {{ mafia.name }}
            </li>
          </ul>
        </div>
        
        <button @click="showRoleModal = false" class="button">Зрозуміло</button>
      </div>
    </div>

    <!-- Модальне вікно голосування -->
    <div v-if="showVoteModal" class="modal">
      <div class="modal-content">
        <h3>Голосування</h3>
        <p class="vote-description">Оберіть гравця, якого хочете вигнати:</p>
        <div class="vote-options">
          <div v-for="player in alivePlayers" :key="player.id" 
            class="vote-option" 
            @click="vote(player.id)">
            <div class="vote-option-avatar">{{ player.id }}</div>
            <div class="vote-option-name">{{ player.name }}</div>
          </div>
        </div>
        <button @click="showVoteModal = false" class="button secondary">Скасувати</button>
      </div>
    </div>

    <!-- Модальне вікно нічних дій -->
    <div v-if="showNightActionModal" class="modal">
      <div class="modal-content">
        <h3>{{ 
          myRole === 'mafia' ? 'Виберіть жертву' : 
          myRole === 'doctor' ? 'Виберіть кого лікувати' : 
          'Виберіть кого перевірити' 
        }}</h3>
        <div class="night-actions">
          <div v-for="player in alivePlayers" :key="player.id" 
            class="action-option" 
            @click="performNightAction(player.id)">
            <div class="action-option-avatar">{{ player.id }}</div>
            <div class="action-option-name">{{ player.name }}</div>
          </div>
        </div>
        <button @click="showNightActionModal = false" class="button secondary">Скасувати</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '@/services/api'
import ThemeToggle from '@/components/ThemeToggle.vue'

const route = useRoute()
const router = useRouter()
const room = ref({})
const players = ref([])
const messages = ref([])
const newMessage = ref('')
const isReady = ref(false)
const isGameStarted = ref(false)
const chatMessages = ref(null)
const ws = ref(null)
const reconnectAttempts = ref(0)
const maxReconnectAttempts = 3
const reconnectTimeout = ref(null)
const updateInterval = ref(null)
const roomOwner = ref(null)
const gamePhase = ref('waiting')
const currentRound = ref(0)
const myRole = ref(null)
const otherMafia = ref([])
const selectedPlayer = ref(null)
const showRoleModal = ref(false)
const showVoteModal = ref(false)
const showNightActionModal = ref(false)

const isOwner = computed(() => {
  const userId = parseInt(localStorage.getItem('userId'))
  return room.value.owner === userId
})

const canStartGame = computed(() => {
  const playersCount = players.value.length
  const minPlayers = room.value?.min_players_number || 6
  const allReady = players.value.every(p => p.is_ready)
  
  console.log('Can start game check:', {
    playersCount,
    minPlayers,
    allReady,
    canStart: playersCount >= minPlayers && allReady,
    players: players.value.map(p => ({ id: p.id, name: p.name, is_ready: p.is_ready }))
  })
  
  return playersCount >= minPlayers && allReady
})

const alivePlayers = computed(() => {
    return players.value.filter(player => player.is_alive)
})

const canPerformNightAction = computed(() => {
    if (gamePhase.value !== 'night') return false
    if (!myRole.value) return false
    return ['mafia', 'doctor', 'detective'].includes(myRole.value)
})

const canVote = computed(() => {
    return gamePhase.value === 'day' && myRole.value
})

const gameStatus = computed(() => {
    if (gamePhase.value === 'waiting') return 'Очікування гравців'
    if (gamePhase.value === 'day') return 'Денна фаза'
    if (gamePhase.value === 'night') return 'Нічна фаза'
    return 'Гра завершена'
})

const fetchRoom = async () => {
  try {
    const response = await api.get(`/api/rooms/${route.params.id}`)
    room.value = response.data
    roomOwner.value = response.data.owner
    console.log('Room data updated:', {
      room: room.value,
      owner: roomOwner.value,
      userId: localStorage.getItem('userId')
    })
    await fetchPlayers()
  } catch (error) {
    console.error('Помилка отримання інформації про кімнату:', error)
    router.push('/rooms')
  }
}

const fetchPlayers = async () => {
  try {
    const response = await api.get(`/api/rooms/${route.params.id}/players`)
    players.value = response.data.map(player => ({
      ...player,
      is_owner: player.id === room.value.owner,
      is_alive: player.is_alive ?? true
    }))
    console.log('Players data:', players.value)
    console.log('Can start game check:', {
      playersCount: players.value.length,
      minPlayers: room.value.min_players_number,
      allReady: players.value.every(player => player.is_ready)
    })
  } catch (error) {
    console.error('Помилка отримання списку гравців:', error)
  }
}

const fetchMessages = async () => {
  try {
    const response = await api.get(`/api/rooms/${route.params.id}/messages`)
    messages.value = response.data.map(msg => ({
      id: msg.id,
      username: msg.username,
      text: msg.message,
      timestamp: msg.created_at
    }))
    // Прокручуємо чат вниз після завантаження повідомлень
    setTimeout(() => {
      if (chatMessages.value) {
        chatMessages.value.scrollTop = chatMessages.value.scrollHeight
      }
    }, 0)
  } catch (error) {
    console.error('Помилка отримання повідомлень:', error)
  }
}

const connectWebSocket = () => {
  if (ws.value && (ws.value.readyState === WebSocket.OPEN || ws.value.readyState === WebSocket.CONNECTING)) {
    console.log('WebSocket already connected or connecting')
    return
  }

  if (reconnectTimeout.value) {
    clearTimeout(reconnectTimeout.value)
  }

  const token = localStorage.getItem('token')
  if (!token) {
    console.error('No token found in localStorage')
    router.push('/login')
    return
  }

  if (!route.params.id) {
    console.error('No room ID found')
    router.push('/rooms')
    return
  }

  const wsUrl = `ws://localhost:8000/api/ws/room/${route.params.id}?token=${token}`
  console.log('Attempting WebSocket connection to:', wsUrl)
  
  try {
    ws.value = new WebSocket(wsUrl)
    
    ws.value.onopen = () => {
      console.log('WebSocket connected successfully')
      reconnectAttempts.value = 0
      if (reconnectTimeout.value) {
        clearTimeout(reconnectTimeout.value)
        reconnectTimeout.value = null
      }
      fetchRoom()
      fetchPlayers()
      fetchMessages()
    }
    
    ws.value.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        console.log('Received WebSocket message:', data)
        handleWebSocketMessage(event)
      } catch (error) {
        console.error('Error parsing message:', error)
      }
    }
    
    ws.value.onerror = (error) => {
      console.error('WebSocket error:', error)
      if (error.target && error.target.readyState) {
        console.log('WebSocket state at error:', error.target.readyState)
      }
    }
    
    ws.value.onclose = (event) => {
      console.log('WebSocket closed:', event.code, event.reason)
      
      if (reconnectTimeout.value) {
        clearTimeout(reconnectTimeout.value)
      }
      
      switch (event.code) {
        case 4000:
          console.error('No token provided')
          router.push('/login')
          return
        case 4001:
          console.error('Invalid token')
          router.push('/login')
          return
        case 4002:
          console.error('Room not found')
          router.push('/rooms')
          return
        case 4003:
          console.error('Failed to add player to room')
          router.push('/rooms')
          return
      }
      
      if (event.code !== 1000 && reconnectAttempts.value < maxReconnectAttempts && route.params.id) {
        reconnectAttempts.value++
        console.log(`Reconnection attempt ${reconnectAttempts.value}/${maxReconnectAttempts}`)
        reconnectTimeout.value = setTimeout(connectWebSocket, 2000 * reconnectAttempts.value)
      } else if (reconnectAttempts.value >= maxReconnectAttempts) {
        console.error('Maximum reconnection attempts reached')
        router.push('/rooms')
      }
    }
  } catch (error) {
    console.error('Error creating WebSocket:', error)
    if (reconnectAttempts.value < maxReconnectAttempts && route.params.id) {
      reconnectAttempts.value++
      reconnectTimeout.value = setTimeout(connectWebSocket, 2000 * reconnectAttempts.value)
    }
  }
}

const handleWebSocketMessage = (event) => {
  try {
    const data = JSON.parse(event.data);
    console.log('Received WebSocket message:', data);
  
    switch (data.type) {
      case 'room_state':
        console.log('Room state update:', data);
        gamePhase.value = data.room.phase;
        currentRound.value = data.room.round;
        players.value = data.room.players;
        break;

      case 'player_joined':
        console.log('Player joined:', data);
        players.value = data.players;
        messages.value.push({
          type: 'system',
          message: `${data.username} приєднався до гри`
        });
        break;

      case 'player_left':
        console.log('Player left:', data);
        players.value = data.players;
        messages.value.push({
          type: 'system',
          message: `${data.username} покинув гру`
        });
        break;

      case 'player_ready':
        console.log('Player ready state changed:', data);
        players.value = data.players;
        const player = players.value.find(p => p.id === data.player_id);
        if (player) {
          messages.value.push({
            type: 'system',
            message: `${player.name} ${player.is_ready ? 'готовий' : 'не готовий'} до гри`
          });
        }
        break;

      case 'role_assigned':
        console.log('Role assigned:', data);
        myRole.value = data.role;
        showRoleModal.value = true;
        
        if (data.role === 'mafia' && data.other_mafia) {
          otherMafia.value = data.other_mafia;
        }
        
        const roleMessage = {
          type: 'personal',
          message: `Ваша роль: ${data.role}`
        };
        messages.value.push(roleMessage);
        break;

      case 'game_started':
        console.log('Game started:', data);
        gamePhase.value = data.phase;
        currentRound.value = data.round;
        isGameStarted.value = true;
        players.value = data.players;
        messages.value.push({
          type: 'system',
          message: 'Гра почалася!'
        });
        break;

      case 'phase_change':
        console.log('Phase change:', data);
        gamePhase.value = data.phase;
        currentRound.value = data.round;
        
        if (data.phase === 'night') {
          if (['mafia', 'doctor', 'detective'].includes(myRole.value)) {
            showNightActionModal.value = true;
          }
        }
        
        messages.value.push({
          type: 'system',
          message: data.phase === 'night' ? 'Настала ніч' : 'Настав день'
        });
        break;

      case 'chat':
        console.log('Chat message:', data);
        messages.value.push({
          type: 'chat',
          username: data.username,
          message: data.message
        });
        break;

      case 'system':
        console.log('System message:', data);
        messages.value.push({
          type: 'system',
          message: data.message
        });
        break;

      case 'error':
        console.error('Error message:', data);
        messages.value.push({
          type: 'error',
          message: data.message
        });
        break;

      default:
        console.warn('Unknown message type:', data.type);
    }

    // Прокручуємо чат вниз після оновлення повідомлень
    nextTick(() => {
      const chatContainer = document.querySelector('.chat-messages');
      if (chatContainer) {
        chatContainer.scrollTop = chatContainer.scrollHeight;
      }
    });
  } catch (error) {
    console.error('Error handling WebSocket message:', error);
  }
};

const sendMessage = () => {
  if (!newMessage.value.trim() || !ws.value) return
  
  if (ws.value.readyState === WebSocket.OPEN) {
    const message = {
      type: 'chat',
      payload: {
        message: newMessage.value
      }
    }
    
    try {
      ws.value.send(JSON.stringify(message))
      newMessage.value = ''
    } catch (error) {
      console.error('Помилка відправки повідомлення:', error)
      if (reconnectAttempts.value < maxReconnectAttempts) {
        connectWebSocket()
      }
    }
  } else {
    console.warn('WebSocket не підключено')
    if (reconnectAttempts.value < maxReconnectAttempts) {
      connectWebSocket()
    }
  }
}

const toggleReady = async () => {
  if (!ws.value || ws.value.readyState !== WebSocket.OPEN) {
    console.warn('WebSocket не підключено')
    return
  }
  
  const message = {
    type: 'toggle_ready',
    payload: {
      is_ready: !isReady.value
    }
  }
  
  console.log('Sending ready toggle:', message)
  
  try {
    ws.value.send(JSON.stringify(message))
    isReady.value = !isReady.value
    console.log('Ready state changed to:', isReady.value)
  } catch (error) {
    console.error('Помилка відправки статусу готовності:', error)
  }
}

const sendWebSocketMessage = async (message) => {
  if (!ws.value || ws.value.readyState !== WebSocket.OPEN) {
    console.warn('WebSocket не підключено')
    throw new Error('WebSocket не підключено')
  }
  
  try {
    ws.value.send(JSON.stringify(message))
  } catch (error) {
    console.error('Помилка відправки повідомлення:', error)
    throw error
  }
}

const startGame = async () => {
  if (!canStartGame.value) {
    console.log('Cannot start game:', {
      playersCount: players.value.length,
      minPlayers: room.value?.min_players_number || 6,
      allReady: players.value.every(p => p.is_ready)
    })
    return
  }
  
  try {
    const message = {
      type: 'start_game',
      payload: {
        room_id: route.params.id
    }
    }
    console.log('Sending start game message:', message)
      ws.value.send(JSON.stringify(message))
      console.log('Start game message sent successfully')
  } catch (error) {
    console.error('Error starting game:', error)
  }
}

const performNightAction = async (targetId) => {
  if (!myRole.value) return;
  
  try {
    const message = {
      type: 'night_action',
      payload: {
        actor_id: parseInt(localStorage.getItem('userId')),
        target_id: targetId
      }
    };
    
    if (ws.value && ws.value.readyState === WebSocket.OPEN) {
      await ws.value.send(JSON.stringify(message));
      showNightActionModal.value = false;
      // player.value.is_ready = True
      messages.value.push({
        type: 'system',
        message: `Ви виконали нічну дію як ${myRole.value}`
      });
    } else {
      console.warn('WebSocket не підключено');
    }
  } catch (error) {
    console.error('Error performing night action:', error);
  }
};

const vote = async (targetId) => {
  try {
    const message = {
      type: 'vote',
      payload: {
        player_id: localStorage.getItem('userId'),
        target_id: targetId
      }
    }
    
    if (ws.value && ws.value.readyState === WebSocket.OPEN) {
      ws.value.send(JSON.stringify(message))
      showVoteModal.value = false
    } else {
      console.warn('WebSocket не підключено')
    }
  } catch (error) {
    console.error('Error voting:', error)
  }
}

onMounted(() => {
  console.log('Component mounted')
  connectWebSocket()
  fetchMessages()
  
  updateInterval.value = setInterval(() => {
    if (route.params.id) {
      console.log('Update interval tick')
      fetchRoom()
    }
  }, 5000)
})

onUnmounted(() => {
  if (ws.value) {
    ws.value.close()
  }
  if (updateInterval.value) {
    clearInterval(updateInterval.value)
  }
  if (reconnectTimeout.value) {
    clearTimeout(reconnectTimeout.value)
  }
})
</script>

<style scoped>
/* Головний контейнер кімнати */
.game-room {
  width: 100%;
  box-sizing: border-box;
  padding: 1rem 0;
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
}

/* Шапка гри */
.game-header {
  background: var(--color-card);
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius-lg);
  padding: var(--spacing-lg);
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: var(--spacing-md);
}

.game-header h1 {
  margin: 0;
  font-size: var(--font-size-xl);
  color: var(--color-text);
  flex: 1 1 100%; /* На мобільних назва займає весь рядок */
}

.room-status, .game-phase {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  font-weight: 500;
}

/* 📊 Основна ігрова зона (Гравці + Чат) */
.game-content {
  display: grid;
  grid-template-columns: 1fr; /* По дефолту (мобілки) — одна колонка */
  gap: var(--spacing-lg);
  width: 100%;
}

/* Картки-контейнери */
.card {
  background: var(--color-card);
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius-lg);
  padding: var(--spacing-lg);
  box-shadow: var(--shadow-md);
  box-sizing: border-box;
}

.players-list h2, .game-chat h2 {
  margin-top: 0;
  margin-bottom: var(--spacing-md);
  font-size: var(--font-size-lg);
  border-bottom: 2px solid var(--color-border);
  padding-bottom: var(--spacing-xs);
}

/* Сітка карток гравців */
.players-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: var(--spacing-md);
}

.player-card {
  background: var(--color-secondary);
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius-md);
  padding: var(--spacing-md);
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  transition: all var(--transition-fast);
}

.player-card.dead {
  opacity: 0.6;
  background: var(--color-dead);
}

.player-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: var(--color-avatar);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
}

.player-info {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
}

.player-name {
  font-weight: bold;
}

.player-status {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-xs);
  font-size: var(--font-size-xs);
}

/* 💬 Стилі ЧАТУ */
.game-chat {
  display: flex;
  flex-direction: column;
  height: 450px; /* Фіксована висота, щоб чат не розповзався */
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: var(--spacing-sm);
  background: var(--color-chat-bg);
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius-md);
  margin-bottom: var(--spacing-md);
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
}

.message {
  padding: var(--spacing-xs) var(--spacing-sm);
  border-radius: var(--border-radius-sm);
  word-break: break-word;
}

.message-sender {
  font-weight: bold;
  color: var(--primary-color);
  margin-right: var(--spacing-xs);
}

.system-message {
  color: var(--color-chat-system);
  font-style: italic;
}

.error-message {
  color: var(--color-danger);
  font-weight: bold;
}

/* Поле введення чату */
.chat-input {
  display: flex;
  gap: var(--spacing-sm);
}

.chat-input .input {
  flex: 1;
  padding: var(--spacing-sm) var(--spacing-md);
  background: var(--color-secondary);
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius-md);
  color: var(--color-text);
}

/* 🎮 Панель керування кнопками */
.game-controls {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-md);
  justify-content: center;
  padding: var(--spacing-md);
  background: var(--color-card);
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius-lg);
}

/* Базові стилі для кнопок */
.button, .start-game-button {
  padding: var(--spacing-sm) var(--spacing-xl);
  font-weight: bold;
  border-radius: var(--border-radius-md);
  border: none;
  cursor: pointer;
  background: var(--color-btn);
  color: var(--color-btn-text);
  transition: background var(--transition-fast);
}

.button:hover, .start-game-button:hover {
  background: var(--color-btn-hover);
}

.button.secondary {
  background: var(--color-secondary);
  border: 1px solid var(--color-border);
  color: var(--color-text);
}

/* Бейджики */
.owner-badge, .ready-badge, .dead-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 2px 6px;
  border-radius: 4px;
  background: rgba(255,255,255,0.1);
}

/* 🖥️🖥️ ВЕЛИКІ ЕКРАНИ (ПК комп'ютери) 🖥️🖥️ */
@media (min-width: 992px) {
  .game-header h1 {
    flex: none; /* Назва більше не падає на весь рядок */
  }

  .game-content {
    /* Перемикаємося у ДВІ колонки: Гравці займають 40%, Чат займає 60% ширини */
    grid-template-columns: 4fr 6fr; 
    align-items: start;
  }

  .game-chat {
    height: 550px; /* Збільшуємо висоту чату на ПК для зручності */
  }

  .players-grid {
    /* На великому моніторі гравці стають компактнішою сіткою по 2 у ряд */
    grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  }
}
</style> -->