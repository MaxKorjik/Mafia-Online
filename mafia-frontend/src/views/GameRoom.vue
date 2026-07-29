<template>
  <div class="newspaper-wrapper">
    <div class="newspaper-main">
      
      <!-- ІНФОРМАЦІЙНА ПАНЕЛЬ КІМНАТИ (БЕЗ ДУБЛЮВАННЯ NAVBAR) -->
      <header class="newspaper-header room-info-header">
        <div class="logo-block">
          <h2 class="room-title">Кімната: {{ room.name }}</h2>
        </div>
        <div class="header-right">
          <div class="room-status-badge">
            Гравців: {{ players.length }}/{{ room.max_players_number }}
          </div>
          <div class="phase-badge" :class="{ 'night-phase-pulse': gamePhase === 'night' }">
            Фаза: {{ gamePhase === 'day' ? 'День ☀️' : gamePhase === 'night' ? 'Ніч 🌙' : 'Очікування ⏳' }}
            <span v-if="currentRound > 0" class="round-num"> | Раунд {{ currentRound }}</span>
          </div>
        </div>
      </header>

      <!-- СЕТКА КОНТЕНТА -->
      <main class="content-grid">
        
        <!-- ЛЕВАЯ КОЛОНКА (Материалы дела / Игроки) -->
        <section class="left-column">
          <h2 class="section-title">Матеріали справи (Гравці)</h2>
          
          <!-- Досье текущего игрока (Вы) -->
          <div class="hero-dossier" v-if="myPlayerObject">
            <div class="dossier-photo-container">
              <div class="dossier-photo">{{ currentUserId }}</div>
            </div>
            <div class="dossier-info">
              <h3>{{ myPlayerObject.name || myPlayerObject.username || 'Ви' }} (Ви)</h3>
              <p><strong>Статус:</strong> {{ myPlayerObject.is_alive ? 'Живий та дає свідчення.' : 'Ліквідований.' }}</p>
              <ul>
                <li v-if="isOwner">Ви є творцем та власником цієї кімнати.</li>
                <li v-if="myPlayerObject.is_ready && !isGameStarted">Ви підтвердили готовність до початку sprawy.</li>
                <li v-else-if="!isGameStarted">Очікування підтвердження вашої готовності.</li>
                <li v-if="isGameStarted && myRole">Ваша роль у цій грі задокументована.</li>
              </ul>
            </div>
            <!-- Печать роли, если игра началась -->
            <div v-if="isGameStarted && myRole" class="stamp-role" :class="myRole">
              {{ 
                myRole === 'mafia' ? 'Мафія' : 
                myRole === 'mafia_don' ? 'Дон' : 
                myRole === 'doctor' ? 'Лікар' : 
                myRole === 'detective' ? 'Шериф' : 
                'Мирний' 
              }}
            </div>
          </div>

          <!-- Разбросанные полароиды игроков -->
          <div class="suspects-area">
            <div 
              v-for="player in otherPlayers" 
              :key="player.id || player.username" 
              class="suspect-polaroid" 
              :class="{ 'dead': !player.is_alive }"
              @click="handlePlayerClick(player)"
            >
              <div class="polaroid-img">
                <span class="polaroid-id-badge">#{{ player.id }}</span>
                <div class="polaroid-overlay">
                  {{ isGameStarted ? 'Взаємодія' : 'Інформація' }}
                </div>
              </div>
              <div class="polaroid-name">
                {{ player.name || player.username || 'Unknown' }}
              </div>
              
              <!-- Кнопки управления и статусы поверх полароида -->
              <div class="polaroid-badges">
                <span v-if="player.id == room.owner || player.is_owner" class="badge-owner-icon" title="Власник">👑</span>
                <span v-if="player.is_ready && !isGameStarted" class="badge-ready-icon" title="Готовий">✔️</span>
              </div>

              <button 
                v-if="isOwner && player.id !== currentUserId && !isGameStarted" 
                @click.stop="kickPlayer(player.id)" 
                class="kick-button-polaroid" 
                title="Вигнати гравця"
              >
                ❌
              </button>
            </div>
          </div>
        </section>

        <!-- ПРАВАЯ КОЛОНКА (Пишущая машинка / Чат) -->
        <aside class="right-column">
          <div class="typewriter-chat" :class="{ 'mafia-mode': activeTab === 'mafia' }">
            <div class="chat-tabs">
              <div 
                class="chat-tab" 
                :class="{ 'active': activeTab === 'general' }"
                @click="setTab('general')"
              >
                Зал суду
              </div>
              <div 
                v-if="isMafia"
                class="chat-tab mafia-tab" 
                :class="{ 'active': activeTab === 'mafia', 'pulse-animation': gamePhase === 'night' }"
                @click="setTab('mafia')"
              >
                Шифровка 🕵️‍♂️
              </div>
            </div>
            
            <div class="chat-messages" ref="chatMessages">
              <!-- Общий чат -->
              <template v-if="activeTab === 'general'">
                <div v-for="message in messages" :key="message.id" class="msg" :class="{
                  'isPersonal': message.type === 'personal',
                  'isSystem': message.type === 'system',
                  'isError': message.type === 'error'
                }">
                  <template v-if="message.type === 'chat'">
                    <strong>{{ message.username }}:</strong> {{ message.message }}
                  </template>
                  <template v-else-if="message.type === 'system'">
                    <span class="system-message-text">{{ message.message }}</span>
                  </template>
                  <template v-else-if="message.type === 'error'">
                    <span class="error-message-text">{{ message.message }}</span>
                  </template>
                  <template v-else>
                    {{ message.message }}
                  </template>
                </div>
              </template>

              <!-- Чат мафии -->
              <template v-else-if="activeTab === 'mafia'">
                <div v-for="(message, index) in mafiaMessages" :key="'mafia-'+index" class="msg mafia-msg">
                  <strong>[Мафія] {{ message.username }}:</strong> {{ message.message }}
                </div>
              </template>
            </div>

            <div class="chat-input">
              <input
                v-if="activeTab === 'general' && gamePhase === 'night' && isGameStarted"
                type="text"
                placeholder="Місто заснуло... Наказувати заборонено."
                disabled
                class="input disabled-input"
              />
              <input
                v-else
                type="text"
                v-model="newMessage"
                @keyup.enter="sendMessage"
                :placeholder="activeTab === 'mafia' ? 'Пишіть спільникам...' : 'Введіть показання...'"
              />
              <button 
                @click="sendMessage"
                :disabled="activeTab === 'general' && gamePhase === 'night' && isGameStarted"
              >
                Ввід
              </button>
            </div>
          </div>
        </aside>

      </main>

      <!-- ПАНЕЛЬ УПРАВЛЕНИЯ -->
      <footer class="game-controls-panel">
        <button @click="leaveRoom" class="btn-newspaper-control danger">
          🚪 Вийти з кімнати
        </button>

        <!-- Кнопка ночного действия -->
        <button
          v-if="gamePhase === 'night' && canPerformNightAction && !hasCompletedNightAction && !showNightActionModal"
          @click="showNightActionModal = true"
          class="btn-newspaper-control night-action"
        >
          🌃 Відкрити нічні дії
        </button>

        <!-- Кнопка голосования (днем) -->
        <button
          v-if="canVote && gamePhase === 'day'"
          @click="showVoteModal = true"
          class="btn-newspaper-control vote-action"
        >
          ⚖️ Голосувати
        </button>

        <!-- Кнопка готовности с механикой удержания -->
        <button 
          v-if="!isGameStarted"
          @mousedown="startHold"
          @mouseup="handleMouseUp"
          @mouseleave="cancelHold"
          @touchstart="startHold"
          @touchend="handleMouseUp"
          @click="handleClick"
          class="btn-newspaper-control hold-ready"
          :class="{ 'ready': isReady }"
        >
          <div v-if="!isReady" class="hold-progress" :style="{ width: progress + '%' }"></div>
          <span class="button-text">
            {{ isReady ? '✔️ Готовий (Натисніть для скасування)' : '⏳ Затисніть для готовності' }}
          </span>
        </button>

        <!-- Кнопка старта игры владельца -->
        <button 
          v-if="isOwner && canStartGame" 
          @click="startGame" 
          class="btn-newspaper-control start-game"
        >
          🏁 Почати гру
        </button>
        <div v-else-if="isOwner && !isGameStarted" class="start-game-waiting">
          <template v-if="players.length < room.min_players_number">
            Очікування гравців ({{ players.length }}/{{ room.min_players_number }})
          </template>
          <template v-else-if="!players.every(p => p.is_ready)">
            Очікування готовності гравців
          </template>
        </div>
      </footer>

    </div>
  </div>

  <!-- УНИВЕРСАЛЬНОЕ МОДАЛЬНОЕ ОКНО (ОВЕРЛЕЙ) -->
  <div class="wow-modal-overlay" :class="{ 'active': isAnyModalOpen }" id="main-modal-overlay">
    
    <!-- МОДАЛКА: ВАША РОЛЬ (ОБЪЯВЛЕНИЕ В НАЧАЛЕ ИГРЫ) -->
    <div v-if="showRoleModal" class="suspect-file-modal" style="display: block;">
      <div class="file-header">ОТРИМАНО СЕКРЕТНЕ ЗАВДАННЯ</div>
      <div class="file-content">
        <div class="file-photo-placeholder role-photo"></div>
        <div class="file-details">
          <h4>Ваша роль: <span class="role-highlight">{{ 
            myRole === 'mafia' ? 'Мафія 🔫' : 
            myRole === 'mafia_don' ? 'Дон Мафії 🕶️' : 
            myRole === 'doctor' ? 'Лікар 🩺' : 
            myRole === 'detective' ? 'Комісар 🔎' : 
            'Мирний житель 👨‍🌾' 
          }}</span></h4>
          <p>Дотримуйтесь таємниці слідства. Не розголошуйте свої документи стороннім особам.</p>
          
          <div v-if="['mafia', 'mafia_don'].includes(myRole) && otherMafia.length > 0" class="other-mafia-box">
            <h5>Ваші спільники:</h5>
            <ul>
              <li v-for="mafia in otherMafia" :key="mafia.id">
                🕵️‍♂️ {{ mafia.name || mafia.username }} (ID: {{ mafia.id }})
              </li>
            </ul>
          </div>
        </div>
      </div>
      <div class="file-actions">
        <button class="btn-vote" @click="showRoleModal = false">Прийняти до відома</button>
      </div>
    </div>

    <!-- МОДАЛКА: КАРТОЧКА ПОДОЗРЕВАЕМОГО ДЛЯ ВЗАИМОДЕЙСТВИЯ -->
    <div v-if="selectedPlayerForModal" class="suspect-file-modal" style="display: block;">
      <button class="btn-close-file" @click="closePlayerModal">✖</button>
      <div class="file-header">ОСОБОВА СПРАВА №{{ selectedPlayerForModal.id }}</div>
      
      <div class="file-content">
        <div class="file-photo-placeholder">
          <span class="placeholder-id">#{{ selectedPlayerForModal.id }}</span>
        </div>
        <div class="file-details">
          <h4>{{ selectedPlayerForModal.name || selectedPlayerForModal.username }}</h4>
          <p><strong>Статус:</strong> {{ selectedPlayerForModal.is_alive ? 'Живий подозрюваний' : 'Ліквідований' }}</p>
          <p><strong>Алібі:</strong> {{ selectedPlayerForModal.is_alive ? 'Перевіряється у залі суду.' : 'Алібі більше не потрібне.' }}</p>
        </div>
      </div>

      <div class="file-actions">
        <!-- Кнопка голосования (днем) -->
        <button 
          v-if="canVote && gamePhase === 'day' && selectedPlayerForModal.is_alive" 
          class="btn-vote" 
          @click="vote(selectedPlayerForModal.id); closePlayerModal();"
        >
          Звинуватити (День)
        </button>
        <!-- Кнопка ночного действия -->
        <button 
          v-if="gamePhase === 'night' && canPerformNightAction && !hasCompletedNightAction && selectedPlayerForModal.is_alive" 
          class="btn-night-action" 
          @click="performNightAction(selectedPlayerForModal.id); closePlayerModal();"
        >
          Обрати ціллю (Ніч)
        </button>
      </div>
    </div>

    <!-- МОДАЛКА: ГОЛОСОВАНИЕ (ОБЩИЙ СПИСОК) -->
    <div v-if="showVoteModal && !showRoleModal" class="suspect-file-modal" style="display: block;">
      <button class="btn-close-file" @click="showVoteModal = false">✖</button>
      <div class="file-header">ДЕННЕ СУДОВЕ ГОЛОСУВАННЯ</div>
      <p class="vote-description">Оберіть справу підсудного для винесення вироку:</p>
      
      <div class="modal-players-list">
        <div 
          v-for="player in alivePlayers" 
          :key="player.id" 
          class="modal-player-row" 
          @click="vote(player.id); showVoteModal = false;"
        >
          <div class="row-avatar">#{{ player.id }}</div>
          <div class="row-name">{{ player.name || player.username }}</div>
          <div class="row-action-indicator">⚖️ Проголосувати</div>
        </div>
      </div>
      <div class="file-actions">
        <button class="btn-vote" @click="showVoteModal = false">Скасувати</button>
      </div>
    </div>

    <!-- МОДАЛКА: НОЧНЫЕ ДЕЙСТВИЯ (ОБЩИЙ СПИСОК) -->
    <div v-if="showNightActionModal && amIAlive && !showRoleModal" class="suspect-file-modal" style="display: block;">
      <button class="btn-close-file" @click="showNightActionModal = false">✖</button>
      <div class="file-header">
        {{ 
          myRole === 'mafia' || myRole === 'mafia_don' ? 'ОБРАТИ ЖЕРТВУ СИНДИКАТУ' : 
          myRole === 'doctor' ? 'ОБРАТИ ГРАВЦЯ ДЛЯ ЛІКУВАННЯ' : 
          'ОБРАТИ ГРАВЦЯ ДЛЯ ПЕРЕВІРКИ' 
        }}
      </div>
      
      <div class="modal-players-list">
        <div 
          v-for="player in alivePlayers" 
          :key="player.id" 
          class="modal-player-row action-row" 
          @click="performNightAction(player.id); showNightActionModal = false;"
        >
          <div class="row-avatar">#{{ player.id }}</div>
          <div class="row-name">{{ player.name }}</div>
          <div class="row-action-indicator night">🌃 Виконати дію</div>
        </div>
      </div>
      <div class="file-actions">
        <button class="btn-vote" @click="showNightActionModal = false">Згорнути</button>
      </div>
    </div>

  </div>

  <!-- ТОСТЫ / УВЕДОМЛЕНИЯ -->
  <div class="notifications-container">
    <transition-group name="toast">
      <div 
        v-for="notif in notifications" 
        :key="notif.id" 
        class="toast" 
        :class="notif.type"
      >
        {{ notif.message }}
      </div>
    </transition-group>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '@/services/api'

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
const selectedPlayerForModal = ref(null) // Для детальной модалки игрока
const showRoleModal = ref(false)
const showVoteModal = ref(false)
const showNightActionModal = ref(false)
const isLeaving = ref(false)
const mafiaMessages = ref([])
const activeTab = ref('general')
const isMafia = computed(() => ['mafia', 'mafia_don'].includes(myRole.value))
const hasCompletedNightAction = ref(false)

