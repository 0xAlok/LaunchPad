<template>
  <div class="container py-4">
    <div class="page-header d-flex flex-column flex-md-row justify-content-between align-items-md-center">
      <div class="mb-3 mb-md-0">
        <h1><Building2 :size="20" /> Company Management</h1>
      </div>
      <div class="d-flex flex-column flex-sm-row gap-3">
        <div class="input-group" style="max-width: 250px;">
          <input v-model="searchQuery" @keyup.enter="fetchCompanies" type="text" class="form-control" placeholder="Search..." />
          <button class="btn-primary-custom px-3" @click="fetchCompanies"><Search :size="20" /></button>
        </div>
        <div class="filter-group">
          <button :class="['btn-outline-custom btn-sm', { active: filter === '' }]" @click="filter = ''">All</button>
          <button :class="['btn-outline-custom btn-sm', { active: filter === 'pending' }]" @click="filter = 'pending'">Pending</button>
          <button :class="['btn-outline-custom btn-sm', { active: filter === 'approved' }]" @click="filter = 'approved'">Approved</button>
          <button :class="['btn-outline-custom btn-sm', { active: filter === 'blacklisted' }]" @click="filter = 'blacklisted'">Blacklisted</button>
        </div>
      </div>
    </div>

    <div v-if="loading" class="loading-container">
      <div class="spinner"></div>
    </div>

    <div v-else-if="companies.length === 0" class="empty-state">
      <Building2 :size="24" />
      <h3>No companies found</h3>
      <p>No companies match the current filter</p>
    </div>

    <div v-else class="table-responsive">
      <table class="table table-dark-custom">
        <thead>
          <tr>
            <th>Company</th>
            <th>Industry</th>
            <th>Email</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="company in companies" :key="company.id">
            <td>
              <div class="company-name">{{ company.name }}</div>
              <small class="text-muted">{{ company.website }}</small>
            </td>
            <td>{{ company.industry || '—' }}</td>
            <td>{{ company.email }}</td>
            <td>
              <span v-if="!company.active" class="badge-status badge-rejected me-1">Deactivated</span>
              <span v-if="company.is_blacklisted" class="badge-status badge-rejected">Blacklisted</span>
              <span v-else-if="company.is_approved" class="badge-status badge-approved">Approved</span>
              <span v-else class="badge-status badge-pending">Pending</span>
            </td>
            <td>
              <div class="action-btns">
                <button
                  v-if="!company.is_approved && !company.is_blacklisted"
                  class="btn-success-custom btn-sm"
                  @click="approveCompany(company.id)"
                >
                  <Check :size="20" /> Approve
                </button>
                <button
                  v-if="!company.is_blacklisted && company.is_approved"
                  class="btn-outline-custom btn-sm"
                  @click="rejectCompany(company.id)"
                >
                  <X :size="20" /> Reject
                </button>
                <button
                  class="btn-danger-custom btn-sm"
                  @click="toggleBlacklist(company.id)"
                >
                  <Ban :size="20" />
                  {{ company.is_blacklisted ? 'Unblock' : 'Blacklist' }}
                </button>
                <button
                  class="btn-outline-custom btn-sm"
                  @click="toggleDeactivate(company.id)"
                >
                  <Power :size="20" />
                  {{ company.active ? 'Deactivate' : 'Activate' }}
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { Building2, Search, Check, X, Ban, Power } from 'lucide-vue-next'
import api from '../../api'
import { useToastStore } from '../../stores/toast'

const toastStore = useToastStore()
const companies = ref([])
const loading = ref(true)
const filter = ref('')
const searchQuery = ref('')

async function fetchCompanies() {
  loading.value = true
  try {
    const params = {}
    if (filter.value) params.status = filter.value
    if (searchQuery.value) params.search = searchQuery.value

    const res = await api.get('/admin/companies', { params })
    companies.value = res.data.companies
  } catch (err) {
    toastStore.danger('Failed to load companies')
  } finally {
    loading.value = false
  }
}

async function approveCompany(id) {
  try {
    await api.put(`/admin/companies/${id}/approve`)
    toastStore.success('Company approved')
    fetchCompanies()
  } catch { toastStore.danger('Action failed') }
}

async function rejectCompany(id) {
  try {
    await api.put(`/admin/companies/${id}/reject`)
    toastStore.warning('Company rejected')
    fetchCompanies()
  } catch { toastStore.danger('Action failed') }
}

async function toggleBlacklist(id) {
  try {
    await api.put(`/admin/companies/${id}/blacklist`)
    toastStore.info('Blacklist status updated')
    fetchCompanies()
  } catch { toastStore.danger('Action failed') }
}

async function toggleDeactivate(id) {
  try {
    await api.put(`/admin/companies/${id}/deactivate`)
    toastStore.info('Active status updated')
    fetchCompanies()
  } catch { toastStore.danger('Action failed') }
}

watch(filter, fetchCompanies)
onMounted(fetchCompanies)
</script>

<style scoped>
.filter-group {
  display: flex;
  gap: 0.5rem;
}

.filter-group .btn-outline-custom.active {
  border-color: var(--accent-primary);
  background: rgba(99, 102, 241, 0.15);
  color: var(--accent-primary);
}

.company-name {
  font-weight: 600;
  color: var(--text-primary);
}

.action-btns {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}
</style>
