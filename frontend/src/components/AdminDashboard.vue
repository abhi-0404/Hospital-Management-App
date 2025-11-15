<template>
  <div class="hero-bg-admin">
    <ToastNotification 
      v-if="toast"
      :message="toast.message" 
      :type="toast.type"
      @close="toast = null"
    />
    
    <div v-if="savingEdit" class="loading-overlay">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>

    <!-- *** NEW: Patient History Modal *** -->
    <div v-if="showHistoryModal" class="modal-overlay" @click.self="closeHistoryModal">
      <div class="modal-content card shadow-lg" style="max-width: 600px;">
        <div class="card-header d-flex justify-content-between align-items-center">
          <h5 class="mb-0">Patient History for {{ historyPatientName }}</h5>
          <button @click="closeHistoryModal" class="btn-close" aria-label="Close"></button>
        </div>
        <div class="card-body" style="max-height: 70vh; overflow-y: auto;">
          <div v-if="patientHistory.length === 0" class="text-center text-muted">
            No past treatment history found.
          </div>
          <div v-else>
            <div v-for="record in patientHistory" :key="record.id" class="history-record card mb-3">
              <div class="card-body">
                <h6 class="card-title text-primary">{{ record.doctor_name }} ({{ record.department }})</h6>
                <p class="card-subtitle mb-2 text-muted">{{ formatToIST(record.datetime) }}</p>
                <hr>
                <p class="mb-1"><strong>Diagnosis:</strong> {{ record.diagnosis || 'N/A' }}</p>
                <p class="mb-1"><strong>Visit Type:</strong> {{ record.visit_type || 'N/A' }}</p>
                <p class="mb-1"><strong>Tests Done:</strong> {{ record.test_done || 'N/A' }}</p>
                <p class="mb-1"><strong>Medicines:</strong></p>
                <ul v-if="record.medicines && record.medicines.length > 0" class="small ps-4">
                  <li v-for="(med, i) in record.medicines" :key="i">{{ med }}</li>
                </ul>
                <p v-else class="small ps-4">N/A</p>
                <p class="mb-0"><strong>Prescription Notes:</strong> {{ record.prescription || 'N/A' }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>


    <!-- Create Doctor Modal -->
    <div v-if="showCreateModal" class="modal-overlay" @click.self="closeCreateModal">
      <div class="modal-content card shadow-lg" style="max-width: 500px;">
        <div class="card-header d-flex justify-content-between align-items-center">
          <h5 class="mb-0">Add New Doctor</h5>
          <button @click="closeCreateModal" class="btn-close" aria-label="Close"></button>
        </div>
        <div class="card-body">
          <form @submit.prevent="submitCreateDoctor">
            <div class="mb-3">
              <label class="form-label" for="create-name">Name</label>
              <input class="form-control" id="create-name" v-model="createForm.name" required />
            </div>
            <div class="mb-3">
              <label class="form-label" for="create-email">Email</label>
              <input type="email" class="form-control" id="create-email" v-model="createForm.email" required />
            </div>
            <div class="mb-3">
              <label class="form-label" for="create-pass">Password</label>
              <input type="password" class="form-control" id="create-pass" v-model="createForm.password" placeholder="Enter a temporary password" required />
            </div>
            <div class="mb-3">
              <label class="form-label" for="create-dept">Department</label>
              <select class="form-select" id="create-dept" v-model="createForm.department_id" required>
                <option :value="null" disabled>Select a department...</option>
                <option v-for="d in departments" :key="d.id" :value="d.id">{{ d.name }}</option>
              </select>
            </div>
            <div class="d-flex justify-content-end gap-2 mt-4">
              <button type="button" class="btn btn-secondary" @click="closeCreateModal">Cancel</button>
              <button type="submit" class="btn btn-primary" :disabled="savingEdit">Add Doctor</button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- Edit modal (inline) -->
    <div v-if="showEditModal" class="modal-overlay" @click.self="closeEditModal">
      <div class="modal-content card shadow-lg" style="max-width: 500px;">
        <div class="card-header d-flex justify-content-between align-items-center">
          <h5 class="mb-0">Edit {{ editingType === 'doctor' ? 'Doctor' : 'Patient' }}</h5>
          <button @click="closeEditModal" class="btn-close" aria-label="Close"></button>
        </div>
        <div class="card-body">
          <div class="mb-3">
            <label class="form-label">Name</label>
            <input class="form-control" v-model="editForm.name" />
          </div>
          <div class="mb-3">
            <label class="form-label">Email</label>
            <input class="form-control" v-model="editForm.email" />
          </div>
          <div class="mb-3">
            <label class="form-label">Password</label>
            <input class="form-control" v-model="editForm.password" placeholder="Leave blank to keep current password" />
          </div>
          <div v-if="editingType === 'doctor'" class="mb-3">
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
    </div>

    <!-- Details modal -->
    <div v-if="showDetailsModal" class="modal-overlay" @click.self="closeDetails">
      <div class="modal-content card shadow-lg" style="max-width: 600px;">
        <div class="card-header d-flex justify-content-between align-items-center">
          <h5 class="mb-0">{{ detailsType === 'doctor' ? 'Doctor Details' : 'Patient Details' }}</h5>
          <button @click="closeDetails" class="btn-close" aria-label="Close"></button>
        </div>
        <div class="card-body">
          <div class="details-header">
            <div><strong>Name:</strong> {{ detailsObject?.name }}</div>
            <div><strong>Email:</strong> {{ detailsObject?.email }}</div>
          </div>
          <div class="details-body">
            <div v-if="detailsType === 'doctor'" class="mb-2"><strong>Department:</strong> {{ detailsObject?.department }}</div>
            <div class="mb-2"><strong>Status:</strong> <span :class="detailsObject?.is_blacklisted ? 'text-danger' : 'text-success'">{{ detailsObject?.is_blacklisted ? 'Blacklisted' : 'Active' }}</span></div>
            <div class="mb-2"><strong>Created:</strong> {{ formatToIST(detailsObject?.created_at) }}</div>
          </div>
          <hr />
          <div class="mb-2"><strong>Recent Appointments</strong></div>
          <div v-if="relatedAppointments.length === 0" class="text-muted">No recent appointments found.</div>
          <div v-else class="details-history-list">
            <ul class="list-unstyled small">
              <li v-for="a in relatedAppointments.slice(0,10)" :key="a.id" class="history-item">
                <span>#{{ a.id }} — {{ a.patient_name || a.doctor_name }}</span>
                <span class="text-muted">{{ formatToIST(a.datetime) }}</span>
                <span>{{ a.department }}</span>
              </li>
            </ul>
          </div>
          <div class="d-flex justify-content-end gap-2 mt-3">
            <button class="btn btn-secondary" @click="closeDetails">Close</button>
            <!-- *** NEW: Export History button for this patient *** -->
            <button class="btn btn-create" @click="exportPatientHistory(detailsObject.id, detailsObject.name)">Export History</button>
          </div>
        </div>
      </div>
    </div>
    
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
              <button class="btn btn-sm btn-create" @click="openCreateModal">+ Create New</button>
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
                        <button class="btn btn-sm btn-view me-1" @click="openDetails(doctor, 'doctor')">View</button>
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
                        <button class="btn btn-sm btn-view me-1" @click="openDetails(patient, 'patient')">View</button>
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
                        <!-- *** UPDATED: Button class and text *** -->
                        <button class="btn btn-sm btn-view" @click="viewHistory(appt.patient_id, appt.patient_name)">View History</button>
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
import ToastNotification from './ToastNotification.vue'

const props = defineProps({ user: Object })
const user = props.user

const emit = defineEmits(['logout'])

// --- Dynamic Data Refs ---
const stats = ref({ patients: 0, doctors: 0, totalAppointments: 0, upcoming: 0 })
const doctors = ref([])
const patients = ref([])
const appointments = ref([])
const departments = ref([]) 
const searchQuery = ref('')
const toast = ref(null) 
const savingEdit = ref(false)

// --- Edit Modal State ---
const showEditModal = ref(false)
const editingUser = ref(null)
const editingType = ref(null)
const editForm = ref({ name: '', email: '', department_id: null, is_blacklisted: false, password: '' })

// --- *** NEW: History Modal State *** ---
const showHistoryModal = ref(false)
const patientHistory = ref([])
const historyPatientName = ref('')

// --- Create Modal State ---
const showCreateModal = ref(false)
const createForm = ref({ name: '', email: '', password: '', department_id: null })

// --- Details modal state ---
const showDetailsModal = ref(false)
const detailsType = ref(null) // 'doctor' | 'patient'
const detailsObject = ref(null)
const relatedAppointments = ref([])

// --- API Helper ---
async function fetchApi(endpoint, options = {}, isFile = false) {
  savingEdit.value = true; 
  const token = localStorage.getItem('token')
  const headers = { ...options.headers }
  if (!isFile) {
    headers['Content-Type'] = 'application/json'
  }
  if (token) headers['Authorization'] = `Bearer ${token}`

  try {
    const response = await fetch(`http://127.0.0.1:8000${endpoint}`, {
      ...options,
      headers,
    })

    if (response.status === 401) {
      emit('logout');
      throw new Error('Unauthorized');
    }

    if (isFile) {
      if (!response.ok) {
        const errData = await response.json().catch(() => ({ message: 'File download failed' }));
        throw new Error(errData.message);
      }
      return await response.blob();
    }
    
    const data = await response.json();
    if (!response.ok) {
      throw new Error((data && data.message) || response.statusText || 'API error')
    }
    return data
  } catch (e) {
    toast.value = { message: `Error: ${e.message}`, type: 'danger' }
    throw e // Re-throw to stop calling function
  } finally {
    savingEdit.value = false;
  }
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
    // Use UTC as fallback for parsing, and display in Indian Time
    return new Intl.DateTimeFormat('en-IN', {
      year: 'numeric', month: 'short', day: 'numeric',
      hour: '2-digit', minute: '2-digit', hour12: true,
      timeZone: 'UTC' 
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

// --- Create Doctor Functions ---
function openCreateModal() {
  createForm.value = {
    name: '',
    email: '',
    password: '',
    department_id: departments.value.length > 0 ? departments.value[0].id : null
  }
  showCreateModal.value = true;
}

function closeCreateModal() {
  showCreateModal.value = false;
}

async function submitCreateDoctor() {
  if (!createForm.value.department_id) {
    toast.value = { message: 'Please select a department.', type: 'danger' };
    return;
  }
  
  try {
    const data = await fetchApi('/api/admin/doctors', {
      method: 'POST',
      body: JSON.stringify(createForm.value)
    });
    
    toast.value = { message: data.message, type: 'success' };
    getDashboardData(); // Refresh all data
    closeCreateModal();
  } catch (e) { 
    // Toast is already handled by fetchApi
  }
}

// --- Edit & Details Functions ---
function editItem(item, type) {
  openEditModal(item, type)
}

function openDetails(item, type) {
  detailsType.value = type
  detailsObject.value = item
  // collect related appointments from loaded appointments
  if (type === 'doctor') {
    relatedAppointments.value = appointments.value.filter(a => Number(a.doctor_id) === Number(item.id || item.user_id)).sort((x,y) => new Date(y.datetime) - new Date(x.datetime))
  } else {
    relatedAppointments.value = appointments.value.filter(a => Number(a.patient_id) === Number(item.id)).sort((x,y) => new Date(y.datetime) - new Date(x.datetime))
  }
  showDetailsModal.value = true
}

function closeDetails() {
  showDetailsModal.value = false
  detailsObject.value = null
  detailsType.value = null
  relatedAppointments.value = []
}

// --- *** NEW: Export Patient History (from Details modal) *** ---
async function exportPatientHistory(patientId, patientName) {
   try {
    toast.value = { message: `Generating history for ${patientName}...`, type: 'success' };
    // Call the backend API to generate and return the CSV file
    const blob = await fetchApi(`/api/patients/${patientId}/export-history`, {
      method: 'GET'
    }, true); // true = isFile

    // Create a link and click it to download the blob
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.style.display = 'none';
    a.href = url;
    a.download = `${patientName.replace(/\s+/g, '_')}_treatment_history.csv`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    a.remove();
    
  } catch (error) {
    // Error handled by fetchApi (it will show a toast)
  }
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
    // Toast is handled by fetchApi
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
    // Toast is handled by fetchApi
  }
}

async function blacklistItem(userId, name) {
  const user = doctors.value.find(d => d.user_id === userId) || patients.value.find(p => p.id === userId)
  const currentlyBlacklisted = !!(user && user.is_blacklisted)
  const action = currentlyBlacklisted ? 'Unblock' : 'Block'
  if (!confirm(`Are you sure you want to ${action.toLowerCase()} ${name}?`)) return;
  try {
    const payload = { is_blacklisted: !currentlyBlacklisted }
    const data = await fetchApi(`/api/admin/users/${userId}/blacklist`, { method: 'PUT', body: JSON.stringify(payload) });
    toast.value = { message: data.message, type: 'success' };
    if (user) {
      const newStatus = (typeof data.is_blacklisted === 'boolean') ? data.is_blacklisted : (data.user && typeof data.user.is_blacklisted === 'boolean' ? data.user.is_blacklisted : !currentlyBlacklisted)
      user.is_blacklisted = !!newStatus
      if (doctors.value.includes(user)) doctors.value = [...doctors.value]
      if (patients.value.includes(user)) patients.value = [...patients.value]
    } else {
      getDashboardData();
    }
  } catch (e) { 
    // Toast is handled by fetchApi
  }
}

// --- *** UPDATED: This function now opens a modal *** ---
async function viewHistory(patientId, patientName) {
  try {
    const history = await fetchApi(`/api/patients/${patientId}/history`);
    patientHistory.value = history;
    historyPatientName.value = patientName;
    if (history.length === 0) {
      toast.value = { message: `No history found for ${patientName}.`, type: 'success' };
    }
    showHistoryModal.value = true; // Open the modal
  } catch (e) { 
    // Toast is handled by fetchApi
  }
}

function closeHistoryModal() {
  showHistoryModal.value = false;
  patientHistory.value = [];
  historyPatientName.value = '';
}

// --- Initialization ---
async function getDashboardData() {
  try {
    const data = await fetchApi('/api/admin/dashboard');
    stats.value = data.stats;
    doctors.value = sortByCreatedDesc(data.doctors || []);
    patients.value = sortByCreatedDesc(data.patients || []);
    appointments.value = data.appointments || [];
    departments.value = data.departments || [];
  } catch (e) {
    console.error('Failed to load admin data', e)
    if (e.message === 'Unauthorized') emit('logout');
  }
}

onMounted(() => {
  getDashboardData();
});
</script>

<style scoped>
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

/* --- NEW: Modal Styles --- */
.loading-overlay {
  position: fixed;
  inset: 0;
  background-color: rgba(255, 255, 255, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}

.modal-overlay {
  position: fixed;
  inset: 0;
  background-color: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(5px);
  display: flex;
  align-items: center; /* Vertically center */
  justify-content: center;
  z-index: 9998;
  padding: 1rem;
  overflow-y: auto; 
}

.modal-content {
  background: #fff;
  border-radius: 1rem;
  border: none;
  width: 90%;
  /* max-width is set inline in the template */
}
/* --- End Modal Styles --- */


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
.btn-primary { font-weight: 600; }
.btn-secondary { font-weight: 600; }

.form-label {
  font-weight: 600;
  color: #333;
}
.form-control, .form-select {
  padding: 0.75rem 1rem;
  border-radius: 0.5rem;
  background-color: rgba(248, 249, 250, 0.7);
  border: 1px solid #e9ecef;
}
.form-control:focus, .form-select:focus {
  background-color: #fff;
  border-color: #8f7ece;
  box-shadow: 0 0 0 0.25rem rgba(142, 197, 252, 0.5);
}

.details-header {
  background-color: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 0.5rem;
  padding: 0.75rem 1.25rem;
  margin-bottom: 1rem;
  display: flex;
  justify-content: space-between;
  font-weight: 600;
}
.details-body {
  padding: 0 0.5rem;
}
.details-history-list {
  max-height: 200px;
  overflow-y: auto;
  padding: 0.5rem;
  background: #fdfdfd;
  border-radius: 0.5rem;
  border: 1px solid #f0f0f0;
}
.history-item {
  display: flex;
  justify-content: space-between;
  padding: 0.25rem 0;
  border-bottom: 1px solid #f0f0f0;
}
.history-item:last-child {
  border-bottom: none;
}

/* *** NEW: History Record (for history modal) *** */
.history-record {
  border-left: 4px solid #0d6efd;
}
</style>