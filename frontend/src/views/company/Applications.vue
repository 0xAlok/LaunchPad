<template>
  <div class="container py-4">
    <div class="page-header">
      <router-link to="/company/drives" class="back-link"><ArrowLeft :size="20" /> Back to Drives</router-link>
      <h1><ClipboardList :size="20" /> Applications</h1>
      <p v-if="driveName">for {{ driveName }}</p>
    </div>

    <div v-if="!driveApproved" class="alert-banner mb-3">
      This drive's approval has been revoked by the admin. Application management is disabled.
    </div>

    <div v-if="loading" class="loading-container"><div class="spinner"></div></div>

    <div v-else-if="applications.length === 0" class="empty-state">
      <Inbox :size="20" />
      <h3>No applications yet</h3>
    </div>

    <div v-else class="table-responsive">
      <table class="table table-dark-custom">
        <thead>
          <tr>
            <th>Student</th>
            <th>ATS Score</th>
            <th>Applied On</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="app in applications" :key="app.id">
            <td>
              <div class="student-info">
                <span class="fw-semibold">{{ app.student_name }}</span>
                <button class="btn-link-sm" @click="toggleStudentDetail(app.id)">
                  {{ expandedStudent === app.id ? 'Hide' : 'Details' }}
                </button>
              </div>
              <div v-if="expandedStudent === app.id" class="student-detail">
                <div><strong>Branch:</strong> {{ app.student_branch }}</div>
                <div><strong>CGPA:</strong> {{ app.student_cgpa }}</div>
                <div><strong>Email:</strong> {{ app.student_email }}</div>
                <div><strong>Phone:</strong> {{ app.student_phone }}</div>
                <div v-if="app.student_skills"><strong>Skills:</strong> {{ app.student_skills }}</div>
                <div v-if="app.student_experience"><strong>Experience:</strong> {{ app.student_experience }}</div>
                <button v-if="app.has_resume" class="btn-outline-custom btn-sm mt-2" @click="downloadResume(app.id, app.student_name)">
                  <Download :size="14" /> Resume
                </button>
              </div>
            </td>
            <td>
              <span class="ats-value">{{ app.ats_score || 0 }}%</span>
            </td>
            <td>{{ formatDate(app.applied_at) }}</td>
            <td>
              <span :class="['badge-status', `badge-${app.status}`]">{{ app.status }}</span>
              <div v-if="app.status === 'selected' && app.joining_date" class="joining-date">
                Joining: {{ formatDate(app.joining_date) }}
              </div>
              <div v-if="app.status === 'rejected' && app.company_feedback" class="feedback-text">
                Feedback: {{ app.company_feedback }}
              </div>
            </td>
            <td>
              <div v-if="driveApproved" class="action-btns">
                <button
                  v-if="app.status === 'applied'"
                  class="btn-success-custom btn-sm"
                  @click="updateStatus(app.id, 'shortlisted')"
                >
                  Shortlist
                </button>
                <button
                  v-if="app.status === 'shortlisted'"
                  class="btn-primary-custom btn-sm"
                  @click="openSelectModal(app)"
                >
                  Select
                </button>
                <button
                  v-if="app.status === 'applied' || app.status === 'shortlisted'"
                  class="btn-danger-custom btn-sm"
                  @click="confirmReject(app.id)"
                >
                  Reject
                </button>
                <button
                  v-if="app.status === 'shortlisted' && !app.interview"
                  class="btn-outline-custom btn-sm"
                  @click="openInterviewModal(app)"
                >
                  <CalendarPlus :size="20" /> Interview
                </button>
              </div>
              <span v-else class="text-muted">—</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="showModal" class="modal-overlay" @click.self="showModal = false">
      <div class="modal-card card-dark">
        <h3>Schedule Interview</h3>
        <p class="text-muted mb-3">for {{ selectedApp?.student_name }}</p>
        <form @submit.prevent="scheduleInterview" class="form-dark">
          <div class="mb-3">
            <label class="form-label">Date & Time *</label>
            <input v-model="interviewForm.scheduled_at" type="datetime-local" class="form-control" required />
          </div>
          <div class="mb-3">
            <label class="form-label">Location</label>
            <input v-model="interviewForm.location" class="form-control" placeholder="Room 101 / Zoom link" />
          </div>
          <div class="mb-3">
            <label class="form-label">Type</label>
            <select v-model="interviewForm.interview_type" class="form-select">
              <option value="in-person">In-Person</option>
              <option value="online">Online</option>
            </select>
          </div>
          <div class="d-flex gap-2">
            <button type="submit" class="btn-primary-custom">Schedule</button>
            <button type="button" class="btn-outline-custom" @click="showModal = false">Cancel</button>
          </div>
        </form>
      </div>
    </div>

    <div v-if="showSelectModal" class="modal-overlay" @click.self="showSelectModal = false">
      <div class="modal-card card-dark" style="max-width: 420px;">
        <h3>Select Candidate</h3>
        <p class="text-muted mb-3">Set joining date for {{ selectApp?.student_name }}</p>
        <form @submit.prevent="confirmSelection" class="form-dark">
          <div class="mb-3">
            <label class="form-label">Joining Date *</label>
            <input v-model="selectForm.joining_date" type="date" class="form-control" :min="minJoiningDate" required />
          </div>
          <div class="d-flex gap-2">
            <button type="submit" class="btn-primary-custom">Confirm Selection</button>
            <button type="button" class="btn-outline-custom" @click="showSelectModal = false">Cancel</button>
          </div>
        </form>
      </div>
    </div>

    <div v-if="showRejectConfirm" class="modal-overlay" @click.self="showRejectConfirm = false">
      <div class="modal-card card-dark" style="max-width: 460px;">
        <h3>Reject Application</h3>
        <p class="text-muted mb-3">Add feedback for {{ rejectTargetName || 'the student' }}.</p>
        <form @submit.prevent="doReject" class="form-dark">
          <div class="mb-3">
            <label class="form-label">Feedback *</label>
            <textarea
              v-model="rejectForm.feedback"
              class="form-control"
              rows="4"
              maxlength="800"
              placeholder="Explain why the application is rejected..."
              required
            ></textarea>
          </div>
          <div class="d-flex gap-2 mt-3">
            <button type="submit" class="btn-danger-custom btn-sm">Submit Rejection</button>
            <button type="button" class="btn-outline-custom btn-sm" @click="showRejectConfirm = false">Cancel</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ArrowLeft, ClipboardList, Inbox, CalendarPlus, Download } from 'lucide-vue-next'
