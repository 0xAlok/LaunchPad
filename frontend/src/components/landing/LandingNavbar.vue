<template>
  <nav :class="['landing-navbar', { 'scrolled': isScrolled }]">
    <div class="nav-container">
      <div class="nav-brand">
        <img src="https://res.cloudinary.com/deibwaqlz/image/upload/v1773065944/Untitled_design_4_u1lm8y.png" alt="LaunchPad Logo" class="brand-logo" />
        <span>LaunchPad</span>
      </div>
      
      <div class="nav-actions">
        <router-link to="/login" class="nav-link btn-login d-none d-md-block">Login</router-link>
        <router-link to="/register" class="btn-cta">Get Started</router-link>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const isScrolled = ref(false)

const handleScroll = () => {
  isScrolled.value = window.scrollY > 100
}

onMounted(() => {
  window.addEventListener('scroll', handleScroll)
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
})
</script>

<style scoped>
.landing-navbar {
  position: fixed;
  top: 1.5rem;
  left: 50%;
  transform: translateX(-50%);
  width: 90%;
  max-width: 1200px;
  z-index: 1000;
  border-radius: 3rem;
  transition: all 0.4s ease-in-out;
  background: transparent;
}

.landing-navbar.scrolled {
  background: rgba(13, 13, 18, 0.85);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(201, 168, 76, 0.15);
  box-shadow: 0 4px 30px rgba(0, 0, 0, 0.5);
}

.nav-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 1.5rem;
}

.nav-brand {
  font-family: var(--font-heading, 'Inter');
  font-weight: 700;
  font-size: 1.25rem;
  color: var(--color-text-light, #FAF8F5);
  letter-spacing: -0.5px;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.brand-logo {
  height: 28px;
  width: auto;
}

.nav-links {
  display: flex;
  gap: 2.5rem;
}

.nav-link {
  font-family: var(--font-heading, 'Inter');
  font-weight: 500;
  font-size: 0.875rem;
  color: #B4B4BC;
  text-decoration: none;
  transition: transform 0.2s ease-out, color 0.2s;
}

.nav-link:hover {
  color: var(--color-accent, #C9A84C);
  transform: translateY(-1px);
}

.nav-actions {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.btn-login {
  color: var(--color-text-light, #FAF8F5);
}

.btn-cta {
  background: var(--color-accent, #C9A84C);
  color: #0D0D12;
  font-family: var(--font-heading, 'Inter');
  font-weight: 600;
  font-size: 0.875rem;
  padding: 0.6rem 1.25rem;
  border-radius: 2rem;
  text-decoration: none;
  transition: transform 0.2s ease-out, box-shadow 0.2s;
}

.btn-cta:hover {
  transform: scale(1.03);
  box-shadow: 0 0 15px rgba(201, 168, 76, 0.4);
}
</style>
