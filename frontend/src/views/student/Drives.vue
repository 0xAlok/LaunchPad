<template>
  <div class="container py-4">
    <div class="page-header">
      <h1><Search :size="20" /> Browse Drives</h1>
    </div>

    <!-- Filters -->
    <div class="filter-bar card-dark mb-4 form-dark">
      <div class="row g-3 align-items-end">
        <div class="col-md-4">
          <label class="form-label">Search</label>
          <input v-model="filters.search" class="form-control" placeholder="Search by title, role, or company..." />
        </div>
        <div class="col-md-3">
          <label class="form-label">Branch</label>
          <select v-model="filters.branch" class="form-select">
            <option value="">All Branches</option>
            <option value="Computer Science">Computer Science</option>
            <option value="Electronics">Electronics</option>
            <option value="Mechanical">Mechanical</option>
            <option value="Electrical">Electrical</option>
            <option value="Civil">Civil</option>
            <option value="Data Science">Data Science</option>
          </select>
        </div>
        <div class="col-md-3">
          <label class="form-label">Min Package (LPA)</label>
          <input v-model="filters.min_package" type="number" step="0.5" class="form-control" placeholder="e.g., 5" />
        </div>
        <div class="col-md-2">
          <button class="btn-primary-custom w-100" @click="fetchDrives">
            <Filter :size="20" /> Filter
          </button>
        </div>
      </div>
    </div>

    <div v-if="!hasResume" class="alert-banner mb-3">
      <FileWarning :size="16" /> You must upload your resume before applying. Go to <router-link to="/student/profile">Profile</router-link> to upload.
    </div>

    <div v-if="loading" class="loading-container"><div class="spinner"></div></div>

    <div v-else-if="drives.length === 0" class="empty-state">
      <Search :size="20" />
      <h3>No drives found</h3>
      <p>Try adjusting your filters or check back later</p>
    </div>

    <div v-else class="drives-grid">
      <div v-for="drive in drives" :key="drive.id" class="card-dark drive-card">
        <div class="d-flex justify-content-between align-items-start mb-2">
          <div>
            <h3 class="drive-title">{{ drive.title }}</h3>
            <p class="company-tag"><Building2 :size="20" /> {{ drive.company_name }}</p>
          </div>
          <span :class="['badge-status', drive.already_applied ? 'badge-applied' : 'badge-open']">
            {{ drive.already_applied ? 'Applied' : 'Open' }}
          </span>
        </div>

        <p v-if="drive.role_offered && drive.role_offered !== drive.title" class="drive-role">{{ drive.role_offered }}</p>

        <div class="drive-details">
          <span><Banknote :size="20" /> {{ drive.package_lpa ? `₹${drive.package_lpa} LPA` : '—' }}</span>
          <span><MapPin :size="20" /> {{ drive.location || '—' }}</span>
          <span><BarChart3 :size="20" /> Min CGPA: {{ drive.eligibility_cgpa || 0 }}</span>
          <span><Calendar :size="20" /> Deadline: {{ formatDate(drive.deadline) }}</span>
          <span v-if="drive.ats_preview"><Gauge :size="20" /> Match: {{ drive.ats_preview }}%</span>
        </div>

        <p v-if="drive.description" class="drive-desc">{{ truncate(drive.description, 150) }}</p>

        <div class="drive-footer">
          <div class="branch-tags">
            <span
              v-for="branch in drive.eligible_branches?.filter(b => b)"
              :key="branch"
              class="branch-tag"
            >{{ branch }}</span>
            <span v-if="!drive.eligible_branches?.length" class="branch-tag">All Branches</span>
          </div>
          <button
            v-if="!drive.already_applied"
            :disabled="!hasResume"
            class="btn-primary-custom btn-sm"
            @click="applyToDrive(drive.id)"
          >
            <Send :size="20" /> Apply
          </button>
          <span v-else class="applied-text"><CheckCircle :size="20" /> Applied</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import api from '../../api'
import { useToastStore } from '../../stores/toast'
import { formatDate } from '../../utils/date'
import { Search, Filter, Building2, Banknote, MapPin, BarChart3, Calendar, Send, CheckCircle, Gauge, FileWarning } from 'lucide-vue-next'

const toastStore = useToastStore()
const drives = ref([])
const loading = ref(true)
const filters = reactive({ search: '', branch: '', min_package: '' })
const hasResume = ref(true)

function truncate(str, len) {
  return str && str.length > len ? str.substring(0, len) + '…' : str
}

async function fetchDrives() {
  loading.value = true
  try {
    const params = {}
    if (filters.search) params.search = filters.search
    if (filters.branch) params.branch = filters.branch
    if (filters.min_package) params.min_package = filters.min_package

    const res = await api.get('/student/drives', { params })
    drives.value = res.data.drives
    hasResume.value = res.data.has_resume !== false
  } catch { toastStore.danger('Failed to load drives') }
  finally { loading.value = false }
}

async function applyToDrive(driveId) {
  try {
    await api.post(`/student/apply/${driveId}`, {})
    toastStore.success('Application submitted!')
    fetchDrives()
  } catch (err) {
    toastStore.danger(err.response?.data?.error || 'Application failed')
  }
}

onMounted(fetchDrives)
</script>

<style scoped>
.drives-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(380px, 1fr)); gap: 1rem; }
.drive-card { display: flex; flex-direction: column; }
.drive-title { font-size: 1.05rem; font-weight: 700; margin: 0; }
.company-tag { color: var(--accent-secondary); font-size: 0.85rem; margin: 0.25rem 0 0; }
.company-tag svg { margin-right: 0.25rem; vertical-align: middle; }
.drive-role { color: var(--text-secondary); font-size: 0.9rem; margin-bottom: 0.75rem; }
.drive-details {
  display: flex; flex-wrap: wrap; gap: 0.75rem;
  font-size: 0.85rem; color: var(--text-muted); margin-bottom: 0.75rem;
}
.drive-details svg { margin-right: 0.25rem; vertical-align: middle; }
.drive-desc { font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 0.75rem; }
.drive-footer {
  display: flex; justify-content: space-between; align-items: center;
  margin-top: auto; padding-top: 0.75rem; border-top: 1px solid var(--border-color);
}
.branch-tags { display: flex; gap: 0.375rem; flex-wrap: wrap; }
.branch-tag {
  background: rgba(99, 102, 241, 0.1); color: var(--accent-primary);
  padding: 0.125rem 0.5rem; border-radius: 50px; font-size: 0.7rem; font-weight: 600;
}
.applied-text { color: var(--accent-success); font-size: 0.85rem; font-weight: 600; }
.alert-banner {
  background: rgba(220, 38, 38, 0.1); border: 1px solid rgba(220, 38, 38, 0.3);
  color: #ef4444; padding: 0.75rem 1rem; border-radius: var(--border-radius-sm, 0.5rem);
  font-size: 0.9rem; font-weight: 600; display: flex; align-items: center; gap: 0.5rem;
}
.alert-banner a { color: var(--accent-primary); text-decoration: underline; }
</style>
