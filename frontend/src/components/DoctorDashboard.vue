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

    <div v-if="currentView === 'setAvailability'" class="modal-overlay" @click.self="currentView = 'dashboard'">
      <div class="modal-content card shadow-lg">
        <div class="card-header d-flex justify-content-between align-items-center">
          <h5 class="mb-0">Set Your Availability</h5>
          <button @click="currentView = 'dashboard'" class="btn-close" aria-label="Close"></button>
        </div>
        <div class="card-body"> 
          <p class="text-muted text-center mb-3">
            You are setting availability for the <strong>{{ doctorInfo.department }}</strong> department.
            Select the time blocks you will be available for the next 7 days.
          </p>
          
          <div class="row d-none d-md-flex fw-bold text-center text-muted mb-2 px-2">
            <div class="col-md-4 text-start">Date</div>
            <div class="col-md-4">Morning</div>
            <div class="col-md-4">Evening</div>
          </div>

          <div v-for="slot in availabilitySlots" :key="slot.date" class="row g-2 mb-2 align-items-center availability-row px-2">
            <div class="col-md-4">
              <div class="p-2 rounded bg-light text-dark h-100 d-flex flex-column justify-content-center date-col">
                <strong>{{ slot.dayName }}</strong>
                <div class="small">{{ slot.date }}</div>
              </div>
            </div>
            <div class="col-6 col-md-4">
              <button 
                class="btn w-100 h-100 slot-toggle-btn"
                :class="slot.morning ? 'btn-success' : (slot.morningDisabled ? 'btn-secondary disabled' : 'btn-outline-secondary')"
                :disabled="slot.morningDisabled"
                @click="toggleSlot(slot, 'morning')">
                <span class="d-md-none small">Morning</span>
                <span class="d-none d-md-inline">8:00 AM - 12:00 PM</span>
                <span v-if="slot.morningDisabled" class="badge bg-danger ms-2">Booked</span>
              </button>
            </div>
            <div class="col-6 col-md-4">
              <button 
                class="btn w-100 h-100 slot-toggle-btn"
                :class="slot.evening ? 'btn-success' : (slot.eveningDisabled ? 'btn-secondary disabled' : 'btn-outline-secondary')"
                :disabled="slot.eveningDisabled"
                @click="toggleSlot(slot, 'evening')">
                <span class="d-md-none small">Evening</span>
                <span class="d-none d-md-inline">4:00 PM - 9:00 PM</span>
                <span v-if="slot.eveningDisabled" class="badge bg-danger ms-2">Booked</span>
              </button>
            </div>
          </div>

            <div class="d-flex justify-content-end gap-2 mt-4 px-2">
            <button class="btn btn-secondary" @click="currentView = 'dashboard'">Cancel</button>
            <button class="btn btn-primary" :disabled="isLoading" @click="saveAvailability">Save Availability</button>
          </div>
        </div>
      </div>
    </div>

    <div v-if="currentView === 'updateHistory'" class="modal-overlay" @click.self="closeHistoryModal">
      <div class="modal-content card shadow-lg">
        <div class="card-header d-flex justify-content-between align-items-center">
          <h5 class="mb-0">Update Patient History</h5>
          <button @click="closeHistoryModal" class="btn-close" aria-label="Close"></button>
        </div>
        <div class="card-body"> 
          <div class="patient-info-header">
            <div>
              <strong>Patient:</strong> {{ editingAppointment?.patient_name }}
            </div>
            <div>
              <strong>Department:</strong> {{ doctorInfo.department }}
            </div>
          </div>
          <form @submit.prevent="submitHistoryUpdate">
            <div class="row">
              <div class="col-md-6 mb-3">
                <label for="visit_type" class="form-label">Visit Type</label>
                <input type="text" class="form-control" id="visit_type" v-model="historyForm.visit_type">
              </div>
              <div class="col-md-6 mb-3">
                <label for="test_done" class="form-label">Test Done</label>
                <input type="text" class="form-control" id="test_done" v-model="historyForm.test_done">
              </div>
            </div>
            <div class="mb-3">
              <label for="diagnosis" class="form-label">Diagnosis</label>
              <textarea class="form-control" id="diagnosis" rows="2" v-model="historyForm.diagnosis"></textarea>
            </div>
            <div class="mb-3">
              <label for="prescription" class="form-label">Prescription / Treatment Notes</label>
              <textarea class="form-control" id="prescription" rows="3" v-model="historyForm.prescription"></textarea>
            </div>
            <div class="mb-3">
              <label for="medicines" class="form-label">Medicines (e.g., "Paracetamol 1-0-1")</label>
              <textarea class="form-control" id="medicines" rows="3" v-model="historyForm.medicines" placeholder="One medicine per line..."></textarea>
            </div>
            <div class="d-flex justify-content-end gap-2 mt-4">
              <button type="button" class="btn btn-secondary" @click="closeHistoryModal">Cancel</button>
              <button type="submit" class="btn btn-primary" :disabled="isLoading">Save History</button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <div v-if="currentView === 'editProfile'" class="modal-overlay" @click.self="currentView = 'dashboard'">
      <div class="modal-content card shadow-lg">
        <div class="card-header d-flex justify-content-between align-items-center">
          <h5 class="mb-0">Edit Your Profile</h5>
          <button @click="currentView = 'dashboard'" class="btn-close" aria-label="Close"></button>
        </div>
        <div class="card-body"> 
          <form @submit.prevent="saveProfile">
            <div class="mb-3">
              <label for="profile-name" class="form-label">Your Name</label>
              <input type="text" class="form-control" id="profile-name" v-model="profileForm.name">
            </div>
            <div class="mb-3">
              <label for="profile-spec" class="form-label">Specialization Details</label>
              <input type="text" class="form-control" id="profile-spec" v-model="profileForm.specialization_details" :placeholder="doctorInfo.department">
            </div>
            <div class="mb-3">
              <label for="profile-exp" class="form-label">Years of Experience</label>
              <input type="number" class="form-control" id="profile-exp" v-model.number="profileForm.experience_years">
            </div>
            <div class="mb-3">
              <label for="profile-edu" class="form-label">Education / Qualifications</label>
              <input type="text" class="form-control" id="profile-edu" v-model="profileForm.education" placeholder="e.g., MBBS, MD">
            </div>
            <div class="mb-3">
              <label for="profile-bio" class="form-label">Biography</label>
              <textarea class="form-control" id="profile-bio" rows="4" v-model="profileForm.bio" placeholder="Write a short bio..."></textarea>
            </div>
            
            <div class="d-flex justify-content-end gap-2 mt-4">
              <button type="button" class="btn btn-secondary" @click="currentView = 'dashboard'">Cancel</button>
              <button type="submit" class="btn btn-primary" :disabled="isLoading">Save Profile</button>
            </div>
          </form>
        </div>
      </div>
    </div>


    <nav class="top-nav">
      <div class="container-fluid d-flex align-items-center">
        <div class="left-actions d-flex align-items-center justify-content-start" style="flex: 1;">
            <span class="nav-title ms-2">Doctors' Dashboard</span>
        </div>
        <div class="nav-center d-flex align-items-center justify-content-center">
          <img :src="logo" alt="logo" class="logo-img" />
        </div>
        <div class="right-actions d-flex align-items-center justify-content-end" style="flex:1">
          <span class="user-name me-3">Welcome, {{ user?.name || 'Doctor' }}</span>
          <button @click="$emit('logout')" class="logout-btn">Logout</button>
        </div>
      </div>
    </nav>

    <main class="container-fluid mt-4 admin-content admin-main-content" v-if="currentView === 'dashboard'">
      
      <div class="row">
        <div class="col-md-6 mb-4">
          <div class="stat-card">
            <div class="stat-card-body">
              <div class="stat-card-title">Upcoming Appointments</div>
              <div class="stat-card-value">{{ upcomingAppointments.length }}</div>
            </div>
            <div class="stat-card-icon">📅</div>
          </div>
        </div>
        <div class="col-md-6 mb-4">
          <div class="stat-card">
            <div class="stat-card-body">
              <div class="stat-card-title">Assigned Patients</div>
              <div class="stat-card-value">{{ assignedPatients.length }}</div>
            </div>
            <div class="stat-card-icon">👤</div>
          </div>
        </div>
      </div>

      <div class="row">
        <div class="col-md-6 mb-4">
          <div class="card shadow-sm h-100">
            <div class="card-body d-flex flex-column justify-content-between text-center">
              <div>
                <h5 class="card-title mb-1" style="font-weight: 700;">Set Your Availability</h5>
                <p class="text-muted mb-0">Manage your schedule for the next 7 days.</p>
              </div>
              <button class="btn btn-create btn-lg mt-3" @click="openAvailabilityModal">
                Provide Availability
              </button>
            </div>
          </div>
        </div>
        <div class="col-md-6 mb-4">
          <div class="card shadow-sm h-100">
            <div class="card-body d-flex flex-column justify-content-between text-center">
              <div>
                <h5 class="card-title mb-1" style="font-weight: 700;">Update Your Profile</h5>
                <p class="text-muted mb-0">Update your bio, experience, and education.</p>
              </div>
              <button class="btn btn-primary btn-lg mt-3" @click="openProfileModal">
                Edit Profile
              </button>
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
                      <th>Patient Name</th>
                      <th>Date & Time</th>
                      <!-- *** REMOVED "Patient History" COLUMN *** -->
                      <th class="text-end">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-if="upcomingAppointments.length === 0">
                      <!-- *** UPDATED colspan to 4 *** -->
                      <td colspan="4" class="text-center text-muted">No upcoming appointments.</td>
                    </tr>
                    <tr v-for="appt in upcomingAppointments" :key="appt.id">
                      <td>{{ appt.id }}</td>
                      <td>{{ appt.patient_name }}</td>
                      <!-- *** UPDATED: toLocaleString() is cleaner *** -->
                      <td>{{ new Date(appt.datetime).toLocaleString('en-IN', { dateStyle: 'short', timeStyle: 'short', timeZone: 'UTC' }) }}</td>
                      <!-- *** REMOVED "View" button cell *** -->
                      <td class="text-end">
                        <button class="btn btn-sm btn-edit me-1" @click="openHistoryModal(appt)">Update</button>
                        <button class="btn btn-sm btn-create me-1" @click="markComplete(appt.id)">Mark as Complete</button>
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

      <div class="row">
        <div class="col-lg-12 mb-4">
          <div class="card shadow-sm">
            <div class="card-header">
              <h5 class="mb-0">Assigned Patients</h5>
            </div>
            <div class="card-body">
              <div class="table-responsive">
                <table class="table table-hover align-middle">
                  <thead>
                    <tr>
                      <th>Patient Name</th>
                      <th>Email</th>
                      <th class="text-end">View History</th>
                    </tr>
                  </thead>
                  <tbody>
                     <tr v-if="assignedPatients.length === 0">
                      <td colspan="3" class="text-center text-muted">No patients assigned yet.</td>
                    </tr>
                    <tr v-for="patient in assignedPatients" :key="patient.id">
                      <td>{{ patient.name }}</td>
                      <td>{{ patient.email }}</td>
                      <td class="text-end">
                        <button class="btn btn-sm btn-view" @click="viewHistory(patient.id, patient.name)">View</button>
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
import { ref, onMounted } from 'vue'
import logo from '../assets/Logo.png' 
import ToastNotification from './ToastNotification.vue'