const isAnyModalOpen = computed(() => {
  return showRoleModal.value || selectedPlayerForModal.value || showVoteModal.value || showNightActionModal.value
})

const myPlayerObject = computed(() => {
  const userId = currentUserId.value
  return players.value.find(p => p.id === userId)
})

const otherPlayers = computed(() => {
  const userId = currentUserId.value
  return players.value.filter(p => p.id !== userId)
})

const setTab = (tab) => {
  if (tab === 'mafia' && !isMafia.value) return
  activeTab.value = tab
  
  nextTick(() => {
    if (chatMessages.value) {
      chatMessages.value.scrollTop = chatMessages.value.scrollHeight
    }
  })
}

const handlePlayerClick = (player) => {
  selectedPlayerForModal.value = player
}

const closePlayerModal = () => {
  selectedPlayerForModal.value = null
}

const progress = ref(0)
let holdTimer = null
let progressInterval = null
const HOLD_DURATION = 1500

let wasHoldCompleted = false

const startHold = (e) => {
  if (isReady.value) return
  if (e.type === 'touchstart') e.preventDefault()

  progress.value = 0
  wasHoldCompleted = false
  
  const tickRate = 30 
  const step = 100 / (HOLD_DURATION / tickRate)

  progressInterval = setInterval(() => {
    if (progress.value < 100) {
      progress.value += step
    }
  }, tickRate)

  holdTimer = setTimeout(() => {
    completeHold()
  }, HOLD_DURATION)
}

