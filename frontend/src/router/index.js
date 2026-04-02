import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

// Auth & Public views
import Landing from '../views/Landing.vue'
import Login from '../views/Login.vue'
import Register from '../views/Register.vue'

// Admin views
import AdminDashboard from '../views/admin/Dashboard.vue'
import AdminCompanies from '../views/admin/Companies.vue'
import AdminDrives from '../views/admin/Drives.vue'
import AdminStudents from '../views/admin/Students.vue'

// Company views
import CompanyDashboard from '../views/company/Dashboard.vue'
import CompanyDrives from '../views/company/Drives.vue'
import CompanyDriveCreate from '../views/company/DriveCreate.vue'
import CompanyApplications from '../views/company/Applications.vue'

// Student views
import StudentDashboard from '../views/student/Dashboard.vue'
import StudentProfile from '../views/student/Profile.vue'
import StudentDrives from '../views/student/Drives.vue'
import StudentApplications from '../views/student/Applications.vue'

const routes = [
  {
    path: '/',
    name: 'Landing',
    component: Landing,
    meta: { public: true },
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { guest: true },
  },
  {
    path: '/register',
    name: 'Register',
    component: Register,
    meta: { guest: true },
  },

  // Admin routes
  {
    path: '/admin',
    name: 'AdminDashboard',
    component: AdminDashboard,
    meta: { requiresAuth: true, role: 'admin' },
  },
  {
    path: '/admin/companies',
    name: 'AdminCompanies',
    component: AdminCompanies,
    meta: { requiresAuth: true, role: 'admin' },
  },
  {
    path: '/admin/drives',
    name: 'AdminDrives',
    component: AdminDrives,
    meta: { requiresAuth: true, role: 'admin' },
  },
  {
    path: '/admin/students',
    name: 'AdminStudents',
    component: AdminStudents,
    meta: { requiresAuth: true, role: 'admin' },
  },

  // Company routes
  {
    path: '/company',
    name: 'CompanyDashboard',
    component: CompanyDashboard,
    meta: { requiresAuth: true, role: 'company' },
  },
  {
    path: '/company/drives',
    name: 'CompanyDrives',
    component: CompanyDrives,
    meta: { requiresAuth: true, role: 'company' },
  },
  {
    path: '/company/drives/new',
    name: 'CompanyDriveCreate',
    component: CompanyDriveCreate,
    meta: { requiresAuth: true, role: 'company' },
  },
  {
    path: '/company/drives/:driveId/applications',
    name: 'CompanyApplications',
    component: CompanyApplications,
    meta: { requiresAuth: true, role: 'company' },
  },

  // Student routes
  {
    path: '/student',
    name: 'StudentDashboard',
    component: StudentDashboard,
    meta: { requiresAuth: true, role: 'student' },
  },
  {
    path: '/student/profile',
    name: 'StudentProfile',
    component: StudentProfile,
    meta: { requiresAuth: true, role: 'student' },
  },
  {
    path: '/student/drives',
    name: 'StudentDrives',
    component: StudentDrives,
    meta: { requiresAuth: true, role: 'student' },
  },
  {
    path: '/student/applications',
    name: 'StudentApplications',
    component: StudentApplications,
    meta: { requiresAuth: true, role: 'student' },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// Navigation guards
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()

  if (to.meta.requiresAuth && !authStore.isLoggedIn) {
    return next('/login')
  }

  if (to.meta.guest && authStore.isLoggedIn) {
    // Redirect logged-in users to their dashboard if they hit guest-only routes
    const role = authStore.userRole
    if (role === 'admin') return next('/admin')
    if (role === 'company') return next('/company')
    if (role === 'student') return next('/student')
    return next('/')
  }

  if (to.meta.role && authStore.userRole !== to.meta.role) {
    return next('/')
  }

  next()
})

export default router