const props = defineProps({ user: Object })
const user = props.user

const emit = defineEmits(['logout'])

// --- Use refs for dynamic data ---
const upcomingAppointments = ref([])
const assignedPatients = ref([])
const doctorInfo = ref({}) // To store doctor's own info, like department

// --- Page State ---
const currentView = ref('dashboard') // 'dashboard', 'setAvailability', 'updateHistory', 'editProfile'
const isLoading = ref(false)
const toast = ref(null)
const availabilitySlots = ref([]) // For the 7-day modal

// --- NEW: Helper function to check for existing bookings ---
function slotHasBookingOnPeriod(dateString, period) {
  try {
    const appts = upcomingAppointments.value || []
    return appts.some(a => {
      if (!a.datetime) return false
      const d = new Date(a.datetime)
      // Convert appointment UTC time to YYYY-MM-DD string
      const apptDateStr = d.toISOString().split('T')[0]
      if (apptDateStr !== dateString) return false
      
      const h = d.getUTCHours()
      if (period === 'morning') return h >= 8 && h < 12 // 8:00 - 11:59
      if (period === 'evening') return h >= 16 && h < 21 // 16:00 - 20:59
      return false
    })
  } catch (e) {
    console.error("Error checking slot booking:", e)
    return false
  }
}

// --- Refs for Update History Modal ---
const editingAppointment = ref(null)
const historyForm = ref({
  diagnosis: '',
  prescription: '',
  visit_type: '',
  test_done: '',
  medicines: ''
})

