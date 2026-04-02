<template>
  <div class="auth-page landing-cinematic">
    <div class="auth-wrapper">
      <div class="auth-image-col">
        <img 
          src="https://res.cloudinary.com/deibwaqlz/image/upload/v1773068097/login_sf32wa.png" 
          alt="Login Visual" 
          class="auth-hero-img"
        />
        <div class="image-overlay"></div>
        <div class="brand-overlay">
          <router-link to="/" class="brand-link">
            <img src="https://res.cloudinary.com/deibwaqlz/image/upload/v1773065944/Untitled_design_4_u1lm8y.png" alt="Logo" class="mini-logo" />
            <span>LaunchPad</span>
          </router-link>
        </div>
      </div>

      <!-- Form Column -->
      <div class="auth-form-col">
        <div class="auth-form-content">
          <div class="auth-form-container">
            <div class="auth-header">
              <h1 class="auth-title">Welcome Back</h1>
            </div>

            <form @submit.prevent="handleLogin" class="auth-form">
              <div class="form-group mb-4">
                <label class="form-label">Email Address</label>
                <input
                  id="login-email"
                  v-model="email"
                  type="email"
                  class="form-input"
                  placeholder="you@university.edu"
                  required
                />
              </div>

              <div class="form-group mb-4">
                <div class="d-flex justify-content-between align-items-center mb-2">
                  <label class="form-label mb-0">Password</label>
                </div>
                <input
                  id="login-password"
                  v-model="password"
                  type="password"
                  class="form-input"
                  placeholder="••••••••"
                  required
                />
              </div>

              <div v-if="authStore.error" class="error-msg">
                <AlertTriangle :size="18" />
                {{ authStore.error }}
              </div>

              <button
                type="submit"
                class="btn-auth-primary w-100"
                :disabled="authStore.loading"
              >
                <span v-if="authStore.loading" class="spinner-border spinner-border-sm"></span>
                <span v-else>Sign In</span>
              </button>
            </form>

            <div class="auth-footer">
              <span class="text-muted">New to the platform?</span>
              <router-link to="/register" class="auth-link">Create Account</router-link>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { AlertTriangle } from 'lucide-vue-next'

const router = useRouter()
const authStore = useAuthStore()

const email = ref('')
const password = ref('')

async function handleLogin() {
  try {
    await authStore.login(email.value, password.value)
    const role = authStore.userRole
    if (role === 'admin') router.push('/admin')
    else if (role === 'company') router.push('/company')
    else if (role === 'student') router.push('/student')
  } catch {}
}
</script>

<style scoped>
@import '../assets/auth.css';
</style>
