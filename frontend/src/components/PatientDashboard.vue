<template>
  <div class="hero-bg-admin">
    <ToastNotification 
      v-if="toast"
      :message="toast.message" 
      :type="toast.type"
      @close="toast = null"
    />

    <div v-if="isLoading" class="loading-overlay">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>

    <div v-if="currentView === 'history'" class="modal-overlay" @click.self="currentView = 'dashboard'">
      <div class="modal-content card shadow-lg">
        <div class="card-header d-flex justify-content-between align-items-center">
          <h5 class="mb-0">Treatment History</h5>
          <button @click="currentView = 'dashboard'" class="btn-close" aria-label="Close"></button>
        </div>
        <div class="card-body" style="max-height: 70vh; overflow-y: auto;">
          <div v-if="patientHistoryFiltered.length === 0" class="text-center text-muted">
            No past treatment history found for selected filters.
          </div>
          <div v-else>
            <div v-for="record in patientHistoryFiltered" :key="record.id" class="history-record card mb-3">
              <div class="card-body">
                <h6 class="card-title text-primary">{{ record.doctor_name }} ({{ record.department }})</h6>
                <p class="card-subtitle mb-2 text-muted">{{ formatDateTime(record.datetime) }}</p>
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

    <div v-if="currentView === 'doctorProfile'" class="modal-overlay" @click.self="currentView = 'department'">
      <div class="modal-content card shadow-lg" style="max-width: 600px;">
        <div class="card-header d-flex justify-content-between align-items-center">
          <h5 class="mb-0">Doctor Profile</h5>
          <button @click="currentView = 'department'" class="btn-close" aria-label="Close"></button>
        </div>
        <div class="card-body">
          <div class="text-center mb-3">
            <h4 class="mb-0">{{ selectedDoctorProfile?.name }}</h4>
            <p class="text-primary mb-0" style="font-weight: 600;">{{ selectedDoctorProfile?.specialization_details }}</p>
            <p class="text-muted mb-0">{{ selectedDoctorProfile?.department }} Department</p>
          </div>
          <hr>
          <div class="profile-details">
            <div class="mb-3">
              <strong>About</strong>
              <p>{{ selectedDoctorProfile?.bio }}</p>
            </div>
            <div class="mb-3">
              <strong>Education</strong>
              <p>{{ selectedDoctorProfile?.education }}</p>
            </div>
            <div class="mb-3">
              <strong>Experience</strong>
              <p>{{ selectedDoctorProfile?.experience_years }} years</p>
            </div>
          </div>

            
          <div class="d-flex justify-content-end gap-2 mt-4">
            <button class="btn btn-secondary" @click="currentView = 'department'">Back to Doctors</button>
            <button class="btn btn-primary" @click="viewAvailability(selectedDoctorProfile)">Book Appointment</button>
          </div>
        </div>
      </div>
    </div>

    <nav class="top-nav">
      <div class="container-fluid d-flex align-items-center">
        <div class="left-actions d-flex align-items-center justify-content-start" style="flex: 1;">
            <span class="nav-title ms-2">Patients' Dashboard</span>
        </div>
        <div class="nav-center d-flex align-items-center justify-content-center">
          <img :src="logo" alt="logo" class="logo-img" />
        </div>
        <div class="right-actions d-flex align-items-center justify-content-end" style="flex:1">
          <span class="user-name me-3">Welcome, {{ user?.name || 'Patient' }}</span>
          <a href="#" class="nav-link me-2" @click.prevent="editProfile">Edit Profile</a>
          <span class="nav-divider">|</span>
          <button @click="$emit('logout')" class="logout-btn ms-2">Logout</button>
        </div>
      </div>
    </nav>

    <div v-if="editProfileModal" class="modal-overlay" @click.self="closeEditProfile">
      <div class="modal-content card shadow-lg" style="max-width:600px;">
        <div class="card-header d-flex justify-content-between align-items-center">
          <h5 class="mb-0">Edit Profile</h5>
          <button @click="closeEditProfile" class="btn-close" aria-label="Close"></button>
        </div>
        <div class="card-body">
          <div class="mb-3">
            <label class="form-label">Full Name</label>
            <input class="form-control" v-model="editProfileForm.name" placeholder="Your full name" />
          </div>
          <div class="mb-3">
            <label class="form-label">Email</label>
            <input class="form-control" v-model="editProfileForm.email" placeholder="you@example.com" />
          </div>
          <div class="mb-3">
            <label class="form-label">Phone</label>
            <input class="form-control" v-model="editProfileForm.phone" placeholder="Mobile number" />
          </div>
          <div class="d-flex justify-content-end gap-2">
            <button class="btn btn-secondary" @click="closeEditProfile">Cancel</button>
            <button class="btn btn-primary" @click="submitEditProfile" :disabled="isLoading">Save</button>
          </div>
        </div>
      </div>
    </div>

    <main class="container-fluid mt-4 admin-content admin-main-content">

      <div v-if="currentView === 'dashboard'">
      
        <div class="row">
          <div class="col-lg-6 mb-4">
            <div class="card shadow-sm h-100">
              <div class="card-body d-flex flex-column justify-content-between text-center">
                <div>
                  <h5 class="card-title mb-1" style="font-weight: 700;">Treatment History</h5>
                  <p class="text-muted">Filter and view your past diagnoses and prescriptions.</p>
                </div>
                <div class="d-flex gap-2 align-items-center mt-3">
                                  <select class="form-select form-select-sm" v-model="historyTreatmentFilter">
                                    <option value="">All Treatments</option>
                                    <option v-for="t in historyTreatmentOptions" :key="t" :value="t">{{ t || 'Unknown' }}</option>
                                  </select>
                  <button class="btn btn-view" @click="viewHistory">View History</button>
                </div>
              </div>
            </div>
          </div>

          <div class="col-lg-6 mb-4">
            <div class="card shadow-sm h-100">
              <div class="card-body d-flex flex-column justify-content-between text-center">
                <div>
                  <h5 class="card-title mb-1" style="font-weight: 700;">Export Treatment History</h5>
                  <p class="text-muted">Download your treatment records with selected filters.</p>
                </div>
                <div class="d-flex gap-2 align-items-center mt-3">
                  <select class="form-select form-select-sm" v-model="historyTreatmentFilter">
                    <option value="">All Treatments</option>
                    <option v-for="t in historyTreatmentOptions" :key="t" :value="t">{{ t || 'Unknown' }}</option>
                  </select>
                  <button class="btn btn-create ms-md-2" @click="exportHistory">Export as CSV</button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="row">
          <div class="col-lg-12 mb-4">
            <div class="card shadow-sm" ref="departmentsCard">
              <div class="card-header">
                <h5 class="mb-0">Browse Departments</h5>
              </div>
              <div class="card-body">
                <div class="table-responsive">
                  <table class="table table-hover align-middle">
                    <tbody>
                      <tr v-if="departments.length === 0">
                        <td class="text-center text-muted">No departments available.</td>
                      </tr>
                      <tr v-for="dept in departments" :key="dept.id">
                        <td>
                          <h6 class="mb-0">{{ dept.name }}</h6>
                        </td>
                        <td class="text-end">
                          <button class="btn btn-sm btn-view" @click="viewDepartment(dept)">
                            View Details
                          </button>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="row">
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
                        <th>Sr No.</th>
                        <th>Doctor Name</th>
                        <th>Department</th>
                        <th>Date</th>
                        <th>Time</th>
                        <th class="text-end">Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-if="upcomingAppointments.length === 0">
                        <td colspan="6" class="text-center text-muted">No upcoming appointments.</td>
                      </tr>
                      <tr v-for="appt in upcomingAppointments" :key="appt.id">
                        <td>{{ appt.id }}</td>
                        <td>{{ appt.doctor_name }}</td>
                        <td>{{ appt.department }}</td>
                        <td>{{ formatDate(appt.datetime) }}</td>
                        <td>{{ formatTime(appt.datetime) }}</td>
                        <td class="text-end">
                          <button class="btn btn-sm btn-delete" @click="cancelAppointment(appt.id)">Cancel</button>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div v-if="currentView === 'department'" class="card shadow-sm">
        <div class="card-header d-flex justify-content-between align-items-center">
          <h5 class="mb-0">Department of {{ selectedDepartment?.name }}</h5>
          <button class="btn-back" @click="currentView = 'dashboard'">&larr; Back to Dashboard</button>
        </div>
        <div class="card-body">
          <div class="department-overview mb-4">
            <h6>Overview</h6>
            <p>{{ selectedDepartment?.description || 'No description available for this department.' }}</p>
          </div>
          <hr>
          <h6>Doctors List</h6>
          <div class="table-responsive">
            <table class="table table-hover align-middle">
              <thead>
                <tr>
                  <th>Doctor Name</th>
                  <th>Email</th>
                  <th class="text-end">Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-if="doctorsInDepartment.length === 0">
                  <td colspan="3" class="text-center text-muted">No doctors found for this department.</td>
                </tr>
                <tr v-for="doctor in doctorsInDepartment" :key="doctor.id">
                  <td>{{ doctor.name }}</td>
                  <td>{{ doctor.email }}</td>
                  <td class="text-end">
                    <button class="btn btn-sm btn-view-profile me-2" @click="viewDoctorProfile(doctor)">
                      View Profile
                    </button>
                    <button class="btn btn-sm btn-create" @click="viewAvailability(doctor)">
                      Check Availability
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <div v-if="currentView === 'availability'" class="card shadow-sm">
        <div class="card-header d-flex justify-content-between align-items-center">
          <h5 class="mb-0">Availability for {{ selectedDoctor?.name }}</h5>
          <button class="btn-back" @click="currentView = 'department'">&larr; Back to Doctors</button>
        </div>
        <div class="card-body">
          <div v-if="Object.keys(groupedAvailability).length === 0" class="text-center text-muted">
            No available slots found for this doctor.
          </div>
          <div v-else>
            <div v-for="(slots, date) in groupedAvailability" :key="date" class="mb-4">
              <h6 class="mb-3">{{ formatDate(date, { weekday: 'long', month: 'long', day: 'numeric' }) }}</h6>
              <div class="availability-grid">
                <button
                  v-for="slot in slots"
                  :key="slot.iso"
                  class="btn slot-btn"
                  :class="{ 
                    'btn-primary': selectedSlot === slot.iso, 
                    'btn-outline-primary': selectedSlot !== slot.iso 
                  }"
                  @click="selectedSlot = slot.iso"
                >
                  {{ slot.time }}
                </button>
              </div>
            </div>
            <hr class="my-4">
            <div class="text-end">
              <button 
                class="btn btn-lg btn-success" 
                :disabled="!selectedSlot || isLoading" 
                @click="confirmBooking"
              >
                Book Selected Slot
              </button>
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
// Make user data reactive
const user = ref(props.user)

