import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useToastStore = defineStore('toast', () => {
  const toasts = ref([])
  let nextId = 0

  function show(message, type = 'info', duration = 4000) {
    const id = nextId++
    toasts.value.push({ id, message, type })
    setTimeout(() => {
      toasts.value = toasts.value.filter((t) => t.id !== id)
    }, duration)
  }

  function success(message) { show(message, 'success') }
  function danger(message) { show(message, 'danger') }
  function warning(message) { show(message, 'warning') }
  function info(message) { show(message, 'info') }

  return { toasts, show, success, danger, warning, info }
})
