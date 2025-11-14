<template>
  <div class="hero-bg-admin">
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

    <main class="container-fluid mt-4 admin-content admin-main-content">
      
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
        <div class="col-12 mb-4">
          <div class="card shadow-sm">
            <div class="card-body d-flex flex-column flex-md-row justify-content-between align-items-center text-center text-md-start">
              <div>
                <h5 class="card-title mb-1" style="font-weight: 700;">Set Your Availability</h5>
                <p class="text-muted mb-0">Let patients know when you're available for the next 7 days.</p>
              </div>
              <button class="btn btn-create btn-lg mt-3 mt-md-0" @click="setAvailability">
                Provide Availability
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
                      <th>Patient History</th>
                      <th class="text-end">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-if="upcomingAppointments.length === 0">
                      <td colspan="5" class="text-center text-muted">No upcoming appointments.</td>
                    </tr>
                    <tr v-for="appt in upcomingAppointments" :key="appt.id">
                      <td>{{ appt.id }}</td>
                      <td>{{ appt.patient_name }}</td>
                      <td>{{ new Date(appt.datetime).toLocaleString() }}</td>
                      <td>
                        <button class="btn btn-sm btn-view-history" @click="viewHistory(appt.patient_id, appt.patient_name)">
                          View
                        </button>
                      </td>
                      <td class="text-end">
                        <button class="btn btn-sm btn-edit me-1" @click="updateHistory(appt)">Update</button>
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
import { ref, onMounted } from 'vue' // Import onMounted
import logo from '../assets/Logo.png' 

const props = defineProps({ user: Object })
const user = props.user

const emit = defineEmits(['logout'])

// --- Use refs for dynamic data ---
const upcomingAppointments = ref([])
const assignedPatients = ref([])

// --- Helper function for API calls ---
async function fetchApi(endpoint, options = {}) {
  const token = localStorage.getItem('token');
  const response = await fetch(`http://127.0.0.1:8000${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
      ...options.headers,
    },
  });

  if (response.status === 401) {
    // Token is invalid or expired, force logout
    emit('logout');
    throw new Error('Unauthorized');
  }
  
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.message || 'API call failed');
  }
  return data;
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
  } catch (error) {
    console.error('Failed to load dashboard data:', error.message);
    alert('Failed to load dashboard data. Please log in again.');
  }
}

// --- Component Functions ---
async function setAvailability() {
  alert('Opening "Set Availability" modal... (API placeholder)');
  // In a real app, this would open a modal
  // For now, we'll just call the placeholder API
  try {
    const data = await fetchApi('/api/doctor/availability', { method: 'POST' });
    alert(data.message);
  } catch (error) {
    alert(`Error: ${error.message}`);
  }
}

async function viewHistory(patientId, patientName) {
  try {
    const history = await fetchApi(`/api/patients/${patientId}/history`);
    // In a real app, you'd show this in a modal
    // For now, we'll just alert the summary
    if (history.length === 0) {
      alert(`No history found for ${patientName}.`);
    } else {
      alert(`Found ${history.length} past records for ${patientName}.`);
      console.log(history);
    }
  } catch (error) {
    alert(`Error fetching history: ${error.message}`);
  }
}

async function updateHistory(appointment) {
  // Use prompts to get info, as required by project doc
  const diagnosis = prompt("Enter Diagnosis:", appointment.diagnosis || "");
  const treatment_notes = prompt("Enter Treatment Notes:", appointment.treatment_notes || "");
  
  if (diagnosis === null || treatment_notes === null) {
    alert("Update cancelled.");
    return;
  }

  try {
    const data = await fetchApi(`/api/appointments/${appointment.id}/history`, {
      method: 'PUT',
      body: JSON.stringify({ diagnosis, treatment_notes }),
    });
    alert(data.message);
    // Refresh dashboard data
    getDashboardData();
  } catch (error) {
    alert(`Error: ${error.message}`);
  }
}

async function markComplete(appointmentId) {
  if (confirm(`Mark appointment #${appointmentId} as complete?`)) {
    try {
      const data = await fetchApi(`/api/appointments/${appointmentId}/complete`, {
        method: 'PUT',
      });
      alert(data.message);
      // Refresh dashboard data by removing the completed appointment
      upcomingAppointments.value = upcomingAppointments.value.filter(
        (appt) => appt.id !== appointmentId
      );
    } catch (error) {
      alert(`Error: ${error.message}`);
    }
  }
}

async function cancelAppointment(appointmentId) {
  if (confirm(`Are you sure you want to cancel appointment #${appointmentId}?`)) {
    try {
      const data = await fetchApi(`/api/appointments/${appointmentId}/cancel`, {
        method: 'PUT',
      });
      alert(data.message);
      // Refresh dashboard data by removing the cancelled appointment
      upcomingAppointments.value = upcomingAppointments.value.filter(
        (appt) => appt.id !== appointmentId
      );
    } catch (error) {
      alert(`Error: ${error.message}`);
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
/* Green button */
.btn-create {
  background-color: #198754;
  color: white;
}
/* Yellow button */
.btn-edit {
  background-color: #ffc107;
  color: #333;
}
/* Red button */
.btn-delete {
  background-color: #dc3545;
  color: white;
}
/* Blue button */
.btn-view {
  background-color: #0d6efd;
  color: white;
}
/* Light blue button (for wireframe "update") */
.btn-view-history {
  background-color: #0dcaf0;
  color: white;
}
.btn-lg {
  font-weight: 600;
}
</style>