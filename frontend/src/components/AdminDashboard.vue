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
          <button @click="$emit('logout')" class="logout-btn">Logout</button>
        </div>
      </div>
    </nav>

      <!-- Edit modal (inline) -->
      <div v-if="showEditModal" class="edit-modal-wrapper">
        <div class="edit-modal">
          <h5 class="mb-3">Edit {{ editingType === 'doctor' ? 'Doctor' : 'Patient' }}</h5>
          <div class="mb-2">
            <label class="form-label">Name</label>
            <input class="form-control" v-model="editForm.name" />
          </div>
          <div class="mb-2">
            <label class="form-label">Email</label>
            <input class="form-control" v-model="editForm.email" />
          </div>
          <div class="mb-2">
            <label class="form-label">Password</label>
            <input class="form-control" v-model="editForm.password" placeholder="Leave blank to keep current password" />
          </div>
          <div v-if="editingType === 'doctor'" class="mb-2">
            <label class="form-label">Department</label>
            <select class="form-select" v-model="editForm.department_id">
              <option v-for="d in departments" :key="d.id" :value="d.id">{{ d.name }}</option>
            </select>
          </div>
          <div class="form-check form-switch mb-3">
            <input class="form-check-input" type="checkbox" id="blacklistToggle" v-model="editForm.is_blacklisted">
            <label class="form-check-label" for="blacklistToggle">Blacklisted</label>
          </div>
          <div class="d-flex justify-content-end gap-2">
            <button class="btn btn-secondary" @click="closeEditModal">Cancel</button>
            <button class="btn btn-primary" :disabled="savingEdit" @click="submitEdit">Save</button>
          </div>
        </div>
      </div>

  <main class="container-fluid mt-4 admin-content admin-main-content">
      <div class="row">
        <div class="col-xl-3 col-md-6 mb-4">
          <div class="stat-card">
            <div class="stat-card-body">
              <div class="stat-card-title">Total Patients</div>
              <div class="stat-card-value">{{ stats.patients }}</div>
            </div>
            <div class="stat-card-icon">👤</div>
          </div>
        </div>
        <div class="col-xl-3 col-md-6 mb-4">
          <div class="stat-card">
            <div class="stat-card-body">
              <div class="stat-card-title">Total Doctors</div>
              <div class="stat-card-value">{{ stats.doctors }}</div>
            </div>
            <div class="stat-card-icon">🩺</div>
          </div>
        </div>
        <div class="col-xl-3 col-md-6 mb-4">
          <div class="stat-card">
            <div class="stat-card-body">
              <div class="stat-card-title">Total Appointments</div>
              <div class="stat-card-value">{{ stats.totalAppointments }}</div>
            </div>
            <div class="stat-card-icon">🏥</div>
          </div>
        </div>
        <div class="col-xl-3 col-md-6 mb-4">
          <div class="stat-card">
            <div class="stat-card-body">
              <div class="stat-card-title">Upcoming Appointments</div>
              <div class="stat-card-value">{{ stats.upcoming }}</div>
            </div>
            <div class="stat-card-icon">📅</div>
          </div>
        </div>
      </div>

      <div class="row mb-3">
        <div class="col">
          <input type="search" v-model="searchQuery" class="form-control search-bar" placeholder="Search for doctors, patients, or departments...">
        </div>
      </div>

      <div class="row">
        <div class="col-lg-12 mb-4">
          <div class="card shadow-sm">
            <div class="card-header d-flex justify-content-between align-items-center">
              <h5 class="mb-0">Registered Doctors</h5>
              <button class="btn btn-sm btn-create" @click="createNewDoctor">+ Create New</button>
            </div>
            <div class="card-body">
              <div class="table-responsive">
                <table class="table table-hover align-middle">
                  <thead>
                    <tr>
                      <th>Name</th>
                      <th>Email</th>
                      <th>Department</th>
                      <th>Created</th>
                      <th>Status</th>
                      <th class="text-end">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-if="filteredDoctors.length === 0">
                      <td colspan="6" class="text-center text-muted">No doctors found.</td>
                    </tr>
                    <tr v-for="doctor in filteredDoctors" :key="doctor.user_id">
                      <td>{{ doctor.name }}</td>
                      <td>{{ doctor.email }}</td>
                      <td>{{ doctor.department }}</td>
                      <td>{{ formatToIST(doctor.created_at) }}</td>
                      <td>
                        <span :class="doctor.is_blacklisted ? 'text-danger' : 'text-success'">
                          {{ doctor.is_blacklisted ? 'Blacklisted' : 'Active' }}
                        </span>
                      </td>
                      <td class="text-end">
                        <button class="btn btn-sm btn-edit me-1" @click="editItem(doctor, 'doctor')">Edit</button>
                        <button class="btn btn-sm btn-delete me-1" @click="deleteItem(doctor.user_id, doctor.name, 'doctor')">Delete</button>
                        <button class="btn btn-sm btn-blacklist" @click="blacklistItem(doctor.user_id, doctor.name)">
                          {{ doctor.is_blacklisted ? 'Unblock' : 'Block' }}
                        </button>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>

        <div class="col-lg-12 mb-4">
          <div class="card shadow-sm">
            <div class="card-header">
              <h5 class="mb-0">Registered Patients</h5>
            </div>
            <div class="card-body">
              <div class="table-responsive">
                <table class="table table-hover align-middle">
                  <thead>
                    <tr>
                      <th>Name</th>
                      <th>Email</th>
                      <th>Registered</th>
                      <th>Status</th>
                      <th class="text-end">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-if="filteredPatients.length === 0">
                      <td colspan="5" class="text-center text-muted">No patients found.</td>
                    </tr>
                    <tr v-for="patient in filteredPatients" :key="patient.id">
                      <td>{{ patient.name }}</td>
                      <td>{{ patient.email }}</td>
                      <td>{{ formatToIST(patient.created_at) }}</td>
                      <td>
                        <span :class="patient.is_blacklisted ? 'text-danger' : 'text-success'">
                          {{ patient.is_blacklisted ? 'Blacklisted' : 'Active' }}
                        </span>
                      </td>
                      <td class="text-end">
                        <button class="btn btn-sm btn-edit me-1" @click="editItem(patient, 'patient')">Edit</button>
                        <button class="btn btn-sm btn-delete me-1" @click="deleteItem(patient.id, patient.name, 'patient')">Delete</button>
                        <button class="btn btn-sm btn-blacklist" @click="blacklistItem(patient.id, patient.name)">
                          {{ patient.is_blacklisted ? 'Unblock' : 'Block' }}
                        </button>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>

        <div class="col-lg-12 mb-4">
          <div class="card shadow-sm">
            <div class="card-header">
              <h5 class="mb-0">Upcoming Appointments</h5>
            </div>
            <div class="card-body">
              <div class="table-responsive">
                <table class="table table-hover align-middle">
                  <thead>
                    <tr>
                      <th>ID</th>
                      <th>Patient</th>
                      <th>Doctor</th>
                      <th>Department</th>
                      <th>Date & Time</th>
                      <th class="text-end">Patient History</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-if="filteredAppointments.length === 0">
                      <td colspan="6" class="text-center text-muted">No upcoming appointments found.</td>
                    </tr>
                    <tr v-for="appt in filteredAppointments" :key="appt.id">
                      <td>{{ appt.id }}</td>
                      <td>{{ appt.patient_name }}</td>
                      <td>{{ appt.doctor_name }}</td>
                      <td>{{ appt.department }}</td>
                      <td>{{ formatToIST(appt.datetime) }}</td>
                      <td class="text-end">
                        <button class="btn btn-sm btn-view" @click="viewHistory(appt.patient_id, appt.patient_name)">View</button>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>

      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import logo from '../assets/Logo.png'