const emit = defineEmits(['logout', 'update:user'])

// --- Page State ---
const currentView = ref('dashboard') // 'dashboard', 'department', 'availability', 'history', 'doctorProfile'
const isLoading = ref(false)
const toast = ref(null)

// --- Data Refs ---
const departments = ref([])
const upcomingAppointments = ref([])
const historyCount = ref(0)
const patientHistory = ref([])
const doctorsInDepartment = ref([])
const doctorAvailability = ref([])

// --- Selection Refs ---
const selectedDepartment = ref(null)
const selectedDoctor = ref(null)
const selectedDoctorProfile = ref(null) // --- NEW: For the profile modal
const selectedSlot = ref(null)
const departmentsCard = ref(null) // For scrolling

// --- Edit Profile modal state ---
const editProfileModal = ref(false)
const editProfileForm = ref({ name: '', email: '', phone: '' })

// --- History filter refs (dropdowns) ---
const historyTreatmentFilter = ref('')
const historyTreatmentOptions = ref([]) // unique treatment/visit_type values from fetched history
const patientHistoryFiltered = computed(() => {
  const all = patientHistory.value || []
  let filtered = all.slice()
  if (historyTreatmentFilter.value) {
    filtered = filtered.filter(r => String(r.visit_type || '') === String(historyTreatmentFilter.value))
  }
  return filtered
})

