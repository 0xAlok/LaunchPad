import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../api'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const profile = ref(null)
  const token = ref(null)
  const loading = ref(false)
  const error = ref(null)

  const isLoggedIn = computed(() => !!token.value)
  const userRole = computed(() => {
    if (!user.value || !user.value.roles) return null
    return user.value.roles[0] || null
  })
  const isAdmin = computed(() => userRole.value === 'admin')
  const isCompany = computed(() => userRole.value === 'company')
  const isStudent = computed(() => userRole.value === 'student')
  const isBlacklisted = computed(() => profile.value?.is_blacklisted === true)

  function loadFromStorage() {
    const storedToken = localStorage.getItem('auth_token')
    const storedUser = localStorage.getItem('user')
    const storedProfile = localStorage.getItem('profile')

    if (storedToken) {
      token.value = storedToken
      user.value = storedUser ? JSON.parse(storedUser) : null
      profile.value = storedProfile ? JSON.parse(storedProfile) : null
    }
  }

  async function login(email, password) {
    loading.value = true
    error.value = null
    try {
      const res = await api.post('/auth/login', { email, password })
      token.value = res.data.token
      user.value = res.data.user
      profile.value = res.data.profile

      localStorage.setItem('auth_token', res.data.token)
      localStorage.setItem('user', JSON.stringify(res.data.user))
      localStorage.setItem('profile', JSON.stringify(res.data.profile))

      return res.data
    } catch (err) {
      error.value = err.response?.data?.error || 'Login failed'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function register(formData) {
    loading.value = true
    error.value = null
    try {
      const res = await api.post('/auth/register', formData)
      return res.data
    } catch (err) {
      error.value = err.response?.data?.error || 'Registration failed'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function logout() {
    try {
      await api.post('/auth/logout')
    } catch {}
    token.value = null
    user.value = null
    profile.value = null
    localStorage.removeItem('auth_token')
    localStorage.removeItem('user')
    localStorage.removeItem('profile')
  }

  async function fetchProfile() {
    try {
      const res = await api.get('/auth/me')
      user.value = res.data.user
      profile.value = res.data.profile
      localStorage.setItem('user', JSON.stringify(res.data.user))
      localStorage.setItem('profile', JSON.stringify(res.data.profile))
    } catch {}
  }

  loadFromStorage()

  return {
    user,
    profile,
    token,
    loading,
    error,
    isLoggedIn,
    userRole,
    isAdmin,
    isCompany,
    isStudent,
    isBlacklisted,
    loadFromStorage,
    login,
    register,
    logout,
    fetchProfile,
  }
})