// Import the notification component
import ToastNotification from './ToastNotification.vue'

const props = defineProps({ user: Object })
const user = props.user

const emit = defineEmits(['logout'])

// --- Dynamic Data Refs ---
const stats = ref({ patients: 0, doctors: 0, totalAppointments: 0, upcoming: 0 })
const doctors = ref([])
const patients = ref([])
const appointments = ref([])
const departments = ref([]) // To create new doctors
const searchQuery = ref('')
const toast = ref(null) // For toast notifications
const showEditModal = ref(false)
const editingUser = ref(null)
const editingType = ref(null)
const editForm = ref({ name: '', email: '', department_id: null, is_blacklisted: false, password: '' })
const savingEdit = ref(false)

// --- API Helper ---
// This is the REAL fetchApi function
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
    // If auth fails, log the user out
    if (response.status === 401) emit('logout');
    throw new Error((data && data.message) || response.statusText || 'API error')
  }
  return data
}

// --- Computed filters (no change) ---
const filteredDoctors = computed(() => {
  const q = searchQuery.value.trim().toLowerCase()
  if (!q) return doctors.value
  return doctors.value.filter(d => (d.name + ' ' + d.email + ' ' + (d.department||'')).toLowerCase().includes(q))
})

const filteredPatients = computed(() => {
  const q = searchQuery.value.trim().toLowerCase()
  if (!q) return patients.value
  return patients.value.filter(p => (p.name + ' ' + p.email).toLowerCase().includes(q))
})

