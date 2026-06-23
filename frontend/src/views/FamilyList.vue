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
            <router-link to="/dashboard" class="text-sm text-gray-600 hover:text-gray-900">Dashboard</router-link>
            <button @click="handleLogout" class="text-sm text-gray-600 hover:text-gray-900">Logout</button>
          </div>
        </div>
      </div>
    </nav>

    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div class="flex justify-between items-center mb-6">
        <h1 class="text-3xl font-bold text-gray-900">My Family Trees</h1>
        <router-link
          to="/families/create"
          class="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700"
        >
          + Create New Family Tree
        </router-link>
      </div>

      <div v-if="loading" class="text-center py-12">
        <p class="text-gray-500">Loading families...</p>
      </div>

      <div v-else-if="families.length === 0" class="text-center py-12 bg-white rounded-lg shadow">
        <p class="text-gray-500 mb-4">You don't have any family trees yet.</p>
        <router-link
          to="/families/create"
          class="inline-block px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700"
        >
          Create Your First Family Tree
        </router-link>
      </div>

      <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div
          v-for="family in families"
          :key="family.id"
          class="bg-white rounded-lg shadow-md hover:shadow-lg transition cursor-pointer"
          @click="$router.push(`/families/${family.id}`)"
        >
          <div class="p-6">
            <h3 class="text-xl font-bold text-gray-900 mb-2">{{ family.name }}</h3>
            <p class="text-gray-600 text-sm mb-4">{{ family.description || 'No description' }}</p>
            
            <div class="flex items-center justify-between text-sm">
              <span class="text-gray-600">
                👥 {{ family.person_count }} / {{ family.person_limit }} members
              </span>
              <span class="px-2 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800 capitalize">
                {{ family.subscription_plan }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useFamilyStore } from '@/stores/family'

const router = useRouter()
const authStore = useAuthStore()
const familyStore = useFamilyStore()

const families = computed(() => familyStore.families)
const loading = computed(() => familyStore.loading)

onMounted(async () => {
  await familyStore.fetchFamilies()
})

function handleLogout() {
  authStore.logout()
  router.push('/login')
}
</script>