const cancelHold = () => {
  if (isReady.value) return
  clearTimeout(holdTimer)
  clearInterval(progressInterval)
  progress.value = 0 
}

const handleMouseUp = () => {
  if (isReady.value) return
  cancelHold()
}

const completeHold = () => {
  clearTimeout(holdTimer)
  clearInterval(progressInterval)
  
  progress.value = 100
  isReady.value = true 
  wasHoldCompleted = true

  sendReadyStateToServer(true)

  setTimeout(() => {
    wasHoldCompleted = false
  }, 500)
}

const handleClick = () => {
  if (wasHoldCompleted) {
    return
  }
  if (isReady.value) {
    isReady.value = false
    progress.value = 0
    sendReadyStateToServer(false)
  }
}

const sendReadyStateToServer = (targetState) => {
  if (!ws.value || ws.value.readyState !== WebSocket.OPEN) {
    console.warn('WebSocket не підключено')
    return
  }

  const message = {
    type: 'toggle_ready',
    payload: {
      is_ready: targetState
    }
  }

  try {
    ws.value.send(JSON.stringify(message))
  } catch (error) {
    console.error('Помилка відправки статусу готовності:', error)
  }
}

const notifications = ref([])
let notifId = 0

const currentUserId = computed(() => parseInt(localStorage.getItem('userId')));

const kickPlayer = (playerId) => {
  if (!confirm('Ви впевнені, що хочете вигнати цього гравця з кімнати?')) return;

  const message = {
    type: 'kick_player',
    payload: {
      player_id: playerId
    }
  };
  
  if (ws.value && ws.value.readyState === WebSocket.OPEN) {
    ws.value.send(JSON.stringify(message));
  } else {
    showNotification('Помилка: WebSocket не підключено', 'error');
  }
};

const showNotification = (message, type = 'info') => {
  const id = notifId++
  notifications.value.push({ id, message, type })
  
  setTimeout(() => {
    notifications.value = notifications.value.filter(n => n.id !== id)
  }, 10000)
}

const leaveRoom = () => {
  if (confirm('Ви впевнені, що хочете вийти з кімнати?')) {
    isLeaving.value = true
    if (ws.value) {
      ws.value.close(1000)
    }
    router.push('/rooms')
  }
};

const isOwner = computed(() => {
  const userId = parseInt(localStorage.getItem('userId'))
  return room.value.owner === userId
})

const canStartGame = computed(() => {
  const playersCount = players.value.length
  const minPlayers = room.value?.min_players_number || 6
  const allReady = players.value.every(p => p.is_ready)
  return playersCount >= minPlayers && allReady
})

const alivePlayers = computed(() => {
  return players.value.filter(player => player.is_alive)
})

const amIAlive = computed(() => {
  const userId = parseInt(localStorage.getItem('userId'))
  const me = players.value.find(p => p.id === userId)
  return me ? me.is_alive : false
})

