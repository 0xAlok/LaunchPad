<template>
  <div class="container py-4">
    <div class="page-header d-flex justify-content-between align-items-center">
      <div>
        <h1><Megaphone :size="20" /> My Drives</h1>
      </div>
      <router-link v-if="authStore.profile?.is_approved" to="/company/drives/new" class="btn-primary-custom">
        <Plus :size="20" /> New Drive
      </router-link>
    </div>

    <div v-if="loading" class="loading-container"><div class="spinner"></div></div>

    <div v-else-if="allDrives.length === 0" class="empty-state">
      <Megaphone :size="20" />
      <h3>No drives yet</h3>
      <p>Create your first placement drive to start recruiting</p>
    </div>

    <template v-else>
      <div v-if="activeDrives.length" class="drives-grid">
        <div v-for="drive in activeDrives" :key="drive.id" class="card-dark drive-card">
          <div class="d-flex justify-content-between align-items-start mb-2">
            <h3 class="drive-card-title">{{ drive.title }}</h3>
            <div class="d-flex align-items-center gap-2">
              <span v-if="drive.is_approved" class="badge-status badge-approved">Approved</span>
              <span v-else-if="drive.application_count > 0" class="badge-status badge-rejected">Revoked</span>
              <span v-else class="badge-status badge-pending">Pending</span>
            </div>
          </div>
          <p v-if="drive.role_offered && drive.role_offered !== drive.title" class="drive-role">{{ drive.role_offered }}</p>
          <div class="drive-details">
            <span><IndianRupee :size="14" /> {{ drive.package_lpa ? `₹${drive.package_lpa} LPA` : '—' }}</span>
            <span><MapPin :size="14" /> {{ drive.location || '—' }}</span>
            <span><CalendarDays :size="14" /> {{ formatDate(drive.deadline) }}</span>
          </div>
          <div class="drive-footer">
            <span class="app-count"><Users :size="14" /> {{ drive.application_count }} applications</span>
          </div>
          <div class="drive-actions">
            <router-link
              v-if="drive.application_count > 0"
              :to="`/company/drives/${drive.id}/applications`"
              class="btn-primary-custom btn-sm"
            >
              View Applications
            </router-link>
            <button
              v-if="drive.status === 'open' && drive.is_approved"
              class="btn-outline-custom btn-sm"
              @click="editDrive = { ...drive }; showEditModal = true"
            >
              <Pencil :size="14" /> Edit
            </button>
            <button
              v-if="drive.status === 'open' && drive.is_approved"
              class="btn-danger-custom btn-sm"
              @click="closeDrive(drive.id)"
            >
              <XCircle :size="14" /> Close Drive
            </button>
          </div>
        </div>
      </div>

      <div v-if="pastDrives.length" class="mt-4">
        <h2 class="section-title"><Archive :size="18" /> Past Drives</h2>
        <div class="drives-grid mt-3">
          <div v-for="drive in pastDrives" :key="drive.id" class="card-dark drive-card past-drive">
            <div class="d-flex justify-content-between align-items-start mb-2">
              <h3 class="drive-card-title">{{ drive.title }}</h3>
              <span class="badge-status badge-closed">Closed</span>
            </div>
            <p v-if="drive.role_offered && drive.role_offered !== drive.title" class="drive-role">{{ drive.role_offered }}</p>
            <div class="drive-details">
              <span><IndianRupee :size="14" /> {{ drive.package_lpa ? `₹${drive.package_lpa} LPA` : '—' }}</span>
              <span><MapPin :size="14" /> {{ drive.location || '—' }}</span>
              <span><CalendarDays :size="14" /> {{ formatDate(drive.deadline) }}</span>
            </div>
            <div class="drive-footer">
              <span class="app-count"><Users :size="14" /> {{ drive.application_count }} applications</span>
            </div>
            <div class="drive-actions">
              <router-link
                v-if="drive.application_count > 0"
                :to="`/company/drives/${drive.id}/applications`"
                class="btn-primary-custom btn-sm"
              >
                View Applications
              </router-link>
              <button class="btn-success-custom btn-sm" @click="reopenDrive(drive.id)">
                <RotateCcw :size="14" /> Reopen
              </button>
            </div>
          </div>
        </div>
      </div>
    </template>
    <div v-if="showEditModal" class="modal-overlay" @click.self="showEditModal = false">
      <div class="modal-card card-dark">
        <h3>Edit Drive</h3>
        <form @submit.prevent="saveEdit" class="form-dark mt-3">
          <div class="mb-3">
            <label class="form-label">Title *</label>
            <input v-model="editDrive.title" class="form-control" required />
          </div>
          <div class="mb-3">
            <label class="form-label">Role Offered</label>
            <input v-model="editDrive.role_offered" class="form-control" />
          </div>
          <div class="row">
            <div class="col-6 mb-3">
              <label class="form-label">Package (LPA)</label>
              <input v-model="editDrive.package_lpa" type="number" step="0.1" class="form-control" />
            </div>
            <div class="col-6 mb-3">
              <label class="form-label">Location</label>
              <input v-model="editDrive.location" class="form-control" />
            </div>
          </div>
          <div class="mb-3">
            <label class="form-label">Description</label>
            <textarea v-model="editDrive.description" class="form-control" rows="3"></textarea>
          </div>
          <div class="d-flex gap-2">
            <button type="submit" class="btn-primary-custom btn-sm" :disabled="saving">
              Save
            </button>
            <button type="button" class="btn-outline-custom btn-sm" @click="showEditModal = false">
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Megaphone, Plus, IndianRupee, MapPin, CalendarDays, Users, Pencil, XCircle, RotateCcw, Archive } from 'lucide-vue-next'
import api from '../../api'
import { useAuthStore } from '../../stores/auth'
import { useToastStore } from '../../stores/toast'
import { formatDate } from '../../utils/date'

