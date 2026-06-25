import { defineStore } from 'pinia'
import api from '@/services/api'

export const useLeaderboardStore = defineStore('leaderboard', {
  state: () => ({
    players: [],
    loading: false,
    error: null,
    currentFilter: 'total_games'
  }),

  getters: {
    getPlayers: (state) => state.players,
    isLoading: (state) => state.loading,
    getError: (state) => state.error,
    getCurrentFilter: (state) => state.currentFilter,
    
    sortedPlayers: (state) => {
      return [...state.players].sort((a, b) => {
        switch (state.currentFilter) {
          case 'total_games':
            return b.total_games - a.total_games
          case 'survivor_matches':
            return b.survivor_matches - a.survivor_matches
          case 'mafia_matches':
            return b.mafia_matches - a.mafia_matches
          default:
            return 0
        }
      })
    }
  },

  actions: {
    async fetchLeaderboard() {
      this.loading = true
      this.error = null
      try {
        const response = await api.get('/leaderboard')
        this.players = response.data
      } catch (error) {
        this.error = error.message
        throw error
      } finally {
        this.loading = false
      }
    },

    setFilter(filter) {
      this.currentFilter = filter
    }
  }
}) 