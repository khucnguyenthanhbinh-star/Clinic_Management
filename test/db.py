import sqlite3
import hashlib
import json
from datetime import datetime, timedelta

class Database:
    def __init__(self, db_name="clinic_final.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()
        self.seed_data()

    def create_tables(self):
        # 1. Users
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL, -- admin, doctor, patient
                created_at TEXT
            )
        """)
        # 2. PatientDetails
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS PatientDetails (
                user_id INTEGER PRIMARY KEY,
                full_name TEXT,
                phone TEXT,
                email TEXT,
                dob TEXT,
                address TEXT,
                medical_history TEXT,
                FOREIGN KEY (user_id) REFERENCES Users(id)
            )
        """)
        # 3. Doctors (Đã xóa consultation_fee)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Doctors (
                user_id INTEGER PRIMARY KEY,
                full_name TEXT,
                specialty TEXT,
                schedule TEXT, -- JSON: {"Mon": "08:00-17:00"}
                FOREIGN KEY (user_id) REFERENCES Users(id)
            )
        """)
        # 4. Medicines
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Medicines (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE,
                price REAL,
                stock INTEGER
            )
        """)
        # 5. Tests
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Tests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE,
                price REAL
            )
        """)
        # 6. Appointments
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Appointments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER,
                doctor_id INTEGER,
                date TEXT,
                time TEXT,
                reason TEXT, -- Loại khám
                symptoms TEXT, -- Mô tả thêm
                status TEXT, -- Pending, Cancelled, Completed
                FOREIGN KEY (patient_id) REFERENCES Users(id),
                FOREIGN KEY (doctor_id) REFERENCES Users(id)
            )
        """)
        # 7. MedicalRecords
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS MedicalRecords (
                appointment_id INTEGER PRIMARY KEY,
                diagnosis TEXT,
                test_results TEXT, -- JSON list các xét nghiệm đã làm
                prescription TEXT, -- JSON list thuốc đã kê
                notes TEXT,
                FOREIGN KEY (appointment_id) REFERENCES Appointments(id)
            )
        """)
        # 8. Invoices
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Invoices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                appointment_id INTEGER,
                patient_id INTEGER,
                total_amount REAL,
                status TEXT, -- Unpaid, Paid
                created_at TEXT,
                FOREIGN KEY (appointment_id) REFERENCES Appointments(id)
            )
        """)
        # 9. Notifications
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                message TEXT,
                is_read INTEGER DEFAULT 0,
                created_at TEXT
            )
        """)
        self.conn.commit()

    def hash_password(self, password):
        """Mã hóa mật khẩu bằng SHA256."""
        return hashlib.sha256(password.encode()).hexdigest()

    def seed_data(self):
        self.cursor.execute("SELECT count(*) FROM Users")
        if self.cursor.fetchone()[0] > 0:
            return

        # Admin
        self.cursor.execute("INSERT INTO Users (username, password_hash, role) VALUES (?, ?, ?)",
                            ('admin', self.hash_password('admin123'), 'admin'))
        
        # Doctors
        schedule = json.dumps({"Mon": "08:00-17:00", "Tue": "08:00-17:00", "Wed": "08:00-17:00", "Thu": "08:00-17:00", "Fri": "08:00-17:00"})
        
        docs = [
            ('bacsi1', '1234567', 'BS. Nguyễn Văn A', 'Chuyên khoa 1'),
            ('bacsi2', '1234567', 'BS. Trần Thị B', 'Chuyên khoa 2'),
            ('bacsi3', '1234567', 'BS. Lê Văn C', 'Chuyên khoa 3')
        ]

        for u, p, name, spec in docs:
            self.cursor.execute("INSERT INTO Users (username, password_hash, role) VALUES (?, ?, ?)",
                                (u, self.hash_password(p), 'doctor'))
            doc_id = self.cursor.lastrowid
            self.cursor.execute("INSERT INTO Doctors (user_id, full_name, specialty, schedule) VALUES (?, ?, ?, ?)",
                                (doc_id, name, spec, schedule))

        # Medicines & Tests
        meds = [('Paracetamol', 5000, 100), ('Antibiotic X', 15000, 50), ('Vitamin C', 2000, 200)]
        self.cursor.executemany("INSERT INTO Medicines (name, price, stock) VALUES (?, ?, ?)", meds)

        tests = [('Xét nghiệm máu', 150000), ('Chụp X-Quang', 200000), ('Siêu âm', 300000)]
        self.cursor.executemany("INSERT INTO Tests (name, price) VALUES (?, ?)", tests)

        self.conn.commit()