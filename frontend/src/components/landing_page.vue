<template>
  <div class="hero-bg">
    <header class="container py-5">
    <nav class="d-flex justify-content-between align-items-center">
      <div class="d-flex align-items-center gap-3">
        <img :src="logo" alt="logo" class="logo-img" />
      </div>
      <div class="d-flex align-items-center">
        <img :src="signinBtn" alt="Sign In" @click="emit('open-signin')" class="signin-img" />
        <img :src="registerBtn" alt="Register" @click="emit('open-signup')" class="register-img" />
      </div>
    </nav>

    <div class="row align-items-center mt-4">
      <div class="col-lg-5">
        <h1 class="title">We help people to get appointment in online</h1>
        <p class="lead mt-3">
          Book appointments, view doctor profiles, and manage treatment history — all in one place.
        </p>
        <div class="mt-4 d-flex gap-3">
          <a class="btn btn-lg btn.primary" href="#">Get Started</a>
        </div>
      </div>
      <div class="col-lg-7 d-flex justify-content-center align-items-center">
        <img :src="studyImg" alt="study" class="study-img" />
      </div>
    </div>
    </header>
  </div>
</template>

<script setup>
const emit = defineEmits(['open-signup', 'open-signin'])
import logo from '../assets/Logo.png'
import signinBtn from '../assets/signin_button.svg'
import registerBtn from '../assets/register_button.svg'
import studyImg from '../assets/study.png'

</script>

<style scoped>
.hero-bg {
  background: linear-gradient(90deg, rgba(142, 197, 252, 0.95) 0%, rgba(224, 195, 252, 0.95) 100%);
min-height: 100vh;
width: 100%;
display: flex;
align-items: flex-start;
/* 3. ADDED: This will prevent any vertical scrolling */
overflow-y: hidden;
}

header {
  border-radius: 0;
}

/* Match SignUp / SignIn heading and subtitle colors */
h1 { color: #4a4a4a; }
.lead { max-width: 520px; color: #6c757d; }

/* Reuse title sizing from SignUp/SignIn */
.title {
  color: #4a4a4a; /* same dark gray */
  font-weight: 800;
  font-size: 2.5rem;
  max-width: 520px;
  line-height: 1.05;
}

.logo-img {
  height: 40px;
  transition: height .18s ease;
}
.signin-img {
  height: 40px;
  cursor: pointer;
  transition: height .12s ease;
  margin-right: 4px;
}
.register-img {
  height: 40px;
  cursor: pointer;
  transition: height .12s ease;
}
.btn-primary.btn-lg {
  padding: .6rem 1.25rem;
  font-size: 1.05rem;
}

.study-img {
  /* This will now fill the larger col-lg-7 container */
  max-width: 2000px;
  width: 100%;
  height: auto;
  transition: transform .18s ease;
}

@media (max-width: 991px) {
  /* 4. REMOVED: .position-absolute { display: none; } */

  header {
    padding-bottom: 2rem;
    border-radius: 12px;
  }
  
  /* 5. ADDED: Hide the image on small screens */
  .study-img {
    display: none;
  }
}
</style>