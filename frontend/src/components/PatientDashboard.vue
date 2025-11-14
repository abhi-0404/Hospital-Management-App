<template>
  <div class="hero-bg-admin">
    <!-- This component will show pop-up alerts -->
    <ToastNotification 
      v-if="toast"
      :message="toast.message" 
      :type="toast.type"
      @close="toast = null"
    />

    <!-- 1. Top Navigation Bar (Consistent with Admin/Doctor) -->
    <nav class="top-nav">
      <div class="container-fluid d-flex align-items-center">

        <!-- Left: Title -->
        <div class="left-actions d-flex align-items-center justify-content-start" style="flex: 1;">
            <span class="nav-title ms-2">Patients' Dashboard</span>
        </div>

        <!-- Center: Logo -->
        <div class="nav-center d-flex align-items-center justify-content-center">
          <img :src="logo" alt="logo" class="logo-img" />
        </div>

        <!-- Right: User & Actions (from wireframe) -->
        <div class="right-actions d-flex align-items-center justify-content-end" style="flex:1">
          <span class="user-name me-3">Welcome, {{ user?.name || 'Patient' }}</span>
          <!-- Profile Links from wireframe -->
          <a href="#" class="nav-link me-2" @click.prevent="editProfile">Edit Profile</a>
          <span class="nav-divider">|</span>
          <button @click="$emit('logout')" class="logout-btn ms-2">Logout</button>
        </div>
      </div>
    </nav>

    <!-- 2. Main Scrolling Content Area -->
    <main class="container-fluid mt-4 admin-content admin-main-content">
      
      <!-- Stat Cards -->
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
              <div class="stat-card-title">Past Treatments</div>
              <div class="stat-card-value">{{ historyCount }}</div>
            </div>
            <div class="stat-card-icon">🩺</div>
          </div>
        </div>
      </div>

      <!-- Action Cards: Book & History -->
      <div class="row">
        <div class="col-lg-6 mb-4">
          <div class="card shadow-sm h-100">
            <div class="card-body d-flex flex-column justify-content-between text-center">
              <div>
                <h5 class="card-title mb-1" style="font-weight: 700;">Book a New Appointment</h5>
                <p class="text-muted">Browse doctors by department and schedule your next visit.</p>
              </div>
              <button class="btn btn-primary btn-lg mt-3" @click="bookAppointment">
                Book Now
              </button>
            </div>
          </div>
        </div>
        <div class="col-lg-6 mb-4">
          <div class="card shadow-sm h-100">
            <div class="card-body d-flex flex-column justify-content-between text-center">
              <div>
                <h5 class="card-title mb-1" style="font-weight: 700;">Treatment History</h5>
                <p class="text-muted">View your past diagnoses and prescriptions.</p>
              </div>
              <div class="d-grid gap-2 d-md-block mt-3">
                <button class="btn btn-view" @click="viewHistory">View History</button>
                <button class="btn btn-create ms-md-2" @click="exportHistory">Export as CSV</button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Departments List (from wireframe) -->
      <div class="row">
        <div class="col-lg-12 mb-4">
          <div class="card shadow-sm">
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

      <!-- Upcoming Appointments Table (from wireframe) -->
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
                      <td>{{ new Date(appt.datetime).toLocaleDateString() }}</td>
                      <td>{{ new Date(appt.datetime).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) }}</td>
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
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import logo from '../assets/Logo.png'
import ToastNotification from './ToastNotification.vue'

const props = defineProps({ user: Object })
// Make user data reactive
const user = ref(props.user)

const emit = defineEmits(['logout', 'update:user']) // Add update event

// --- Dynamic Data Refs ---
const departments = ref([])
const upcomingAppointments = ref([])
const historyCount = ref(0)
const toast = ref(null)

