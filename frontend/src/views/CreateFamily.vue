<template>
  <div class="min-h-screen bg-gray-50">
    <nav class="bg-white shadow">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between h-16">
          <div class="flex items-center">
            <router-link to="/dashboard" class="flex items-center">
              <span class="text-2xl">🌳</span>
              <span class="ml-2 text-xl font-bold text-gray-900">Family Tree</span>
            </router-link>
          </div>
        </div>
      </div>
    </nav>

    <main class="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div class="bg-white rounded-lg shadow-lg p-8">
        <h1 class="text-3xl font-bold text-gray-900 mb-6">Create New Family Tree</h1>

        <div v-if="error" class="mb-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
          {{ error }}
        </div>

        <form @submit.prevent="handleCreate" class="space-y-6">
          <div>
            <label for="name" class="block text-sm font-medium text-gray-700">Family Tree Name *</label>
            <input
              id="name"
              v-model="form.name"
              type="text"
              required
              class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
              placeholder="The Smith Family"
            />
          </div>

          <div>
            <label for="description" class="block text-sm font-medium text-gray-700">Description</label>
            <textarea
              id="description"
              v-model="form.description"
              rows="4"
              class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
              placeholder="A brief description of your family tree..."
            ></textarea>
          </div>

          <div class="flex space-x-4">
            <button
              type="submit"
              :disabled="loading"
              class="flex-1 py-3 px-4 bg-primary-600 text-white rounded-md hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:bg-gray-400 disabled:cursor-not-allowed"
            >
              <span v-if=loading>Creating...</span>
              <span v-else>Create Family Tree</span>
            </button>
            <router-link
              to="/families"
              class="flex-1 py-3 px-4 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300 text-center"
            >
              Cancel
            </router-link>
          </div>
        </form>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useFamilyStore } from '@/stores/family'

const router = useRouter()
const familyStore = useFamilyStore()

const form = ref({
  name: '',
  description: '',
})

const loading = ref(false)
const error = ref('')

async function handleCreate() {
  loading.value = true
  error.value = ''
  
  try {
    const family = await familyStore.createFamily(form.value)
    router.push(`/families/${family.id}`)
  } catch (err) {
    error.value = familyStore.error || 'Failed to create family tree'
  } finally {
    loading.value = false
  }
}
</script>
