<template>
  <nav class="navbar-custom">
    <div class="container-fluid px-4">
      <router-link :to="homePath" class="navbar-brand">
        <img src="https://res.cloudinary.com/deibwaqlz/image/upload/v1773065944/Untitled_design_4_u1lm8y.png" alt="Logo" class="brand-logo" />
        <span class="brand-text">LaunchPad</span>
      </router-link>

      <button class="menu-toggle" aria-label="Toggle menu" @click="menuOpen = !menuOpen">
        <X v-if="menuOpen" :size="24" />
        <Menu v-else :size="24" />
      </button>

      <div class="nav-links" :class="{ 'is-open': menuOpen }">
        <!-- Admin links -->
        <template v-if="authStore.isAdmin">
          <router-link to="/admin" class="nav-link" exact-active-class="active" @click="menuOpen = false">
            Dashboard
          </router-link>
          <router-link to="/admin/companies" class="nav-link" active-class="active" @click="menuOpen = false">
            <Building2 :size="18" /> Companies
          </router-link>
          <router-link to="/admin/drives" class="nav-link" active-class="active" @click="menuOpen = false">
            <Megaphone :size="18" /> Drives
          </router-link>
          <router-link to="/admin/students" class="nav-link" active-class="active" @click="menuOpen = false">
            <Users :size="18" /> Students
          </router-link>
        </template>

        <!-- Company links -->
        <template v-if="authStore.isCompany">
          <router-link to="/company" class="nav-link" exact-active-class="active" @click="menuOpen = false">
            Dashboard
          </router-link>
          <router-link to="/company/drives" class="nav-link" active-class="active" @click="menuOpen = false">
            My Drives
          </router-link>
        </template>

        <!-- Student links -->
        <template v-if="authStore.isStudent">
          <router-link to="/student" class="nav-link" exact-active-class="active" @click="menuOpen = false">
            Dashboard
          </router-link>
          <router-link to="/student/drives" class="nav-link" active-class="active" @click="menuOpen = false">
            Browse Drives
          </router-link>
          <router-link to="/student/applications" class="nav-link" active-class="active" @click="menuOpen = false">
            Applications
          </router-link>
          <router-link to="/student/profile" class="nav-link" active-class="active" @click="menuOpen = false">
            Profile
          </router-link>
        </template>

        <!-- Mobile Logout -->
        <button class="btn-outline-custom btn-sm mobile-logout" @click="handleLogout">
          <LogOut :size="16" /> Logout
        </button>
      </div>

      <div class="nav-user d-none d-md-flex">
        <span class="user-email">{{ authStore.user?.email }}</span>
        <button class="btn-outline-custom btn-sm" @click="handleLogout">
          <LogOut :size="16" /> Logout
        </button>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { Building2, Megaphone, Users, LogOut, Menu, X } from 'lucide-vue-next'

const router = useRouter()
const authStore = useAuthStore()
const menuOpen = ref(false)

const homePath = computed(() => {
  if (authStore.isAdmin) return '/admin'
  if (authStore.isCompany) return '/company'
  if (authStore.isStudent) return '/student'
  return '/'
})

async function handleLogout() {
  await authStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.navbar-custom {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 72px;
  background: rgba(13, 13, 18, 0.9);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--border-color);
  display: flex;
  align-items: center;
  z-index: 1000;
}

.container-fluid {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
}

.navbar-brand {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 1.5rem;
  font-weight: 400;
  text-decoration: none;
  font-family: var(--font-heading);
  letter-spacing: -0.02em;
}

.brand-logo {
  height: 28px;
  width: auto;
}

.brand-text {
  color: var(--text-primary);
}

.nav-links {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.5rem 0.875rem;
  border-radius: var(--border-radius-sm);
  color: var(--text-secondary) !important;
  font-size: 0.875rem;
  font-weight: 500;
  transition: var(--transition);
  text-decoration: none;
}

.nav-link:hover {
  color: var(--text-primary) !important;
  background: rgba(201, 168, 76, 0.05);
}

.nav-link.active {
  color: var(--accent-primary) !important;
  background: rgba(201, 168, 76, 0.1);
}

.nav-user {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.user-email {
  font-size: 0.825rem;
  color: var(--text-secondary);
}

.mobile-logout {
  display: none;
}

.menu-toggle {
  display: none;
  background: transparent;
  border: none;
  color: var(--text-primary);
  font-size: 1.5rem;
  cursor: pointer;
}

@media (max-width: 768px) {
  .menu-toggle {
    display: block;
  }

  .nav-links {
    position: absolute;
    top: 72px;
    left: 0;
    width: 100%;
    background: rgba(13, 13, 18, 0.95);
    backdrop-filter: blur(12px);
    flex-direction: column;
    align-items: flex-start;
    padding: 1rem;
    gap: 1rem;
    display: none;
    border-bottom: 1px solid var(--border-color);
  }

  .nav-links.is-open {
    display: flex;
  }

  .nav-link {
    width: 100%;
  }

  .mobile-logout {
    display: flex;
    margin-top: 1rem;
  }
}
</style>
