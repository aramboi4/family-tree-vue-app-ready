<template>
  <div class="min-h-screen bg-gray-50 py-8">
    <div class="max-w-full mx-auto px-4 sm:px-6 lg:px-8">
      <!-- Header -->
      <div class="mb-8">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-3xl font-bold text-gray-900">Family Members</h1>
            <p class="mt-2 text-gray-600">{{ familyName }}</p>
          </div>
          <div class="flex items-center gap-4">
            <!-- View Toggle -->
            <div class="bg-white rounded-lg shadow p-1 flex">
              <button
                @click="viewMode = 'grid'"
                :class="[
                  'px-4 py-2 rounded text-sm font-medium transition-colors',
                  viewMode === 'grid' ? 'bg-blue-600 text-white' : 'text-gray-600 hover:text-gray-900'
                ]"
              >
                📋 Grid
              </button>
              <button
                @click="viewMode = 'tree'"
                :class="[
                  'px-4 py-2 rounded text-sm font-medium transition-colors',
                  viewMode === 'tree' ? 'bg-blue-600 text-white' : 'text-gray-600 hover:text-gray-900'
                ]"
              >
                🌳 Tree
              </button>
            </div>
            <button
              v-if="canEdit"
              @click="showAddModal = true"
              class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md font-medium"
            >
              + Add Person
            </button>
          </div>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="text-center py-12">
        <p class="text-gray-500">Loading family members...</p>
      </div>

      <!-- Tree View -->
      <div v-else-if="viewMode === 'tree'" class="bg-white rounded-lg shadow-lg p-4">
        <FamilyTreeVisualization
          :persons="personsWithPositions"
          :user-role="userRole"
          @update:persons="updatePersonPositions"
        />
      </div>

      <!-- Grid View -->
      <div v-else-if="persons.length > 0" class="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        <div
          v-for="person in persons"
          :key="person._id"
          class="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow"
        >
          <div class="flex items-start justify-between">
            <div class="flex-1">
              <h3 class="text-lg font-semibold text-gray-900">
                {{ person.first_name }} {{ person.last_name }}
              </h3>
              <p v-if="person.nickname" class="text-sm text-gray-500">"{{ person.nickname }}"</p>
            </div>
            <span
              v-if="person.is_deceased"
              class="px-2 py-1 text-xs font-medium bg-gray-100 text-gray-600 rounded"
            >
              Deceased
            </span>
          </div>

          <div class="mt-4 space-y-2 text-sm">
            <div v-if="person.gender" class="flex items-center text-gray-600">
              <span class="w-20 font-medium">Gender:</span>
              <span>{{ person.gender }}</span>
            </div>
            <div v-if="person.birth_date" class="flex items-center text-gray-600">
              <span class="w-20 font-medium">Born:</span>
              <span>{{ person.birth_date }} ({{ calculateAge(person.birth_date) }} yrs)</span>
            </div>
            <div v-if="!isViewer && person.birth_place" class="flex items-center text-gray-600">
              <span class="w-20 font-medium">Place:</span>
              <span>{{ person.birth_place }}</span>
            </div>
            <!-- Parent information (always visible) -->
            <div v-if="getParentNames(person).length > 0" class="mt-3 pt-3 border-t">
              <span class="font-medium text-gray-700">Parents:</span>
              <div v-for="parent in getParentNames(person)" :key="parent" class="text-sm text-gray-600 ml-2">
                • {{ parent }}
              </div>
            </div>
            <div v-if="!isViewer && person.bio" class="mt-3 text-gray-600">
              <p class="line-clamp-2">{{ person.bio }}</p>
            </div>
          </div>

          <div v-if="canEdit" class="mt-4 flex gap-2">
            <button
              @click="editPerson(person)"
              class="flex-1 bg-gray-100 hover:bg-gray-200 text-gray-700 px-3 py-2 rounded text-sm font-medium"
            >
              Edit
            </button>
            <button
              @click="confirmDelete(person)"
              class="flex-1 bg-red-50 hover:bg-red-100 text-red-600 px-3 py-2 rounded text-sm font-medium"
            >
              Delete
            </button>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-else class="text-center py-12 bg-white rounded-lg shadow">
        <p class="text-gray-500 mb-4">No family members added yet</p>
        <button
          v-if="canEdit"
          @click="showAddModal = true"
          class="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-md font-medium"
        >
          Add First Person
        </button>
      </div>
    </div>

    <!-- Add/Edit Person Modal -->
    <div
      v-if="showAddModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"
      @click.self="closeModal"
    >
      <div class="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto p-6">
        <div class="flex items-center justify-between mb-6">
          <h2 class="text-2xl font-bold text-gray-900">
            {{ editingPerson ? 'Edit Person' : 'Add New Person' }}
          </h2>
          <button @click="closeModal" class="text-gray-400 hover:text-gray-600">
            <span class="text-2xl">&times;</span>
          </button>
        </div>

        <form @submit.prevent="savePerson" class="space-y-4">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">First Name *</label>
              <input
                v-model="personForm.first_name"
                type="text"
                required
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Last Name *</label>
              <input
                v-model="personForm.last_name"
                type="text"
                required
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Middle Name</label>
              <input
                v-model="personForm.middle_name"
                type="text"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Nickname</label>
              <input
                v-model="personForm.nickname"
                type="text"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>

          <!-- Parent Selection -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4 p-4 bg-blue-50 rounded-lg">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Father</label>
              <select
                v-model="personForm.father_id"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Select Father...</option>
                <option
                  v-for="person in malePersons"
                  :key="person._id"
                  :value="person._id"
                >
                  {{ person.first_name }} {{ person.last_name }}
                </option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Mother</label>
              <select
                v-model="personForm.mother_id"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Select Mother...</option>
                <option
                  v-for="person in femalePersons"
                  :key="person._id"
                  :value="person._id"
                >
                  {{ person.first_name }} {{ person.last_name }}
                </option>
              </select>
            </div>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Gender</label>
              <select
                v-model="personForm.gender"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Select...</option>
                <option value="male">Male</option>
                <option value="female">Female</option>
                <option value="other">Other</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Birth Date</label>
              <input
                v-model="personForm.birth_date"
                type="date"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Birth Place</label>
            <input
              v-model="personForm.birth_place"
              type="text"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label class="flex items-center">
              <input
                v-model="personForm.is_deceased"
                type="checkbox"
                class="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
              />
              <span class="ml-2 text-sm text-gray-700">Deceased</span>
            </label>
          </div>

          <div v-if="personForm.is_deceased">
            <label class="block text-sm font-medium text-gray-700 mb-1">Death Date</label>
            <input
              v-model="personForm.death_date"
              type="date"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Biography</label>
            <textarea
              v-model="personForm.bio"
              rows="4"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            ></textarea>
          </div>

          <div v-if="formError" class="text-red-600 text-sm">
            {{ formError }}
          </div>

          <div class="flex gap-3 pt-4">
            <button
              type="submit"
              :disabled="submitting"
              class="flex-1 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md font-medium disabled:bg-gray-400"
            >
              {{ submitting ? 'Saving...' : (editingPerson ? 'Update Person' : 'Add Person') }}
            </button>
            <button
              type="button"
              @click="closeModal"
              class="px-4 py-2 border border-gray-300 text-gray-700 rounded-md font-medium hover:bg-gray-50"
            >
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import api from '@/services/api'
import FamilyTreeVisualization from '@/components/FamilyTreeVisualization.vue'