// --- API Helper ---
async function fetchApi(endpoint, options = {}, isFile = false) {
  isLoading.value = true
  const token = localStorage.getItem('token');
  try {
    const response = await fetch(`http://127.0.0.1:8000${endpoint}`, {
      ...options,
      headers: {
        'Authorization': `Bearer ${token}`,
        ...(!isFile && {'Content-Type': 'application/json'}),
        ...options.headers,
      },
    });

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
      throw new Error(data.message || 'API call failed');
    }
    return data;
  } catch (error) {
    console.error(`API Error on ${endpoint}:`, error.message);
    toast.value = { message: `Error: ${error.message}`, type: 'danger' };
    throw error; // Re-throw to stop calling function
  } finally {
    isLoading.value = false
  }
}

// --- Load data on component mount ---
onMounted(() => {
  getDashboardData();
  // Also pre-fetch history to populate dropdowns
  preFetchHistory();
});

async function getDashboardData() {
  try {
    const data = await fetchApi('/api/patient/dashboard');
    departments.value = data.departments;
    upcomingAppointments.value = data.upcomingAppointments;
    historyCount.value = data.historyCount;
  } catch (error) {
    // Error is already handled by fetchApi
  }
}

// --- NEW: Pre-fetch history to populate filters ---
async function preFetchHistory() {
  try {
    const history = await fetchApi(`/api/patients/${user.value.id}/history`);
    patientHistory.value = history; // Save full history
    // populate treatment options
    const set = new Set()
    history.forEach(r => {
      set.add(r.visit_type || '')
    })
    historyTreatmentOptions.value = Array.from(set).filter(x => x !== null && x !== undefined && x !== '');
  } catch (error) {
    // Fails silently, will try again when user clicks "View History"
    console.error("Pre-fetch history failed:", error.message)
  }
}

