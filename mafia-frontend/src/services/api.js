import axios from 'axios'
import { showError } from './toast'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Інтерцептор для додавання токену до запитів
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Інтерцептор для обробки помилок
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      // Помилка від сервера
      const message = error.response.data.detail || 'Сталася помилка'
      showError(message)
      
      // Якщо токен недійсний, перенаправляємо на сторінку входу
      if (error.response.status === 401) {
        localStorage.removeItem('token')
        window.location.href = '/login'
      }
    } else if (error.request) {
      // Помилка мережі
      showError('Помилка мережі. Перевірте підключення до інтернету')
    } else {
      // Інші помилки
      showError('Сталася невідома помилка')
    }
    
    return Promise.reject(error)
  }
)

export default api 