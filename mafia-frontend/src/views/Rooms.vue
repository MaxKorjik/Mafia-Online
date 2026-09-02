<template>
  <div class="rooms-container">
    
    <div class="rooms-page-header">
      <h2 class="archive-title">АКТИВНІ СИНДИКАТИ ТА КРИМІНАЛЬНІ СПРАВИ</h2>
      <button @click="showCreateRoomModal = true" class="btn-newspaper create-room-btn">
        Відкрити нове провадження
      </button>
    </div>

    <div class="newspaper-grid">
      
      <section class="dossier-list">
        <div v-if="rooms.length === 0" class="no-rooms-notice">
          <p>У місті Чикаго затишшя... Жодного активного злочинного угрупування не виявлено в реєстрах.</p>
        </div>
        
        <div v-for="room in rooms" :key="room.id" class="dossier-card">
          <div class="dossier-header">
            <h3 class="room-title">Справа: «{{ room.name }}»</h3>
            <span class="players-counter">
              Фігуранти: <strong>{{ room.players_number }}</strong> / {{ room.max_players_number }}
            </span>
          </div>
          
          <div class="dossier-body">
            <div class="dossier-meta">
              <p class="meta-item"><strong>Умова старту:</strong> мінімум {{ room.min_players_number }} оперативників для облави</p>
              
              <div v-if="room.is_private" class="status-stamp stamp-private">
                СЕКРЕТНИЙ АРХІВ
              </div>
              <div v-else class="status-stamp stamp-open">
                ВІДКРИТА ОБЛАВА
              </div>
            </div>
            
            <div class="room-players-section">
              <h4>Підозрювані на місці збору:</h4>
              <div class="players-avatars">
                <template v-if="room.players && room.players.length">
                  <div 
                    v-for="player in room.players" 
                    :key="player.id" 
                    class="player-badge-avatar"
                    :title="player.username"
                  >
                    {{ player.username[0].toUpperCase() }}
                  </div>
                </template>
                <span v-else class="no-players-text">Угрупування формується (немає гравців)</span>
              </div>
            </div>
          </div>

          <div class="dossier-footer">
            <button 
              @click="joinRoom(room)" 
              class="btn-newspaper btn-join"
              :disabled="room.players_number >= room.max_players_number"
            >
              {{ room.players_number >= room.max_players_number ? 'Справу укомплектовано' : 'Впровадитись у синдикат →' }}
            </button>
          </div>
        </div>
      </section>

      <aside class="newspaper-sidebar">
        <div class="sidebar-block filter-section">
          <h3 class="sidebar-heading">Кримінальний розшук</h3>
          <div class="filter-group">
            <p class="filter-tip">Сортування поточних зведень:</p>
            <label class="newspaper-checkbox">
              <input type="checkbox" />
              <span class="checkmark"></span> Приховати повні справи
            </label>
            <label class="newspaper-checkbox">
              <input type="checkbox" />
              <span class="checkmark"></span> Тільки таємні збори
            </label>
          </div>
        </div>
        
        <div class="sidebar-block ad-vintage-block">
          <h4 class="ad-title">УВАГА ГРОМАДЯНАМ!</h4>
          <p class="ad-text">
            Місто засинає... Перевірте, чи добре зачинені ваші клямки та вікна. 
            Редакція «The Mafia News» не несе відповідальності за нічні візити невідомих осіб у чорних капелюхах та довгих плащах.
          </p>
        </div>
      </aside>

    </div>

    <div v-if="showCreateRoomModal" class="newspaper-modal-overlay">
      <div class="newspaper-modal">
        <div class="modal-case-badge">ФОРМА №1932</div>
        
        <h2 class="modal-title">РЕЄСТРАЦІЯ НОВОЇ СПРАВИ</h2>
        <p class="modal-subtitle">Заповніть офіційний бланк детективного відомства Чикаго</p>
        
        <form @submit.prevent="createRoom" class="create-room-form">
          
          <div class="form-group-vintage">
            <label for="roomName">Шифр / Назва синдикату</label>
            <input
              type="text"
              id="roomName"
              v-model="newRoom.name"
              class="input-vintage"
              required
              placeholder="Наприклад: Коза Ностра, Секретний підвал"
            />
          </div>

          <div class="form-row-vintage">
            <div class="form-group-vintage">
              <label for="minPlayers">Мін. детективів (4-12)</label>
              <input
                type="number"
                id="minPlayers"
                v-model="newRoom.min_players_number"
                class="input-vintage"
                required
                min="4"
                max="12"
              />
            </div>

            <div class="form-group-vintage">
              <label for="maxPlayers">Макс. детективів (4-12)</label>
              <input
                type="number"
                id="maxPlayers"
                v-model="newRoom.max_players_number"
                class="input-vintage"
                required
                min="4"
                max="12"
              />
            </div>
          </div>

          <div class="form-group-vintage checkbox-group-vintage">
            <label class="newspaper-checkbox">
              <input
                type="checkbox"
                v-model="newRoom.is_private"
              />
              <span class="checkmark"></span> Засекретити архів (вхід за паролем)
            </label>
          </div>

          <div v-if="newRoom.is_private" class="form-group-vintage encryption-field">
            <label for="password">Секретний шифр доступу</label>
            <input
              type="password"
              id="password"
              v-model="newRoom.password"
              class="input-vintage code-font"
              required
              placeholder="Введіть код доступу"
            />
          </div>

          <div class="modal-buttons-vintage">
            <button type="button" @click="showCreateRoomModal = false" class="btn-vintage-secondary">
              Скасувати запит
            </button>
            <button type="submit" class="btn-vintage-primary" :disabled="loading">
              {{ loading ? 'Запис у реєстр...' : 'Підписати ордер →' }}
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
    fetchRooms() 

    await new Promise(resolve => setTimeout(resolve, 150))
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
  }
  router.push(`/room/${room.id}`)
}

