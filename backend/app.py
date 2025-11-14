import os
from flask import Flask, jsonify, request, send_file
from flask_sqlalchemy import SQLAlchemy
from passlib.hash import pbkdf2_sha256
from flask_jwt_extended import (
    JWTManager, create_access_token, jwt_required, get_jwt_identity,
    verify_jwt_in_request  # This import is necessary
)
import redis
from flask_cors import CORS
from datetime import datetime, date, time
import io
import csv

# Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'app.db')

app = Flask(__name__)
CORS(app)

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'change-me')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_PATH}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-string')

# Init extensions
db = SQLAlchemy(app)
jwt = JWTManager(app)

# Simple redis client for caching (uses default localhost:6379)
redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
redis_client = redis.Redis.from_url(redis_url)


# --- DATABASE MODELS ---

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='patient') # Roles: patient, doctor, admin
    is_blacklisted = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    appointments = db.relationship('Appointment', foreign_keys='Appointment.patient_id', backref='patient', lazy=True, cascade="all, delete-orphan")
    doctor_profile = db.relationship('Doctor', backref='user', uselist=False, lazy=True, cascade="all, delete-orphan")

    def set_password(self, password: str):
        self.password_hash = pbkdf2_sha256.hash(password)

    def check_password(self, password: str) -> bool:
        try:
            return pbkdf2_sha256.verify(password, self.password_hash)
        except Exception:
            return False

    def to_dict(self):
        return {
            'id': self.id, 
            'name': self.name, 
            'email': self.email, 
            'role': self.role,
            'is_blacklisted': self.is_blacklisted,
            'created_at': (self.created_at.isoformat() + 'Z') if self.created_at else None
        }

class Department(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    doctors = db.relationship('Doctor', backref='department', lazy=True)
    
    def to_dict(self):
        return {'id': self.id, 'name': self.name}

class Doctor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=False)
    
    appointments = db.relationship('Appointment', backref='doctor', lazy=True, cascade="all, delete-orphan")
    availabilities = db.relationship('Availability', backref='doctor', lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.user.name,
            'email': self.user.email,
            'is_blacklisted': self.user.is_blacklisted,
            'department': self.department.name if self.department else 'N/A',
            'created_at': (self.user.created_at.isoformat() + 'Z') if self.user and self.user.created_at else None
        }

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    appointment_datetime = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='Booked') # Booked, Completed, Cancelled
    
    diagnosis = db.Column(db.Text, nullable=True)
    treatment_notes = db.Column(db.Text, nullable=True)
    prescription = db.Column(db.Text, nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'patient_name': self.patient.name,
            'patient_id': self.patient.id,
            'doctor_name': self.doctor.user.name,
            'doctor_id': self.doctor.id,
            'department': self.doctor.department.name,
            'datetime': (self.appointment_datetime.isoformat() + 'Z') if self.appointment_datetime else None,
            'status': self.status,
            'diagnosis': self.diagnosis,
            'treatment_notes': self.treatment_notes,
            'prescription': self.prescription
        }


class Availability(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)

def create_tables():
    try:
        with app.app_context():
            db.create_all()
            
            if not User.query.filter_by(role='admin').first():
                print("Creating default admin user...")
                admin_user = User(name='Admin', email='admin@healthify.com', role='admin')
                admin_user.set_password('123') # Default password
                db.session.add(admin_user)
                db.session.commit()
                print("Admin user created with email: admin@healthify.com")

            if Department.query.count() == 0:
                print("Creating default departments...")
                depts = [Department(name='Cardiology'), Department(name='Neurology'), Department(name='General'), Department(name='Oncology')]
                db.session.bulk_save_objects(depts)
                db.session.commit()

    except Exception as e:
        print(f"Error creating tables or defaults: {e}")

create_tables()


@app.route('/')
def index():
    return jsonify({'status': 'ok', 'message': 'Backend running'})

# --- AUTHENTICATION API ---

