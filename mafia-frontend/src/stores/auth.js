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
        
        // Сразу подтягиваем профиль
        await this.fetchUserProfile()
        
        return true
      } catch (error) {
        throw error
      }
    },

    async register(username, email, password) {
      try {
        const response = await axios.post(`${import.meta.env.VITE_API_URL}/auth/register`, {
          username,
          email,
          password
        }, {
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
        })
        
        const token = response.data.access_token
        this.token = token
        localStorage.setItem('token', token)
        
        await this.fetchUserProfile()
        
        return true
      } catch (error) {
        throw error
      }
    },

    async logout() {
      try {
        if (this.token) {
          await axios.post(`${import.meta.env.VITE_API_URL}/auth/logout`, {}, {
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
        
        // Обновляем данные юзера и статус авторизации
        this.user = response.data
        this.isAuthenticated = true
        
        localStorage.setItem('userId', response.data.id)
        localStorage.setItem('username', response.data.username)
        
        return response.data
      } catch (error) {
        // Если токен протух или недействителен — разлогиниваем
        this.logout()
        throw error
      }
    }
  }
})