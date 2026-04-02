<template>
  <div class="container py-4">
    <div class="page-header">
      <h1>Company Dashboard</h1>
      <p>Welcome back, {{ authStore.profile?.name || 'Company' }}</p>
    </div>

    <div v-if="!authStore.profile?.is_approved" class="alert-card mb-4">
      <Clock :size="20" />
      <div>
        <strong>Pending Approval</strong>
        <p>Your company registration is awaiting admin approval. You'll be able to create drives once approved.</p>
      </div>
    </div>

    <div class="stats-grid">
      <router-link to="/company/drives" class="stat-card stat-card-link">
        <div class="stat-icon purple"><Megaphone :size="20" /></div>
        <div>
          <div class="stat-value">{{ drives.length }}</div>
          <div class="stat-label">My Drives</div>
        </div>
      </router-link>
      <router-link to="/company/drives" class="stat-card stat-card-link">
        <div class="stat-icon green"><CheckCircle :size="20" /></div>
        <div>
          <div class="stat-value">{{ approvedDrives }}</div>
          <div class="stat-label">Approved</div>
        </div>
      </router-link>
      <router-link to="/company/drives" class="stat-card stat-card-link">
        <div class="stat-icon blue"><Users :size="20" /></div>
        <div>
          <div class="stat-value">{{ totalApplications }}</div>
          <div class="stat-label">Applications Received</div>
        </div>
      </router-link>
    </div>

    <div class="card-dark">
      <div class="d-flex justify-content-between align-items-center mb-3">
        <h3 class="section-title">Recent Drives</h3>
        <div class="d-flex gap-2">
          <button class="btn-outline-custom btn-sm" @click="exportCompanyCSV" :disabled="exporting">
            <span v-if="exporting" class="spinner-border spinner-border-sm me-1"></span>
            <Download v-else :size="20" /> {{ exporting ? 'Exporting...' : 'Export CSV' }}
          </button>
          <router-link to="/company/drives/new" class="btn-primary-custom btn-sm" v-if="authStore.profile?.is_approved">
            <Plus :size="20" /> New Drive
          </router-link>
        </div>
      </div>

      <div v-if="drives.length === 0" class="empty-state">
        <Megaphone :size="20" />
        <h3>No drives yet</h3>
        <p>Create your first placement drive</p>
      </div>

      <div v-else class="drive-list">
        <router-link
          v-for="drive in drives.slice(0, 5)"
          :key="drive.id"
          :to="drive.application_count > 0 ? `/company/drives/${drive.id}/applications` : '/company/drives'"
          class="drive-item"
        >
          <div class="drive-info">
            <div class="drive-title">{{ drive.title }}</div>
            <small class="text-muted">{{ drive.role_offered && drive.role_offered !== drive.title ? drive.role_offered + ' · ' : '' }}{{ formatDate(drive.deadline) }}</small>
          </div>
          <div class="drive-meta">
            <span :class="['badge-status', drive.is_approved ? 'badge-approved' : 'badge-pending']">
              {{ drive.is_approved ? 'Approved' : 'Pending' }}
            </span>
            <span class="app-count">{{ drive.application_count }} apps</span>
          </div>
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Megaphone, CheckCircle, Users, Plus, Clock, Download } from 'lucide-vue-next'
import { useAuthStore } from '../../stores/auth'
import { useToastStore } from '../../stores/toast'
import api from '../../api'
import { formatDate } from '../../utils/date'

const authStore = useAuthStore()
const toastStore = useToastStore()
const drives = ref([])
const exporting = ref(false)

const approvedDrives = computed(() => drives.value.filter(d => d.is_approved).length)
const totalApplications = computed(() => drives.value.reduce((sum, d) => sum + (d.application_count || 0), 0))

async function exportCompanyCSV() {
  exporting.value = true
  try {
    const res = await api.post('/company/applications/export')
    toastStore.success(res.data.message || 'Export started')
  } catch (err) {
    toastStore.danger(err.response?.data?.error || 'Export failed')
  } finally {
    exporting.value = false
  }
}

onMounted(async () => {
  try {
    const res = await api.get('/company/drives')
    drives.value = res.data.drives
  } catch (err) {
    console.error(err)
  }
})
</script>

<style scoped>
.alert-card {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  padding: 1.25rem;
  background: rgba(245, 158, 11, 0.1);
  border: 1px solid rgba(245, 158, 11, 0.3);
  border-radius: var(--border-radius);
  color: #fbbf24;
}
.alert-card i { font-size: 1.5rem; margin-top: 0.125rem; }
.alert-card p { margin: 0.25rem 0 0; font-size: 0.85rem; color: var(--text-secondary); }

.section-title { font-size: 1rem; font-weight: 600; margin: 0; }

.drive-list { display: flex; flex-direction: column; gap: 0.5rem; }

.drive-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.875rem 1rem;
  background: var(--bg-secondary);
  border-radius: var(--border-radius-sm);
  transition: var(--transition);
  text-decoration: none;
  color: inherit;
}
.drive-item:hover {
  background: var(--bg-card-hover);
  color: inherit;
}

.drive-title { font-weight: 600; font-size: 0.9rem; }

.drive-meta {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.app-count {
  font-size: 0.8rem;
  color: var(--text-muted);
}
</style>