onMounted(fetchRooms)
</script>

<style scoped>
/* Контейнер страницы */
.rooms-container {
  padding: 10px 0;
  min-height: 75vh;
}

/* Заголовок страницы в виде газетной ленты */
.rooms-page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 2px solid var(--ink-color);
  padding-bottom: 15px;
  margin-bottom: 30px;
  flex-wrap: wrap;
  gap: 15px;
}

.archive-title {
  font-family: var(--font-heading);
  font-size: 1.6rem;
  font-weight: 800;
  letter-spacing: 1px;
  color: var(--ink-color);
}

/* Двухколоночная сетка газеты */
.newspaper-grid {
  display: grid;
  grid-template-columns: 3fr 1fr;
  gap: 40px;
}

/* Список досье / карточек комнат */
.dossier-list {
  display: flex;
  flex-direction: column;
  gap: 35px;
}

.no-rooms-notice {
  font-family: var(--font-text);
  font-style: italic;
  opacity: 0.7;
  padding: 20px 0;
}

/* =========================================
   КАРТОЧКА ДЕЛА (Анимации из референса)
   ========================================= */
.dossier-card {
  border: 1px solid var(--ink-color);
  padding: 24px;
  background-color: var(--card-bg, rgba(0, 0, 0, 0.03));
  display: flex;
  flex-direction: column;
  position: relative;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.dossier-card:hover {
  transform: translateY(-2px);
  box-shadow: 5px 5px 0 var(--ink-color);
}

.dossier-card:not(:last-child) {
  margin-bottom: 15px;
}

.dossier-header {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  border-bottom: 1px dashed var(--ink-color);
  padding-bottom: 8px;
  margin-bottom: 15px;
  flex-wrap: wrap;
  gap: 10px;
}

.room-title {
  font-family: var(--font-heading);
  font-size: 1.4rem;
  font-weight: 700;
  text-transform: uppercase;
}

.players-counter {
  font-family: var(--font-ui);
  font-size: 0.95rem;
  text-transform: uppercase;
}

.dossier-body {
  margin-bottom: 20px;
}

.dossier-meta {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 15px;
}

.meta-item {
  font-family: var(--font-text);
  font-size: 0.95rem;
  margin: 0;
}

/* Штампы статуса комнат */
.status-stamp {
  font-family: var(--font-heading);
  font-weight: 900;
  font-size: 0.85rem;
  padding: 4px 10px;
  border: 2px solid var(--ink-color);
  text-transform: uppercase;
  letter-spacing: 1px;
  transform: rotate(-1.5deg);
  opacity: 0.8;
  display: inline-block;
}
.stamp-private {
  color: var(--accent-color);
  border-color: var(--accent-color);
  transform: rotate(2deg);
}
.stamp-open {
  color: #2e5a2e;
  border-color: #2e5a2e;
}

/* Фигуранты дела (Аватары) */
.room-players-section h4 {
  font-family: var(--font-ui);
  font-size: 0.85rem;
  text-transform: uppercase;
  margin-bottom: 10px;
  font-weight: bold;
  letter-spacing: 0.5px;
}

.players-avatars {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  min-height: 34px;
}

.player-badge-avatar {
  width: 34px;
  height: 34px;
  border: 1px solid var(--ink-color);
  background-color: var(--paper-shadow);
  color: var(--ink-color);
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: var(--font-heading);
  font-weight: bold;
  font-size: 1rem;
}

.no-players-text {
  font-family: var(--font-text);
  font-style: italic;
  font-size: 0.9rem;
  opacity: 0.6;
}

/* =========================================
   ГАЗЕТНЫЕ КНОПКИ
   ========================================= */
.btn-newspaper {
  align-self: flex-start;
  padding: 6px 18px;
  background: transparent;
  border: 1px solid var(--ink-color);
  color: var(--ink-color);
  font-family: var(--font-text);
  font-weight: bold;
  text-transform: uppercase;
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-newspaper:hover:not(:disabled) {
  background: var(--ink-color);
  color: var(--paper-color);
}

.btn-newspaper:disabled {
  opacity: 0.4;
  cursor: not-allowed;
  border-style: dashed;
}

/* Специфично для кнопки входа в карточке */
.btn-join {
  width: 100%;
  text-align: center;
}

.create-room-btn {
  align-self: center;
}

/* САЙДБАР (Правая колонка) */
.newspaper-sidebar {
  display: flex;
  flex-direction: column;
  gap: 35px;
  border-left: 2px solid var(--ink-color);
  padding-left: 24px;
}

.sidebar-heading {
  font-family: var(--font-heading);
  font-size: 1.25rem;
  text-transform: uppercase;
  border-bottom: 1px dashed var(--ink-color);
  padding-bottom: 12px;
  margin-bottom: 15px;
  font-weight: bold;
  text-align: center;
  letter-spacing: 1px;
}

.filter-tip {
  font-family: var(--font-text);
  font-size: 0.9rem;
  margin-bottom: 15px;
  text-transform: uppercase;
  font-weight: bold;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

/* =========================================
   КАСТОМНЫЕ РЕТРО-ЧЕКБОКСЫ
   ========================================= */
.newspaper-checkbox {
  display: flex;
  align-items: center;
  gap: 10px;
  font-family: var(--font-text);
  font-size: 0.9rem;
  cursor: pointer;
  user-select: none;
  margin-bottom: 8px;
}

.newspaper-checkbox input[type="checkbox"] {
  appearance: none;
  width: 15px;
  height: 15px;
  border: 1px solid var(--ink-color);
  background-color: transparent;
  position: relative;
  cursor: pointer;
  border-radius: 0;
  margin: 0;
}

.newspaper-checkbox input[type="checkbox"]:checked::after {
  content: 'X';
  position: absolute;
  top: 50%; left: 50%;
  transform: translate(-50%, -50%);
  font-family: var(--font-text);
  font-weight: bold;
  color: var(--accent-color);
  font-size: 12px;
}

/* Блок винтажной рекламы */
.ad-vintage-block {
  border: 2px solid var(--ink-color);
  padding: 15px;
  text-align: center;
  background-color: rgba(0,0,0,0.02);
}

.ad-title {
  font-family: var(--font-heading);
  color: var(--ink-color);
  font-weight: 900;
  font-size: 1.2rem;
  margin-bottom: 5px;
  letter-spacing: 1px;
}

.ad-text {
  font-family: var(--font-text);
  font-size: 0.75rem;
  line-height: 1.3;
  margin: 0;
  text-align: center;
}

/* МОДАЛЬНОЕ ОКНО — ДЕТЕКТИВНЫЙ БЛАНК */
.newspaper-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background-color: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(2px);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  padding: 20px;
}

.newspaper-modal {
  background-color: var(--paper-color);
  color: var(--ink-color);
  border: 3px solid var(--ink-color);
  box-shadow: 10px 10px 0px rgba(0, 0, 0, 0.15);
  padding: 35px 30px;
  width: 100%;
  max-width: 500px;
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
  font-size: 1.5rem;
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

/* Поля формы под печатную машинку */
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

.form-row-vintage {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.checkbox-group-vintage {
  margin: 15px 0;
}

.encryption-field {
  background-color: rgba(107, 33, 33, 0.03);
  padding: 12px;
  border: 1px dashed var(--accent-color);
}

.code-font {
  font-family: 'Courier Prime', monospace;
  letter-spacing: 2px;
}

/* Кнопки модального бланка */
.modal-buttons-vintage {
  display: flex;
  justify-content: flex-end;
  gap: 15px;
  margin-top: 30px;
  border-top: 1px solid var(--ink-color);
  padding-top: 20px;
}

.btn-vintage-secondary {
  background: transparent;
  border: 1px solid var(--ink-color);
  color: var(--ink-color);
  font-family: var(--font-text);
  padding: 8px 16px;
  font-size: 0.9rem;
  cursor: pointer;
  text-transform: uppercase;
  transition: all 0.2s ease;
}
.btn-vintage-secondary:hover {
  background-color: var(--ink-color);
  color: var(--paper-color);
}

.btn-vintage-primary {
  background: var(--ink-color);
  color: var(--paper-color);
  border: 1px solid var(--ink-color);
  font-family: var(--font-heading);
  font-weight: bold;
  padding: 8px 20px;
  font-size: 0.95rem;
  cursor: pointer;
  text-transform: uppercase;
  transition: all 0.2s ease;
}
.btn-vintage-primary:hover:not(:disabled) {
  background-color: var(--accent-color);
  border-color: var(--accent-color);
}
.btn-vintage-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Адаптивные контроллеры для мобильных экранов */
@media (max-width: 900px) {
  .newspaper-grid {
    grid-template-columns: 1fr;
  }
  .newspaper-sidebar {
    border-left: none;
    border-top: 2px solid var(--ink-color);
    padding-left: 0;
    padding-top: 25px;
  }
}

@media (max-width: 550px) {
  .archive-title { font-size: 1.3rem; }
  .form-row-vintage { grid-template-columns: 1fr; gap: 0; }
  .dossier-meta { flex-direction: column; align-items: flex-start; }
  .status-stamp { transform: none; margin-top: 5px; }
  .newspaper-modal { padding: 25px 15px; }
}
</style>