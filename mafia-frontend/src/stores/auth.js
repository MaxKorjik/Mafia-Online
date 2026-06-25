import { defineStore } from 'pinia'
import axios from 'axios'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    token: localStorage.getItem('token') || null,
    isAuthenticated: !!localStorage.getItem('token')
  }),

  getters: {
    getUser: (state) => state.user,
    getToken: (state) => state.token,
    isLoggedIn: (state) => state.isAuthenticated
  },

  actions: {
    async login(username, password) {
      try {
        // Меняем только адрес, тело запроса оставляем как у тебя и было
        const response = await axios.post(`${import.meta.env.VITE_API_URL}/auth/login`, {
          username,
          password
        }, {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
          }
        })
        
        const token = response.data.access_token
        this.token = token
        localStorage.setItem('token', token)
        
        // Тут тоже просто меняем адрес на переменную
        const userResponse = await axios.get(`${import.meta.env.VITE_API_URL}/api/profile`, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        })
        
        this.user = userResponse.data
        this.isAuthenticated = true
        
        localStorage.setItem('userId', userResponse.data.id)
        localStorage.setItem('username', userResponse.data.username)
        
        return true
      } catch (error) {
        throw error
      }
    },

    async register(username, email, password) {
      try {
        const response = await api.post('/auth/register', {
          username,
          email,
          password
        })
        
        const token = response.data.access_token
        this.token = token
        localStorage.setItem('token', token)
        
        // Отримуємо дані користувача
        const userResponse = await api.get('/api/profile', {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        })
        
        this.user = userResponse.data
        this.isAuthenticated = true
        
        localStorage.setItem('userId', userResponse.data.id)
        localStorage.setItem('username', userResponse.data.username)
        
        return true
      } catch (error) {
        throw error
      }
    },

    async logout() {
      try {
        if (this.token) {
          await api.post('/auth/logout', {}, {
            headers: {
              'Authorization': `Bearer ${this.token}`
            }
          })
        }

      } catch (error) {
        console.error('Logout error:', error)
      } finally {
        this.token = null
        this.user = null
        this.isAuthenticated = false
        localStorage.removeItem('token')
        localStorage.removeItem('userId')
        localStorage.removeItem('username')
      }
    },

    async fetchUserProfile() {
      try {
        if (!this.token) return null
        
        const response = await axios.get(`${import.meta.env.VITE_API_URL}/api/profile`, {
          headers: {
            'Authorization': `Bearer ${this.token}`
          }
        })
        
        this.user = response.data
        return response.data
      } catch (error) {
        this.logout()
        throw error
      }
    }
  }
}) 