<template>
  <section id="features" class="features-section">
    <div class="container">
      <div class="row section-header" :class="{ 'is-visible': isHeaderVisible }" ref="headerRef">
        <div class="col-12 text-center text-md-start">
          <h2 class="section-title">The LaunchPad Ecosystem</h2>
        </div>
      </div>

      <div class="row flex-column flex-lg-row gx-5 gy-4 mt-4">
        <!-- Card 1: Students -->
        <div class="col-lg-4 d-flex">
          <div class="feature-card card-rounded" :class="{ 'is-visible': isCard1Visible }" ref="card1Ref">
            <h3 class="card-title">For Students</h3>
            <p class="card-desc">Discover and apply to placement drives in one centralized hub.</p>
            
            <div class="card-static-list">
              <ul class="static-list">
                <li><Circle :size="8" class="list-icon" /> Build and manage your academic profile</li>
                <li><Circle :size="8" class="list-icon" /> Discover matching placement drives</li>
                <li><Circle :size="8" class="list-icon" /> Track application status in real-time</li>
              </ul>
            </div>
          </div>
        </div>
        
        <!-- Card 2: Companies -->
        <div class="col-lg-4 d-flex">
          <div class="feature-card card-rounded" :class="{ 'is-visible': isCard2Visible }" ref="card2Ref" style="transition-delay: 0.15s">
            <h3 class="card-title">For Companies</h3>
            <p class="card-desc">Manage recruitment, shortlisting, and selections end to end.</p>
            
            <div class="card-static-list">
              <ul class="static-list">
                <li><Circle :size="8" class="list-icon" /> Define robust eligibility criteria</li>
                <li><Circle :size="8" class="list-icon" /> Automate candidate shortlisting</li>
                <li><Circle :size="8" class="list-icon" /> Organize structured interview rounds</li>
              </ul>
            </div>
          </div>
        </div>
        
        <!-- Card 3: Institutes -->
        <div class="col-lg-4 d-flex">
          <div class="feature-card card-rounded" :class="{ 'is-visible': isCard3Visible }" ref="card3Ref" style="transition-delay: 0.3s">
            <h3 class="card-title">For Institutes</h3>
            <p class="card-desc">Full visibility and control over every placement activity.</p>
            
            <div class="card-static-list">
              <ul class="static-list">
                <li><Circle :size="8" class="list-icon" /> Verify student details and academic records</li>
                <li><Circle :size="8" class="list-icon" /> Export comprehensive placement reports</li>
                <li><Circle :size="8" class="list-icon" /> Monitor active drive progress end-to-end</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { Circle } from 'lucide-vue-next'

const headerRef = ref(null)
const card1Ref = ref(null)
const card2Ref = ref(null)
const card3Ref = ref(null)

const isHeaderVisible = ref(false)
const isCard1Visible = ref(false)
const isCard2Visible = ref(false)
const isCard3Visible = ref(false)

let observer = null

onMounted(() => {
  observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        if (entry.target === headerRef.value) isHeaderVisible.value = true
        if (entry.target === card1Ref.value) isCard1Visible.value = true
        if (entry.target === card2Ref.value) isCard2Visible.value = true
        if (entry.target === card3Ref.value) isCard3Visible.value = true
      }
    })
  }, { threshold: 0.2 })
  
  if (headerRef.value) observer.observe(headerRef.value)
  if (card1Ref.value) observer.observe(card1Ref.value)
  if (card2Ref.value) observer.observe(card2Ref.value)
  if (card3Ref.value) observer.observe(card3Ref.value)
})

onUnmounted(() => {
  if (observer) observer.disconnect()
})
</script>

<style scoped>
.features-section {
  padding: 8rem 0;
  background-color: var(--color-background);
  overflow: hidden;
}

.section-title {
  font-family: var(--font-heading);
  font-weight: 700;
  font-size: clamp(2rem, 4vw, 3rem);
  letter-spacing: -0.02em;
  color: var(--color-text-light);
  margin-bottom: 0.5rem;
}

.feature-card {
  background-color: rgba(250, 248, 245, 0.03);
  border: 1px solid rgba(250, 248, 245, 0.08);
  border-radius: 2rem;
  padding: 2.5rem;
  width: 100%;
  display: flex;
  flex-direction: column;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
  transition: transform 0.4s ease-out, opacity 0.6s ease-out;
  opacity: 0;
  transform: translateY(40px);
}

.card-title {
  font-family: var(--font-heading);
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--color-accent);
  margin-bottom: 0.75rem;
}

.card-desc {
  font-family: var(--font-heading);
  font-size: 1rem;
  color: #B4B4BC;
  margin-bottom: 2rem;
  line-height: 1.5;
  min-height: 3rem;
}

.card-static-list {
  flex-grow: 1;
  display: flex;
  flex-direction: column;
}

.static-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.static-list li {
  padding: 1rem 1.25rem;
  background: rgba(13, 13, 18, 0.5);
  border: 1px solid rgba(201, 168, 76, 0.2);
  border-radius: 1rem;
  font-family: var(--font-heading);
  color: var(--color-text-light);
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  font-size: 0.95rem;
  line-height: 1.4;
  transition: transform 0.2s ease-out, border-color 0.2s ease-out;
}

.static-list li:hover {
  transform: translateY(-2px);
  border-color: rgba(201, 168, 76, 0.5);
}

.list-icon {
  color: var(--color-accent);
  margin-top: 8px;
  font-size: 0.5rem;
}

.section-header {
  opacity: 0;
  transform: translateY(40px);
  transition: opacity 0.6s ease-out, transform 0.6s ease-out;
}

.is-visible {
  opacity: 1 !important;
  transform: translateY(0) !important;
}
</style>