const route = useRoute()
const familyId = route.params.id
const familyName = ref('')
const persons = ref([])
const loading = ref(true)
const userRole = ref('')
const viewMode = ref('grid')
const showAddModal = ref(false)
const editingPerson = ref(null)
const submitting = ref(false)
const formError = ref('')

const personForm = ref({
  first_name: '',
  middle_name: '',
  last_name: '',
  nickname: '',
  gender: '',
  birth_date: '',
  death_date: '',
  birth_place: '',
  bio: '',
  is_deceased: false,
  father_id: '',
  mother_id: ''
})

const canEdit = computed(() => userRole.value === 'admin' || userRole.value === 'editor')
const isViewer = computed(() => userRole.value === 'viewer')

const malePersons = computed(() => persons.value.filter(p => p.gender === 'male'))
const femalePersons = computed(() => persons.value.filter(p => p.gender === 'female'))

const personsWithPositions = computed(() => {
  return persons.value.map(p => ({
    ...p,
    x: p.x || 0,
    y: p.y || 0
  }))
})

onMounted(async () => {
  await loadFamilyDetails()
  await loadPersons()
  await loadUserRole()
})

async function loadFamilyDetails() {
  try {
    const response = await api.get(`/api/families/${familyId}`)
    familyName.value = response.data.name
  } catch (error) {
    console.error('Failed to load family:', error)
  }
}

