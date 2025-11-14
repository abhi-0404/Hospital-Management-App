<template>
  <div class="hero-bg">
    <ToastNotification 
      v-if="toast"
      :message="toast.message" 
      :type="toast.type"
      @close="toast = null"
    />

    <header class="container py-5">
      <nav class="d-flex justify-content-between align-items-center">
        <div class="d-flex align-items-center gap-3">
          <img :src="logo" alt="logo" class="logo-img" @click.prevent="emit('back')" style="cursor:pointer" />
        </div>
        <div class="d-flex align-items-center">
          <img :src="signinBtn" alt="Sign In" @click="emit('open-signin')" class="signin-img" />
        </div>
      </nav>

    <div class="row mt-5"> 
      <div class="col-lg-6 col-md-8">
          
          <div>
            <h1 class="title">Sign Up</h1>
            <p class="subtitle mb-4">Please sign up to continue</p>
          </div>

          <form @submit.prevent="handleRegister">
            <div class="form-floating mb-3">
              <input type="text" class="form-control" id="firstName" placeholder="First Name" v-model="firstName" required>
              <label for="firstName">First Name</label>
            </div>

            <div class="form-floating mb-3">
              <input type="email" class="form-control" id="email" placeholder="name@example.com" v-model="email" required>
              <label for="email">Email address</label>
            </div>

            <div class="form-floating mb-4">
              <input type="password" class="form-control" id="password" placeholder="Password" v-model="password" required>
              <label for="password">Password</label>
            </div>

            <div class="form-actions d-flex justify-content-between align-items-center mt-4">
              
              <p class="signin-text mb-0">
                Already have an account? 
                <a href="#" @click.prevent="emit('open-signin')" class="signin-link">Sign In</a>
              </p>

              <img 
                :src="registerBtn" 
                alt="Register" 
                @click="handleRegister" 
                class="register-img" 
              />
            </div>

          </form>

          </div>
        <div class="col-lg-6 d-none d-lg-flex justify-content-center align-items-center">
          <img :src="signupVec" alt="signup illustration" class="signup-vec" />
        </div>
      </div>
    </header>
  </div>
</template>

<script setup>
import { ref } from 'vue'
// Import the new component
import ToastNotification from './ToastNotification.vue'

// --- RE-USED ASSETS ---
import logo from '../assets/Logo.png'
import signinBtn from '../assets/signin_button.svg'
import registerBtn from '../assets/register_button.svg'
import signupVec from '../assets/signup_vec.png' 


// --- EMITS ---
const emit = defineEmits(['open-signin', 'back'])

// --- FORM DATA ---
const firstName = ref('')
const email = ref('')
const password = ref('')
// --- *** UPDATED: selectedRole ref is removed as it's patient-only *** ---
// const selectedRole = ref('Patient') 

// --- Replaced 'message' and 'messageType' with 'toast'
const toast = ref(null) // Will be an object like { message: '...', type: '...' }


// --- UPDATED HANDLER ---
const handleRegister = async () => {
  // Clear any old toast
  toast.value = null

  if (!firstName.value || !email.value || !password.value) {
    // Set the toast object for an error
    toast.value = { message: 'Please fill out all fields.', type: 'danger' }
    return;
  }
  
  // --- *** UPDATED: All checks removed, role is hardcoded to 'Patient' *** ---

  try {
    const response = await fetch('http://127.0.0.1:8000/api/signup', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        firstName: firstName.value, 
        email: email.value,
        password: password.value,
        role: 'Patient' // Hardcoded to 'Patient' as per project rules
      })
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.message || 'Signup failed');
    }

    // Success!
    console.log('Signup successful:', data);
    // Set the toast object for success
    toast.value = { message: 'Registration successful! Please sign in.', type: 'success' }
    
    // Still emit to change page after 2 seconds
    setTimeout(() => {
      emit('open-signin');
    }, 2000);

  } catch (error) {
    console.error('Error:', error);
    // Set the toast object for an error
    toast.value = { message: error.message, type: 'danger' }
  }
}
</script>

<style scoped>
/* --- RE-USED STYLES --- */
.hero-bg {
  background: linear-gradient(90deg, rgba(142, 197, 252, 0.95) 0%, rgba(224, 195, 252, 0.95) 100%);
  min-height: 100vh;
  width: 100%;
  display: flex;
  align-items: flex-start;
  overflow-y: hidden; 
}

header {
  width: 100%;
}

.logo-img {
  height: 40px;
}

.signin-img {
  height: 40px;
  cursor: pointer;
  margin-right: 4px;
}

/* --- STYLES for Sign Up Form --- */

/* Headings */
.title {
  color: #4a4a4a;
  font-weight: 800;
  font-size: 2.5rem;
}

.subtitle {
  color: #6c757d;
  font-size: 1.25rem;
}

/* Custom Form Fields */
.form-control {
  background-color: rgba(255, 255, 255, 0.4);
  border: 1px solid rgba(255, 255, 255, 0.7);
  border-radius: 0.75rem; 
  padding: 1.15rem 1rem;
  color: #333;
}

.form-control:focus {
  background-color: rgba(255, 255, 255, 0.7);
  border-color: #fff;
  box-shadow: 0 0 0 0.25rem rgba(142, 197, 252, 0.5); 
  color: #000;
}

.form-floating > label {
  color: #555; 
}

.form-control:-webkit-autofill,
.form-control:-webkit-autofill:hover, 
.form-control:-webkit-autofill:focus, 
.form-control:-webkit-autofill:active  {
    -webkit-box-shadow: 0 0 0 30px rgba(255, 255, 255, 0.7) inset !important;
    -webkit-text-fill-color: #000 !important;
}

.register-img {
  height: 40px; /* normalized to 40px */
  cursor: pointer;
  transition: height .12s ease;
  
}

/* Bottom "Sign In" Link */
.signin-text {
  color: #4a4a4a;
}
.signin-link {
  color: #333;
  font-weight: 600;
  text-decoration: none;
}
.signin-link:hover { text-decoration: underline; }

/* Signup illustration */
.signup-vec {
  max-width: 520px;
  width: 100%;
  height: auto;
}

/* --- *** Role selector styles are no longer needed *** --- */
</style>