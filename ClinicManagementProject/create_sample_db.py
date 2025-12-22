import sqlite3
import os
import json
import unicodedata
from datetime import datetime, timedelta
from database.models import ClinicDatabase 
from core.password_hasher import PasswordHasher

def remove_accents(input_str):
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)])

def create_sample_data():
    print("--- KHOI TAO DB: DU LIEU DA DANG BENH NHAN ---")
    
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database', 'clinic.db')
    if os.path.exists(db_path):
        try: os.remove(db_path); print("-> Da xoa DB cu.")
        except: pass

    db = ClinicDatabase() 
    cursor = db.cursor
    pw_hash = PasswordHasher.hash_password("123456")

    # --- 2. DỊCH VỤ ---
    services = [("Khám Lâm sàng", 0, ""), ("Khám VIP", 200000, ""), ("Tư vấn từ xa", -50000, "")]
    cursor.executemany("INSERT INTO services (name, price, description) VALUES (?, ?, ?)", services)

    # --- 3. TẠO USERS (NHIỀU BỆNH NHÂN) ---
    def doc(name, spec, branch, price, img="doc_male.png"):
        info = json.dumps({"specialty": spec, "exp": 12, "rating": 4.9, "price": price, "branch": branch, "image": img}, ensure_ascii=False)
        name_clean = remove_accents(name.split()[-1]).lower()
        username = f"bs_{name_clean}_{branch.lower()}"
        return (username, pw_hash, "doctor", name, info)

    def patient(name, cccd, address="Hà Nội", history=""):
        info = json.dumps({"dob": "01/01/1990", "gender": "Nam", "phone": "0912345678", "cccd": cccd, "address": address, "history": history}, ensure_ascii=False)
        name_clean = remove_accents(name.split()[-1]).lower()
        username = f"bn_{name_clean}"
        return (username, pw_hash, "patient", name, info)

    users = [
        ("admin", pw_hash, "admin", "Admin", "{}"),
        ("letan1", pw_hash, "receptionist", "Lễ Tân", json.dumps({"branch": "CS1"})),
        
        # BÁC SĨ
        doc("ThS.BS Trần Văn Hùng", "Tim mạch", "CS1", 500000),
        doc("BS.CKII Nguyễn Thị Liên", "Nhi khoa", "CS1", 400000, "doc_female.png"),
        doc("BS. Phạm Quốc Khánh", "Tai Mũi Họng", "CS1", 300000),
        doc("BS. Lê Nhật Minh", "Da liễu", "CS2", 300000),
        doc("BS. Phạm Thanh Thảo", "Nội tổng quát", "CS2", 250000, "doc_female.png"),
        doc("TS.BS Hoàng Anh Tuấn", "Răng Hàm Mặt", "CS2", 350000),

        # DANH SÁCH BỆNH NHÂN ĐA DẠNG
        patient("Nguyễn Văn An", "00109000001", "Cầu Giấy", "Tiền sử Tim mạch"),
        patient("Trần Thị Bình", "00109000002", "Hoàn Kiếm", "Dị ứng hải sản"), # Khám Da liễu
        patient("Lê Văn Cường", "00109000003", "Đống Đa", "Đau dạ dày"),         # Khám Nội
        patient("Phạm Thu Dung", "00109000004", "Ba Đình", ""),                  # Mẹ bé (Khám Nhi)
        patient("Hoàng Văn Em", "", "Hà Đông", ""),                              # Thiếu thông tin
    ]
    cursor.executemany("INSERT INTO users VALUES (?, ?, ?, ?, ?)", users)

    # --- 4. THUỐC ---
    medicines = [("Paracetamol", 1000, "Viên", 2000), ("Amoxicillin", 500, "Viên", 5000), ("Vitamin C", 200, "Lọ", 50000), ("Nexium 40mg", 150, "Viên", 22000)]
    cursor.executemany("INSERT INTO medicines (name, quantity, unit, price) VALUES (?, ?, ?, ?)", medicines)

    # --- 5. PHÂN BỔ LỊCH HẸN (LOGIC HỢP LÝ) ---
    now = datetime.now()
    d_today = now.strftime("%Y-%m-%d")
    d_tmr = (now + timedelta(days=1)).strftime("%Y-%m-%d")
    d_past = (now - timedelta(days=30)).strftime("%Y-%m-%d")

    appointments = [
        # 1. Ông An (Bệnh tim) -> Khám BS Hùng (Tim mạch)
        ("bn_an", d_past, "09:00", 
         "[BK01] [CS1] [BN: An] Đau tức ngực trái, khó thở.", 
         "Hoan thanh", "bs_hung_cs1"),

        # 2. Anh Cường (Đau bụng) -> Khám BS Thảo (Nội)
        ("bn_cuong", d_past, "14:00", 
         "[BK02] [CS2] [BN: Cường] Đau bụng thượng vị, ợ chua.", 
         "Hoan thanh", "bs_thao_cs2"),

        # 3. Chị Bình (Nổi mẩn) -> Khám BS Minh (Da liễu) - Đang chờ
        ("bn_binh", d_today, "08:30", 
         "[BK03] [CS2] [BN: Bình] Nổi mẩn đỏ ngứa vùng lưng.", 
         "Checked-in", "bs_minh_cs2"),

        # 4. Chị Dung (Con ốm) -> Khám BS Liên (Nhi) - Đang chờ
        ("bn_dung", d_today, "09:00", 
         "[BK04] [CS1] [BN: Con trai 5 tuổi] Sốt cao 39 độ, ho.", 
         "Checked-in", "bs_lien_cs1"),
         
        # 5. Ông An tái khám ngày mai
        ("bn_an", d_tmr, "10:00", 
         "[BK05] [CS1] [BN: An] Tái khám định kỳ.", 
         "Da dat", "bs_hung_cs1"),
    ]
    
    cursor.executemany("""
        INSERT INTO appointments (patient_username, date, time, reason, status, doctor_username) 
        VALUES (?, ?, ?, ?, ?, ?)
    """, appointments)

    # --- 6. HÓA ĐƠN ---
    invoices = [
        ("bn_an", "Phí khám Tim mạch (BK01)", 500000, "Paid", d_past),
        ("bn_cuong", "Phí khám Nội (BK02)", 250000, "Paid", d_past),
        ("bn_binh", "Phí khám Da liễu (BK03)", 300000, "Unpaid", d_today),
        ("bn_dung", "Phí khám Nhi (BK04)", 400000, "Unpaid", d_today),
    ]
    cursor.executemany("INSERT INTO invoices (patient_username, service_name, amount, status, created_at) VALUES (?, ?, ?, ?, ?)", invoices)

    db.conn.commit()
    db.conn.close()
    print("\n=== DB DA CAP NHAT: NHIEU BENH NHAN - LOGIC THUC TE ===")
    print("1. bn_an (Tim mạch) - User: bn_an / 123456")
    print("2. bn_binh (Da liễu) - User: bn_binh / 123456")
    print("3. bn_cuong (Nội khoa) - User: bn_cuong / 123456")
    print("4. bn_dung (Nhi khoa) - User: bn_dung / 123456")

if __name__ == "__main__":
    create_sample_data()