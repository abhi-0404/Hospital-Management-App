<template>
  <div :class="`toast-notification ${type}`">
    {{ message }}
  </div>
</template>

<script setup>
import { onMounted, onUnmounted } from 'vue'

const props = defineProps({
  message: String,
  type: String // 'success' or 'danger'
})

const emit = defineEmits(['close'])

let timer = null

// When the component is created, start a 3-second timer
onMounted(() => {
  timer = setTimeout(() => {
    emit('close')
  }, 3000) // 3000ms = 3 seconds
})

// Clear the timer if the component is destroyed early
onUnmounted(() => {
  clearTimeout(timer)
})
</script>

<style scoped>
/* Positions the toast in the top-right corner */
.toast-notification {
  position: fixed;
  top: 20px;
  right: 20px;
  padding: 1rem 1.5rem;
  border-radius: 0.5rem;
  font-weight: 600;
  
  /* --- *** CHANGED THIS LINE *** --- */
  /* Was 1000, changed to 2000 (must be > 1020) */
  z-index: 2000; 

  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  
  /* Added for frosted glass effect */
  backdrop-filter: blur(10px);

  /* Animation to slide in from the right */
  animation: slideIn 0.3s ease-out;

  /* Set a minimum width */
  min-width: 300px;
}

.toast-notification.success {
  /* Light, transparent green */
  background-color: rgba(209, 231, 221, 0.85); 
  color: #0f5132;
  border: 1px solid rgba(186, 220, 204, 0.9);
}

.toast-notification.danger {
  /* Light, transparent red */
  background-color: rgba(248, 215, 218, 0.85); 
  color: #842029;
  border: 1px solid rgba(245, 194, 199, 0.9);
}


@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}
</style>