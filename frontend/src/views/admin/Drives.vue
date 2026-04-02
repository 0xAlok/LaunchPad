<template>
  <div class="container py-4">
    <div class="page-header d-flex justify-content-between align-items-center">
      <div>
        <h1><Megaphone :size="20" /> Drive Management</h1>
      </div>
      <div class="filter-group">
        <button :class="['btn-outline-custom btn-sm', { active: filter === '' }]" @click="filter = ''">All</button>
        <button :class="['btn-outline-custom btn-sm', { active: filter === 'pending' }]" @click="filter = 'pending'">Pending</button>
        <button :class="['btn-outline-custom btn-sm', { active: filter === 'approved' }]" @click="filter = 'approved'">Approved</button>
      </div>
    </div>

    <div v-if="loading" class="loading-container"><div class="spinner"></div></div>

    <div v-else-if="drives.length === 0" class="empty-state">
      <Megaphone :size="24" />
      <h3>No drives found</h3>
    </div>

    <div v-else class="table-responsive">
      <table class="table table-dark-custom">
        <thead>
          <tr>
            <th>Title</th>
            <th>Company</th>
            <th>Location</th>
            <th>Package</th>
            <th>Deadline</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <template v-for="drive in drives" :key="drive.id">
          <tr>
            <td>
              <div class="drive-title">{{ drive.title }}</div>
              <small v-if="drive.role_offered && drive.role_offered !== drive.title" class="text-muted">{{ drive.role_offered }}</small>
            </td>
            <td>{{ drive.company_name }}</td>
            <td>{{ drive.location || '—' }}</td>
            <td>{{ drive.package_lpa ? `₹${drive.package_lpa} LPA` : '—' }}</td>
            <td>{{ formatDate(drive.deadline) }}</td>
            <td>
              <span :class="['badge-status', drive.is_approved ? 'badge-approved' : 'badge-pending']">
                {{ drive.is_approved ? 'Approved' : 'Pending' }}
              </span>
            </td>
            <td>
              <div class="action-btns">
                <button class="btn-outline-custom btn-sm" @click="toggleDetails(drive)" title="View Details">
                  <Info :size="14" /> View
                </button>
                <button v-if="!drive.is_approved" class="btn-success-custom btn-sm" @click="approveDrive(drive.id)">
                  <Check :size="14" /> Approve
                </button>
                <button v-if="!drive.is_approved" class="btn-danger-custom btn-sm" @click="rejectDrive(drive.id)">
                  <X :size="14" /> Reject
                </button>
                <button v-if="drive.is_approved" class="btn-danger-custom btn-sm" @click="rejectDrive(drive.id)">
                  <X :size="14" /> Revoke
                </button>
              </div>
            </td>
          </tr>
          <tr v-if="drive.showDetails" class="details-row">
            <td colspan="7">
              <div class="detail-panel">
                <div class="detail-grid">
                  <div class="detail-item">
                    <span class="detail-label">Role Offered</span>
                    <span class="detail-value">{{ drive.role_offered || '—' }}</span>
                  </div>
                  <div class="detail-item">
                    <span class="detail-label">Minimum CGPA</span>
                    <span class="detail-value">{{ drive.eligibility_cgpa ? drive.eligibility_cgpa : 'No minimum' }}</span>
                  </div>
                  <div class="detail-item">
                    <span class="detail-label">Eligible Branches</span>
                    <div class="branch-pills" v-if="drive.eligible_branches?.length">
                      <span v-for="branch in drive.eligible_branches" :key="branch" class="branch-pill">{{ branch }}</span>
                    </div>
                    <span v-else class="detail-value">All Branches</span>
                  </div>
                </div>
                <div class="detail-desc" v-if="drive.description">
                  <span class="detail-label">Description</span>
                  <p class="detail-value" style="white-space: pre-wrap;">{{ drive.description }}</p>
                </div>
              </div>
            </td>
          </tr>
          </template>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { Megaphone, Info, Check, X } from 'lucide-vue-next'
import api from '../../api'
import { useToastStore } from '../../stores/toast'
import { formatDate } from '../../utils/date'

const toastStore = useToastStore()
const drives = ref([])
const loading = ref(true)
const filter = ref('')

function toggleDetails(drive) {
  drive.showDetails = !drive.showDetails
}

async function fetchDrives() {
  loading.value = true
  try {
    const params = filter.value ? { status: filter.value } : {}
    const res = await api.get('/admin/drives', { params })
    drives.value = res.data.drives.map(d => ({ ...d, showDetails: false }))
  } catch { toastStore.danger('Failed to load drives') }
  finally { loading.value = false }
}

async function approveDrive(id) {
  try {
    await api.put(`/admin/drives/${id}/approve`)
    toastStore.success('Drive approved')
    fetchDrives()
  } catch { toastStore.danger('Action failed') }
}

async function rejectDrive(id) {
  try {
    await api.put(`/admin/drives/${id}/reject`)
    toastStore.warning('Drive rejected')
    fetchDrives()
  } catch { toastStore.danger('Action failed') }
}

watch(filter, fetchDrives)
onMounted(fetchDrives)
</script>

<style scoped>
.filter-group { display: flex; gap: 0.5rem; }
.filter-group .btn-outline-custom.active {
  border-color: var(--accent-primary);
  background: rgba(99, 102, 241, 0.15);
  color: var(--accent-primary);
}
.drive-title { font-weight: 600; color: var(--text-primary); }

.action-btns { display: flex; gap: 0.5rem; align-items: center; }
.action-btns button {
  padding: 0.375rem 0.875rem !important;
  font-size: 0.8rem !important;
}

:deep(.table-dark-custom thead th) {
  text-align: center;
}
:deep(.table-dark-custom thead th:first-child) {
  text-align: left;
}
.details-row td { border-top: none; padding-top: 0; padding-bottom: 1rem; }

.detail-panel {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-sm);
  padding: 1.25rem;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
  margin-bottom: 1rem;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.detail-label {
  font-size: 0.7rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--text-secondary);
}

.detail-value {
  font-size: 0.9rem;
  color: var(--text-primary);
}

.branch-pills {
  display: flex;
  flex-wrap: wrap;
  gap: 0.375rem;
}

.branch-pill {
  background: rgba(201, 168, 76, 0.1);
  color: var(--accent-primary);
  padding: 0.125rem 0.625rem;
  border-radius: 50px;
  font-size: 0.75rem;
  font-weight: 600;
}

.detail-desc {
  border-top: 1px solid var(--border-color);
  padding-top: 1rem;
}

.detail-desc p {
  margin: 0.25rem 0 0;
}
</style>
