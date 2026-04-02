<template>
  <div class="container py-4">
    <div class="page-header">
      <h1><Users :size="20" /> Student Management</h1>
    </div>

    <div class="search-bar mb-4 form-dark">
      <div class="input-group">
        <span class="input-group-text" style="background: var(--bg-input); border-color: var(--border-color); color: var(--text-muted);">
          <Search :size="20" />
        </span>
        <input
          v-model="search"
          type="text"
          class="form-control"
          placeholder="Search by name, contact, or education..."
          @input="debouncedFetch"
        />
      </div>
    </div>

    <div v-if="loading" class="loading-container"><div class="spinner"></div></div>

    <div v-else-if="students.length === 0" class="empty-state">
      <UserX :size="24" />
      <h3>No students found</h3>
    </div>

    <div v-else class="table-responsive">
      <table class="table table-dark-custom">
        <thead>
          <tr>
            <th>Name</th>
            <th>Contact No.</th>
            <th>Education</th>
            <th>CGPA</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="student in students" :key="student.id">
            <td><span class="fw-semibold">{{ student.name }}</span></td>
            <td>{{ student.phone || 'N/A' }}</td>
            <td>{{ student.branch }}</td>
            <td>{{ student.cgpa }}</td>
            <td>
              <span :class="['badge-status', student.active ? 'badge-approved' : 'badge-rejected']" class="me-1">
                {{ student.active ? 'Active' : 'Deactivated' }}
              </span>
              <span v-if="student.is_blacklisted" class="badge-status badge-rejected">
                Blacklisted
              </span>
            </td>
            <td>
              <div class="d-flex gap-2">
                <button class="btn-danger-custom btn-sm" @click="toggleBlacklist(student.id)">
                  <Ban :size="20" />
                  {{ student.is_blacklisted ? 'Unblock' : 'Blacklist' }}
                </button>
                <button class="btn-outline-custom btn-sm" @click="toggleDeactivate(student.id)">
                  <Power :size="20" />
                  {{ student.active ? 'Deactivate' : 'Activate' }}
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
import { ref, onMounted } from 'vue'
import { Users, Search, UserX, Ban, Power } from 'lucide-vue-next'
import api from '../../api'
import { useToastStore } from '../../stores/toast'

const toastStore = useToastStore()
const students = ref([])
const loading = ref(true)
const search = ref('')
let debounceTimer = null

async function fetchStudents() {
  loading.value = true
  try {
    const params = search.value ? { search: search.value } : {}
    const res = await api.get('/admin/students', { params })
    students.value = res.data.students
  } catch { toastStore.danger('Failed to load students') }
  finally { loading.value = false }
}

function debouncedFetch() {
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(fetchStudents, 300)
}

async function toggleBlacklist(id) {
  try {
    await api.put(`/admin/students/${id}/blacklist`)
    toastStore.info('Blacklist status updated')
    fetchStudents()
  } catch { toastStore.danger('Action failed') }
}

async function toggleDeactivate(id) {
  try {
    await api.put(`/admin/students/${id}/deactivate`)
    toastStore.info('Active status updated')
    fetchStudents()
  } catch { toastStore.danger('Action failed') }
}

onMounted(fetchStudents)
</script>
