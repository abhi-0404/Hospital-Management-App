<template>
  <div class="hero-bg-admin">
    <ToastNotification 
      v-if="toast"
      :message="toast.message" 
      :type="toast.type"
      @close="toast = null"
    />
    
    <nav class="top-nav">
      <div class="container-fluid d-flex align-items-center">
        <div class="left-actions d-flex align-items-center justify-content-start" style="flex: 1;">
            <span class="nav-title ms-2">Admin Dashboard</span>
        </div>
        <div class="nav-center d-flex align-items-center justify-content-center">
          <img :src="logo" alt="logo" class="logo-img" />
        </div>
        <div class="right-actions d-flex align-items-center justify-content-end" style="flex:1">
          <span class="user-name me-3">Welcome, {{ user?.name || 'Admin' }}</span>
          <button @click="$emit('logout')" class="logout-btn ms-2">Logout</button>
        </div>
      </div>
    </nav>

    <main class="container-fluid mt-4 admin-content admin-main-content">
      
      <div class="row justify-content-center">
        <div class="col-lg-8">
          <div class="card shadow-sm">
            <div class="card-header d-flex justify-content-between align-items-center">
              <h5 class="mb-0">Create New Doctor</h5>
              <button class="back-btn" @click="$emit('back')">
                &larr; Back to Dashboard
              </button>
            </div>
            <div class="card-body">
              <form @submit.prevent="handleCreateDoctor">
                <div class="mb-3">
                  <label for="docName" class="form-label">Full Name</label>
                  <input type="text" class="form-control" id="docName" v-model="doctor.name" required>
                </div>
                
                <div class="mb-3">
                  <label for="docEmail" class="form-label">Email Address</label>
                  <input type="email" class="form-control" id="docEmail" v-model="doctor.email" required>
                </div>
                
                <div class="mb-3">
                  <label for="docPassword" class="form-label">Temporary Password</label>
                  <input type="password" class="form-control" id="docPassword" v-model="doctor.password" required>
                </div>
                
                <div class="mb-3">
                  <label for="docDept" class="form-label">Department</label>
                  <select class="form-select" id="docDept" v-model="doctor.department_id" required>
                    <option :value="null" disabled>Select a department...</option>
                    <option v-for="dept in departments" :key="dept.id" :value="dept.id">
                      {{ dept.name }}
                    </option>
                  </select>
                </div>

                <hr class="my-4">
                
                <button type="submit" class="btn btn-create btn-lg">Create Doctor</button>
              </form>
            </div>
          </div>
        </div>
      </div>
      
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import logo from '../assets/Logo.png'
import ToastNotification from './ToastNotification.vue'

const props = defineProps({ user: Object })
const emit = defineEmits(['back', 'logout'])

// Holds the new doctor's form data
const doctor = ref({
  name: '',
  email: '',
  password: '',
  department_id: null
})

const departments = ref([]) // To populate the dropdown
const toast = ref(null)

// --- API Helper (copied from AdminDashboard) ---
async function fetchApi(endpoint, options = {}) {
  const token = localStorage.getItem('token')
  const headers = { 'Content-Type': 'application/json', ...(options.headers || {}) }
  if (token) headers['Authorization'] = `Bearer ${token}`

  const response = await fetch(`http://127.0.0.1:8000${endpoint}`, {
    ...options,
    headers,
  })

  let data = null
  try { data = await response.json() } catch (e) { data = null }
  
  if (!response.ok) {
    if (response.status === 401) emit('logout');
    throw new Error((data && data.message) || response.statusText || 'API error')
  }
  return data
}

// --- Fetch departments on page load ---
onMounted(() => {
  getDepartments();
});

async function getDepartments() {
  try {
    // We can get the department list from the main admin dashboard endpoint
    const data = await fetchApi('/api/admin/dashboard');
    departments.value = data.departments;
    // Set a default selection if list is not empty
    if (data.departments.length > 0) {
      doctor.value.department_id = data.departments[0].id;
    }
  } catch (e) {
    toast.value = { message: `Failed to load departments: ${e.message}`, type: 'danger' };
  }
}

// --- Form Submit Handler ---
async function handleCreateDoctor() {
  toast.value = null;
  // Basic validation
  if (!doctor.value.name || !doctor.value.email || !doctor.value.password || !doctor.value.department_id) {
    toast.value = { message: 'Please fill out all fields.', type: 'danger' };
    return;
  }

  try {
    // Call the create doctor endpoint
    const data = await fetchApi('/api/admin/doctors', {
      method: 'POST',
      body: JSON.stringify(doctor.value)
    });
    
    // Show success and go back to the dashboard
    toast.value = { message: data.message, type: 'success' };
    setTimeout(() => {
      emit('back');
    }, 1500); // Wait 1.5s so admin can see the success message
    
  } catch (e) { 
    toast.value = { message: e.message, type: 'danger' };
  }
}

</script>

<style scoped>
/* All styles copied from AdminDashboard.vue for consistency */
.hero-bg-admin {
  background: linear-gradient(90deg, rgba(142, 197, 252, 0.95) 0%, rgba(224, 195, 252, 0.95) 100%);
  height: 100vh;
  width: 100%;
  display: flex;
  flex-direction: column;
}

.top-nav {
  position: sticky;
  top: 0;
  z-index: 1020;
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(10px);
  padding: 0.75rem 0;
  flex-shrink: 0; 
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
}

.logo-img { height: 40px }
.nav-title { font-weight: 600; font-size: 1.1rem; color: #333 }
.nav-center { flex: 0 0 auto; text-align: center; }
.left-actions { min-width: 2rem }
.right-actions { min-width: 2rem }

.admin-content { padding-left: 1.5rem; padding-right: 1.5rem }

.admin-main-content {
  flex: 1;
  overflow-y: auto;
  padding-bottom: 2rem;
}

.user-name { font-weight: 600; color: #444; font-size: 0.95rem }
.logout-btn { background-color: #dc3545; color: white; border: none; padding: 0.4rem 1rem; border-radius: 8px; font-weight: 600 }
.logout-btn:hover { background-color: #c82333 }

.card { background:#fff; border-radius:1rem; border:none }
.card-header { background-color: transparent; border-bottom:1px solid #f0f0f0; padding:1.25rem 1.5rem }
.card-header h5 { font-weight: 700; color: #222; }
.card-body { padding: 1.5rem; }

/* Form styles */
.form-label {
  font-weight: 600;
  color: #333;
}
.form-control, .form-select {
  padding: 0.75rem 1rem;
  border-radius: 0.5rem;
}

/* Button styles */
.btn-create {
  background-color: #198754;
  color: white;
  font-weight: 600;
}
.btn-lg {
  padding: 0.75rem 1.5rem;
}
.back-btn {
  background: none;
  border: none;
  font-weight: 600;
  color: #555;
  font-size: 0.9rem;
}
.back-btn:hover {
  color: #0d6efd;
  text-decoration: underline;
}
</style>