const filteredAppointments = computed(() => {
  const q = searchQuery.value.trim().toLowerCase()
  if (!q) return appointments.value
  return appointments.value.filter(a => (a.patient_name + ' ' + a.doctor_name + ' ' + (a.department||'')).toLowerCase().includes(q))
})

// --- Functional Buttons ---

// --- Date formatting helper (IST) ---
function formatToIST(isoString) {
  if (!isoString) return '—'
  try {
    const dt = new Date(isoString)
    return new Intl.DateTimeFormat('en-IN', {
      year: 'numeric', month: 'short', day: 'numeric',
      hour: '2-digit', minute: '2-digit', hour12: true,
      timeZone: 'Asia/Kolkata'
    }).format(dt)
  } catch (e) {
    return new Date(isoString).toLocaleString()
  }
}
// Sort helper: newest first based on created_at (ISO string)
function sortByCreatedDesc(list) {
  if (!Array.isArray(list)) return list
  return list.slice().sort((a, b) => {
    const ta = a && a.created_at ? Date.parse(a.created_at) : 0
    const tb = b && b.created_at ? Date.parse(b.created_at) : 0
    return tb - ta
  })
}

async function createNewDoctor() {
  const name = prompt("Enter new doctor's full name:");
  if (!name) return;
  const email = prompt("Enter new doctor's email:");
  if (!email) return;
  const password = prompt("Enter a temporary password:");
  if (!password) return;
  
  const deptList = departments.value.map(d => `${d.id}: ${d.name}`).join('\n');
  const deptId = prompt(`Enter Department ID:\n${deptList}`);
  if (!deptId) return;

  try {
    const data = await fetchApi('/api/admin/doctors', {
      method: 'POST',
      body: JSON.stringify({
        name: name,
        email: email,
        password: password,
        department_id: parseInt(deptId)
      })
    });
    // Show success and the temporary password so admin can note credentials
    toast.value = { message: data.message, type: 'success' };
    if (data.temp_password) {
      alert(`Doctor created. Temporary password: ${data.temp_password} \nMake sure to copy it now — it won't be shown again.`)
    }
    getDashboardData(); // Refresh all data
  } catch (e) { 
    toast.value = { message: e.message, type: 'danger' };
  }
}

function editItem(item, type) {
  openEditModal(item, type)
}

function openEditModal(item, type) {
  editingType.value = type
  editingUser.value = item
  // populate form
  editForm.value.name = item.name || ''
  editForm.value.email = item.email || ''
  editForm.value.is_blacklisted = !!item.is_blacklisted
  // find department id for doctors
  if (type === 'doctor') {
    const dept = departments.value.find(d => d.name === item.department)
    editForm.value.department_id = dept ? dept.id : (departments.value[0] ? departments.value[0].id : null)
    editForm.value.password = ''
  } else {
    editForm.value.department_id = null
    editForm.value.password = ''
  }
  showEditModal.value = true
}

function closeEditModal() {
  showEditModal.value = false
  editingUser.value = null
  editingType.value = null
  editForm.value = { name: '', email: '', department_id: null, is_blacklisted: false, password: '' }
  savingEdit.value = false
}

