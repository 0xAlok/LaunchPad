<template>
  <div class="container py-4">
    <div class="page-header">
      <h1>Admin Dashboard</h1>
    </div>

    <div v-if="loading" class="loading-container">
      <div class="spinner"></div>
      <span>Loading analytics…</span>
    </div>

    <template v-else>
      <div class="stats-grid">
        <router-link to="/admin/students" class="stat-card stat-card-link">
          <div class="stat-icon purple"><Users :size="24" /></div>
          <div>
            <div class="stat-value">{{ analytics.summary?.total_students || 0 }}</div>
            <div class="stat-label">Students</div>
          </div>
        </router-link>
        <router-link to="/admin/companies" class="stat-card stat-card-link">
          <div class="stat-icon blue"><Building2 :size="24" /></div>
          <div>
            <div class="stat-value">{{ analytics.summary?.total_companies || 0 }}</div>
            <div class="stat-label">Companies</div>
          </div>
        </router-link>
        <router-link to="/admin/drives" class="stat-card stat-card-link">
          <div class="stat-icon green"><Megaphone :size="24" /></div>
          <div>
            <div class="stat-value">{{ analytics.summary?.total_drives || 0 }}</div>
            <div class="stat-label">Placement Drives</div>
          </div>
        </router-link>
        <div class="stat-card">
          <div class="stat-icon orange"><TrendingUp :size="24" /></div>
          <div>
            <div class="stat-value">{{ analytics.summary?.selection_rate || 0 }}%</div>
            <div class="stat-label">Selection Rate</div>
          </div>
        </div>
      </div>

      <div class="charts-grid">
        <div class="card-dark chart-card">
          <h3 class="chart-title">Applications by Status</h3>
          <div class="chart-wrapper chart-wrapper-doughnut">
            <canvas ref="statusChart"></canvas>
          </div>
        </div>
        <div class="card-dark chart-card">
          <h3 class="chart-title">Branch-wise Applications</h3>
          <div class="chart-wrapper">
            <canvas ref="branchChart"></canvas>
          </div>
        </div>
        <div class="card-dark chart-card">
          <h3 class="chart-title">Top Companies by Selections</h3>
          <div class="chart-wrapper">
            <canvas ref="topCompaniesChart"></canvas>
          </div>
        </div>
        <div class="card-dark chart-card">
          <h3 class="chart-title">Quick Stats</h3>
          <div class="quick-stats">
            <div class="quick-stat-row">
              <span>Total Applications</span>
              <span class="stat-num">{{ analytics.summary?.total_applications || 0 }}</span>
            </div>
            <div class="quick-stat-row">
              <span>Approved Companies</span>
              <span class="stat-num">{{ analytics.summary?.approved_companies || 0 }}</span>
            </div>
            <div class="quick-stat-row">
              <span>Active Drives</span>
              <span class="stat-num">{{ analytics.summary?.approved_drives || 0 }}</span>
            </div>
            
            <button 
              class="btn-outline-custom btn-sm mt-3 w-100" 
              @click="triggerReport"
              :disabled="reporting"
            >
              <FileText :size="18" /> 
              {{ reporting ? 'Generating...' : 'Generate Monthly Report' }}
            </button>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { Chart, registerables } from 'chart.js'
import { Users, Building2, Megaphone, TrendingUp, FileText } from 'lucide-vue-next'
import api from '../../api'
import { useToastStore } from '../../stores/toast'

Chart.register(...registerables)

const toastStore = useToastStore()
const loading = ref(true)
const reporting = ref(false)
const analytics = ref({})

async function triggerReport() {
  reporting.value = true
  try {
    const res = await api.post('/admin/reports/monthly')
    toastStore.success(res.data.message || 'Report generation started')
  } catch (err) {
    toastStore.danger(err.response?.data?.error || 'Failed to trigger report')
  } finally {
    reporting.value = false
  }
}
const statusChart = ref(null)
const branchChart = ref(null)
const topCompaniesChart = ref(null)
const chartInstances = []

