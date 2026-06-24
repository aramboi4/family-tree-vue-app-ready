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
          <div class="flex items-center space-x-4">
            <router-link to="/families" class="text-sm text-gray-600 hover:text-gray-900">My Families</router-link>
          </div>
        </div>
      </div>
    </nav>

    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div v-if="loading" class="text-center py-12">
        <p class="text-gray-500">Loading family details...</p>
      </div>

      <div v-else-if="family" class="space-y-6">
        <!-- Header -->
        <div class="bg-white rounded-lg shadow-lg p-6">
          <div class="flex justify-between items-start">
            <div>
              <h1 class="text-3xl font-bold text-gray-900">{{ family.name }}</h1>
              <p class="text-gray-600 mt-2">{{ family.description || 'No description' }}</p>
              <div class="mt-4 flex items-center space-x-4">
                <span class="px-3 py-1 text-sm font-semibold rounded-full bg-green-100 text-green-800 capitalize">
                  {{ family.subscription_plan }} Plan
                </span>
                <span class="text-sm text-gray-600">
                  {{ family.person_count }} / {{ family.person_limit }} members
                </span>
                <span class="text-sm text-gray-500">
                  Join Code: <span class="font-mono font-bold">{{ family.join_code }}</span>
                </span>
              </div>
            </div>
            <div class="flex space-x-2">
              <router-link
                :to=\"`/families/${family._id}/persons`\"
                class=\"px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700\"
              >
                Manage Family Members
              </router-link>
            </div>
          </div>
        </div>

        <!-- Family Members Link -->
        <div class="bg-white rounded-lg shadow-lg p-6">
          <h2 class="text-xl font-bold text-gray-900 mb-4">Family Members</h2>
          <div class="text-center py-12">
            <p class="text-gray-600 mb-4">View and manage family tree members</p>
            <router-link
              :to=\"`/families/${family._id}/persons`\"
              class=\"inline-block px-6 py-3 bg-blue-600 text-white rounded-md hover:bg-blue-700 font-medium\"
            >
              View Family Members
            </router-link>
          </div>
        </div>
      </div>

      <div v-else class="text-center py-12">
        <p class="text-red-500">Failed to load family details</p>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useFamilyStore } from '@/stores/family'

const route = useRoute()
const familyStore = useFamilyStore()

const family = ref(null)
const loading = ref(true)

onMounted(async () => {
  try {
    family.value = await familyStore.fetchFamily(route.params.id)
  } catch (err) {
    console.error('Failed to fetch family:', err)
  } finally {
    loading.value = false
  }
})
</script>