// --- Date/Time Formatters ---
function formatDate(isoString, options = {}) {
  const dt = new Date(isoString);
  // Add timeZone to ensure consistency, as isoString without 'Z' is local
  return dt.toLocaleDateString('en-US', {
    timeZone: 'UTC', 
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    ...options
  });
}

function formatTime(isoString) {
  const dt = new Date(isoString);
  return dt.toLocaleTimeString([], { 
    timeZone: 'UTC', // Use UTC to match the ISO string
    hour: '2-digit', 
    minute: '2-digit' 
  });
}

function formatDateTime(isoString) {
  return `${formatDate(isoString)}, ${formatTime(isoString)}`;
}

// --- Computed Property for Availability ---
const groupedAvailability = computed(() => {
  const groups = {};
  doctorAvailability.value.forEach(slot => {
    const dt = new Date(slot.time);
    const date = dt.toISOString().split('T')[0]; // Group by YYYY-MM-DD
    const time = formatTime(dt);
    if (!groups[date]) groups[date] = [];
    groups[date].push({ iso: slot.time, time });
  });
  return groups;
});


// --- Component Functions ---

function editProfile() {
  // open edit modal and populate form with current user values
  editProfileForm.value = {
    name: user.value?.name || '',
    email: user.value?.email || '',
    phone: user.value?.phone || ''
  }
  editProfileModal.value = true
}

function closeEditProfile() {
  editProfileModal.value = false
}

async function submitEditProfile() {
  try {
    const payload = {
      name: editProfileForm.value.name,
      email: editProfileForm.value.email,
      phone: editProfileForm.value.phone
    }
    const data = await fetchApi('/api/patient/profile', {
      method: 'PUT',
      body: JSON.stringify(payload)
    })
    // Update local user and notify parent
    if (data && data.user) {
      user.value = data.user
      emit('update:user', data.user)
    }
    toast.value = { message: data.message || 'Profile updated', type: 'success' }
    editProfileModal.value = false
  } catch (err) {
    // fetchApi already sets toast; keep modal open for retry
  }
}

async function viewHistory() {
  try {
    // Data is already fetched, just open the modal
    if (patientHistory.value.length === 0) {
       await preFetchHistory(); // Try fetching again if it failed on load
    }
    currentView.value = 'history';
  } catch (error) {
    // Error handled by fetchApi
  }
}

// *** UPDATED: This function now calls the backend endpoint ***
async function exportHistory() {
  try {
    toast.value = { message: "Generating your report...", type: 'success' };
    
    // Call the backend API to generate and return the CSV file
    const blob = await fetchApi('/api/patient/export-history', {
      method: 'POST',
      body: JSON.stringify({
        treatment_filter: historyTreatmentFilter.value // Send the selected filter
      })
    }, true); // true = isFile

    // Create a link and click it to download the blob
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.style.display = 'none';
    a.href = url;
    a.download = `${(user.value && user.value.name) ? user.value.name.replace(/\s+/g, '_') : 'patient'}_treatment_history.csv`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    a.remove();
    
  } catch (error) {
    // Error handled by fetchApi (it will show a toast)
    // e.g., "No history to export for these filters"
  }
}

function bookAppointment() {
  // Scroll to the departments card
  departmentsCard.value?.scrollIntoView({ behavior: 'smooth' });
}

// *** UPDATED: This function now correctly parses the API response ***
async function viewDepartment(department) {
  try {
    // The API returns an object: { doctors: [], department: {} }
    const data = await fetchApi(`/api/departments/${department.id}/doctors`);
    
    // 1. Set the doctors list from the 'doctors' key
    doctorsInDepartment.value = data.doctors; 
    
    // 2. Set the selected department from the 'department' key
    selectedDepartment.value = data.department; 
    
    currentView.value = 'department';
  } catch (error) {
    // Error handled by fetchApi
  }
}

// --- *** NEW: Function to open profile modal *** ---
function viewDoctorProfile(doctor) {
  selectedDoctorProfile.value = doctor;
  currentView.value = 'doctorProfile';
}

