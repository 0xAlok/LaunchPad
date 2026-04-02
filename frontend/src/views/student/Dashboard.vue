<template>
  <div class="container py-4">
    <div class="page-header">
      <h1>Student Dashboard</h1>
      <p>Welcome back, {{ authStore.profile?.name || 'Student' }}</p>
    </div>

    <div class="stats-grid">
      <router-link to="/student/applications" class="stat-card stat-card-link">
        <div class="stat-icon purple"><FileText :size="20" /></div>
        <div>
          <div class="stat-value">{{ applications.length }}</div>
          <div class="stat-label">Applications</div>
        </div>
      </router-link>
      <router-link to="/student/applications" class="stat-card stat-card-link">
        <div class="stat-icon green"><CheckCircle :size="20" /></div>
        <div>
          <div class="stat-value">{{ selectedCount }}</div>
          <div class="stat-label">Selected</div>
        </div>
      </router-link>
      <router-link to="/student/applications" class="stat-card stat-card-link">
        <div class="stat-icon orange"><Timer :size="20" /></div>
        <div>
          <div class="stat-value">{{ pendingCount }}</div>
          <div class="stat-label">Pending</div>
        </div>
      </router-link>
      <router-link to="/student/applications" class="stat-card stat-card-link">
        <div class="stat-icon blue"><CalendarCheck :size="20" /></div>
        <div>
          <div class="stat-value">{{ interviewCount }}</div>
          <div class="stat-label">Interviews</div>
        </div>
      </router-link>
    </div>

    <div class="card-dark">
      <div class="d-flex justify-content-between align-items-center mb-3">
        <h3 class="section-title">Recent Applications</h3>
        <router-link to="/student/drives" class="btn-primary-custom btn-sm">
          <Search :size="20" /> Browse Drives
        </router-link>
      </div>

      <div v-if="applications.length === 0" class="empty-state">
        <Inbox :size="20" />
        <h3>No applications yet</h3>
        <p>Start by browsing available placement drives</p>
      </div>

      <div v-else class="app-list">
        <router-link v-for="app in applications.slice(0, 5)" :key="app.id" to="/student/applications" class="app-item">
          <div>
            <div class="app-title">{{ app.drive_title }}</div>
            <small class="text-muted">{{ app.company_name }} · Applied {{ formatDateShort(app.applied_at) }}</small>
          </div>
          <span :class="['badge-status', `badge-${app.status}`]">{{ app.status }}</span>
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '../../stores/auth'
import api from '../../api'
import { formatDateShort } from '../../utils/date'
import { FileText, CheckCircle, Timer, CalendarCheck, Search, Inbox } from 'lucide-vue-next'

const authStore = useAuthStore()
const applications = ref([])

const selectedCount = computed(() => applications.value.filter(a => a.status === 'selected').length)
const pendingCount = computed(() => applications.value.filter(a => ['applied', 'shortlisted'].includes(a.status)).length)
const interviewCount = computed(() => applications.value.filter(a => a.interview).length)

onMounted(async () => {
  try {
    const res = await api.get('/student/applications')
    applications.value = res.data.applications
  } catch (err) { console.error(err) }
})
</script>

<style scoped>
.section-title { font-size: 1rem; font-weight: 600; margin: 0; }
.app-list { display: flex; flex-direction: column; gap: 0.5rem; }
.app-item {
  display: flex; justify-content: space-between; align-items: center;
  padding: 0.875rem 1rem;
  background: var(--bg-secondary); border-radius: var(--border-radius-sm);
  transition: var(--transition);
  text-decoration: none; color: inherit; cursor: pointer;
}
.app-item:hover { background: var(--bg-card-hover); }
.app-title { font-weight: 600; font-size: 0.9rem; }
</style>
