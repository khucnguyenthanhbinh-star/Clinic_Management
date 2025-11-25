import hashlib
import json
import re
from datetime import datetime, timedelta

class Controller:
    def __init__(self, db):
        self.db = db
        self.conn = db.conn
        self.cursor = db.cursor
        self.current_user = None

    # --- Auth & Validation ---
    def hash_password(self, password):
        """Mã hóa mật khẩu bằng SHA256."""
        return hashlib.sha256(password.encode()).hexdigest()

    def login(self, username, password):
        pwd_hash = self.hash_password(password)
        self.cursor.execute("SELECT id, role FROM Users WHERE username=? AND password_hash=?", (username, pwd_hash))
        return self.cursor.fetchone()

    def validate_registration(self, phone, email, password):
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email): return False, "Email không đúng định dạng."
        if not re.match(r"^\d{10,11}$", phone): return False, "Số điện thoại phải là số (10-11 ký tự)."
        if len(password) < 6: return False, "Mật khẩu phải có ít nhất 6 ký tự."
        self.cursor.execute("SELECT user_id FROM PatientDetails WHERE phone=? OR email=?", (phone, email))
        if self.cursor.fetchone(): return False, "Số điện thoại hoặc Email đã tồn tại."
        return True, ""

    def register_patient(self, phone, email, password, fullname):
        is_valid, msg = self.validate_registration(phone, email, password)
        if not is_valid: return False, msg
        try:
            pwd_hash = self.hash_password(password)
            self.cursor.execute("INSERT INTO Users (username, password_hash, role, created_at) VALUES (?, ?, 'patient', ?)", 
                                (email, pwd_hash, datetime.now().strftime("%Y-%m-%d")))
            user_id = self.cursor.lastrowid
            self.cursor.execute("INSERT INTO PatientDetails (user_id, full_name, phone, email) VALUES (?, ?, ?, ?)",
                                (user_id, fullname, phone, email))
            self.conn.commit()
            return True, "Đăng ký thành công!"
        except Exception as e: return False, str(e)
        
    def reset_user_password(self, user_id, new_password):
        """Đặt lại mật khẩu cho người dùng đã chọn."""
        try:
            if len(new_password) < 6:
                return False, "Mật khẩu mới phải có ít nhất 6 ký tự."
            
            new_hash = self.hash_password(new_password)
            self.cursor.execute("UPDATE Users SET password_hash=? WHERE id=?", (new_hash, user_id))
            self.conn.commit()
            return True, "Đã đặt lại mật khẩu thành công."
        except Exception as e:
            return False, str(e)


    # --- Patient Logic ---
    def update_patient_info(self, uid, dob, address, history):
        self.cursor.execute("UPDATE PatientDetails SET dob=?, address=?, medical_history=? WHERE user_id=?", (dob, address, history, uid))
        self.conn.commit()

    def get_patient_info(self, uid):
        self.cursor.execute("SELECT * FROM PatientDetails WHERE user_id=?", (uid,))
        return self.cursor.fetchone()

    def get_doctors_by_type(self, type_str):
        self.cursor.execute("SELECT user_id, full_name FROM Doctors WHERE specialty=?", (type_str,))
        return self.cursor.fetchall()

    def get_all_doctor_slots(self, doctor_id):
        slots = []
        today = datetime.now().date()
        self.cursor.execute("SELECT date, time FROM Appointments WHERE doctor_id=? AND status != 'Cancelled'", (doctor_id,))
        taken = set((row[0], row[1]) for row in self.cursor.fetchall())
        for i in range(30):
            day = today + timedelta(days=i)
            day_str = day.strftime("%Y-%m-%d")
            for h in range(8, 17):
                time_str = f"{h:02d}:00"
                if (day_str, time_str) not in taken: slots.append((day_str, time_str))
        return slots

    def book_appointment(self, patient_id, doctor_id, date, time, reason, symptoms):
        self.cursor.execute("INSERT INTO Appointments (patient_id, doctor_id, date, time, reason, symptoms, status) VALUES (?, ?, ?, ?, ?, ?, 'Pending')", (patient_id, doctor_id, date, time, reason, symptoms))
        msg = f"Có lịch hẹn mới vào {date} {time}. Lý do: {reason}"
        self.cursor.execute("INSERT INTO Notifications (user_id, message, created_at) VALUES (?, ?, ?)", (doctor_id, msg, datetime.now().strftime("%Y-%m-%d")))
        self.conn.commit()

    def cancel_appointment(self, app_id):
        self.cursor.execute("UPDATE Appointments SET status='Cancelled' WHERE id=?", (app_id,))
        self.conn.commit()
        return True

    def get_patient_records(self, patient_id):
        query = """SELECT A.date, D.full_name, M.diagnosis, M.test_results, M.prescription FROM Appointments A JOIN Doctors D ON A.doctor_id = D.user_id INNER JOIN MedicalRecords M ON A.id = M.appointment_id WHERE A.patient_id = ? AND A.status = 'Completed' ORDER BY A.date DESC"""
        self.cursor.execute(query, (patient_id,))
        return self.cursor.fetchall()
    
    def get_unpaid_invoices(self, patient_id):
        self.cursor.execute("SELECT id, total_amount, created_at FROM Invoices WHERE patient_id=? AND status='Unpaid'", (patient_id,))
        return self.cursor.fetchall()
    
    def pay_invoice(self, invoice_id):
        self.cursor.execute("UPDATE Invoices SET status='Paid' WHERE id=?", (invoice_id,))
        self.conn.commit()

    # --- Doctor Logic ---
    def get_doctor_appointments(self, doctor_id):
        self.cursor.execute("SELECT A.id, P.full_name, A.date, A.time, A.reason, A.status, A.patient_id FROM Appointments A JOIN PatientDetails P ON A.patient_id = P.user_id WHERE A.doctor_id = ? AND A.status IN ('Pending', 'Processing') ORDER BY A.date, A.time", (doctor_id,))
        return self.cursor.fetchall()

    def start_examination(self, app_id):
        self.cursor.execute("INSERT OR IGNORE INTO MedicalRecords (appointment_id) VALUES (?)", (app_id,))
        self.conn.commit()
    
    def update_test_results(self, app_id, tests_json):
        self.cursor.execute("UPDATE MedicalRecords SET test_results=? WHERE appointment_id=?", (json.dumps(tests_json), app_id))
        self.conn.commit()

    def check_stock(self, med_name, qty):
        self.cursor.execute("SELECT stock FROM Medicines WHERE name=?", (med_name,))
        res = self.cursor.fetchone()
        return res and res[0] >= qty

    def update_prescription(self, app_id, meds_list):
        self.cursor.execute("UPDATE MedicalRecords SET prescription=? WHERE appointment_id=?", (json.dumps(meds_list), app_id))
        self.conn.commit()

    def finish_examination(self, app_id, diagnosis, meds_list, tests_list):
        try:
            total_cost = 0
            for m in meds_list:
                self.cursor.execute("UPDATE Medicines SET stock = stock - ? WHERE name=?", (m['qty'], m['name']))
                self.cursor.execute("SELECT price FROM Medicines WHERE name=?", (m['name'],))
                total_cost += self.cursor.fetchone()[0] * m['qty']
            for t in tests_list:
                self.cursor.execute("SELECT price FROM Tests WHERE name=?", (t['name'],))
                total_cost += self.cursor.fetchone()[0]
            
            self.cursor.execute("UPDATE MedicalRecords SET diagnosis=? WHERE appointment_id=?", (diagnosis, app_id))
            self.cursor.execute("UPDATE Appointments SET status='Completed' WHERE id=?", (app_id,))
            
            self.cursor.execute("SELECT patient_id FROM Appointments WHERE id=?", (app_id,))
            pid = self.cursor.fetchone()[0]
            self.cursor.execute("INSERT INTO Invoices (appointment_id, patient_id, total_amount, status, created_at) VALUES (?, ?, ?, 'Unpaid', ?)", (app_id, pid, total_cost, datetime.now().strftime("%Y-%m-%d")))
            self.conn.commit()
            return True
        except: return False

    # --- ADMIN LOGIC ---
    def get_revenue(self):
        self.cursor.execute("SELECT sum(total_amount) FROM Invoices WHERE status='Paid'")
        res = self.cursor.fetchone()[0]
        return res if res else 0

    def get_all_users_admin(self):
        self.cursor.execute("""SELECT U.id, U.username, U.password_hash, U.role, COALESCE(D.full_name, P.full_name, 'Admin') as name, COALESCE(D.specialty, '') as specialty FROM Users U LEFT JOIN Doctors D ON U.id = D.user_id LEFT JOIN PatientDetails P ON U.id = P.user_id ORDER BY U.id""")
        return self.cursor.fetchall()

    def add_user_admin(self, role, username, password, fullname, specialty=None):
        try:
            self.cursor.execute("SELECT id FROM Users WHERE username=?", (username,))
            if self.cursor.fetchone(): return False, "Username đã tồn tại"
            pwd_hash = self.hash_password(password)
            self.cursor.execute("INSERT INTO Users (username, password_hash, role, created_at) VALUES (?, ?, ?, ?)", (username, pwd_hash, role, datetime.now().strftime("%Y-%m-%d")))
            user_id = self.cursor.lastrowid
            if role == 'doctor':
                schedule = json.dumps({"Mon": "08:00-17:00", "Tue": "08:00-17:00", "Wed": "08:00-17:00", "Thu": "08:00-17:00", "Fri": "08:00-17:00"})
                self.cursor.execute("INSERT INTO Doctors (user_id, full_name, specialty, schedule) VALUES (?, ?, ?, ?)", (user_id, fullname, specialty, schedule))
            elif role == 'patient':
                self.cursor.execute("INSERT INTO PatientDetails (user_id, full_name) VALUES (?, ?)", (user_id, fullname))
            self.conn.commit()
            return True, "Thêm tài khoản thành công"
        except Exception as e: return False, str(e)

    def delete_user(self, user_id):
        try:
            self.cursor.execute("DELETE FROM Doctors WHERE user_id=?", (user_id,))
            self.cursor.execute("DELETE FROM PatientDetails WHERE user_id=?", (user_id,))
            self.cursor.execute("DELETE FROM Users WHERE id=?", (user_id,))
            self.conn.commit()
            return True
        except: return False

    def add_medicine(self, name, price, stock):
        try:
            self.cursor.execute("INSERT INTO Medicines (name, price, stock) VALUES (?, ?, ?)", (name, float(price), int(stock)))
            self.conn.commit()
            return True
        except: return False

    def update_medicine(self, med_id, name, price, stock):
        try:
            self.cursor.execute("UPDATE Medicines SET name=?, price=?, stock=? WHERE id=?", (name, float(price), int(stock), med_id))
            self.conn.commit()
            return True
        except: return False

    def delete_medicine(self, med_id):
        self.cursor.execute("DELETE FROM Medicines WHERE id=?", (med_id,))
        self.conn.commit()

    def get_all_appointments_admin(self):
        self.cursor.execute("SELECT A.id, A.date, A.time, P.full_name, D.full_name, A.status FROM Appointments A LEFT JOIN PatientDetails P ON A.patient_id = P.user_id LEFT JOIN Doctors D ON A.doctor_id = D.user_id ORDER BY A.date DESC, A.time DESC")
        return self.cursor.fetchall()