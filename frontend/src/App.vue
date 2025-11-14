<template>
  <div id="app">
    <LandingHero v-if="view === 'landing'" @open-signup="view = 'signup'" @open-signin="view = 'signin'" />
    <SignIn v-else-if="view === 'signin'" @back="view = 'landing'" @authenticated="onAuthenticated" @open-signup="view = 'signup'" />

    <SignUp v-else-if="view === 'signup'" @back="view = 'landing'" @open-signin="view = 'signin'" />

    <PatientDashboard v-else-if="view === 'patient-dashboard'" :user="user" @logout="onLogout" />
    <DoctorDashboard v-else-if="view === 'doctor-dashboard'" :user="user" @logout="onLogout" />
    <AdminDashboard v-else-if="view === 'admin-dashboard'" :user="user" @logout="onLogout" />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import LandingHero from './components/landing_page.vue'
import SignUp from './components/SignUp.vue'
import SignIn from './components/SignIn.vue'
import PatientDashboard from './components/PatientDashboard.vue'
import DoctorDashboard from './components/DoctorDashboard.vue'
import AdminDashboard from './components/AdminDashboard.vue'

const view = ref('landing')
const user = ref(null)

function onAuthenticated(payload) {
  // payload: { token, user }
  if (!payload) return
  if (payload.token) localStorage.setItem('token', payload.token)
  user.value = payload.user || null

  // Route to dashboard based on role
  const role = (user.value && user.value.role) ? user.value.role.toString().toLowerCase() : null
  if (role === 'doctor') view.value = 'doctor-dashboard'
  else if (role === 'admin') view.value = 'admin-dashboard'
  else view.value = 'patient-dashboard'
}

function onLogout() {
  localStorage.removeItem('token')
  user.value = null
  view.value = 'landing'
}
</script>

<style>
/* app-level background to match screenshot */
#app {
  background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
  min-height: 100vh;
  font-family: "Helvetica Neue", Arial, sans-serif;
}
</style>