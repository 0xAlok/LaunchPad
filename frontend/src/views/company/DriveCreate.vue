<template>
  <div class="container py-4">
    <div class="page-header">
      <router-link to="/company/drives" class="back-link"><ArrowLeft :size="20" /> Back to Drives</router-link>
      <h1><Plus :size="20" /> Create Placement Drive</h1>
    </div>

    <div class="card-dark" style="max-width: 700px;">
      <form @submit.prevent="handleCreate" class="form-dark">
        <div class="mb-3">
          <label class="form-label" for="drive-title">Drive Title *</label>
          <input id="drive-title" v-model="form.title" class="form-control" required placeholder="e.g., Software Engineer — Batch 2026" />
        </div>

        <div class="mb-3">
          <label class="form-label" for="drive-role">Role Offered</label>
          <input id="drive-role" v-model="form.role_offered" class="form-control" placeholder="e.g., Backend Developer" />
        </div>

        <div class="row">
          <div class="col-md-6 mb-3">
            <label class="form-label" for="drive-package">Package (LPA)</label>
            <input id="drive-package" v-model="form.package_lpa" type="number" step="0.1" class="form-control" />
          </div>
          <div class="col-md-6 mb-3">
            <label class="form-label" for="drive-location">Location</label>
            <input id="drive-location" v-model="form.location" class="form-control" placeholder="e.g., Bangalore" />
          </div>
        </div>

        <div class="row">
          <div class="col-md-6 mb-3">
            <div class="d-flex align-items-center justify-content-between">
              <label class="form-label mb-0" for="drive-cgpa">Minimum CGPA</label>
              <label class="no-min-check">
                <input type="checkbox" v-model="noCgpaMin" @change="onNoCgpaToggle" />
                <span>No minimum</span>
              </label>
            </div>
            <input
              id="drive-cgpa"
              v-model="form.eligibility_cgpa"
              type="number"
              step="0.1"
              max="10"
              class="form-control mt-1"
              :disabled="noCgpaMin"
              :class="{ 'input-disabled': noCgpaMin }"
            />
          </div>
          <div class="col-md-6 mb-3">
            <label class="form-label" for="drive-deadline">Deadline *</label>
            <input id="drive-deadline" v-model="form.deadline" type="datetime-local" class="form-control" required />
          </div>
        </div>

        <div class="mb-3">
          <label class="form-label">Eligible Branches</label>
          <div class="branch-checkboxes">
            <label v-for="b in allBranches" :key="b.value" class="branch-check">
              <input type="checkbox" :value="b.value" v-model="form.eligible_branches" />
              <span>{{ b.label }}</span>
            </label>
          </div>
        </div>

        <div class="mb-3">
          <label class="form-label" for="drive-desc">Description</label>
          <textarea id="drive-desc" v-model="form.description" class="form-control" rows="4" placeholder="Job requirements, responsibilities, etc."></textarea>
        </div>

        <button type="submit" class="btn-primary-custom" :disabled="submitting">
          <span v-if="submitting" class="spinner-border spinner-border-sm"></span>
          <span v-else><Send :size="20" /> Submit for Approval</span>
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ArrowLeft, Plus, Send } from 'lucide-vue-next'
import api from '../../api'
import { useToastStore } from '../../stores/toast'

const router = useRouter()
const toastStore = useToastStore()
const submitting = ref(false)
const noCgpaMin = ref(false)

function onNoCgpaToggle() {
  if (noCgpaMin.value) {
    form.eligibility_cgpa = 0
  }
}

const allBranches = [
  { value: 'Computer Science', label: 'Computer Science' },
  { value: 'Electronics', label: 'Electronics' },
  { value: 'Mechanical', label: 'Mechanical' },
  { value: 'Electrical', label: 'Electrical' },
  { value: 'Civil', label: 'Civil' },
  { value: 'Data Science', label: 'Data Science' },
]

const form = reactive({
  title: '',
  role_offered: '',
  package_lpa: '',
  location: '',
  eligibility_cgpa: 0,
  deadline: '',
  eligible_branches: [],
  description: '',
})

async function handleCreate() {
  submitting.value = true
  try {
    const payload = {
      ...form,
      package_lpa: parseFloat(form.package_lpa) || 0,
      eligibility_cgpa: parseFloat(form.eligibility_cgpa) || 0,
    }
    if (payload.deadline) {
      payload.deadline = new Date(payload.deadline).toISOString()
    }
    await api.post('/company/drives', payload)
    toastStore.success('Drive created and submitted for approval!')
    router.push('/company/drives')
  } catch (err) {
    toastStore.danger(err.response?.data?.error || 'Failed to create drive')
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.back-link {
  font-size: 0.875rem;
  color: var(--text-secondary);
  margin-bottom: 0.5rem;
  display: inline-block;
}
.back-link:hover { color: var(--accent-primary); }

.branch-checkboxes {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
}
.branch-check {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  font-size: 0.875rem;
  color: var(--text-secondary);
  cursor: pointer;
}
.branch-check input { accent-color: var(--accent-primary); }

.no-min-check {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  font-size: 0.8rem;
  color: var(--text-secondary);
  cursor: pointer;
  user-select: none;
}
.no-min-check input { accent-color: var(--accent-primary); }

.input-disabled {
  opacity: 0.4;
  cursor: not-allowed;
}
</style>
