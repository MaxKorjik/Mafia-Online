import { defineStore } from 'pinia'
import api from '@/services/api'

export const useRoomsStore = defineStore('rooms', {
  state: () => ({
    rooms: [],
    currentRoom: null,
    loading: false,
    error: null
  }),

  getters: {
    getRooms: (state) => state.rooms,
    getCurrentRoom: (state) => state.currentRoom,
    isLoading: (state) => state.loading,
    getError: (state) => state.error
  },

  actions: {
    async fetchRooms() {
      this.loading = true
      this.error = null
      try {
        const response = await api.get('/rooms')
        this.rooms = response.data
      } catch (error) {
        this.error = error.message
        throw error
      } finally {
        this.loading = false
      }
    },

    async createRoom(name, maxPlayers) {
      this.loading = true
      this.error = null
      try {
        const response = await api.post('/rooms', { name, max_players: maxPlayers })
        this.rooms.push(response.data)
        return response.data
      } catch (error) {
        this.error = error.message
        throw error
      } finally {
        this.loading = false
      }
    },

    async joinRoom(roomId) {
      this.loading = true
      this.error = null
      try {
        const response = await api.post(`/rooms/${roomId}/join`)
        this.currentRoom = response.data
        return response.data
      } catch (error) {
        this.error = error.message
        throw error
      } finally {
        this.loading = false
      }
    },

    async leaveRoom(roomId) {
      this.loading = true
      this.error = null
      try {
        await api.post(`/rooms/${roomId}/leave`)
        this.currentRoom = null
      } catch (error) {
        this.error = error.message
        throw error
      } finally {
        this.loading = false
      }
    },

    async startGame(roomId) {
      this.loading = true
      this.error = null
      try {
        const response = await api.post(`/rooms/${roomId}/start`)
        this.currentRoom = response.data
        return response.data
      } catch (error) {
        this.error = error.message
        throw error
      } finally {
        this.loading = false
      }
    },

    async vote(roomId, targetId) {
      this.loading = true
      this.error = null
      try {
        const response = await api.post(`/rooms/${roomId}/vote`, { target_id: targetId })
        this.currentRoom = response.data
        return response.data
      } catch (error) {
        this.error = error.message
        throw error
      } finally {
        this.loading = false
      }
    },

    async useAbility(roomId, targetId) {
      this.loading = true
      this.error = null
      try {
        const response = await api.post(`/rooms/${roomId}/ability`, { target_id: targetId })
        this.currentRoom = response.data
        return response.data
      } catch (error) {
        this.error = error.message
        throw error
      } finally {
        this.loading = false
      }
    }
  }
}) 