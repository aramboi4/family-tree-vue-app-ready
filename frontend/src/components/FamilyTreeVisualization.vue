<template>
  <div class="family-tree-container relative bg-gray-50 border-2 border-gray-200 rounded-lg p-8" style="min-height: 600px; overflow: auto;">
    <svg class="absolute top-0 left-0 w-full h-full pointer-events-none" style="z-index: 1;">
      <!-- Spouse lines (horizontal) -->
      <line
        v-for="(line, idx) in spouseLines"
        :key="'spouse-' + idx"
        :x1="line.x1"
        :y1="line.y1"
        :x2="line.x2"
        :y2="line.y2"
        stroke="#3b82f6"
        stroke-width="2"
      />
      
      <!-- Parent-child lines (vertical with connector) -->
      <g v-for="(line, idx) in parentChildLines" :key="'parent-' + idx">
        <!-- Vertical line from parent connector to child -->
        <line
          :x1="line.parentMidX"
          :y1="line.parentY"
          :x2="line.parentMidX"
          :y2="line.connectorY"
          stroke="#10b981"
          stroke-width="2"
        />
        <line
          :x1="line.parentMidX"
          :y1="line.connectorY"
          :x2="line.childX"
          :y2="line.connectorY"
          stroke="#10b981"
          stroke-width="2"
        />
        <line
          :x1="line.childX"
          :y1="line.connectorY"
          :x2="line.childX"
          :y2="line.childY"
          stroke="#10b981"
          stroke-width="2"
        />
      </g>
    </svg>

    <!-- Person nodes -->
    <div
      v-for="person in persons"
      :key="person._id"
      :style="{
        position: 'absolute',
        left: person.x + 'px',
        top: person.y + 'px',
        zIndex: 2
      }"
      class="person-node bg-white border-2 rounded-lg shadow-lg p-4 cursor-move"
      style="width: 200px;"
      @mousedown="startDrag(person, $event)"
    >
      <div class="flex items-center space-x-3">
        <div class="w-12 h-12 rounded-full bg-gray-200 flex items-center justify-center text-xl">
          {{ person.gender === 'male' ? '👨' : person.gender === 'female' ? '👩' : '🧑' }}
        </div>
        <div class="flex-1 min-w-0">
          <h3 class="font-semibold text-sm text-gray-900 truncate">
            {{ person.first_name }} {{ person.last_name }}
          </h3>
          <p v-if="person.birth_date" class="text-xs text-gray-500">
            {{ calculateAge(person.birth_date) }} years
          </p>
        </div>
      </div>
      <div v-if="!isViewer" class="mt-2 text-xs text-gray-600">
        <p v-if="person.nickname">"{{ person.nickname }}"</p>
        <p v-if="person.birth_place" class="truncate">📍 {{ person.birth_place }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'

const props = defineProps({
  persons: {
    type: Array,
    required: true
  },
  userRole: {
    type: String,
    default: 'viewer'
  }
})

const emit = defineEmits(['update:persons'])

const isViewer = computed(() => props.userRole === 'viewer')

const draggingPerson = ref(null)
const dragOffset = ref({ x: 0, y: 0 })

// Initialize positions if not set
onMounted(() => {
  if (props.persons.length > 0 && !props.persons[0].x) {
    layoutPersons()
  }
})

watch(() => props.persons, (newPersons) => {
  if (newPersons.length > 0 && !newPersons[0].x) {
    layoutPersons()
  }
}, { deep: true })

function layoutPersons() {
  const updatedPersons = [...props.persons]
  
  // Simple generation-based layout
  const generations = {}
  
  // Group by generation (0 = no parents, 1 = has parents, etc.)
  updatedPersons.forEach(person => {
    const gen = person.generation_level || 0
    if (!generations[gen]) generations[gen] = []
    generations[gen].push(person)
  })
  
  // Layout by generation
  let yOffset = 50
  Object.keys(generations).sort().forEach(gen => {
    const genPersons = generations[gen]
    const xSpacing = 250
    const startX = 50
    
    genPersons.forEach((person, idx) => {
      person.x = startX + (idx * xSpacing)
      person.y = yOffset
    })
    
    yOffset += 180
  })
  
  emit('update:persons', updatedPersons)
}

function startDrag(person, event) {
  draggingPerson.value = person
  dragOffset.value = {
    x: event.clientX - person.x,
    y: event.clientY - person.y
  }
  
  document.addEventListener('mousemove', onDrag)
  document.addEventListener('mouseup', stopDrag)
}

function onDrag(event) {
  if (!draggingPerson.value) return
  
  draggingPerson.value.x = event.clientX - dragOffset.value.x
  draggingPerson.value.y = event.clientY - dragOffset.value.y
}

function stopDrag() {
  draggingPerson.value = null
  document.removeEventListener('mousemove', onDrag)
  document.removeEventListener('mouseup', stopDrag)
  
  // Emit updated positions
  emit('update:persons', [...props.persons])
}

const spouseLines = computed(() => {
  const lines = []
  const processed = new Set()
  
  props.persons.forEach(person => {
    if (!person.spouse_ids || person.spouse_ids.length === 0) return
    
    person.spouse_ids.forEach(spouseId => {
      const pairKey = [person._id, spouseId].sort().join('-')
      if (processed.has(pairKey)) return
      processed.add(pairKey)
      
      const spouse = props.persons.find(p => p._id === spouseId)
      if (spouse && person.x !== undefined && spouse.x !== undefined) {
        lines.push({
          x1: person.x + 100,
          y1: person.y + 40,
          x2: spouse.x + 100,
          y2: spouse.y + 40
        })
      }
    })
  })
  
  return lines
})

const parentChildLines = computed(() => {
  const lines = []
  
  props.persons.forEach(child => {
    const father = props.persons.find(p => p._id === child.father_id)
    const mother = props.persons.find(p => p._id === child.mother_id)
    
    if (father && mother && father.x !== undefined && mother.x !== undefined && child.x !== undefined) {
      // Calculate midpoint between parents
      const parentMidX = (father.x + mother.x) / 2 + 100
      const parentY = Math.max(father.y, mother.y) + 80
      const childY = child.y
      const connectorY = (parentY + childY) / 2
      
      lines.push({
        parentMidX,
        parentY,
        childX: child.x + 100,
        childY,
        connectorY
      })
    } else if (father && father.x !== undefined && child.x !== undefined) {
      // Only father
      lines.push({
        parentMidX: father.x + 100,
        parentY: father.y + 80,
        childX: child.x + 100,
        childY: child.y,
        connectorY: (father.y + 80 + child.y) / 2
      })
    } else if (mother && mother.x !== undefined && child.x !== undefined) {
      // Only mother
      lines.push({
        parentMidX: mother.x + 100,
        parentY: mother.y + 80,
        childX: child.x + 100,
        childY: child.y,
        connectorY: (mother.y + 80 + child.y) / 2
      })
    }
  })
  
  return lines
})

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
</script>

<style scoped>
.person-node {
  transition: box-shadow 0.2s;
}

.person-node:hover {
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
}

.family-tree-container {
  position: relative;
  user-select: none;
}
</style>