import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/services/api'

export const useFamilyStore = defineStore('family', () => {
  // State
  const families = ref([])
  const currentFamily = ref(null)
  const loading = ref(false)
  const error = ref(null)

  // Actions
  async function fetchFamilies() {
    loading.value = true
    error.value = null
    
    try {
      const response = await api.get('/api/families')
      families.value = response.data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to fetch families'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function createFamily(familyData) {
    loading.value = true
    error.value = null
    
    try {
      const response = await api.post('/api/families', familyData)
      families.value.unshift(response.data)
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to create family'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchFamily(familyId) {
    loading.value = true
    error.value = null
    
    try {
      const response = await api.get(`/api/families/${familyId}`)
      currentFamily.value = response.data
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to fetch family'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function updateFamily(familyId, familyData) {
    loading.value = true
    error.value = null
    
    try {
      const response = await api.put(`/api/families/${familyId}`, familyData)
      const index = families.value.findIndex(f => f.id === familyId)
      if (index !== -1) {
        families.value[index] = response.data
      }
      if (currentFamily.value?.id === familyId) {
        currentFamily.value = response.data
      }
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to update family'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function deleteFamily(familyId) {
    loading.value = true
    error.value = null
    
    try {
      await api.delete(`/api/families/${familyId}`)
      families.value = families.value.filter(f => f.id !== familyId)
      if (currentFamily.value?.id === familyId) {
        currentFamily.value = null
      }
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to delete family'
      throw err
    } finally {
      loading.value = false
    }
  }

  return {
    families,
    currentFamily,
    loading,
    error,
    fetchFamilies,
    createFamily,
    fetchFamily,
    updateFamily,
    deleteFamily,
  }
})
