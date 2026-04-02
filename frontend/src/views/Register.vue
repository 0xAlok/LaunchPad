<template>
  <div class="auth-page landing-cinematic">
    <div class="auth-wrapper">
      <div class="auth-image-col">
        <transition name="fade-image" mode="out-in">
          <img 
            :key="role"
            :src="role === 'student' ? 'https://res.cloudinary.com/deibwaqlz/image/upload/v1773068098/student_wb4sqh.png' : 'https://res.cloudinary.com/deibwaqlz/image/upload/v1773068097/recruiter_rq6zek.png'" 
            :alt="role === 'student' ? 'Student Registration' : 'Recruiter Registration'" 
            class="auth-hero-img"
          />
        </transition>
        <div class="image-overlay"></div>
        <div class="brand-overlay">
          <router-link to="/" class="brand-link">
            <img src="https://res.cloudinary.com/deibwaqlz/image/upload/v1773065944/Untitled_design_4_u1lm8y.png" alt="Logo" class="mini-logo" />
            <span>LaunchPad</span>
          </router-link>
        </div>
        
        <div class="quote-overlay">
          <p class="quote-text">
            {{ role === 'student' ? 'Accelerate your career trajectory.' : 'Discover the next generation of talent.' }}
          </p>
        </div>
      </div>

      <div class="auth-form-col">
        <div class="auth-form-content">
          <div class="auth-form-container">
            <div class="auth-header">
              <h1 class="auth-title">Create Account</h1>
            </div>

            <div class="role-selector mb-3">
              <button
                :class="['role-btn', { active: role === 'student' }]"
                @click="role = 'student'"
              >
                I'm a Student
              </button>
              <button
                :class="['role-btn', { active: role === 'company' }]"
                @click="role = 'company'"
              >
                I'm a Company
              </button>
            </div>

            <form @submit.prevent="handleRegister" class="auth-form">
              <div class="form-group mb-2">
                <label class="form-label">Email Address</label>
                <input id="reg-email" v-model="email" type="email" class="form-input" placeholder="you@university.edu" required />
              </div>

              <div class="form-group mb-2">
                <label class="form-label">Password</label>
                <input id="reg-password" v-model="password" type="password" class="form-input" minlength="8" placeholder="At least 8 characters" required />
              </div>

              <div class="divider mb-2"></div>

              <transition name="slide-fade" mode="out-in">
                <div v-if="role === 'student'" key="student-fields">
                  <div class="mb-2">
                    <label class="form-label">Full Name</label>
                    <input id="reg-name" v-model="name" type="text" class="form-input" placeholder="Full name as per records" required />
                  </div>
                  <div class="row gx-3">
                    <div class="col-6 mb-2">
                      <label class="form-label">Contact</label>
                      <input id="reg-phone" v-model="phone" type="tel" class="form-input" placeholder="10-digit number" pattern="[0-9]{10}" maxlength="10" title="Enter exactly 10 digits" required />
                    </div>
                    <div class="col-6 mb-2">
                      <label class="form-label">CGPA</label>
                      <input id="reg-cgpa" v-model="cgpa" type="number" step="0.01" min="0" max="10" class="form-input" placeholder="e.g. 8.5" required />
                    </div>
                  </div>
                  <div class="mb-2">
                    <label class="form-label">Branch / Discipline</label>
                    <select id="reg-education" v-model="branch" class="form-input" required>
                      <option value="" disabled>Select your branch</option>
                      <option value="Computer Science">Computer Science</option>
                      <option value="Electronics">Electronics</option>
                      <option value="Mechanical">Mechanical</option>
                      <option value="Electrical">Electrical</option>
                      <option value="Civil">Civil</option>
                      <option value="Data Science">Data Science</option>
                    </select>
                  </div>
                  <div class="mb-2">
                    <label class="form-label">Key Skills (Comma separated)</label>
                    <input id="reg-skills" v-model="skills" type="text" class="form-input" placeholder="Python, Vue.js, Data Analysis" />
                  </div>
                  <div class="mb-2">
                    <label class="form-label">Brief Experience</label>
                    <textarea id="reg-expr" v-model="experience" class="form-input" placeholder="Any past internships or projects..." rows="1"></textarea>
                  </div>
                </div>

                <div v-else key="company-fields">
                  <div class="mb-2">
                    <label class="form-label">Company Name</label>
                    <input id="reg-cname" v-model="companyName" type="text" class="form-input" placeholder="Full registered company name" required />
                  </div>
                  <div class="mb-2">
                    <label class="form-label">Industry</label>
                    <input id="reg-industry" v-model="industry" type="text" class="form-input" placeholder="e.g., Technology, Finance" />
                  </div>
                  <div class="mb-2">
                    <label class="form-label">Location</label>
                    <input id="reg-location" v-model="location" type="text" class="form-input" placeholder="e.g. Bangalore, Remote" />
                  </div>
                  <div class="mb-2">
                    <label class="form-label">HR Contact Details</label>
                    <input id="reg-hr-contact" v-model="hrContact" type="text" class="form-input" placeholder="Name / Phone / Email of HR" />
                  </div>
                </div>
              </transition>

              <div v-if="authStore.error" class="error-msg">
                <AlertTriangle :size="18" />
                {{ authStore.error }}
              </div>

              <button type="submit" class="btn-auth-primary w-100" :disabled="authStore.loading">
                <span v-if="authStore.loading" class="spinner-border spinner-border-sm"></span>
                <span v-else>Register</span>
              </button>
            </form>

            <div class="auth-footer">
              <span class="text-muted">Already registered?</span>
              <router-link to="/login" class="auth-link">Sign In</router-link>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { useToastStore } from '../stores/toast'