const canPerformNightAction = computed(() => {
  if (gamePhase.value !== 'night') return false
  if (!myRole.value) return false
  return ['mafia','mafia_don', 'doctor', 'detective'].includes(myRole.value)
})

const canVote = computed(() => {
  return gamePhase.value === 'day' && myRole.value
})

const fetchRoom = async () => {
  try {
    const response = await api.get(`/api/rooms/${route.params.id}`)
    room.value = response.data
    roomOwner.value = response.data.owner
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
      is_owner: player.id == room.value.owner,
      is_alive: player.is_alive ?? true
    }))
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
      message: msg.message,
      type: msg.type || 'chat',
      timestamp: msg.created_at
    }))
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
    return
  }

  if (reconnectTimeout.value) {
    clearTimeout(reconnectTimeout.value)
  }

  const token = localStorage.getItem('token')
  if (!token) {
    router.push('/login')
    return
  }

  if (!route.params.id) {
    router.push('/rooms')
    return
  }

  const backendHost = import.meta.env.VITE_API_URL.replace(/^https?:\/\//, '')
  const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  const wsUrl = `${wsProtocol}//${backendHost}/api/ws/room/${route.params.id}?token=${token}`
  
  try {
    ws.value = new WebSocket(wsUrl)
    
    ws.value.onopen = async () => {
      reconnectAttempts.value = 0
      if (reconnectTimeout.value) {
        clearTimeout(reconnectTimeout.value)
        reconnectTimeout.value = null
      }
      await fetchRoom()
      await fetchPlayers()
      fetchMessages()
    }
    
    ws.value.onmessage = (event) => {
      try {
        handleWebSocketMessage(event)
      } catch (error) {
        console.error('Error parsing message:', error)
      }
    }
    
    ws.value.onerror = (error) => {
      console.error('WebSocket error:', error)
    }
    
    ws.value.onclose = (event) => {
      if (isLeaving.value) {
        return
      }

      if (reconnectTimeout.value) {
        clearTimeout(reconnectTimeout.value)
      }
      
      switch (event.code) {
        case 4000:
        case 4001:
          router.push('/login')
          return
        case 4002:
        case 4003:
          router.push('/rooms')
          return
      }
      
      if (event.code !== 1000 && reconnectAttempts.value < maxReconnectAttempts && route.params.id) {
        reconnectAttempts.value++
        reconnectTimeout.value = setTimeout(connectWebSocket, 2000 * reconnectAttempts.value)
      } else if (reconnectAttempts.value >= maxReconnectAttempts) {
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
    
    switch (data.type) {
      case 'game_over':
        showNotification(data.message, data.winner === 'citizens' ? 'success' : 'error')
        break;

      case 'you_were_kicked':
        showNotification('Вас було вигнано з кімнати власником', 'error');
        isLeaving.value = true;
        if (ws.value) {
          ws.value.close(1000);
        }
        router.push('/rooms');
        break;

      case 'roles_reveal':
        let revealMessage = '🕵️‍♂️ СКЛАД КОМАНД:\n'
        data.players.forEach(p => {
          let roleEmoji = '👨‍🌾 Мирний'
          if (p.role === 'mafia') roleEmoji = '🔫 Мафія'
          if (p.role === 'mafia_don') roleEmoji = '🔫 Мафія Дон'
          if (p.role === 'doctor') roleEmoji = '🩺 Лікар'
          if (p.role === 'detective') roleEmoji = '🔎 Комісар'
          
          const status = p.is_alive ? '❤️ Живий' : '💀 Вбитий'
          revealMessage += `• ${p.name}: ${roleEmoji} (${status})\n`
        })
        showNotification(revealMessage, 'info')
        break;

      case 'player_saved':
        showNotification(data.message, 'success')
        break;
      
      case 'player_killed':
      case 'player_killed_vote':
        showNotification(data.message, 'error')
        const killedId = data.target_id || data.player_id; 
        if (killedId) {
          const victim = players.value.find(p => p.id === killedId);
          if (victim) {
            victim.is_alive = false;
          }
        }
        break;
        
      case 'investigation_result':
        const roleMsg = data.is_mafia ? 'МАФІЯ 🔫' : 'Мирний 👨‍🌾'
        showNotification(`Результат перевірки: ${data.target} — ${roleMsg}`, 'info')
        break;
        
      case 'vote_cast':
        showNotification(`${data.from} голосує проти: ${data.to}`, 'warning')
        break;
        
      case 'vote_tie':
        showNotification(data.message, 'warning')
        break;

      case 'room_state':
        gamePhase.value = data.room.phase;
        currentRound.value = data.room.round;
        players.value = data.room.players;
        break;

      case 'player_joined':
        players.value = data.players;
        messages.value.push({
          type: 'system',
          message: `${data.username} приєднався до гри`
        });
        break;

      case 'player_left':
        players.value = data.players;
        messages.value.push({
          type: 'system',
          message: `${data.username} покинув гру`
        });
        break;

      case 'player_ready':
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
        myRole.value = data.role;
        showRoleModal.value = true;
        
        if (['mafia', 'mafia_don'].includes(data.role) && data.other_mafia) {
          otherMafia.value = data.other_mafia;
        }
        
        messages.value.push({
          type: 'personal',
          message: `Ваша роль: ${data.role}`
        });
        break;

      case 'game_started':
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
        gamePhase.value = data.phase;
        currentRound.value = data.round;
        hasCompletedNightAction.value = false;

        if (data.phase === 'night') {
          if (['mafia','mafia_don', 'doctor', 'detective'].includes(myRole.value)) {
            showNightActionModal.value = true;
          }
        }
        
        messages.value.push({
          type: 'system',
          message: data.phase === 'night' ? 'Настала ніч' : 'Настав день'
        });
        break;

      case 'chat':
        messages.value.push({
          type: 'chat',
          username: data.username,
          message: data.message
        });
        break;

      case 'mafia_chat':
        mafiaMessages.value.push({
          type: 'mafia_chat',
          username: data.username,
          message: data.message
        });
        break;

      case 'system':
        messages.value.push({
          type: 'system',
          message: data.message
        });
        break;

      case 'error':
        messages.value.push({
          type: 'error',
          message: data.message
        });
        break;

      default:
        console.warn('Unknown message type:', data.type);
    }

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
    const targetType = activeTab.value === 'mafia' ? 'mafia_chat' : 'chat'
    const message = {
      type: targetType, 
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
    if (reconnectAttempts.value < maxReconnectAttempts) {
      connectWebSocket()
    }
  }
}

const startGame = async () => {
  if (!canStartGame.value) return
  try {
    const message = {
      type: 'start_game',
      payload: {
        room_id: route.params.id
      }
    }
    ws.value.send(JSON.stringify(message))
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
      hasCompletedNightAction.value = true;
      messages.value.push({
        type: 'system',
        message: `Ви виконали нічну дію як ${myRole.value}`
      });
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
        player_id: parseInt(localStorage.getItem('userId')),
        target_id: targetId
      }
    }
    if (ws.value && ws.value.readyState === WebSocket.OPEN) {
      ws.value.send(JSON.stringify(message))
      showVoteModal.value = false
    }
  } catch (error) {
    console.error('Error voting:', error)
  }
}

onMounted(() => {
  connectWebSocket()
  fetchMessages()
  fetchRoom()
})

onUnmounted(() => {
  isLeaving.value = true
  if (ws.value) {
    ws.value.onclose = null
    ws.value.onerror = null
    ws.value.close(1000) 
    ws.value = null
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
/* =========================================
   ОБЩИЕ ПЕРЕМЕННЫЕ И ШРИФТЫ
   ========================================= */
.newspaper-wrapper {
  position: relative;
  max-width: 1300px;
  width: 100%;
  margin: 40px auto;
  z-index: 1;
  filter: drop-shadow(0 25px 35px rgba(0, 0, 0, 0.8));
  box-sizing: border-box;
}

/* Эффект многослойной старой бумаги за газетой */
.newspaper-wrapper::before,
.newspaper-wrapper::after {
  content: '';
  position: absolute;
  background-color: var(--paper-shadow);
  border: 1px solid rgba(0, 0, 0, 0.15);
  transition: background-color 0.4s ease;
}
.newspaper-wrapper::before { top: 4px; left: -6px; right: 6px; bottom: -4px; transform: rotate(-0.5deg); z-index: -1; }
.newspaper-wrapper::after { top: 8px; left: 4px; right: -8px; bottom: -3px; transform: rotate(0.8deg); z-index: -2; }

.newspaper-main {
  background-color: var(--paper-color);
  padding: 35px 45px;
  position: relative;
  z-index: 2;
  box-shadow: inset 0 0 60px rgba(0, 0, 0, 0.2);
  font-family: var(--font-ui);
  color: var(--ink-color);
  transition: background-color 0.4s ease, color 0.4s ease, border-color 0.4s ease, box-shadow 0.4s ease;
}

.newspaper-main,
.hero-dossier,
.room-status-badge,
.phase-badge,
.suspect-polaroid,
.polaroid-img,
.polaroid-name,
.polaroid-overlay,
.typewriter-chat,
.chat-tabs .chat-tab,
.chat-messages,
.chat-input input,
.chat-input button,
.game-controls-panel,
.hold-ready {
  transition: background-color 0.4s ease, color 0.4s ease, border-color 0.4s ease, box-shadow 0.4s ease;
}

/* Шум поверх основной подложки */
.newspaper-main::before {
  content: '';
  position: absolute;
  top: 0; left: 0; width: 100%; height: 100%;
  background-image: url('data:image/svg+xml;utf8,<svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg"><filter id="noiseFilter"><feTurbulence type="fractalNoise" baseFrequency="0.8" numOctaves="3" stitchTiles="stitch"/></filter><rect width="100%" height="100%" filter="url(%23noiseFilter)" opacity="0.04"/></svg>');
  pointer-events: none;
  z-index: 99;
}



/* =========================================
   ГАЗЕТНЫЙ ХЕДЕР
   ========================================= */
.newspaper-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-top: 5px double var(--ink-color);
  border-bottom: 2px solid var(--ink-color);
  padding: 20px 0;
  margin-bottom: 35px;
  flex-wrap: wrap;
  gap: 20px;
}

.logo-block {
  display: flex;
  flex-direction: column;
}

.room-info-header {
  padding: 10px 0;
  margin-bottom: 25px;
}

.room-title {
  font-family: var(--font-heading);
  font-size: 2rem;
  font-weight: bold;
  text-transform: uppercase;
  color: var(--ink-color);
  margin: 0;
}

.header-right { 
  display: flex; 
  align-items: center; 
  gap: 20px; 
  flex-wrap: wrap;
}

.room-status-badge {
  font-family: var(--font-text);
  font-size: 1rem;
  border: 1px solid var(--ink-color);
  padding: 5px 10px;
}

.phase-badge {
  font-family: var(--font-text);
  font-size: 1.1rem;
  font-weight: bold;
  color: var(--accent-color);
}

.night-phase-pulse {
  animation: pulse-night-badge 2s infinite;
}

@keyframes pulse-night-badge { 
  0% { opacity: 1; } 
  50% { opacity: 0.4; } 
  100% { opacity: 1; } 
}

/* =========================================
   СЕТКА КОНТЕНТА
   ========================================= */
.content-grid {
  display: grid; 
  grid-template-columns: 2.5fr 1.5fr; 
  gap: 40px;
  margin-bottom: 40px;
}

.section-title {
  font-family: var(--font-heading); 
  font-size: 1.8rem; 
  text-transform: uppercase;
  border-bottom: 2px solid var(--ink-color); 
  padding-bottom: 5px; 
  margin-bottom: 25px;
  color: var(--ink-color);
}

/* =========================================
   ДОСЬЕ ТЕКУЩЕГО ИГРОКА (ДЕЛЮКС ОФОРМЛЕНИЕ)
   ========================================= */
.hero-dossier {
  background-color: var(--paper-color); 
  padding: 20px;
  border: 1px solid var(--ink-color);
  box-shadow: 10px 10px 20px rgba(0,0,0,0.4), inset 0 0 40px rgba(0,0,0,0.05);
  position: relative; 
  transform: rotate(-1deg);
  transition: background-color 0.4s ease, color 0.4s ease, border-color 0.4s ease, transform 0.4s ease, box-shadow 0.4s ease;
  display: flex; 
  gap: 20px; 
  margin-bottom: 40px;
  z-index: 5;
}

.hero-dossier:hover {
  transform: rotate(0deg) scale(1.02) translateY(-5px);
  box-shadow: 15px 15px 30px rgba(0,0,0,0.6);
}

.dossier-photo-container {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.dossier-photo {
  width: 140px; 
  height: 180px; 
  flex-shrink: 0;
  background: var(--ink-color); 
  border: 4px solid var(--paper-color);
  box-shadow: 0 0 0 1px var(--ink-color);
  background-image: repeating-radial-gradient(circle at 50% 50%, transparent 0, transparent 4px, rgba(255,255,255,0.05) 5px);
  display: flex;
  justify-content: center;
  align-items: center;
  color: var(--paper-color);
  font-family: var(--font-heading);
  font-size: 2rem;
  font-weight: bold;
}

.dossier-info { 
  font-family: var(--font-text); 
  font-size: 0.9rem; 
  line-height: 1.5; 
  color: var(--ink-color);
}

.dossier-info h3 { 
  font-family: var(--font-heading); 
  font-size: 1.6rem; 
  text-transform: uppercase; 
  margin-bottom: 10px;
}

.dossier-info ul { 
  margin-top: 10px; 
  list-style: square inside; 
}

/* Штамп роли */
.stamp-role {
  position: absolute; 
  bottom: 15px; 
  right: 15px;
  font-family: var(--font-heading); 
  font-size: 2.2rem; 
  font-weight: 900;
  color: var(--accent-color); 
  border: 4px solid var(--accent-color);
  padding: 5px 20px; 
  border-radius: 5px; 
  text-transform: uppercase;
  transform: rotate(-15deg);
  opacity: 0.95;
  pointer-events: none;
  background-color: var(--paper-color);
}

/* =========================================
   ПОЛАРОИДНЫЕ СНИМКИ (ПОДОЗРЕВАЕМЫЕ)
   ========================================= */
.suspects-area {
  display: flex; 
  flex-wrap: wrap; 
  gap: 25px; 
  padding-top: 10px;
}

.suspect-polaroid {
  background: var(--paper-color); 
  width: 160px; 
  height: 200px;
  padding: 10px 10px 20px 10px; 
  border: 1px solid rgba(0,0,0,0.2);
  box-shadow: 5px 10px 15px rgba(0,0,0,0.4);
  display: flex; 
  flex-direction: column; 
  position: relative; 
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.25, 1.5, 0.5, 1);
}

/* Случайный поворот для эффекта разбросанных снимков */
.suspect-polaroid:nth-child(odd) { transform: rotate(-3deg); }
.suspect-polaroid:nth-child(even) { transform: rotate(4deg) translateY(-5px); }

.suspect-polaroid:hover {
  transform: rotate(0deg) scale(1.15) translateY(-15px) !important;
  box-shadow: 0 25px 35px rgba(0,0,0,0.6); 
  z-index: 50;
}

.polaroid-img {
  flex-grow: 1; 
  background: var(--ink-color); 
  margin-bottom: 10px; 
  position: relative; 
  overflow: hidden;
}

.polaroid-id-badge {
  position: absolute;
  top: 5px;
  left: 5px;
  background: rgba(0, 0, 0, 0.6);
  color: #fff;
  padding: 2px 6px;
  font-size: 0.7rem;
  font-family: var(--font-text);
}

.polaroid-overlay {
  position: absolute; 
  top: 0; left: 0; width: 100%; height: 100%;
  background: rgba(43, 43, 43, 0.8); 
  display: flex; 
  justify-content: center; 
  align-items: center;
  font-family: var(--font-heading); 
  font-size: 1.1rem; 
  color: #fff; 
  font-weight: bold;
  text-transform: uppercase; 
  opacity: 0; 
  transition: opacity 0.3s;
  border: 2px dashed rgba(255,255,255,0.5);
  text-align: center;
}



.suspect-polaroid:hover .polaroid-overlay { 
  opacity: 1; 
}

.polaroid-name { 
  font-family: var(--font-text); 
  font-size: 0.9rem; 
  font-weight: bold; 
  text-align: center; 
  text-transform: uppercase; 
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  color: var(--ink-color);
}

/* Значки поверх полароида */
.polaroid-badges {
  position: absolute;
  bottom: 25px;
  right: 12px;
  display: flex;
  gap: 5px;
}

.badge-owner-icon,
.badge-ready-icon {
  background: rgba(0,0,0,0.7);
  border-radius: 50%;
  width: 22px;
  height: 22px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.8rem;
}

/* Ликвидированные (мертвые) игроки */
.suspect-polaroid.dead { 
  filter: grayscale(100%); 
}

.suspect-polaroid.dead::after {
  content: 'ЛІКВІДОВАНИЙ'; 
  position: absolute; 
  top: 40%; 
  left: -10px; 
  width: 120%;
  font-family: var(--font-heading); 
  font-size: 1.1rem; 
  font-weight: bold; 
  color: var(--accent-color);
  border-top: 2px solid; 
  border-bottom: 2px solid; 
  text-align: center; 
  transform: rotate(-20deg);
  background: rgba(255, 255, 255, 0.95); 
  padding: 5px 0; 
  box-shadow: 0 5px 15px rgba(0,0,0,0.5);
  z-index: 5;
}


/* Кнопка кика внутри полароида */
.kick-button-polaroid {
  position: absolute;
  top: -5px;
  right: -5px;
  background: var(--accent-color);
  border: 1px solid var(--ink-color);
  color: #fff;
  border-radius: 50%;
  width: 24px;
  height: 24px;
  font-size: 0.8rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.2s;
  z-index: 20;
}

.kick-button-polaroid:hover {
  transform: scale(1.2);
}

/* =========================================
   ПИШУЩАЯ МАШИНКА (ИГРОВОЙ ЧАТ)
   ========================================= */
.typewriter-chat {
  background: var(--paper-color); 
  border: 1px solid var(--ink-color);
  box-shadow: 8px 8px 15px rgba(0,0,0,0.4);
  display: flex; 
  flex-direction: column; 
  height: 100%; 
  min-height: 550px;
  position: relative; 
  transform: rotate(0.5deg);
}

.typewriter-chat::before {
  content: ''; 
  position: absolute; 
  top: -12px; 
  left: -5px; 
  right: -5px; 
  height: 20px;
  background: #111; 
  border-radius: 4px; 
  box-shadow: inset 0 -3px 8px rgba(255,255,255,0.2), 0 5px 10px rgba(0,0,0,0.5); 
  z-index: 10;
}

.chat-tabs { 
  display: flex; 
  margin-top: 20px; 
  border-bottom: 2px solid var(--ink-color); 
}

.chat-tab {
  flex: 1; 
  text-align: center; 
  padding: 12px; 
  font-family: var(--font-text); 
  font-weight: bold;
  cursor: pointer; 
  text-transform: uppercase; 
  background: var(--card-bg); 
  opacity: 0.6; 
  transition: 0.3s;
  color: var(--ink-color);
  user-select: none;
}

.chat-tab.active { 
  opacity: 1; 
  background: transparent; 
  border-bottom: 3px solid var(--accent-color); 
}

.mafia-tab.active {
  color: var(--accent-color);
}

.typewriter-chat.mafia-mode {
  border-color: var(--accent-color);
}

.chat-messages {
  flex-grow: 1; 
  padding: 20px; 
  overflow-y: auto;
  font-family: var(--font-text); 
  font-size: 0.95rem; 
  line-height: 1.6;
  display: flex; 
  flex-direction: column; 
  gap: 15px;
  max-height: 420px;
  background: transparent;
}

.msg { 
  position: relative; 
  padding-left: 15px; 
  border-bottom: 1px dashed rgba(0,0,0,0.1); 
  padding-bottom: 10px;
  color: var(--ink-color);
}


.msg::before { 
  content: '►'; 
  position: absolute; 
  left: 0; 
  color: var(--accent-color); 
  font-size: 0.6rem; 
  top: 5px; 
}

.msg strong { 
  font-family: var(--font-heading); 
  font-size: 1.1rem; 
}

/* Системные и Личные типы сообщений */
.msg.isPersonal {
  background: rgba(107, 33, 33, 0.08);
  border-left: 3px solid var(--accent-color);
  padding-left: 10px;
  font-weight: bold;
}

.msg.isSystem {
  font-style: italic;
  opacity: 0.8;
}

.system-message-text {
  color: var(--accent-color);
  font-weight: bold;
}

.msg.isError {
  border-left: 3px solid #f44336;
  background: rgba(244, 67, 54, 0.05);
  padding-left: 10px;
}

.error-message-text {
  color: #f44336;
  font-weight: bold;
}

/* Чат мафии */
.mafia-msg {
  background: rgba(107, 33, 33, 0.05);
  border-left: 3px solid var(--accent-color);
  padding-left: 10px;
}

/* Форма отправки в стиле пишущей машинки */
.chat-input { 
  padding: 15px; 
  border-top: 2px dashed var(--ink-color); 
  display: flex; 
  background: rgba(0,0,0,0.02); 
}

.chat-input input {
  flex-grow: 1; 
  background: transparent; 
  border: none; 
  outline: none; 
  border-bottom: 1px solid var(--ink-color);
  font-family: var(--font-text); 
  font-size: 1rem; 
  color: var(--ink-color); 
  padding: 5px;
}

.chat-input button {
  background: var(--ink-color); 
  color: var(--paper-color); 
  border: none; 
  padding: 5px 20px;
  font-family: var(--font-text); 
  font-weight: bold; 
  cursor: pointer; 
  text-transform: uppercase; 
  margin-left: 15px;
  transition: all 0.2s;
}

.chat-input button:hover:not(:disabled) { 
  background: var(--accent-color); 
}

.chat-input button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.disabled-input {
  cursor: not-allowed;
  font-style: italic;
}

/* =========================================
   ПАНЕЛЬ КНОПОК УПРАВЛЕНИЯ
   ========================================= */
.game-controls-panel {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  justify-content: center;
  border-top: 2px solid var(--ink-color);
  padding-top: 25px;
  margin-top: 25px;
}

.btn-newspaper-control {
  background: transparent; 
  border: 2px solid var(--ink-color);
  color: var(--ink-color); 
  padding: 10px 20px; 
  font-family: var(--font-text);
  cursor: pointer; 
  text-transform: uppercase; 
  font-weight: bold;
  transition: all 0.3s ease; 
  box-shadow: 4px 4px 0 var(--ink-color);
  font-size: 0.95rem;
}

.btn-newspaper-control:hover:not(:disabled) {
  transform: translate(2px, 2px); 
  box-shadow: 2px 2px 0 var(--ink-color);
  background: var(--ink-color); 
  color: var(--paper-color);
}

.btn-newspaper-control.danger {
  border-color: var(--accent-color);
  color: var(--accent-color);
  box-shadow: 4px 4px 0 var(--accent-color);
}

.btn-newspaper-control.danger:hover {
  background: var(--accent-color);
  color: #fff;
}

.btn-newspaper-control.night-action {
  border-color: #3f51b5;
  color: #3f51b5;
  box-shadow: 4px 4px 0 #3f51b5;
}

.btn-newspaper-control.night-action:hover {
  background: #3f51b5;
  color: #fff;
}

.btn-newspaper-control.vote-action {
  border-color: var(--accent-color);
  color: var(--accent-color);
  box-shadow: 4px 4px 0 var(--accent-color);
}

.btn-newspaper-control.vote-action:hover {
  background: var(--accent-color);
  color: #fff;
}

/* Кнопка с удержанием */
.btn-newspaper-control.hold-ready {
  position: relative;
  overflow: hidden;
  user-select: none;
  -webkit-user-select: none;
}

.hold-progress {
  position: absolute;
  top: 0; left: 0; height: 100%;
  background-color: rgba(76, 175, 80, 0.3);
  transition: width 0.03s linear;
  z-index: 1;
}

.btn-newspaper-control.hold-ready.ready {
  background: #4caf50;
  color: #fff;
  border-color: #4caf50;
}

.btn-newspaper-control.hold-ready.ready:hover {
  background: var(--accent-color);
  border-color: var(--accent-color);
}

.button-text {
  position: relative;
  z-index: 2;
}

/* Старт игры владельца */
.btn-newspaper-control.start-game {
  border-color: #ff9800;
  color: #ff9800;
  box-shadow: 4px 4px 0 #ff9800;
}

.btn-newspaper-control.start-game:hover {
  background: #ff9800;
  color: #fff;
}

.start-game-waiting {
  display: flex;
  align-items: center;
  font-family: var(--font-text);
  font-size: 0.95rem;
  border: 1px dashed var(--ink-color);
  padding: 5px 15px;
}

/* =========================================
   МОДАЛЬНЫЕ ОКНА (ДЕЛЮКС СТИЛИЗАЦИЯ)
   ========================================= */
.wow-modal-overlay {
  position: fixed; 
  top: 0; left: 0; width: 100%; height: 100%;
  background: rgba(0,0,0,0.85); 
  backdrop-filter: blur(8px);
  display: none; 
  justify-content: center; 
  align-items: center; 
  z-index: 1000;
}

.wow-modal-overlay.active {
  display: flex;
}

.suspect-file-modal {
  background: var(--paper-color);
  border: 2px solid var(--ink-color);
  width: 90%; 
  max-width: 650px;
  padding: 30px;
  box-shadow: 15px 15px 40px rgba(0,0,0,0.8);
  position: relative;
  box-sizing: border-box;
  animation: modal-slam 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.15) forwards;
}

@keyframes modal-slam {
  from { transform: scale(0.8) rotate(-5deg); opacity: 0; }
  to { transform: scale(1) rotate(0deg); opacity: 1; }
}

/* Скрепка на досье */
.suspect-file-modal::before {
  content: ''; 
  position: absolute; 
  top: -15px; 
  left: 50%; 
  transform: translateX(-50%) rotate(5deg);
  width: 30px; 
  height: 80px; 
  border: 4px solid #888; 
  border-radius: 15px;
  box-shadow: 2px 2px 5px rgba(0,0,0,0.5); 
  z-index: 10;
}

.file-header {
  font-family: var(--font-heading); 
  font-size: 1.8rem; 
  text-transform: uppercase;
  border-bottom: 3px double var(--ink-color); 
  padding-bottom: 10px; 
  margin-bottom: 20px;
  text-align: center; 
  letter-spacing: 2px;
  color: var(--ink-color);
}

.file-content { 
  display: flex; 
  gap: 25px; 
  margin-bottom: 30px; 
}

.file-photo-placeholder {
  width: 150px; 
  height: 180px; 
  background: var(--ink-color); 
  flex-shrink: 0;
  border: 5px solid var(--paper-color); 
  box-shadow: 0 0 0 1px var(--ink-color);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--paper-color);
  font-family: var(--font-heading);
  font-size: 1.8rem;
}

.placeholder-id {
  opacity: 0.5;
}

.file-details { 
  font-family: var(--font-text); 
  font-size: 1rem; 
  line-height: 1.6; 
  flex-grow: 1; 
  color: var(--ink-color);
}

.file-details h4 { 
  font-family: var(--font-heading); 
  font-size: 1.5rem; 
  margin-bottom: 15px; 
  color: var(--accent-color); 
}

.file-details p { 
  margin-bottom: 10px; 
  border-bottom: 1px dashed rgba(0,0,0,0.2); 
  padding-bottom: 5px;
}


.role-highlight {
  text-decoration: underline;
}

.other-mafia-box {
  margin-top: 15px;
  padding: 10px;
  background: rgba(107, 33, 33, 0.05);
  border: 1px solid var(--accent-color);
}

.other-mafia-box h5 {
  font-family: var(--font-heading);
  font-size: 1.1rem;
  color: var(--accent-color);
  margin-bottom: 5px;
}

.other-mafia-box ul {
  list-style: none;
  padding: 0;
}

/* Действия в модальном окне */
.file-actions {
  display: flex; 
  gap: 15px; 
  justify-content: flex-end; 
  border-top: 2px solid var(--ink-color); 
  padding-top: 20px;
}

.btn-vote {
  background: transparent; 
  color: var(--ink-color); 
  border: 2px solid var(--ink-color);
  padding: 10px 20px; 
  font-family: var(--font-text); 
  font-weight: bold; 
  cursor: pointer; 
  text-transform: uppercase;
  transition: all 0.2s; 
  box-shadow: 4px 4px 0 var(--ink-color);
}

.btn-vote:hover { 
  background: var(--ink-color); 
  color: var(--paper-color); 
  transform: translate(2px, 2px); 
  box-shadow: 2px 2px 0 var(--ink-color); 
}

.btn-night-action {
  background: var(--accent-color); 
  color: #fff; 
  border: 2px solid var(--accent-color);
  padding: 10px 20px; 
  font-family: var(--font-text); 
  font-weight: bold; 
  cursor: pointer; 
  text-transform: uppercase;
  transition: all 0.2s; 
  box-shadow: 4px 4px 0 rgba(0,0,0,0.5);
}

.btn-night-action:hover { 
  background: #8b0000; 
  transform: translate(2px, 2px); 
  box-shadow: 2px 2px 0 rgba(0,0,0,0.5); 
}

.btn-close-file {
  position: absolute; 
  top: 15px; 
  right: 15px; 
  background: transparent; 
  border: none; 
  font-size: 1.5rem; 
  cursor: pointer; 
  color: var(--ink-color);
  z-index: 50;
}

/* =========================================
   СПИСКИ ИГРОКОВ В МОДАЛКАХ (ДЛЯ ГОЛОСОВАНИЙ)
   ========================================= */
.vote-description {
  font-family: var(--font-text);
  text-align: center;
  margin-bottom: 20px;
  color: var(--ink-color);
}

.modal-players-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 25px;
  max-height: 250px;
  overflow-y: auto;
}