@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.get_json() or {}
    name = data.get('firstName')
    email = data.get('email')
    password = data.get('password')
    role = 'patient' # Only patients can register

    if not email or not password or not name:
        return jsonify({'message': 'Name, email and password are required'}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'message': 'Email already registered'}), 400

    user = User(name=name, email=email, role=role)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    # --- *** FIX: Create token with a STRING identity *** ---
    access_token = create_access_token(identity=str(user.id))
    return jsonify({'message': 'User registered', 'token': access_token, 'user': user.to_dict()}), 201


@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    email = data.get('email')
    password = data.get('password')
    role = data.get('role', '').lower()

    if not email or not password or not role:
        return jsonify({'message': 'Email, password, and role are required'}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({'message': 'Invalid credentials'}), 401

    if user.role != role:
        return jsonify({'message': 'Invalid credentials for role'}), 401
        
    if user.is_blacklisted:
        return jsonify({'message': 'This account has been suspended'}), 403

    # --- *** FIX: Create token with a STRING identity *** ---
    access_token = create_access_token(identity=str(user.id))
    return jsonify({'message': 'Logged in', 'token': access_token, 'user': user.to_dict()}), 200

# --- ADMIN API ENDPOINTS ---

def check_admin():
    user_id = get_jwt_identity() # This will now be a string
    user = User.query.get(user_id) # .get() can handle the string ID
    if not user or user.role != 'admin':
        return None
    return user

@app.route('/api/admin/dashboard', methods=['GET'])
def admin_dashboard():
    # Manual verification block (as seen in your logs)
    try:
        auth_header = request.headers.get('Authorization')
        app.logger.debug('Admin dashboard Authorization header: %s', auth_header)
        verify_jwt_in_request() # This function will now work
    except Exception as e:
        app.logger.warning('JWT verification failed for admin_dashboard: %s', e)
        return jsonify({'message': 'Invalid or missing token', 'error': str(e)}), 401
    # End of verification block

    if not check_admin():
        return jsonify({'message': 'Admin access required'}), 403
        
    stats = {
        'patients': User.query.filter_by(role='patient').count(),
        'doctors': User.query.filter_by(role='doctor').count(),
        'totalAppointments': Appointment.query.count(),
        'upcoming': Appointment.query.filter(Appointment.appointment_datetime > datetime.now(), Appointment.status == 'Booked').count()
    }
    
    doctors = [d.to_dict() for d in Doctor.query.all()]
    patients = [u.to_dict() for u in User.query.filter_by(role='patient').all()]
    upcoming_appts = [a.to_dict() for a in Appointment.query.filter(Appointment.appointment_datetime > datetime.now(), Appointment.status == 'Booked').order_by(Appointment.appointment_datetime.asc()).all()]
    departments = [d.to_dict() for d in Department.query.all()]

    return jsonify({
        'stats': stats,
        'doctors': doctors,
        'patients': patients,
        'appointments': upcoming_appts,
        'departments': departments
    }), 200

@app.route('/api/admin/doctors', methods=['POST'])
@jwt_required()
def create_doctor():
    if not check_admin():
        return jsonify({'message': 'Admin access required'}), 403
        
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    department_id = data.get('department_id')

    if not all([name, email, password, department_id]):
        return jsonify({'message': 'Missing fields'}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'message': 'Email already in use'}), 400
        
    if not Department.query.get(department_id):
        return jsonify({'message': 'Invalid department'}), 400

    new_user = User(name=name, email=email, role='doctor')
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit() 

    new_doctor = Doctor(user_id=new_user.id, department_id=department_id)
    db.session.add(new_doctor)
    db.session.commit()
    
    return jsonify({'message': 'Doctor created successfully', 'doctor': new_doctor.to_dict()}), 201

