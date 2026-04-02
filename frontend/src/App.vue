<template>
  <div id="placement-app">
    <Navbar v-if="authStore.isLoggedIn" />
    <div v-if="authStore.isBlacklisted" class="blacklist-banner">
      Your account has been blacklisted by the administrator. You can view your data but cannot perform any actions.
    </div>
    <main :class="{ 'with-nav': authStore.isLoggedIn }">
      <router-view />
    </main>
    <Toast />
  </div>
</template>

<script setup>
import { useAuthStore } from './stores/auth'
import Navbar from './components/Navbar.vue'
import Toast from './components/Toast.vue'

const authStore = useAuthStore()
</script>

<style>
#placement-app {
  min-height: 100vh;
  background: var(--bg-primary);
}

main.with-nav {
  padding-top: 72px;
}

.blacklist-banner {
  position: fixed;
  top: 60px;
  left: 0;
  right: 0;
  z-index: 1050;
  background: rgba(220, 38, 38, 0.95);
  color: #fff;
  text-align: center;
  padding: 0.5rem 1rem;
  font-size: 0.85rem;
  font-weight: 600;
}
</style>
