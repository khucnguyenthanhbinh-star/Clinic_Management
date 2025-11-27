import sqlite3
import os
from datetime import datetime
from core.password_hasher import PasswordHasher

class ClinicDatabase:
    def __init__(self, db_name="clinic.db"):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(base_dir, db_name)
        
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.create_tables()
        self.seed_data()

    def create_tables(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password TEXT NOT NULL,
                role TEXT NOT NULL,
                name TEXT NOT NULL,
                info TEXT
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS medicines (
                name TEXT PRIMARY KEY,
                quantity INTEGER,
                unit TEXT
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS appointments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_username TEXT,
                date TEXT,
                time TEXT,
                reason TEXT,
                status TEXT,
                FOREIGN KEY(patient_username) REFERENCES users(username)
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS invoices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_username TEXT,
                service_name TEXT,
                amount INTEGER,
                status TEXT, 
                created_at TEXT
            )
        """)
        self.conn.commit()

    def seed_data(self):
        pass

    # --- USER METHODS ---
    def get_user(self, username):
        self.cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        row = self.cursor.fetchone()
        if row:
            return {"username": row[0], "password": row[1], "role": row[2], "name": row[3], "info": row[4]}
        return None

    def add_user(self, username, password, role, name, info=""):
        try:
            hashed_pw = PasswordHasher.hash_password(password)
            self.cursor.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?)", 
                                (username, hashed_pw, role, name, info))
            self.conn.commit()
            return True, "Đăng ký thành công"
        except sqlite3.IntegrityError:
            return False, "Tên đăng nhập đã tồn tại"

    def get_users_by_role(self, role):
        self.cursor.execute("SELECT username, name, role, info FROM users WHERE role = ?", (role,))
        rows = self.cursor.fetchall()
        return [{"username": r[0], "name": r[1], "role": r[2], "info": r[3]} for r in rows]

    def get_all_users(self):
        self.cursor.execute("SELECT username, name, role FROM users")
        rows = self.cursor.fetchall()
        return {r[0]: {"name": r[1], "role": r[2]} for r in rows}

    # --- MEDICINE METHODS ---
    def get_medicines(self):
        self.cursor.execute("SELECT * FROM medicines")
        rows = self.cursor.fetchall()
        return {r[0]: {"quantity": r[1], "unit": r[2]} for r in rows}

    def add_medicine(self, name, quantity, unit):
        current = self.cursor.execute("SELECT quantity FROM medicines WHERE name = ?", (name,)).fetchone()
        if current:
            new_qty = current[0] + int(quantity)
            self.cursor.execute("UPDATE medicines SET quantity = ? WHERE name = ?", (new_qty, name))
        else:
            self.cursor.execute("INSERT INTO medicines VALUES (?, ?, ?)", (name, int(quantity), unit))
        self.conn.commit()

    # --- APPOINTMENT METHODS ---
    def add_appointment(self, patient_user, date, time, reason, status="Đã đặt"):
        self.cursor.execute("INSERT INTO appointments (patient_username, date, time, reason, status) VALUES (?, ?, ?, ?, ?)",
                            (patient_user, date, time, reason, status))
        self.conn.commit()

    def get_appointments(self, patient_username=None):
        sql = "SELECT * FROM appointments"
        params = ()
        if patient_username:
            sql += " WHERE patient_username = ?"
            params = (patient_username,)
        self.cursor.execute(sql, params)
        rows = self.cursor.fetchall()
        result = []
        for r in rows:
            result.append({
                "id": r[0], "patient": r[1], "date": r[2], 
                "time": r[3], "reason": r[4], "status": r[5]
            })
        return result

    # --- INVOICE METHODS ---
    def add_invoice(self, username, service, amount, status="Unpaid"):
        date = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.cursor.execute("INSERT INTO invoices (patient_username, service_name, amount, status, created_at) VALUES (?, ?, ?, ?, ?)", 
                            (username, service, amount, status, date))
        self.conn.commit()

    def get_unpaid_invoices(self, username):
        self.cursor.execute("SELECT id, service_name, amount, created_at FROM invoices WHERE patient_username = ? AND status = 'Unpaid'", (username,))
        rows = self.cursor.fetchall()
        return [{"id": r[0], "service": r[1], "amount": r[2], "date": r[3]} for r in rows]

    # --- HÀM MỚI: LẤY TẤT CẢ HÓA ĐƠN ---
    def get_all_patient_invoices(self, username):
        self.cursor.execute("SELECT id, service_name, amount, created_at, status FROM invoices WHERE patient_username = ? ORDER BY id DESC", (username,))
        rows = self.cursor.fetchall()
        return [{"id": r[0], "service": r[1], "amount": r[2], "date": r[3], "status": r[4]} for r in rows]

    def pay_invoice(self, invoice_id):
        self.cursor.execute("UPDATE invoices SET status = 'Paid' WHERE id = ?", (invoice_id,))
        self.conn.commit()

    def close(self):
        self.conn.close()

    def cancel_appointment(self, appointment_id):
        # Cập nhật trạng thái thành 'Đã hủy'
        self.cursor.execute("UPDATE appointments SET status = 'Đã hủy' WHERE id = ?", (appointment_id,))
        self.conn.commit()

    def finish_examination(self, appointment_id, full_report_text):
        """
        Lưu kết quả khám vào cột 'reason' (hoặc cột result nếu có)
        và chuyển trạng thái thành 'Hoan thanh'
        """
        self.cursor.execute(
            "UPDATE appointments SET status = 'Hoan thanh', reason = ? WHERE id = ?", 
            (full_report_text, appointment_id)
        )
        self.conn.commit()