import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      redirect: '/dashboard',
    },
    {
      path: '/login',
      name: 'Login',
      component: () => import('@/views/Login.vue'),
      meta: { guest: true },
    },
    {
      path: '/register',
      name: 'Register',
      component: () => import('@/views/Register.vue'),
      meta: { guest: true },
    },
    {
      path: '/dashboard',
      name: 'Dashboard',
      component: () => import('@/views/Dashboard.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/families',
      name: 'FamilyList',
      component: () => import('@/views/FamilyList.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/families/create',
      name: 'CreateFamily',
      component: () => import('@/views/CreateFamily.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/families/:id',
      name: 'FamilyDetails',
      component: () => import('@/views/FamilyDetails.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/families/:id/persons',
      name: 'PersonManagement',
      component: () => import('@/views/PersonManagement.vue'),
      meta: { requiresAuth: true },
    },
  ],
})

// Navigation guard
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  
  // Wait for auth check to complete
  if (authStore.isChecking) {
    await authStore.init()
  }

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next('/login')
  } else if (to.meta.guest && authStore.isAuthenticated) {
    next('/dashboard')
  } else {
    next()
  }
})

export default router
