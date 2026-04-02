<template>
  <section class="cta-section" ref="ctaRef">
    <div class="container text-center cta-content" :class="{ 'is-visible': isVisible }">
      <h2 class="cta-title">Get started with LaunchPad!</h2>
      
      <div class="cta-actions">
        <router-link to="/register?role=student" class="btn-primary-custom btn-lg cta-btn">
          I'm a Student
        </router-link>
        <router-link to="/register?role=company" class="btn-outline-custom btn-lg cta-btn-outline ms-0 ms-md-3 mt-3 mt-md-0">
          I'm a Company
        </router-link>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const ctaRef = ref(null)
const isVisible = ref(false)
let observer = null

onMounted(() => {
  observer = new IntersectionObserver((entries) => {
    if (entries[0].isIntersecting) {
      isVisible.value = true
    }
  }, { threshold: 0.3 })
  
  if (ctaRef.value) observer.observe(ctaRef.value)
})

onUnmounted(() => {
  if (observer) observer.disconnect()
})
</script>

<style scoped>
.cta-section {
  padding: 10rem 0;
  background-color: var(--color-background);
  display: flex;
  align-items: center;
  justify-content: center;
  border-bottom: 1px solid rgba(250, 248, 245, 0.05);
}

.cta-content {
  max-width: 800px;
  opacity: 0;
  transform: translateY(40px);
  transition: opacity 0.8s ease-out, transform 0.8s ease-out;
}

.is-visible {
  opacity: 1 !important;
  transform: translateY(0) !important;
}

.cta-title {
  font-family: var(--font-heading);
  font-weight: 700;
  font-size: clamp(2.5rem, 5vw, 4.5rem);
  letter-spacing: -0.02em;
  color: var(--color-text-light);
  margin-bottom: 1.5rem;
}

.cta-subtitle {
  font-family: var(--font-heading);
  font-size: clamp(1.125rem, 2vw, 1.35rem);
  color: #B4B4BC;
  margin-bottom: 3rem;
  font-weight: 300;
}

.cta-actions {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

@media (min-width: 768px) {
  .cta-actions {
    flex-direction: row;
  }
}

.cta-btn {
  background: var(--color-accent);
  color: #0D0D12;
  font-family: var(--font-heading);
  font-weight: 600;
  padding: 1rem 3rem;
  border-radius: 3rem;
  border: none;
  font-size: 1.125rem;
  transition: transform 0.2s ease-out, background-color 0.2s;
  text-decoration: none;
  display: inline-block;
}

.cta-btn:hover {
  transform: scale(1.03);
  background: #E0C16A;
}

.cta-btn-outline {
  background: transparent;
  color: var(--color-text-light);
  font-family: var(--font-heading);
  font-weight: 500;
  padding: 1rem 3rem;
  border-radius: 3rem;
  border: 1px solid rgba(250, 248, 245, 0.2);
  font-size: 1.125rem;
  transition: transform 0.2s ease-out, background-color 0.2s;
  text-decoration: none;
  display: inline-block;
}

.cta-btn-outline:hover {
  background: rgba(250, 248, 245, 0.05);
  transform: scale(1.03);
  color: var(--color-text-light);
}
</style>
