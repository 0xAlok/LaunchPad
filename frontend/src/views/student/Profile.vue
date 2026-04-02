<template>
  <div class="container py-4">
    <div class="page-header">
      <h1><UserCog :size="20" /> My Profile</h1>
    </div>

    <div class="row g-4">
      <div class="col-lg-7">
        <div class="card-dark">
          <h3 class="section-title mb-3">Personal Details</h3>
          <form @submit.prevent="updateProfile" class="form-dark">
            <div class="mb-3">
              <label class="form-label">Full Name</label>
              <input v-model="form.name" class="form-control" placeholder="Your full name" required />
            </div>
            <div class="row">
              <div class="col-md-6 mb-3">
                <label class="form-label">Contact No.</label>
                <input v-model="form.phone" type="tel" class="form-control" placeholder="10-digit number" pattern="[0-9]{10}" maxlength="10" title="Enter exactly 10 digits" required />
              </div>
              <div class="col-md-6 mb-3">
                <label class="form-label">Email</label>
                <input :value="profile?.email" class="form-control" disabled />
              </div>
            </div>
            <div class="row">
              <div class="col-md-6 mb-3">
                <label class="form-label">Branch / Discipline</label>
                <select v-model="form.branch" class="form-control" required>
                  <option value="" disabled>Select your branch</option>
                  <option value="Computer Science">Computer Science</option>
                  <option value="Electronics">Electronics</option>
                  <option value="Mechanical">Mechanical</option>
                  <option value="Electrical">Electrical</option>
                  <option value="Civil">Civil</option>
                  <option value="Data Science">Data Science</option>
                </select>
              </div>
              <div class="col-md-6 mb-3">
                <label class="form-label">Current CGPA</label>
                <input v-model="form.cgpa" type="number" step="0.01" min="0" max="10" class="form-control" />
              </div>
            </div>
            <div class="mb-3">
              <label class="form-label">Key Skills</label>
              <textarea v-model="form.skills" class="form-control" rows="2" placeholder="e.g. Python, React, Data Analysis"></textarea>
            </div>
            <div class="mb-3">
              <label class="form-label">Brief Experience</label>
              <textarea v-model="form.experience" class="form-control" rows="3" placeholder="Internships, projects, or relevant experience"></textarea>
            </div>
            <button type="submit" class="btn-primary-custom" :disabled="saving">
              <Check :size="20" /> Save Changes
            </button>
          </form>
        </div>
      </div>

      <!-- Resume upload -->
      <div class="col-lg-5">
        <div class="card-dark">
          <h3 class="section-title mb-3">Resume</h3>
          <div class="resume-zone" @click="$refs.fileInput.click()" @dragover.prevent @drop.prevent="handleDrop">
            <FileText :size="40" />
            <p v-if="profile?.resume_path">Resume uploaded!</p>
            <p v-else>Drop PDF here or click to upload</p>
            <small>Max 5 MB · PDF only</small>
          </div>
          <input ref="fileInput" type="file" accept=".pdf" style="display: none" @change="handleFileChange" />
          <button
            v-if="selectedFile"
            class="btn-primary-custom btn-sm mt-3 w-100"
            @click="uploadResume"
            :disabled="uploading"
          >
            <span v-if="uploading" class="spinner-border spinner-border-sm"></span>
            <span v-else><Upload :size="20" /> Upload {{ selectedFile.name }}</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useAuthStore } from '../../stores/auth'
import { useToastStore } from '../../stores/toast'
import api from '../../api'
import { UserCog, Check, FileText, Upload } from 'lucide-vue-next'

const authStore = useAuthStore()
const toastStore = useToastStore()
const profile = ref(null)
const saving = ref(false)
const uploading = ref(false)
const selectedFile = ref(null)

const form = reactive({
  name: '',
  branch: '',
  cgpa: 0,
  phone: '',
  skills: '',
  experience: '',
})

onMounted(async () => {
  try {
    const res = await api.get('/student/profile')
    profile.value = res.data.student
    form.name = profile.value.name
    form.branch = profile.value.branch
    form.cgpa = profile.value.cgpa
    form.phone = profile.value.phone || ''
    form.skills = profile.value.skills || ''
    form.experience = profile.value.experience || ''
  } catch (err) {
    toastStore.danger('Failed to load profile')
  }
})

async function updateProfile() {
  saving.value = true
  try {
    await api.put('/student/profile', form)
    toastStore.success('Profile updated')
    authStore.fetchProfile()
  } catch (err) {
    toastStore.danger(err.response?.data?.error || 'Update failed')
  } finally { saving.value = false }
}

function handleFileChange(e) {
  selectedFile.value = e.target.files[0]
}

function handleDrop(e) {
  const file = e.dataTransfer.files[0]
  if (file && file.type === 'application/pdf') {
    selectedFile.value = file
  } else if (file) {
    toastStore.danger('Only PDF files are allowed')
  }
}

async function uploadResume() {
  if (!selectedFile.value) return
  uploading.value = true
  const formData = new FormData()
  formData.append('resume', selectedFile.value)
  try {
    await api.post('/student/resume', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    toastStore.success('Resume uploaded')
    selectedFile.value = null
    const res = await api.get('/student/profile')
    profile.value = res.data.student
  } catch (err) {
    toastStore.danger(err.response?.data?.error || 'Upload failed')
  } finally { uploading.value = false }
}
</script>

<style scoped>
.section-title { font-size: 1rem; font-weight: 600; }

.resume-zone {
  border: 2px dashed var(--border-color);
  border-radius: var(--border-radius);
  padding: 2rem;
  text-align: center;
  cursor: pointer;
  transition: var(--transition);
  color: var(--text-muted);
}
.resume-zone:hover {
  border-color: var(--accent-primary);
  background: rgba(99, 102, 241, 0.05);
}
.resume-zone svg { color: var(--accent-danger); margin-bottom: 0.5rem; display: block; margin-left: auto; margin-right: auto; }
.resume-zone p { margin: 0.25rem 0; font-size: 0.9rem; }
.resume-zone small { font-size: 0.75rem; }
</style>
