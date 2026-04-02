<template>
  <header class="hero-section">
    <div class="hero-bg">
      <img src="https://images.unsplash.com/photo-1706074793638-da28b90ea8ae?q=80&w=2000&auto=format&fit=crop" alt="Dark Minimalist Interior" class="hero-image" />
      <div class="hero-gradient"></div>
    </div>
    
    <div class="container hero-content">
      <h1 class="hero-title">
        <span class="d-block line line-1" :class="{ 'is-visible': mounted }">Ambition meets</span>
        <span class="d-block line line-2" :class="{ 'is-visible': mounted }">Opportunity.</span>
      </h1>
      
      <p class="hero-subtitle" :class="{ 'is-visible': mounted }">
        LaunchPad - the campus placement portal that connects students, companies, and institutes for seamless recruitment.
      </p>
      
      <div class="hero-actions" :class="{ 'is-visible': mounted }">
        <router-link to="/register" class="btn-primary-hero">Get Started</router-link>
      </div>
    </div>
  </header>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const mounted = ref(false)

onMounted(() => {
  setTimeout(() => {
    mounted.value = true
  }, 100)
})
</script>

<style scoped>
.hero-section {
  position: relative;
  height: 100dvh;
  min-height: 800px;
  display: flex;
  align-items: flex-end;
  padding-bottom: 12vh;
  overflow: hidden;
}

.hero-bg {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 0;
}

.hero-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: center;
}

.hero-gradient {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(
    to top,
    rgba(13, 13, 18, 1) 0%,
    rgba(13, 13, 18, 0.8) 40%,
    rgba(13, 13, 18, 0.3) 100%
  );
}

.hero-content {
  position: relative;
  z-index: 10;
  max-width: 900px;
}

.line {
  opacity: 0;
  transform: translateY(40px);
  transition: opacity 0.8s ease-out, transform 0.8s ease-out;
}

.line-1 { transition-delay: 0.1s; }
.line-2 { transition-delay: 0.2s; }
.hero-subtitle {
  opacity: 0;
  transform: translateY(40px);
  transition: opacity 0.8s ease-out 0.3s, transform 0.8s ease-out 0.3s;
}
.hero-actions {
  opacity: 0;
  transform: translateY(40px);
  transition: opacity 0.8s ease-out 0.4s, transform 0.8s ease-out 0.4s;
}

.is-visible {
  opacity: 1 !important;
  transform: translateY(0) !important;
}

.hero-title .line-1 {
  font-family: var(--font-heading, 'Inter');
  font-weight: 700;
  font-size: clamp(2rem, 5vw, 3rem);
  letter-spacing: -0.02em;
  color: var(--color-text-light, #FAF8F5);
  margin-bottom: -1rem;
}

.hero-title .line-2 {
  font-family: var(--font-drama, 'Playfair Display');
  font-style: italic;
  font-weight: 400;
  font-size: clamp(4rem, 12vw, 9rem);
  line-height: 1;
  color: var(--color-accent, #C9A84C);
  letter-spacing: -0.04em;
  margin-bottom: 2rem;
}

.hero-subtitle {
  font-family: var(--font-heading, 'Inter');
  font-size: clamp(1.125rem, 2vw, 1.35rem);
  color: #B4B4BC;
  max-width: 600px;
  line-height: 1.5;
  margin-bottom: 3rem;
  font-weight: 300;
}

.hero-actions {
  display: flex;
  gap: 1.5rem;
  align-items: center;
}

.btn-primary-hero {
  background: var(--color-accent, #C9A84C);
  color: #0D0D12;
  font-family: var(--font-heading, 'Inter');
  font-weight: 600;
  font-size: 1rem;
  padding: 1rem 2.5rem;
  border-radius: 3rem;
  text-decoration: none;
  transition: transform 0.2s ease-out, background-color 0.2s ease-out;
}

.btn-primary-hero:hover {
  transform: scale(1.03);
  background: #E0C16A;
}

.btn-outline-hero {
  background: transparent;
  color: var(--color-text-light, #FAF8F5);
  font-family: var(--font-heading, 'Inter');
  font-weight: 500;
  font-size: 1rem;
  padding: 1rem 2rem;
  border-radius: 3rem;
  border: 1px solid rgba(250, 248, 245, 0.2);
  text-decoration: none;
  transition: transform 0.2s ease-out, background-color 0.2s ease-out;
}

.btn-outline-hero:hover {
  background: rgba(250, 248, 245, 0.05);
  transform: translateY(-1px);
  color: var(--color-text-light, #FAF8F5);
}
</style>