async function submitEdit() {
  if (!editingUser.value) return
  savingEdit.value = true
  const userId = editingType.value === 'doctor' ? editingUser.value.user_id : (editingUser.value.id || editingUser.value.user_id)
  const payload = {
    name: editForm.value.name,
    email: editForm.value.email,
    is_blacklisted: !!editForm.value.is_blacklisted
  }
  if (editingType.value === 'doctor' && editForm.value.department_id) {
    payload.department_id = editForm.value.department_id
  }
  if (editForm.value.password) {
    payload.password = editForm.value.password
  }
  try {
    const data = await fetchApi(`/api/admin/users/${userId}`, {
      method: 'PUT',
      body: JSON.stringify(payload)
    })

    toast.value = { message: data.message, type: 'success' }
    // Update local arrays in-place for immediate UI update
    const updatedUser = data.user
    if (editingType.value === 'doctor') {
      const idx = doctors.value.findIndex(d => d.user_id === updatedUser.id)
        if (idx !== -1) {
        // merge updated fields
        doctors.value[idx] = { ...doctors.value[idx], name: updatedUser.name, email: updatedUser.email, is_blacklisted: updatedUser.is_blacklisted, created_at: updatedUser.created_at || doctors.value[idx].created_at }
        // update department name if possible
        const deptObj = departments.value.find(d => d.id === editForm.value.department_id)
        if (deptObj) doctors.value[idx].department = deptObj.name
        doctors.value = sortByCreatedDesc(doctors.value)
      }
    } else {
      const idx = patients.value.findIndex(p => p.id === updatedUser.id)
      if (idx !== -1) {
        patients.value[idx] = { ...patients.value[idx], name: updatedUser.name, email: updatedUser.email, is_blacklisted: updatedUser.is_blacklisted, created_at: updatedUser.created_at || patients.value[idx].created_at }
        patients.value = sortByCreatedDesc(patients.value)
      }
    }

    closeEditModal()
  } catch (e) {
    toast.value = { message: e.message, type: 'danger' }
    savingEdit.value = false
  }
}

async function deleteItem(userId, name, type) {
  if (!confirm(`Are you sure you want to permanently DELETE ${type} ${name}? This cannot be undone.`)) return;
  try {
    const data = await fetchApi(`/api/admin/users/${userId}`, { method: 'DELETE' });
    toast.value = { message: data.message, type: 'success' };
    getDashboardData(); // Refresh all data
  } catch (e) { 
    toast.value = { message: e.message, type: 'danger' };
  }
}

async function blacklistItem(userId, name) {
  // Determine current status from local state so confirmation can be specific
  const user = doctors.value.find(d => d.user_id === userId) || patients.value.find(p => p.id === userId)
  const currentlyBlacklisted = !!(user && user.is_blacklisted)
  const action = currentlyBlacklisted ? 'Unblock' : 'Block'
  if (!confirm(`Are you sure you want to ${action.toLowerCase()} ${name}?`)) return;
  try {
    // Explicitly set new status to avoid backend toggle surprises
    const payload = { is_blacklisted: !currentlyBlacklisted }
    const data = await fetchApi(`/api/admin/users/${userId}/blacklist`, { method: 'PUT', body: JSON.stringify(payload) });
    toast.value = { message: data.message, type: 'success' };
    // Update local copy so UI updates immediately without full reload
    if (user) {
      user.is_blacklisted = !!data.is_blacklisted
      // trigger reactivity
      if (doctors.value.includes(user)) doctors.value = [...doctors.value]
      if (patients.value.includes(user)) patients.value = [...patients.value]
    } else {
      // fallback to refresh
      getDashboardData();
    }
  } catch (e) { 
    toast.value = { message: e.message, type: 'danger' };
  }
}

async function viewHistory(patientId, patientName) {
  try {
    const history = await fetchApi(`/api/patients/${patientId}/history`);
    if (history.length === 0) {
      toast.value = { message: `No history found for ${patientName}.`, type: 'success' };
    } else {
      toast.value = { message: `Found ${history.length} records for ${patientName}. Check console.`, type: 'success' };
      console.log(`History for ${patientName}:`, history);
    }
  } catch (e) { 
    toast.value = { message: e.message, type: 'danger' };
  }
}