import api from '../../api'
import { useToastStore } from '../../stores/toast'
import { formatDate } from '../../utils/date'

const route = useRoute()
const toastStore = useToastStore()
const driveId = route.params.driveId
const driveName = ref('')
const driveApproved = ref(true)
const applications = ref([])
const loading = ref(true)
const showModal = ref(false)
const selectedApp = ref(null)
const interviewForm = reactive({ scheduled_at: '', location: '', interview_type: 'in-person' })
const showSelectModal = ref(false)
const selectApp = ref(null)
const minJoiningDate = getTodayDateInput()
const selectForm = reactive({ joining_date: minJoiningDate })
const showRejectConfirm = ref(false)
const rejectTargetId = ref(null)
const rejectTargetName = ref('')
const rejectForm = reactive({ feedback: '' })

function confirmReject(id) {
  rejectTargetId.value = id
  const target = applications.value.find((a) => a.id === id)
  rejectTargetName.value = target?.student_name || ''
  rejectForm.feedback = ''
  showRejectConfirm.value = true
}

async function doReject() {
  const feedback = rejectForm.feedback.trim()
  if (!feedback) {
    toastStore.danger('Feedback is required for rejection')
    return
  }
  const ok = await updateStatus(rejectTargetId.value, 'rejected', { feedback })
  if (ok) {
    showRejectConfirm.value = false
  }
}