import { AlertTriangle } from 'lucide-vue-next'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const toastStore = useToastStore()

const role = ref(route.query.role === 'company' ? 'company' : 'student')
const email = ref('')
const password = ref('')
const name = ref('')
const phone = ref('')
const branch = ref('')
const cgpa = ref('')
const skills = ref('')
const experience = ref('')
const companyName = ref('')
const industry = ref('')
const location = ref('')
const hrContact = ref('')

async function handleRegister() {
  if (password.value.length < 8) {
    toastStore.danger('Password must be at least 8 characters')
    return
  }

  if (role.value === 'student') {
    if (!/^\d{10}$/.test(phone.value)) {
      toastStore.danger('Phone number must be exactly 10 digits')
      return
    }
    if (parseFloat(cgpa.value) < 0 || parseFloat(cgpa.value) > 10) {
      toastStore.danger('CGPA must be between 0 and 10')
      return
    }
  }

  const payload = { email: email.value, password: password.value, role: role.value }

  if (role.value === 'student') {
    payload.name = name.value
    payload.phone = phone.value
    payload.branch = branch.value
    payload.cgpa = parseFloat(cgpa.value) || 0
    payload.skills = skills.value
    payload.experience = experience.value
  } else {
    payload.company_name = companyName.value
    payload.industry = industry.value
    payload.location = location.value
    payload.hr_contact = hrContact.value
  }

  try {
    await authStore.register(payload)
    toastStore.success('Account created! Please sign in.')
    router.push('/login')
  } catch {}
}
</script>

<style scoped>
@import '../assets/auth.css';

.auth-image-col {
  overflow: hidden;
}

.quote-overlay {
  position: absolute;
  bottom: 4rem;
  left: 3rem;
  right: 3rem;
  z-index: 10;
}

.quote-text {
  font-family: var(--font-heading);
  font-weight: 500;
  font-size: 1.5rem;
  color: var(--color-text-light);
  max-width: 400px;
  line-height: 1.4;
  opacity: 0.9;
}

.role-selector {
  display: flex;
  background: rgba(250, 248, 245, 0.03);
  padding: 0.5rem;
  border-radius: 1.25rem;
  border: 1px solid rgba(250, 248, 245, 0.08);
  gap: 0.5rem;
}

.role-btn {
  flex: 1;
  padding: 0.625rem;
  border: none;
  background: transparent;
  color: #B4B4BC;
  border-radius: 0.9rem;
  font-family: var(--font-heading);
  font-weight: 600;
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.2, 0.8, 0.2, 1);
}

.role-btn.active {
  background: var(--color-accent);
  color: #0D0D12;
  box-shadow: 0 4px 12px rgba(201, 168, 76, 0.2);
}

.divider {
  height: 1px;
  background: rgba(250, 248, 245, 0.08);
  width: 100%;
}

/* Transitions */
.fade-image-enter-active, .fade-image-leave-active {
  transition: opacity 0.5s ease;
}
.fade-image-enter-from, .fade-image-leave-to {
  opacity: 0;
}

.slide-fade-enter-active {
  transition: all 0.3s ease-out;
}
.slide-fade-enter-from {
  transform: translateX(10px);
  opacity: 0;
}
</style>
