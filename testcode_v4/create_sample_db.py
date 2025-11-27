import sqlite3
import os
import json
from datetime import datetime, timedelta
from database.models import ClinicDatabase 
from core.password_hasher import PasswordHasher

def create_sample_data():
    print("--- KHOI TAO DU LIEU TEST (DA THEM CHUYEN KHOA) ---")
    db = ClinicDatabase()
    conn = db.conn
    cursor = db.cursor

    # 1. XÓA SẠCH DỮ LIỆU CŨ
    tables = ["invoices", "appointments", "medicines", "users"]
    for t in tables:
        cursor.execute(f"DELETE FROM {t}")
    cursor.execute("DELETE FROM sqlite_sequence") # Reset ID tự tăng

    # Mật khẩu chung: 123456
    pw_hash = PasswordHasher.hash_password("123456")

    # --- HÀM TẠO JSON ---
    def doc_info(specialty, exp, rating, price, branch, image="doc_male.png"):
        return json.dumps({
            "specialty": specialty, "exp": exp, "rating": rating, 
            "price": price, "branch": branch, "image": image, "phone": "0988777666"
        }, ensure_ascii=False)

    def patient_info(dob, gender, phone, cccd, address, history=""):
        return json.dumps({
            "dob": dob, "gender": gender, "phone": phone, "cccd": cccd,
            "address": address, "history": history, "insurance": "BHYT-SAMPLE"
        }, ensure_ascii=False)

    # 2. TẠO USERS (Admin, Lễ tân, Bác sĩ, Bệnh nhân)
    users = [
        ("admin", pw_hash, "admin", "Quản Trị Viên", "{}"),
        ("letan1", pw_hash, "receptionist", "Lễ Tân (CS1)", json.dumps({"branch": "CS1"})),
        
        # --- BÁC SĨ (Đã bổ sung thêm chuyên khoa) ---
        
        # 1. Tim mạch (CS1)
        ("bs_hung", pw_hash, "doctor", "ThS.BS Trần Văn Hùng", 
         doc_info("Tim mạch", 15, 4.9, 500000, "CS1")), 
         
        # 2. Nhi khoa (CS1)
        ("bs_lien", pw_hash, "doctor", "BS.CKII Nguyễn Thị Liên", 
         doc_info("Nhi khoa", 20, 5.0, 400000, "CS1", "doc_female.png")), 
         
        # 3. Da liễu (CS2)
        ("bs_minh", pw_hash, "doctor", "BS. Lê Nhật Minh", 
         doc_info("Da liễu", 8, 4.7, 300000, "CS2")), 
         
        # 4. Nội tổng quát (CS2)
        ("bs_thao", pw_hash, "doctor", "ThS.BS Phạm Thanh Thảo", 
         doc_info("Nội tổng quát", 12, 4.8, 250000, "CS2", "doc_female.png")),

        # --- CÁC CHUYÊN KHOA MỚI THÊM ---
        # 5. Tai Mũi Họng (CS1)
        ("bs_khanh", pw_hash, "doctor", "BS. Phạm Quốc Khánh", 
         doc_info("Tai Mũi Họng", 10, 4.6, 300000, "CS1")),

        # 6. Răng Hàm Mặt (CS2)
        ("bs_tuan", pw_hash, "doctor", "TS.BS Hoàng Anh Tuấn", 
         doc_info("Răng Hàm Mặt", 14, 4.9, 350000, "CS2")),

        # --- BỆNH NHÂN ---
        ("bn_an", pw_hash, "patient", "Nguyễn Văn An", 
         patient_info("12/05/1990", "Nam", "0912345678", "001090000001", "123 Kim Mã, Hà Nội", "Dị ứng Penicillin")),
         
        ("bn_binh", pw_hash, "patient", "Trần Thị Bình", "{}"), 
    ]
    cursor.executemany("INSERT INTO users VALUES (?, ?, ?, ?, ?)", users)

    # 3. TẠO KHO THUỐC
    medicines = [
        ("Paracetamol 500mg", 500, "Viên"), ("Amoxicillin 500mg", 200, "Viên"),
        ("Vitamin C 500mg", 100, "Lọ"), ("Siro ho Prospan", 50, "Chai"),
        ("Amlodipin 5mg", 300, "Viên"), ("Berberin", 100, "Lọ"),
        ("Oresol", 200, "Gói"), ("Fucidin Cream", 40, "Tuýp")
    ]
    cursor.executemany("INSERT INTO medicines VALUES (?, ?, ?)", medicines)

    # 4. TẠO LỊCH HẸN & LỊCH SỬ KHÁM
    today = datetime.now()
    d_today = today.strftime("%Y-%m-%d")
    d_tmr = (today + timedelta(days=1)).strftime("%Y-%m-%d")
    d_past1 = (today - timedelta(days=30)).strftime("%Y-%m-%d")
    d_past2 = (today - timedelta(days=1)).strftime("%Y-%m-%d")

    appointments = [
        # --- QUÁ KHỨ (Đã xong) ---
        # 1. Khám Tim (Tháng trước)
        ("bn_an", d_past1, "09:00", 
         "[BK01] [CS1] [ThS.BS Trần Văn Hùng] [BN: Nguyễn Văn An]\nCHẨN ĐOÁN: I10 - Tăng huyết áp\nCHỈ ĐỊNH: Điện tâm đồ\nLỜI DẶN: Ăn nhạt.", 
         "Hoan thanh"),
         
        # 2. Khám Nội (Hôm qua)
        ("bn_an", d_past2, "14:00", 
         "[BK02] [CS2] [ThS.BS Phạm Thanh Thảo] [BN: Nguyễn Văn An]\nCHẨN ĐOÁN: J00 - Cúm mùa\nLỜI DẶN: Nghỉ ngơi.", 
         "Hoan thanh"),

        # --- HÔM NAY ---
        # 3. Đã Check-in
        ("bn_an", d_today, "08:00", 
         "[BK03] [CS1] [BS.CKII Nguyễn Thị Liên] [BN: Con trai] Bé ho nhiều về đêm, sốt nhẹ.", 
         "Checked-in"),

        # 4. Mới đặt
        ("bn_binh", d_today, "10:30", 
         "[BK04] [CS2] [BS. Lê Nhật Minh] Tư vấn da liễu.", 
         "Da dat"),

        # --- TƯƠNG LAI ---
        # 5. Ngày mai
        ("bn_an", d_tmr, "09:00", 
         "[BK05] [CS1] [ThS.BS Trần Văn Hùng] Tái khám định kỳ.", 
         "Da dat"),
    ]
    cursor.executemany("INSERT INTO appointments (patient_username, date, time, reason, status) VALUES (?, ?, ?, ?, ?)", appointments)

    # 5. TẠO HÓA ĐƠN
    invoices = [
        # Hóa đơn cũ (Đã trả)
        ("bn_an", "Phí khám Tim mạch (BK01)", 500000, "Paid", d_past1),
        ("bn_an", "Thuốc: Amlodipin (BK01)", 150000, "Paid", d_past1),
        
        # Hóa đơn hôm nay (Chưa trả)
        ("bn_an", "Phí khám Nhi (BK03)", 400000, "Unpaid", d_today),
        ("bn_binh", "Phí khám Da liễu (BK04)", 300000, "Unpaid", d_today),
    ]
    cursor.executemany("INSERT INTO invoices (patient_username, service_name, amount, status, created_at) VALUES (?, ?, ?, ?, ?)", invoices)

    conn.commit()
    conn.close()
    print("\n=== KHOI TAO DB THANH CONG! ===")
    print("1. Admin: admin / 123456")
    print("2. Bac si (Tim): bs_hung / 123456")
    print("3. Bac si (Tai Mui Hong): bs_khanh / 123456")
    print("4. Benh nhan: bn_an / 123456")

if __name__ == "__main__":
    create_sample_data()