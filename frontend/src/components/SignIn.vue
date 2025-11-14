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
          <img :src="registerBtn" alt="Sign Up" @click="emit('open-signup')" class="register-img" />
        </div>
      </nav>

    <div class="row mt-5"> 
      <div class="col-lg-6 col-md-8">
          
          <div>
            <h1 class="title">Sign In</h1>
            <p class="subtitle mb-4">Please sign in to continue</p>
          </div>

          <div class="role-selector mb-2">
            <button 
              type="button" 
              :class="['role-btn', { active: selectedRole === 'Patient' }]"
              @click="selectedRole = 'Patient'">
              Patient
            </button>
            <button 
              type="button" 
              :class="['role-btn', { active: selectedRole === 'Doctor' }]"
              @click="selectedRole = 'Doctor'">
              Doctor
            </button>
            <button 
              type="button" 
              :class="['role-btn', { active: selectedRole === 'Admin' }]"
              @click="selectedRole = 'Admin'">
              Admin
            </button>
          </div>

          <form @submit.prevent="handleLogin">
            
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
                Don't have an account? 
                <a href="#" @click.prevent="emit('open-signup')" class="signin-link">Sign Up</a>
              </p>

              <img 
                :src="signinBtn" 
                alt="Sign In" 
                @click="handleLogin" 
                class="signin-img" 
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

// --- ASSETS ---
import logo from '../assets/Logo.png'
import signinBtn from '../assets/signin_button.svg'
import registerBtn from '../assets/register_button.svg'
import signupVec from '../assets/signup_vec.png' 


// --- EMITS ---
const emit = defineEmits(['open-signup', 'back', 'authenticated'])

// --- FORM DATA ---
const email = ref('')
const password = ref('')
const selectedRole = ref('Patient')

// --- Replaced 'message' and 'messageType' with 'toast'
const toast = ref(null) 


// --- UPDATED HANDLER ---
const handleLogin = async () => {
  toast.value = null

  if (!email.value || !password.value) {
    toast.value = { message: 'Please fill out all fields.', type: 'danger' }
    return;
  }
  
  // *** REMOVED ADMIN CHECK ***
  // The user can now select their role directly.
  let roleToLogin = (selectedRole.value || 'Patient').toString().toLowerCase();

  try {
    const response = await fetch('http://127.0.0.1:8000/api/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
        body: JSON.stringify({
          email: email.value,
          password: password.value,
          role: roleToLogin 
        })
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.message || 'Login failed');
    }

    // Success!
    console.log('Login successful:', data);
    toast.value = { message: 'Login successful! Redirecting...', type: 'success' }
    
    localStorage.setItem('token', data.token);

    // Emit the full auth payload (token + user) so App.vue can route by role
    setTimeout(() => {
      emit('authenticated', { token: data.token, user: data.user });
    }, 800);

  } catch (error) {
    console.error('Error:', error);
    toast.value = { message: error.message, type: 'danger' }
  }
}
</script>

<style scoped>
/* --- ALL STYLES ARE COPIED DIRECTLY FROM SIGNUP.VUE --- */
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

.register-img {
  height: 40px; 
  cursor: pointer;
  transition: height .12s ease;
}

.signin-img {
  height: 40px;
  cursor: pointer;
  margin-right: 4px;
}

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
  border: 1px solid rgba(255, 255, 252, 0.7);
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

/* Bottom "Sign Up" Link */
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

/* STYLES FOR ROLE SELECTOR */
.role-selector {
  display: flex;
  width: 100%;
  background-color: #f0ebf9;
  border-radius: 12px;
}
.role-btn {
  flex: 1;
  padding: 0.6rem 0.75rem;
  border: none;
  background-color: transparent;
  color: #333;
  font-weight: 600;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.2s ease;
  border-radius: 12px;
}
.role-btn.active {
  background-color: #8f7ece;
  color: #fff;
  box-shadow: 0 2px 5px rgba(0,0,0,0.15);
}
</style>