onMounted(async () => {
  try {
    const res = await api.get('/admin/analytics')
    analytics.value = res.data
  } catch (err) {
    console.error('Failed to load analytics:', err)
  } finally {
    loading.value = false
  }

  if (Object.keys(analytics.value).length) {
    await nextTick()
    renderCharts()
  }
})

onBeforeUnmount(() => {
  chartInstances.forEach(c => c.destroy())
})

const chartDefaults = {
  color: '#9ca3af',
  gridColor: 'rgba(250, 248, 245, 0.06)',
}

function renderCharts() {
  const data = analytics.value

  if (statusChart.value && data.application_status) {
    const statuses = data.application_status
    chartInstances.push(new Chart(statusChart.value, {
      type: 'doughnut',
      data: {
        labels: Object.keys(statuses).map(s => s.charAt(0).toUpperCase() + s.slice(1)),
        datasets: [{
          data: Object.values(statuses),
          backgroundColor: ['#60a5fa', '#f59e0b', '#ef4444', '#34d399', '#a78bfa'],
          borderWidth: 0,
          hoverOffset: 6,
        }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: '65%',
        plugins: {
          legend: {
            position: 'bottom',
            labels: { color: chartDefaults.color, padding: 16, usePointStyle: true, pointStyleWidth: 10 },
          },
        },
      },
    }))
  }

  if (branchChart.value && data.branch_applications?.length) {
    const branchColors = ['#60a5fa', '#34d399', '#f59e0b', '#a78bfa', '#f87171', '#38bdf8']
    chartInstances.push(new Chart(branchChart.value, {
      type: 'bar',
      data: {
        labels: data.branch_applications.map(b => b.branch),
        datasets: [{
          label: 'Applications',
          data: data.branch_applications.map(b => b.count),
          backgroundColor: data.branch_applications.map((_, i) => branchColors[i % branchColors.length]),
          borderWidth: 0,
          borderRadius: 8,
          barPercentage: 0.6,
          categoryPercentage: 0.7,
        }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: { ticks: { color: chartDefaults.color }, grid: { display: false } },
          y: { ticks: { color: chartDefaults.color, stepSize: 1 }, grid: { color: chartDefaults.gridColor } },
        },
        plugins: { legend: { display: false } },
      },
    }))
  }

  if (topCompaniesChart.value && data.top_companies?.length) {
    const companyColors = ['#c9a84c', '#34d399', '#60a5fa', '#a78bfa', '#f59e0b']
    chartInstances.push(new Chart(topCompaniesChart.value, {
      type: 'bar',
      data: {
        labels: data.top_companies.map(c => c.name),
        datasets: [{
          label: 'Selections',
          data: data.top_companies.map(c => c.selections),
          backgroundColor: data.top_companies.map((_, i) => companyColors[i % companyColors.length]),
          borderWidth: 0,
          borderRadius: 8,
          barPercentage: 0.5,
        }],
      },
      options: {
        indexAxis: 'y',
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: { ticks: { color: chartDefaults.color, stepSize: 1 }, grid: { color: chartDefaults.gridColor } },
          y: { ticks: { color: chartDefaults.color }, grid: { display: false } },
        },
        plugins: { legend: { display: false } },
      },
    }))
  }
}
</script>

<style scoped>
.charts-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1.5rem;
}

@media (max-width: 768px) {
  .charts-grid {
    grid-template-columns: 1fr;
  }
}

.chart-card {
  display: flex;
  flex-direction: column;
}

.chart-card:hover {
  transform: none;
}

.chart-title {
  font-family: var(--font-heading);
  font-size: 1rem;
  font-weight: 600;
  margin-bottom: 1.25rem;
  color: var(--text-primary);
  letter-spacing: -0.01em;
}

.chart-wrapper {
  position: relative;
  height: 260px;
}

.chart-wrapper-doughnut {
  height: 280px;
}

.quick-stats {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding-top: 0.5rem;
}

.quick-stat-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.25rem;
  background: var(--bg-secondary);
  border-radius: var(--border-radius-sm);
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.stat-num {
  font-weight: 700;
  color: var(--accent-primary);
  font-size: 1.25rem;
}
</style>