.modal-player-row {
  display: flex;
  align-items: center;
  padding: 12px 15px;
  border: 1px solid var(--ink-color);
  cursor: pointer;
  transition: all 0.2s;
  background: rgba(0, 0, 0, 0.02);
}

.modal-player-row:hover {
  background: var(--ink-color);
  color: var(--paper-color);
}

.row-avatar {
  font-family: var(--font-heading);
  font-weight: bold;
  margin-right: 15px;
  font-size: 1.1rem;
}

.row-name {
  font-family: var(--font-text);
  font-size: 1.05rem;
  flex-grow: 1;
}

.row-action-indicator {
  font-family: var(--font-text);
  font-size: 0.9rem;
  font-weight: bold;
}

.modal-player-row:hover .row-action-indicator {
  text-decoration: underline;
}

/* =========================================
   СИСТЕМА ТОСТОВ (УВЕДОМЛЕНИЙ)
   ========================================= */
.notifications-container {
  position: fixed;
  top: 80px;
  right: 20px;
  z-index: 9999;
  display: flex;
  flex-direction: column;
  gap: 12px;
  pointer-events: none;
}

.toast {
  padding: 15px 25px;
  border: 1px solid var(--ink-color);
  background: var(--paper-color);
  color: var(--ink-color);
  font-family: var(--font-text);
  box-shadow: 8px 8px 0 rgba(0,0,0,0.5);
  pointer-events: auto;
  min-width: 280px;
  max-width: 380px;
  line-height: 1.4;
}

.toast.success {
  border-color: #2ecc71;
  background: rgba(46, 204, 113, 0.1);
  color: #27ae60;
}

.toast.error {
  border-color: var(--accent-color);
  background: rgba(107, 33, 33, 0.1);
  color: var(--accent-color);
}

.toast.warning {
  border-color: #f1c40f;
  background: rgba(241, 196, 15, 0.1);
  color: #d35400;
}

/* Анимация тостов */
.toast-enter-active,
.toast-leave-active {
  transition: all 0.4s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}

.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translateX(100%);
}

/* =========================================
   АДАПТИВНАЯ ВЕРСТКА
   ========================================= */
@media (max-width: 1000px) {
  .content-grid { 
    grid-template-columns: 1fr; 
  }
  .hero-dossier { 
    flex-direction: column; 
    align-items: center; 
    text-align: center; 
  }
  .typewriter-chat { 
    min-height: 400px; 
    transform: none; 
    margin-top: 20px; 
  }
  .file-content { 
    flex-direction: column; 
    align-items: center; 
    text-align: center; 
  }
  .file-actions { 
    flex-direction: column; 
  }
  .btn-newspaper-control {
    width: 100%;
  }
}
</style>