// --- API Helper ---
async function fetchApi(endpoint, options = {}, isFile = false) {
  const token = localStorage.getItem('token');
  const response = await fetch(`http://127.0.0.1:8000${endpoint}`, {
    ...options,
    headers: {
      'Authorization': `Bearer ${token}`,
      ...(!isFile && {'Content-Type': 'application/json'}), // Don't set content-type for file downloads
      ...options.headers,
    },
  });

  if (response.status === 401) {
    emit('logout');
    throw new Error('Unauthorized');
  }

  if (isFile) {
    if (!response.ok) {
       const err = await response.json();
      throw new Error(err.message || 'File download failed');
    }
    return response.blob(); // Return the file blob
  }
  
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.message || 'API call failed');
  }
  return data;
}

// --- Load data on component mount ---
onMounted(() => {
  getDashboardData();
});

async function getDashboardData() {
  try {
    const data = await fetchApi('/api/patient/dashboard');
    departments.value = data.departments;
    upcomingAppointments.value = data.upcomingAppointments;
    historyCount.value = data.historyCount;
  } catch (error) {
    console.error('Failed to load dashboard data:', error.message);
    toast.value = { message: `Failed to load dashboard: ${error.message}`, type: 'danger' };
  }
}

// --- Component Functions ---

async function editProfile() {
  const newName = prompt("Enter your new name:", user.value.name);
  if (newName && newName !== user.value.name) {
    try {
      const data = await fetchApi('/api/patient/profile', {
        method: 'PUT',
        body: JSON.stringify({ name: newName })
      });
      user.value.name = data.user.name; // Update local user name
      emit('update:user', data.user); // Inform App.vue of the change
      toast.value = { message: data.message, type: 'success' };
    } catch (error) {
      toast.value = { message: `Error: ${error.message}`, type: 'danger' };
    }
  }
}

async function viewHistory() {
  try {
    const history = await fetchApi(`/api/patients/${user.value.id}/history`);
    if (history.length === 0) {
      toast.value = { message: "You have no past treatment history.", type: 'success' };
    } else {
      toast.value = { message: `Found ${history.length} past records. Check console for details.`, type: 'success' };
      console.log("Patient History:", history);
      // In a real app, you would open a modal here and pass `history` as a prop
    }
  } catch (error) {
    toast.value = { message: `Error: ${error.message}`, type: 'danger' };
  }
}

async function exportHistory() {
  try {
    toast.value = { message: "Generating your report...", type: 'success' };
    const blob = await fetchApi('/api/patient/export-history', {
      method: 'POST'
    }, true); // true = isFile

    // Create a link and click it to download the file
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.style.display = 'none';
    a.href = url;
    a.download = `${user.value.name}_treatment_history.csv`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    a.remove();
    
  } catch (error)
{
    toast.value = { message: `Error exporting history: ${error.message}`, type: 'danger' };
  }
}

function bookAppointment() {
  alert('Navigating to "Book Appointment" page... (Not implemented yet)');
  // Here you would emit an event to App.vue to change the view
  // emit('navigate', 'book-appointment');
}

function viewDepartment(department) {
  alert(`Viewing details for ${department.name}... (Not implemented yet)`);
  // Here you would emit an event to App.vue to show a new view/modal
  // emit('view-department', department.id);
}

async function cancelAppointment(appointmentId) {
  if (confirm(`Are you sure you want to cancel appointment #${appointmentId}?`)) {
    try {
      const data = await fetchApi(`/api/appointments/${appointmentId}/cancel`, {
        method: 'PUT'
      });
      toast.value = { message: data.message, type: 'success' };
      // Refresh data
      getDashboardData();
    } catch (error) {
      toast.value = { message: `Error: ${error.message}`, type: 'danger' };
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

/* Nav link styles */
.nav-link {
  font-weight: 600;
  color: #555;
  font-size: 0.9rem;
  text-decoration: none;
  background: none;
  border: none;
  padding: 0;
}
.nav-link:hover {
  color: #0d6efd;
}
.nav-divider {
  color: #ccc;
  font-size: 0.9rem;
}

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
/* Green button */
.btn-create {
  background-color: #198754;
  color: white;
}
/* Primary button (for main actions) */
.btn-primary {
  font-weight: 600;
}
.btn-lg {
  font-weight: 600;
}
</style>