async function viewAvailability(doctor) {
  try {
    selectedDoctor.value = doctor;
    selectedSlot.value = null; // Reset selection
    const availabilityData = await fetchApi(`/api/doctors/${doctor.id}/availability`);
    doctorAvailability.value = availabilityData;
    currentView.value = 'availability';
  } catch (error) {
    // Error handled by fetchApi
  }
}

async function confirmBooking() {
  if (!selectedSlot.value || !selectedDoctor.value) {
    toast.value = { message: 'Please select a time slot first.', type: 'danger' };
    return;
  }

  try {
    const payload = {
      doctor_id: selectedDoctor.value.id,
      datetime: selectedSlot.value
    };
    const data = await fetchApi('/api/appointments', {
      method: 'POST',
      body: JSON.stringify(payload)
    });
    
    toast.value = { message: data.message, type: 'success' };
    selectedSlot.value = null;
    currentView.value = 'dashboard';
    getDashboardData(); // Refresh the main dashboard

  } catch (error) {
    // Error (e.g., "slot no longer available") is handled by fetchApi
  }
}

async function cancelAppointment(appointmentId) {
  // Using confirm as it's not alert and is acceptable per guidelines
  if (confirm(`Are you sure you want to cancel appointment #${appointmentId}?`)) {
    try {
      const data = await fetchApi(`/api/appointments/${appointmentId}/cancel`, {
        method: 'PUT'
      });
      toast.value = { message: data.message, type: 'success' };
      getDashboardData(); // Refresh data
    } catch (error) {
      // Error handled by fetchApi
    }
  }
}
</script>

<style scoped>
/* Copied all styles from AdminDashboard.vue for UI consistency */
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
.logout-btn { background-color: #dc3545; color: white; border: none; padding: 0.4rem 1rem; border-radius: 8px; font-weight: 600; font-size: 0.9rem; }
.logout-btn:hover { background-color: #c82333 }

.nav-link {
  font-weight: 600;
  color: #555;
  font-size: 0.9rem;
  text-decoration: none;
  background: none;
  border: none;
  padding: 0;
}
.nav-link:hover { color: #0d6efd; }
.nav-divider { color: #ccc; font-size: 0.9rem; }

.stat-card { background: rgba(255,255,255,0.85); border-radius: 1rem; padding: 1.5rem; box-shadow: 0 4px 15px rgba(0,0,0,0.05); display:flex; justify-content:space-between }
.stat-card-title { font-size: 0.95rem; color:#555; font-weight:600; margin-bottom:0.25rem }
.stat-card-value { font-size:2.25rem; font-weight:700; color:#111 }
.stat-card-icon { font-size:2.5rem; opacity:0.5 }

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
.table tbody tr { background-color: #fcfcfc; }
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

/* Button Styles */
.btn-sm {
  font-size: 0.8rem;
  font-weight: 600;
  padding: 0.3rem 0.75rem;
  border-radius: 6px;
}
.btn-delete { background-color: #dc3545; color: white; }
.btn-view { background-color: #0d6efd; color: white; }
.btn-create { background-color: #198754; color: white; }
.btn-primary { font-weight: 600; }
.btn-lg { font-weight: 600; }
.btn-success { font-weight: 600; }
.btn-view-profile {
  background-color: #6f42c1;
  color: white;
}


/* NEW STYLES for Modals, Navigation, and Loaders */
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
  align-items: center;
  justify-content: center;
  z-index: 9998;
  padding: 1rem;
}

.modal-content {
  width: 90%;
  max-width: 600px;
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
.form-select-sm {
  padding-top: 0.5rem;
  padding-bottom: 0.5rem;
  padding-left: 0.75rem;
  font-size: .875rem;
}


.history-record {
  border-left: 4px solid #0d6efd;
}

.btn-back {
  background: none;
  border: none;
  font-weight: 600;
  color: #555;
  font-size: 0.9rem;
}
.btn-back:hover {
  color: #0d6efd;
  text-decoration: underline;
}

.availability-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
  gap: 0.75rem;
}

.slot-btn {
  font-weight: 600;
}

/* *** NEW: Department Overview Style *** */
.department-overview {
  background-color: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 0.5rem;
  padding: 1.25rem;
}
.department-overview h6 {
  font-weight: 700;
  color: #333;
}
.department-overview p {
  color: #555;
  margin-bottom: 0;
}

/* *** NEW: Doctor Profile Modal Styles *** */
.profile-details p {
  margin-bottom: 0.25rem;
  color: #333;
}
.profile-details strong {
  display: block;
  color: #777;
  font-size: 0.85rem;
  text-transform: uppercase;
  margin-bottom: 0.1rem;
}

</style>