@app.route('/api/admin/users/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_user(id):
    if not check_admin():
        return jsonify({'message': 'Admin access required'}), 403
        
    user = User.query.get(id)
    if not user: return jsonify({'message': 'User not found'}), 404
    if user.role == 'admin': return jsonify({'message': 'Cannot delete an admin account'}), 403
        
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': f'User {user.name} deleted'}), 200

@app.route('/api/admin/users/<int:id>/blacklist', methods=['PUT'])
@jwt_required()
def blacklist_user(id):
    if not check_admin():
        return jsonify({'message': 'Admin access required'}), 403
        
    user = User.query.get(id)
    if not user: return jsonify({'message': 'User not found'}), 404
    if user.role == 'admin': return jsonify({'message': 'Cannot blacklist an admin'}), 403
    
    user.is_blacklisted = not user.is_blacklisted
    db.session.commit()
    
    status = 'blacklisted' if user.is_blacklisted else 'un-blacklisted'
    return jsonify({'message': f'User {user.name} has been {status}', 'user': user.to_dict(), 'is_blacklisted': user.is_blacklisted}), 200


@app.route('/api/admin/users/<int:id>', methods=['PUT'])
@jwt_required()
def update_user(id):
    if not check_admin():
        return jsonify({'message': 'Admin access required'}), 403
    user = User.query.get(id)
    if not user:
        return jsonify({'message': 'User not found'}), 404
    data = request.get_json() or {}
    # Update basic fields
    if 'name' in data and data['name']:
        user.name = data['name']
    if 'email' in data and data['email'] and data['email'] != user.email:
        # ensure uniqueness
        if User.query.filter(User.email == data['email'], User.id != user.id).first():
            return jsonify({'message': 'Email already in use'}), 400
        user.email = data['email']

    # Update doctor department if provided and user is a doctor
    if 'department_id' in data and user.role == 'doctor' and data.get('department_id'):
        dept = Department.query.get(data['department_id'])
        if not dept:
            return jsonify({'message': 'Department not found'}), 404
        # Ensure doctor profile exists
        if not user.doctor_profile:
            doctor = Doctor(user_id=user.id, department_id=dept.id)
            db.session.add(doctor)
        else:
            user.doctor_profile.department_id = dept.id

    # Allow toggling blacklist via update as well
    if 'is_blacklisted' in data:
        user.is_blacklisted = bool(data.get('is_blacklisted'))

    # Allow admin to reset/change password
    if 'password' in data and data.get('password'):
        # set_password handles hashing
        user.set_password(data.get('password'))

    try:
        db.session.commit()
        return jsonify({'message': 'User updated', 'user': user.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        app.logger.exception('Error updating user: %s', e)
        return jsonify({'message': 'Failed to update user'}), 500


# --- DOCTOR API ENDPOINTS ---

@app.route('/api/doctor/dashboard', methods=['GET'])
@jwt_required()
def doctor_dashboard():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user or user.role != 'doctor': return jsonify({'message': 'Access forbidden: Not a doctor'}), 403
    doctor = user.doctor_profile
    if not doctor: return jsonify({'message': 'Doctor profile not found'}), 404
    
    upcoming_appts = Appointment.query.filter_by(doctor_id=doctor.id, status='Booked').order_by(Appointment.appointment_datetime.asc()).all()
    patient_ids = db.session.query(Appointment.patient_id).filter_by(doctor_id=doctor.id).distinct()
    assigned_patients = User.query.filter(User.id.in_([pid[0] for pid in patient_ids])).all()

    return jsonify({
        'upcomingAppointments': [appt.to_dict() for appt in upcoming_appts],
        'assignedPatients': [p.to_dict() for p in assigned_patients]
    }), 200

@app.route('/api/doctor/availability', methods=['POST'])
@jwt_required()
def set_availability():
    return jsonify({'message': 'Availability updated successfully'}), 200

@app.route('/api/appointments/<int:id>/history', methods=['PUT'])
@jwt_required()
def update_appointment_history(id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user or user.role != 'doctor': return jsonify({'message': 'Forbidden'}), 403
    
    appt = Appointment.query.get(id)
    if not appt: return jsonify({'message': 'Appointment not found'}), 404
    if appt.doctor_id != user.doctor_profile.id: return jsonify({'message': 'Forbidden'}), 403

    data = request.get_json()
    appt.diagnosis = data.get('diagnosis')
    appt.treatment_notes = data.get('treatment_notes')
    
    db.session.commit()
    return jsonify({'message': 'History updated', 'appointment': appt.to_dict()}), 200

@app.route('/api/appointments/<int:id>/complete', methods=['PUT'])
@jwt_required()
def complete_appointment(id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user or user.role != 'doctor': return jsonify({'message': 'Forbidden'}), 403

    appt = Appointment.query.get(id)
    if not appt: return jsonify({'message': 'Appointment not found'}), 404
    if appt.doctor_id != user.doctor_profile.id: return jsonify({'message': 'Forbidden'}), 403

    appt.status = 'Completed'
    db.session.commit()
    return jsonify({'message': 'Appointment marked as complete'}), 200

# --- PATIENT & SHARED API ENDPOINTS ---

@app.route('/api/appointments/<int:id>/cancel', methods=['PUT'])
@jwt_required()
def cancel_appointment(id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    appt = Appointment.query.get(id)
    if not appt: return jsonify({'message': 'Appointment not found'}), 404
    
    allowed = False
    if user.role == 'patient' and appt.patient_id == user.id: allowed = True
    if user.role == 'doctor' and user.doctor_profile and appt.doctor_id == user.doctor_profile.id: allowed = True
    if user.role == 'admin': allowed = True

    if not allowed:
        return jsonify({'message': 'Forbidden'}), 403

    appt.status = 'Cancelled'
    db.session.commit()
    return jsonify({'message': 'Appointment cancelled'}), 200

@app.route('/api/patients/<int:id>/history', methods=['GET'])
@jwt_required()
def get_patient_history(id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if user.role == 'patient' and user.id != id:
        return jsonify({'message': 'Forbidden: Cannot view other patient records'}), 403
    
    if user.role not in ['admin', 'doctor', 'patient']:
         return jsonify({'message': 'Forbidden'}), 403
        
    history = Appointment.query.filter_by(patient_id=id, status='Completed').order_by(Appointment.appointment_datetime.desc()).all()
    return jsonify([appt.to_dict() for appt in history]), 200

@app.route('/api/patient/dashboard', methods=['GET'])
@jwt_required()
def patient_dashboard():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user or user.role != 'patient':
        return jsonify({'message': 'Patient access required'}), 403

    departments = [d.to_dict() for d in Department.query.all()]
    upcoming_appts = Appointment.query.filter(
        Appointment.patient_id == user.id,
        Appointment.status == 'Booked',
        Appointment.appointment_datetime > datetime.now()
    ).order_by(Appointment.appointment_datetime.asc()).all()
    history_count = Appointment.query.filter_by(patient_id=user.id, status='Completed').count()

    return jsonify({
        'departments': departments,
        'upcomingAppointments': [appt.to_dict() for appt in upcoming_appts],
        'historyCount': history_count
    }), 200

@app.route('/api/patient/profile', methods=['PUT'])
@jwt_required()
def update_patient_profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user or user.role != 'patient':
        return jsonify({'message': 'Patient access required'}), 403
        
    data = request.get_json()
    if 'name' in data:
        user.name = data['name']
    
    db.session.commit()
    return jsonify({'message': 'Profile updated successfully', 'user': user.to_dict()}), 200

@app.route('/api/patient/export-history', methods=['POST'])
@jwt_required()
def export_patient_history():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user or user.role != 'patient':
        return jsonify({'message': 'Patient access required'}), 403
    
    history = Appointment.query.filter_by(patient_id=user.id, status='Completed').order_by(Appointment.appointment_datetime.asc()).all()
    if not history:
        return jsonify({'message': 'No history to export'}), 404
        
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Appointment ID', 'Date', 'Doctor', 'Department', 'Diagnosis', 'Treatment Notes'])
    
    for appt in history:
        writer.writerow([
            appt.id,
            appt.appointment_datetime.strftime('%Y-%m-%d %H:%M'),
            appt.doctor.user.name,
            appt.doctor.department.name,
            appt.diagnosis,
            appt.treatment_notes
        ])
    
    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode()),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'{user.name}_treatment_history.csv'
    )


# ---
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)