// --- Refs for Edit Profile Modal ---
const profileForm = ref({
  name: '',
  bio: '',
  specialization_details: '',
  experience_years: 0,
  education: ''
})


// --- Helper function for API calls ---
async function fetchApi(endpoint, options = {}) {
  isLoading.value = true;
  const token = localStorage.getItem('token');
  try {
    const response = await fetch(`http://127.0.0.1:8000${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
        ...options.headers,
      },
    });

    if (response.status === 401) {
      emit('logout');
      throw new Error('Unauthorized');
    }
    
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.message || 'API call failed');
    }
    return data;
  } catch (error) {
    toast.value = { message: `Error: ${error.message}`, type: 'danger' };
    throw error; // Propagate error
  } finally {
    isLoading.value = false;
  }
}

// --- Fetch data when component is loaded ---
onMounted(() => {
  getDashboardData();
});

async function getDashboardData() {
  try {
    const data = await fetchApi('/api/doctor/dashboard');
    upcomingAppointments.value = data.upcomingAppointments;
    assignedPatients.value = data.assignedPatients;
    doctorInfo.value = data.doctorInfo; // Store doctor's info
  } catch (error) {
    console.error('Failed to load dashboard data:', error.message);
    // Toast is already shown by fetchApi
  }
}

// --- Component Functions ---
async function openAvailabilityModal() {
  try {
    // 1. Fetch the doctor's currently saved availability blocks
    // *** FIXED: Calling the correct /blocks endpoint ***
    const savedAvailability = await fetchApi('/api/doctor/availability/blocks');
    
    const today = new Date();
    const slots = [];
    
    // 2. Generate the 7-day template
    for (let i = 0; i < 7; i++) {
      const day = new Date(today);
      day.setDate(today.getDate() + i + 1); // Start from tomorrow
      const dateString = day.toISOString().split('T')[0]; // YYYY-MM-DD
      
      // 3. Check if saved data has blocks for this date
      const morningBlock = savedAvailability.find(b => 
        b.start_time.startsWith(dateString) && new Date(b.start_time).getUTCHours() === 8
      );
      const eveningBlock = savedAvailability.find(b => 
        b.start_time.startsWith(dateString) && new Date(b.start_time).getUTCHours() === 16
      );

      // 4. NEW: Check if there are appointments in those periods
      const morningDisabled = slotHasBookingOnPeriod(dateString, 'morning')
      const eveningDisabled = slotHasBookingOnPeriod(dateString, 'evening')

      // 5. Create the slot with the toggles pre-set
      slots.push({
        date: dateString,
        dayName: day.toLocaleDateString('en-US', { weekday: 'long' }),
        morning: !!morningBlock,
        evening: !!eveningBlock,
        morningDisabled, // Disable if booked
        eveningDisabled  // Disable if booked
      });
    }
    
    // 6. Update the UI
    availabilitySlots.value = slots;
    currentView.value = 'setAvailability';

  } catch (error) {
    console.error("Failed to open availability modal:", error);
  }
}


async function saveAvailability() {
  try {
    // send only date+morning/evening booleans to backend
    const payloadSlots = availabilitySlots.value.map(s => ({ date: s.date, morning: !!s.morning, evening: !!s.evening }))
    const data = await fetchApi('/api/doctor/availability', {
      method: 'POST',
      body: JSON.stringify({ slots: payloadSlots })
    });
    toast.value = { message: data.message, type: 'success' };
    currentView.value = 'dashboard';
    getDashboardData(); // Refresh upcoming appointments
  } catch (error) {
    // Toast is already shown by fetchApi
  }
}

// --- UPDATED: Shows toast alert if slot is disabled ---
function toggleSlot(slot, period) {
  // prevent toggling if disabled (booked)
  if (period === 'morning' && slot.morningDisabled) {
    toast.value = { message: 'Cannot remove morning availability: slot already has bookings.', type: 'info' }
    return
  }
  if (period === 'evening' && slot.eveningDisabled) {
    toast.value = { message: 'Cannot remove evening availability: slot already has bookings.', type: 'info' }
    return
  }
  // This will toggle the value
  slot[period] = !slot[period]
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
  } catch (error) {
    // Toast is already shown by fetchApi
  }
}

function openHistoryModal(appointment) {
  editingAppointment.value = appointment;
  
  // *** THIS IS THE FIX ***
  // Populate form with the correctly parsed data
  historyForm.value.diagnosis = appointment.diagnosis || '';
  historyForm.value.prescription = appointment.prescription || ''; // This is now the text field
  historyForm.value.visit_type = appointment.visit_type || ''; 
  historyForm.value.test_done = appointment.test_done || '';
  historyForm.value.medicines = (appointment.medicines || []).join('\n'); // This is now the array

  currentView.value = 'updateHistory';
}

function closeHistoryModal() {
  currentView.value = 'dashboard';
  editingAppointment.value = null;
  historyForm.value = { diagnosis: '', prescription: '', visit_type: '', test_done: '', medicines: '' };
}

async function submitHistoryUpdate() {
  if (!editingAppointment.value) return;

  try {
    // We send all fields, including the new ones
    const payload = {
      diagnosis: historyForm.value.diagnosis,
      prescription: historyForm.value.prescription,
      treatment_notes: historyForm.value.prescription, // Use prescription as notes
      visit_type: historyForm.value.visit_type,
      test_done: historyForm.value.test_done,
      medicines: historyForm.value.medicines.split('\n').filter(m => m.trim() !== '')
    };

    const data = await fetchApi(`/api/appointments/${editingAppointment.value.id}/history`, {
      method: 'PUT',
      body: JSON.stringify(payload),
    });
    
    toast.value = { message: data.message, type: 'success' };
    closeHistoryModal(); // Close modal and clear form
    getDashboardData(); // Refresh data
    
  } catch (error) {
    // Toast is already shown by fetchApi
  }
}

// --- Profile Modal Functions ---
function openProfileModal() {
  // Load current profile data from doctorInfo into the form
  profileForm.value = {
    name: doctorInfo.value.name || user.name,
    bio: doctorInfo.value.bio || '',
    specialization_details: doctorInfo.value.specialization_details || '',
    experience_years: doctorInfo.value.experience_years || 0,
    education: doctorInfo.value.education || ''
  };
  currentView.value = 'editProfile';
}

async function saveProfile() {
  try {
    const data = await fetchApi('/api/doctor/profile', {
      method: 'PUT',
      body: JSON.stringify(profileForm.value)
    });
    
    toast.value = { message: data.message, type: 'success' };
    doctorInfo.value = data.doctorInfo; // Update local doctorInfo with saved data
    currentView.value = 'dashboard'; // Close modal
    
  } catch (error) {
    // Toast is already shown by fetchApi
  }
}


async function markComplete(appointmentId) {
  if (confirm(`Mark appointment #${appointmentId} as complete?`)) {
    try {
      const data = await fetchApi(`/api/appointments/${appointmentId}/complete`, {
        method: 'PUT',
      });
      toast.value = { message: data.message, type: 'success' };
      getDashboardData(); // Refresh list
    } catch (error) {
      // Toast is already shown by fetchApi
    }
  }
}

async function cancelAppointment(appointmentId) {
  if (confirm(`Are you sure you want to cancel appointment #${appointmentId}?`)) {
    try {
      const data = await fetchApi(`/api/appointments/${appointmentId}/cancel`, {
        method: 'PUT',
      });
      toast.value = { message: data.message, type: 'success' };
      getDashboardData(); // Refresh list
    } catch (error) {
      // Toast is already shown by fetchApi
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
.logout-btn { background-color: #dc3545; color: white; border: none; padding: 0.4rem 1rem; border-radius: 8px; font-weight: 600 }
.logout-btn:hover { background-color: #c82333 }

.stat-card { background: rgba(255,255,252,0.85); border-radius: 1rem; padding: 1.5rem; box-shadow: 0 4px 15px rgba(0,0,0,0.05); display:flex; justify-content:space-between }
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

/* Action Button Styles */
.btn-sm {
  font-size: 0.8rem;
  font-weight: 600;
  padding: 0.3rem 0.75rem;
  border-radius: 6px;
}
.btn-create { background-color: #198754; color: white; }
.btn-edit { background-color: #ffc107; color: #333; }
.btn-delete { background-color: #dc3545; color: white; }
.btn-view { background-color: #0d6efd; color: white; }
.btn-view-history { background-color: #0dcaf0; color: white; }
.btn-lg { font-weight: 600; }
.btn-primary { font-weight: 600; }

/* UPDATED: Modal & Availability Styles */
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
  width: 90%;
  max-width: 800px; /* Wider modal */
}

.availability-row {
  min-height: 70px; /* Give rows some height */
}

.slot-toggle-btn {
  font-weight: 600;
  padding: 0.75rem 0.5rem;
  font-size: 0.9rem;
  height: 100%; /* Fill the column height */
}
.slot-toggle-btn .badge {
  font-size: 0.7em;
  vertical-align: middle;
}

.date-col {
  background-color: #f8f9fa !important;
  border: 1px solid #e9ecef;
  text-align: center;
}

/* Responsive adjustment for date column on mobile */
@media (max-width: 767.98px) {
  .date-col {
    text-align: center;
    padding: 0.5rem !important;
  }
  .slot-toggle-btn {
    padding: 0.75rem 0.25rem;
  }
}

/* *** NEW: Styles for History Modal *** */
.patient-info-header {
  background-color: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 0.5rem;
  padding: 0.75rem 1.25rem;
  margin-bottom: 1.5rem;
  display: flex;
  justify-content: space-between;
  font-weight: 600;
}

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
</style>