const authStore = useAuthStore()
const toastStore = useToastStore()
const allDrives = ref([])
const loading = ref(true)
const showEditModal = ref(false)
const editDrive = ref({})
const saving = ref(false)
const activeDrives = computed(() => allDrives.value.filter(d => d.status !== 'closed'))
const pastDrives = computed(() => allDrives.value.filter(d => d.status === 'closed'))

async function fetchDrives() {
  loading.value = true
  try {
    const res = await api.get('/company/drives')
    allDrives.value = res.data.drives
  } catch { toastStore.danger('Failed to load drives') }
  finally { loading.value = false }
}

async function closeDrive(id) {
  try {
    await api.put(`/company/drives/${id}`, { status: 'closed' })
    toastStore.success('Drive closed')
    fetchDrives()
  } catch { toastStore.danger('Failed to close drive') }
}

async function reopenDrive(id) {
  try {
    await api.put(`/company/drives/${id}`, { status: 'open' })
    toastStore.success('Drive reopened')
    fetchDrives()
  } catch { toastStore.danger('Failed to reopen drive') }
}

async function saveEdit() {
  saving.value = true
  try {
    await api.put(`/company/drives/${editDrive.value.id}`, {
      title: editDrive.value.title,
      role_offered: editDrive.value.role_offered,
      package_lpa: editDrive.value.package_lpa,
      location: editDrive.value.location,
      description: editDrive.value.description,
    })
    toastStore.success('Drive updated')
    showEditModal.value = false
    fetchDrives()
  } catch { toastStore.danger('Failed to update drive') }
  finally { saving.value = false }
}

onMounted(fetchDrives)
</script>

<style scoped>
.drives-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
  gap: 1rem;
}
.drive-card { display: flex; flex-direction: column; }
.drive-card-title { font-size: 1.05rem; font-weight: 700; margin: 0; }
.drive-role { color: var(--text-secondary); font-size: 0.9rem; margin-bottom: 0.75rem; }
.drive-details {
  display: flex; flex-wrap: wrap; gap: 1rem;
  font-size: 0.85rem; color: var(--text-muted);
  margin-bottom: 1rem;
}
.drive-details i { margin-right: 0.25rem; }
.drive-footer {
  margin-top: auto;
  padding-top: 0.75rem;
  border-top: 1px solid var(--border-color);
}
.app-count { font-size: 0.85rem; color: var(--text-secondary); display: flex; align-items: center; gap: 0.25rem; }

.drive-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 0.75rem;
}

.modal-overlay {
  position: fixed; top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.6); display: flex; align-items: center; justify-content: center;
  z-index: 2000;
}
.modal-card { width: 100%; max-width: 500px; }
.section-title { font-size: 1.1rem; font-weight: 700; display: flex; align-items: center; gap: 0.5rem; }
.past-drive { opacity: 0.7; }
</style>