function getTodayDateInput() {
  const today = new Date()
  const year = today.getFullYear()
  const month = String(today.getMonth() + 1).padStart(2, '0')
  const day = String(today.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

const expandedStudent = ref(null)

function toggleStudentDetail(id) {
  expandedStudent.value = expandedStudent.value === id ? null : id
}

async function downloadResume(appId, studentName) {
  try {
    const res = await api.get(`/company/applications/${appId}/resume`, { responseType: 'blob' })
    const url = window.URL.createObjectURL(new Blob([res.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `${studentName}_resume.pdf`)
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)
  } catch (err) {
    toastStore.danger(err.response?.data?.error || 'Failed to download resume')
  }
}

async function fetchApplications() {
  loading.value = true
  try {
    const res = await api.get(`/company/drives/${driveId}/applications`)
    applications.value = res.data.applications
    if (res.data.drive) {
      driveName.value = res.data.drive.title
      driveApproved.value = res.data.drive.is_approved
    }
  } catch { toastStore.danger('Failed to load applications') }
  finally { loading.value = false }
}

async function updateStatus(appId, status, extraPayload = {}) {
  try {
    await api.put(`/company/applications/${appId}/status`, { status, ...extraPayload })
    toastStore.success(`Application ${status}`)
    fetchApplications()
    return true
  } catch (err) {
    toastStore.danger(err.response?.data?.error || 'Action failed')
    return false
  }
}

function openSelectModal(app) {
  selectApp.value = app
  selectForm.joining_date = getTodayDateInput()
  showSelectModal.value = true
}

async function confirmSelection() {
  if (!selectApp.value?.id) return
  await updateStatus(selectApp.value.id, 'selected', { joining_date: selectForm.joining_date })
  showSelectModal.value = false
}

function openInterviewModal(app) {
  selectedApp.value = app
  interviewForm.scheduled_at = ''
  interviewForm.location = ''
  interviewForm.interview_type = 'in-person'
  showModal.value = true
}

async function scheduleInterview() {
  try {
    const payload = { ...interviewForm }
    if (payload.scheduled_at) {
      payload.scheduled_at = new Date(payload.scheduled_at).toISOString()
    }
    await api.post(`/company/applications/${selectedApp.value.id}/interview`, payload)
    toastStore.success('Interview scheduled')
    showModal.value = false
    fetchApplications()
  } catch (err) {
    toastStore.danger(err.response?.data?.error || 'Failed to schedule interview')
  }
}

onMounted(fetchApplications)
</script>

<style scoped>
.back-link { font-size: 0.875rem; color: var(--text-secondary); margin-bottom: 0.5rem; display: inline-block; }
.back-link:hover { color: var(--accent-primary); }

.action-btns { display: flex; gap: 0.5rem; flex-wrap: wrap; }

.ats-value {
  font-size: 0.875rem;
  font-weight: 700;
  color: var(--accent-primary);
}

.modal-overlay {
  position: fixed; top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.6); display: flex; align-items: center; justify-content: center;
  z-index: 2000;
}
.modal-card { width: 100%; max-width: 450px; }
.joining-date {
  margin-top: 0.35rem;
  font-size: 0.78rem;
  color: var(--text-muted);
}
.feedback-text {
  margin-top: 0.35rem;
  font-size: 0.78rem;
  color: #fca5a5;
  max-width: 320px;
}

.alert-banner {
  background: rgba(220, 38, 38, 0.1);
  border: 1px solid rgba(220, 38, 38, 0.3);
  color: #ef4444;
  padding: 0.75rem 1rem;
  border-radius: var(--border-radius-sm, 0.5rem);
  font-size: 0.9rem;
  font-weight: 600;
}

.student-info { display: flex; align-items: center; gap: 0.5rem; }
.btn-link-sm {
  background: none; border: none; color: var(--accent-primary);
  font-size: 0.75rem; cursor: pointer; padding: 0; text-decoration: underline;
}
.student-detail {
  margin-top: 0.5rem; padding: 0.75rem;
  background: var(--bg-secondary); border-radius: var(--border-radius-sm);
  font-size: 0.8rem; color: var(--text-secondary);
  display: flex; flex-direction: column; gap: 0.25rem;
}
</style>
