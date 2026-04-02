<template>
  <div class="landing-cinematic">
    <LandingNavbar v-if="!authStore.isLoggedIn" />
    <LandingHero />
    <LandingFeatures />
    <LandingCTA v-if="!authStore.isLoggedIn" />
    <LandingFooter />
  </div>
</template>

<script setup>
import { useAuthStore } from '../stores/auth'
import LandingNavbar from '../components/landing/LandingNavbar.vue'
import LandingHero from '../components/landing/LandingHero.vue'
import LandingFeatures from '../components/landing/LandingFeatures.vue'
import LandingCTA from '../components/landing/LandingCTA.vue'
import LandingFooter from '../components/landing/LandingFooter.vue'

import '../assets/landing.css'

const authStore = useAuthStore()
</script>

<style scoped>
.landing-cinematic {
  overflow-x: hidden;
  background-color: var(--color-background);
  color: var(--color-text-light);
}
</style>
