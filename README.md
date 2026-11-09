# Healthify: Hospital Management App

A role-based hospital management system with separate dashboards for **admins**, **doctors** and **patients**. Patients book appointments against doctors' published availability, doctors record diagnoses and prescriptions, and admins manage departments, doctors and users.

Built with a **Flask** REST API (JWT auth, SQLAlchemy, Celery + Redis for background jobs) and a **Vue 3** single-page frontend.

## Features

**Patients**
- Sign up and sign in (patient is the only self-service role)
- Browse departments and the doctors in each
- See a doctor's open time slots and book an appointment
- Cancel bookings, view past treatment history, and export it as CSV (optionally filtered by visit type)
- Edit their profile

**Doctors**
- Dashboard of upcoming and completed appointments
- Publish availability blocks that patients book against
- Record diagnosis, treatment notes and prescriptions, then mark an appointment complete
- View and export a patient's treatment history as CSV
- Edit their profile (bio, specialization, experience, education)

**Admins**
- Dashboard with counts of patients, doctors and appointments
- Create doctor accounts and assign them to departments
- Edit, blacklist or delete users (admin accounts are protected)

**Platform**
- JWT-protected API with a role check on every endpoint
- Passwords hashed with bcrypt (passlib)
- Celery worker on Redis for background jobs (welcome emails are simulated for now)
- Four departments seeded on first run: Cardiology, Neurology, General, Oncology

## Tech Stack

| Layer | Technology |
|---|---|
| API | Flask, Flask-JWT-Extended, Flask-Cors |
| Data | SQLite via Flask-SQLAlchemy |
| Security | passlib (bcrypt) password hashing, JWT |
| Background jobs | Celery with Redis as broker and result backend |
| Frontend | Vue 3, Vite, Bootstrap 5 |

## Data Model

| Table | Holds |
|---|---|
| `User` | Name, email, password hash, role (`admin` / `doctor` / `patient`), blacklist flag |
| `Department` | Name and description |
| `Doctor` | Profile linked to a `User` and a `Department` |
| `Availability` | A doctor's bookable time blocks |
| `Appointment` | Patient, doctor, time, status (`Booked` / `Completed` / `Cancelled`), diagnosis, notes, prescription |

## Getting Started

### Backend (port 8000)

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate          # macOS / Linux: source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

On first run the app creates the SQLite database, the four departments and a default admin account:

| Email | Password |
|---|---|
| `admin@healthify.com` | `123` |

This account is for local development only. **Change the password (and set `SECRET_KEY` and `JWT_SECRET_KEY` environment variables) before deploying anywhere.**

### Background worker (optional)

Requires a running Redis server (`REDIS_URL`, default `redis://localhost:6379/0`):

```bash
cd backend
celery -A celery_worker.celery worker --loglevel=info
```

### Frontend (Vite dev server)

```bash
cd frontend
npm install
npm run dev
```

The frontend calls the API at `http://127.0.0.1:8000`.

## API Overview

| Area | Endpoints |
|---|---|
| Auth | `POST /api/signup`, `POST /api/login` |
| Admin | `GET /api/admin/dashboard`, `POST /api/admin/doctors`, `PUT` / `DELETE /api/admin/users/<id>`, `PUT /api/admin/users/<id>/blacklist` |
| Doctor | `GET /api/doctor/dashboard`, `PUT /api/doctor/profile`, `POST /api/doctor/availability`, `GET /api/doctor/availability/blocks` |
| Appointments | `POST /api/appointments`, `PUT /api/appointments/<id>/history`, `PUT /api/appointments/<id>/complete`, `PUT /api/appointments/<id>/cancel` |
| Patient | `GET /api/patient/dashboard`, `PUT /api/patient/profile`, `POST /api/patient/export-history` |
| History | `GET /api/patients/<id>/history`, `GET /api/patients/<id>/export-history` |
| Booking | `GET /api/departments/<id>/doctors`, `GET /api/doctors/<id>/availability` |