async function loadPersons() {
  try {
    const response = await api.get(`/api/families/${familyId}/persons`)
    persons.value = response.data
  } catch (error) {
    console.error('Failed to load persons:', error)
  } finally {
    loading.value = false
  }
}

async function loadUserRole() {
  try {
    const response = await api.get(`/api/families/${familyId}/my-role`)
    userRole.value = response.data.role
  } catch (error) {
    console.error('Failed to load role:', error)
  }
}

function getParentNames(person) {
  const names = []
  if (person.father_id) {
    const father = persons.value.find(p => p._id === person.father_id)
    if (father) names.push(`Father: ${father.first_name} ${father.last_name}`)
  }
  if (person.mother_id) {
    const mother = persons.value.find(p => p._id === person.mother_id)
    if (mother) names.push(`Mother: ${mother.first_name} ${mother.last_name}`)
  }
  return names
}

function calculateAge(birthDate) {
  if (!birthDate) return 0
  const today = new Date()
  const birth = new Date(birthDate)
  let age = today.getFullYear() - birth.getFullYear()
  const monthDiff = today.getMonth() - birth.getMonth()
  if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birth.getDate())) {
    age--
  }
  return age
}

function editPerson(person) {
  editingPerson.value = person
  personForm.value = {
    first_name: person.first_name || '',
    middle_name: person.middle_name || '',
    last_name: person.last_name || '',
    nickname: person.nickname || '',
    gender: person.gender || '',
    birth_date: person.birth_date || '',
    death_date: person.death_date || '',
    birth_place: person.birth_place || '',
    bio: person.bio || '',
    is_deceased: person.is_deceased || false,
    father_id: person.father_id || '',
    mother_id: person.mother_id || ''
  }
  showAddModal.value = true
}

async function savePerson() {
  submitting.value = true
  formError.value = ''

  try {
    if (editingPerson.value) {
      await api.put(`/api/persons/${editingPerson.value._id}`, personForm.value)
    } else {
      await api.post('/api/persons', {
        ...personForm.value,
        family_id: familyId
      })
    }

    await loadPersons()
    closeModal()
  } catch (error) {
    formError.value = error.response?.data?.detail || 'Failed to save person'
  } finally {
    submitting.value = false
  }
}

async function confirmDelete(person) {
  if (confirm(`Are you sure you want to delete ${person.first_name} ${person.last_name}?`)) {
    try {
      await api.delete(`/api/persons/${person._id}`)
      await loadPersons()
    } catch (error) {
      alert('Failed to delete person')
    }
  }
}

function updatePersonPositions(updatedPersons) {
  persons.value = updatedPersons
}

function closeModal() {
  showAddModal.value = false
  editingPerson.value = null
  personForm.value = {
    first_name: '',
    middle_name: '',
    last_name: '',
    nickname: '',
    gender: '',
    birth_date: '',
    death_date: '',
    birth_place: '',
    bio: '',
    is_deceased: false,
    father_id: '',
    mother_id: ''
  }
  formError.value = ''
}
</script>
