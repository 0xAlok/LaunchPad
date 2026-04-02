<template>
  <div class="container py-4">
    <div class="page-header d-flex justify-content-between align-items-center">
      <div>
        <h1><FileText :size="20" /> My Applications</h1>
      </div>
      <button class="btn-primary-custom btn-sm" @click="exportCSV" :disabled="exporting" v-if="applications.length > 0">
        <span v-if="exporting" class="spinner-border spinner-border-sm me-1"></span>
        <Download v-else :size="20" /> {{ exporting ? 'Exporting...' : 'Export CSV' }}
      </button>
    </div>

    <div v-if="loading" class="loading-container"><div class="spinner"></div></div>

    <div v-else-if="applications.length === 0" class="empty-state">
      <Inbox :size="20" />
      <h3>No applications yet</h3>
      <p>
        <router-link to="/student/drives">Browse drives</router-link> and start applying!
      </p>
    </div>

    <div v-else class="app-cards">
      <div v-for="app in applications" :key="app.id" class="card-dark app-card">
        <div class="d-flex justify-content-between align-items-start">
          <div>
            <h3 class="app-title">{{ app.drive_title }}</h3>
            <p class="app-company"><Building2 :size="20" /> {{ app.company_name }}</p>
          </div>
          <span :class="['badge-status', `badge-${app.status}`]">{{ app.status }}</span>
        </div>

        <div class="app-meta">
          <span><Calendar :size="20" /> Applied: {{ formatDate(app.applied_at) }}</span>
          <span v-if="app.ats_score"><Gauge :size="20" /> ATS: {{ app.ats_score }}%</span>
          <span v-if="app.status === 'selected' && app.joining_date"><CalendarCheck :size="20" /> Joining: {{ formatDate(app.joining_date) }}</span>
        </div>

        <div v-if="app.interview" class="interview-card">
          <h4><Video :size="20" /> Interview Scheduled</h4>
          <div class="interview-details">
            <span><Clock :size="20" /> {{ formatDateTime(app.interview.scheduled_at) }}</span>
            <span><MapPin :size="20" /> {{ app.interview.location || 'TBD' }}</span>
            <span><Tag :size="20" /> {{ app.interview.interview_type }}</span>
          </div>
        </div>

        <div v-if="app.status === 'rejected' && app.company_feedback" class="feedback-card">
          <h4><MessageSquareWarning :size="20" /> Rejection Feedback</h4>
          <p>{{ app.company_feedback }}</p>
        </div>

        <div v-if="app.status === 'applied'" class="app-actions">
          <button class="btn-outline-custom btn-sm" @click="confirmWithdraw(app.id)">
            <XCircle :size="20" /> Withdraw
          </button>
        </div>
      </div>
    </div>

    <div v-if="showWithdrawConfirm" class="modal-overlay" @click.self="showWithdrawConfirm = false">
      <div class="modal-card card-dark" style="max-width: 400px;">
        <h3>Withdraw Application?</h3>
        <p class="text-muted">Are you sure you want to withdraw this application? This action cannot be undone.</p>
        <div class="d-flex gap-2 mt-3">
          <button class="btn-danger-custom btn-sm" @click="doWithdraw">Yes, Withdraw</button>
          <button class="btn-outline-custom btn-sm" @click="showWithdrawConfirm = false">Cancel</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../../api'
import { useToastStore } from '../../stores/toast'
import { formatDate, formatDateTime } from '../../utils/date'
import { FileText, Download, Inbox, Building2, Calendar, CalendarCheck, Gauge, Video, Clock, MapPin, Tag, MessageSquareWarning, XCircle } from 'lucide-vue-next'

const toastStore = useToastStore()
const applications = ref([])
const loading = ref(true)
const exporting = ref(false)
const showWithdrawConfirm = ref(false)
const withdrawTargetId = ref(null)

function confirmWithdraw(id) {
  withdrawTargetId.value = id
  showWithdrawConfirm.value = true
}

async function doWithdraw() {
  showWithdrawConfirm.value = false
  await withdrawApp(withdrawTargetId.value)
}

async function fetchApps() {
  loading.value = true
  try {
    const res = await api.get('/student/applications')
    applications.value = res.data.applications
  } catch { toastStore.danger('Failed to load applications') }
  finally { loading.value = false }
}

async function withdrawApp(id) {
  try {
    await api.put(`/student/applications/${id}/withdraw`)
    toastStore.info('Application withdrawn')
    fetchApps()
  } catch (err) {
    toastStore.danger(err.response?.data?.error || 'Action failed')
  }
}

async function exportCSV() {
  exporting.value = true
  try {
    const res = await api.post('/student/applications/export')
    toastStore.success(res.data.message || 'Export started')
  } catch (err) {
    toastStore.danger(err.response?.data?.error || 'Export failed')
  } finally {
    exporting.value = false
  }
}

onMounted(fetchApps)
</script>

<style scoped>
.app-cards { display: grid; grid-template-columns: repeat(auto-fill, minmax(380px, 1fr)); gap: 1rem; }
.app-card { display: flex; flex-direction: column; gap: 0.75rem; }
.app-title { font-size: 1.05rem; font-weight: 700; margin: 0; }
.app-company { color: var(--accent-secondary); font-size: 0.85rem; margin: 0.25rem 0 0; }
.app-company svg { margin-right: 0.25rem; vertical-align: middle; }
.app-meta { display: flex; gap: 1rem; font-size: 0.85rem; color: var(--text-muted); }
.app-meta svg { margin-right: 0.25rem; vertical-align: middle; }

.interview-card {
  background: rgba(99, 102, 241, 0.08); border: 1px solid rgba(99, 102, 241, 0.2);
  border-radius: var(--border-radius-sm); padding: 1rem;
}
.interview-card h4 { font-size: 0.9rem; font-weight: 600; color: var(--accent-primary); margin-bottom: 0.5rem; }
.interview-card h4 svg { margin-right: 0.25rem; vertical-align: middle; }
.interview-details { display: flex; flex-wrap: wrap; gap: 1rem; font-size: 0.85rem; color: var(--text-secondary); }
.interview-details svg { margin-right: 0.25rem; vertical-align: middle; }

.feedback-card {
  background: rgba(239, 68, 68, 0.08); border: 1px solid rgba(239, 68, 68, 0.3);
  border-radius: var(--border-radius-sm); padding: 1rem;
}
.feedback-card h4 { font-size: 0.9rem; font-weight: 600; color: #fca5a5; margin-bottom: 0.5rem; }
.feedback-card h4 svg { margin-right: 0.25rem; vertical-align: middle; }
.feedback-card p { margin: 0; font-size: 0.85rem; color: var(--text-secondary); white-space: pre-wrap; }

.app-actions { margin-top: auto; padding-top: 0.5rem; }
.modal-overlay {
  position: fixed; top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.6); display: flex; align-items: center; justify-content: center;
  z-index: 2000;
}
.modal-card { padding: 1.5rem; }
</style>