// --- Initialization ---
// Fetches real data from the backend
async function getDashboardData() {
  try {
    const data = await fetchApi('/api/admin/dashboard');
    console.debug('admin/dashboard response:', data)
    stats.value = data.stats;
    doctors.value = sortByCreatedDesc(data.doctors || []);
    patients.value = sortByCreatedDesc(data.patients || []);
    console.debug('patients loaded:', patients.value.length, patients.value.slice(0,3))
    appointments.value = data.appointments || [];
    departments.value = data.departments || [];
  } catch (e) {
    console.error('Failed to load admin data', e)
    toast.value = { message: `Failed to load dashboard data: ${e.message}`, type: 'danger' };
    if (e.message === 'Unauthorized') emit('logout');
  }
}

onMounted(() => {
  getDashboardData();
});
</script>

<style scoped>
/* --- THIS IS THE RESTORED, FULL CSS --- */
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

/* Edit modal styles */
.edit-modal-wrapper {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}
.edit-modal {
  background: white;
  padding: 1.25rem;
  border-radius: 8px;
  width: 420px;
  box-shadow: 0 8px 24px rgba(0,0,0,0.15);
}

.user-name { font-weight: 600; color: #444; font-size: 0.95rem }
.logout-btn { background-color: #dc3545; color: white; border: none; padding: 0.4rem 1rem; border-radius: 8px; font-weight: 600 }
.logout-btn:hover { background-color: #c82333 }

.stat-card { background: rgba(255,255,255,0.85); border-radius: 1rem; padding: 1.5rem; box-shadow: 0 4px 15px rgba(0,0,0,0.05); display:flex; justify-content:space-between }
.stat-card-title { font-size: 0.95rem; color:#555; font-weight:600; margin-bottom:0.25rem }
.stat-card-value { font-size:2.25rem; font-weight:700; color:#111 }
.stat-card-icon { font-size:2.5rem; opacity:0.5 }

.search-bar { background-color: rgba(255,255,255,0.7); border:1px solid rgba(255,255,255,0.9); border-radius:0.75rem; padding:0.9rem 1rem }
.search-bar:focus { background-color: rgba(255,255,255,0.9); border-color: #fff; box-shadow: 0 0 0 0.25rem rgba(142,197,252,0.5) }

.card { background:#fff; border-radius:1rem; border:none }
.card-header { background-color: transparent; border-bottom:1px solid #f0f0f0; padding:1.25rem 1.5rem }
.card-header h5 { font-weight: 700; color: #222; }
.card-body { padding: 1.5rem; }

.table {
  border-collapse: separate;
  border-spacing: 0 0.5rem;
}
.table thead th {
  border: none;
  color: #777;
  font-weight: 600;
  font-size: 0.85rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
.table tbody tr {
  background-color: #fcfcfc;
}
.table tbody td {
  vertical-align: middle;
  padding: 1rem;
  font-weight: 500;
  border-top: 1px solid #f0f0f0;
  border-bottom: 1px solid #f0f0f0;
}
.table tbody tr td:first-child {
  border-left: 1px solid #f0f0f0;
  border-top-left-radius: 8px;
  border-bottom-left-radius: 8px;
}
.table tbody tr td:last-child {
  border-right: 1px solid #f0f0f0;
  border-top-right-radius: 8px;
  border-bottom-right-radius: 8px;
}
.table-hover tbody tr:hover {
  background-color: #f5f5f5;
  box-shadow: 0 2px 5px rgba(0,0,0,0.03);
}

.btn-sm {
  font-size: 0.8rem;
  font-weight: 600;
  padding: 0.3rem 0.75rem;
  border-radius: 6px;
}
.btn-create {
  background-color: #198754;
  color: white;
}
.btn-edit {
  background-color: #ffc107;
  color: #333;
}
.btn-delete {
  background-color: #dc3545;
  color: white;
}
.btn-blacklist {
  background-color: #343a40;
  color: white;
}
.btn-view {
  background-color: #0d6efd;
  color: white;
}
</style>