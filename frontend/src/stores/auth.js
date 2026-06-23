import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/services/api'

// Helper function to format API error details
function formatApiErrorDetail(detail) {
  if (detail == null) return "Something went wrong. Please try again.";
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail))
    return detail.map((e) => (e && typeof e.msg === "string" ? e.msg : JSON.stringify(e))).filter(Boolean).join(" ");
  if (detail && typeof detail.msg === "string") return detail.msg;
  return String(detail);
}

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref(null)
  const loading = ref(false)
  const error = ref(null)
  const isChecking = ref(true)

  // Getters
  const isAuthenticated = computed(() => user.value !== null)
  const currentUser = computed(() => user.value)

  // Actions
  async function register(userData) {
    loading.value = true
    error.value = null
    
    try {
      const response = await api.post('/api/auth/register', userData)
      user.value = response.data
      return true
    } catch (err) {
      error.value = formatApiErrorDetail(err.response?.data?.detail)
      throw err
    } finally {
      loading.value = false
    }
  }

  async function login(credentials) {
    loading.value = true
    error.value = null
    
    try {
      const response = await api.post('/api/auth/login', credentials)
      user.value = response.data
      return true
    } catch (err) {
      error.value = formatApiErrorDetail(err.response?.data?.detail)
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchUser() {
    try {
      const response = await api.get('/api/auth/me')
      user.value = response.data
      return true
    } catch (err) {
      user.value = null
      return false
    } finally {
      isChecking.value = false
    }
  }

  async function logout() {
    try {
      await api.post('/api/auth/logout')
    } catch (err) {
      console.error('Logout error:', err)
    } finally {
      user.value = null
    }
  }

  // Initialize user on app load
  async function init() {
    if (isChecking.value) {
      await fetchUser()
    }
  }

  return {
    user,
    loading,
    error,
    isChecking,
    isAuthenticated,
    currentUser,
    register,
    login,
    fetchUser,
    logout,
    init,
  }
})
