import sqlite3
import os
import json
from datetime import datetime, timedelta
from database.models import ClinicDatabase 
from core.password_hasher import PasswordHasher

def create_sample_data():
    print("--- KHOI TAO DU LIEU TEST LICH SU KHAM ---")
    db = ClinicDatabase()
    conn = db.conn
    cursor = db.cursor

    # 1. Reset dữ liệu
    cursor.execute("DELETE FROM invoices")
    cursor.execute("DELETE FROM appointments") 
    cursor.execute("DELETE FROM medicines")
    cursor.execute("DELETE FROM users")
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='appointments'")
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='invoices'")

    pw_hash = PasswordHasher.hash_password("123456")

    # --- HÀM HỖ TRỢ JSON ---
    def doc_info(specialty, exp, rating, price, branch, image="doc_male.png"):
        data = {
            "specialty": specialty, "exp": exp, "rating": rating, 
            "price": price, "branch": branch, "image": image, "phone": "0901234567"
        }
        return json.dumps(data, ensure_ascii=False)

    def patient_info(history="", dob="", gender="Nam", phone="", address="", insurance="", cccd=""):
        data = {
            "history": history, "dob": dob, "gender": gender, 
            "phone": phone, "address": address, "insurance": insurance, 
            "cccd": cccd, "blood_type": "A", "weight": "65", "height": "170"
        }
        return json.dumps(data, ensure_ascii=False)

    # 2. DỮ LIỆU USERS
    users = [
        ("admin", pw_hash, "admin", "Administrator", "{}"),
        ("letan1", pw_hash, "receptionist", "Lễ Tân Ca Sáng", "{}"),
        ("letan2", pw_hash, "receptionist", "Lễ Tân Ca Chiều", "{}"),

        # Bác sĩ
        ("bs_hung", pw_hash, "doctor", "ThS.BS Trần Văn Hùng", doc_info("Tim mạch", 15, 4.9, 500000, "CS1")),
        ("bs_lien", pw_hash, "doctor", "BS.CKII Nguyễn Thị Liên", doc_info("Nhi khoa", 20, 5.0, 450000, "CS1", "doc_female.png")),
        ("bs_minh", pw_hash, "doctor", "BS. Lê Nhật Minh", doc_info("Da liễu", 8, 4.7, 300000, "CS1")),
        ("bs_thao", pw_hash, "doctor", "ThS.BS Phạm Thanh Thảo", doc_info("Nội tổng quát", 10, 4.8, 250000, "CS2", "doc_female.png")),
        ("bs_nam", pw_hash, "doctor", "BS. Hoàng Văn Nam", doc_info("Phẫu thuật", 12, 4.9, 750000, "CS1")),

        # Bệnh nhân test chính: bn_an
        ("bn_an", pw_hash, "patient", "Nguyễn Văn An", 
         patient_info(
             history="Tiền sử dạ dày, Dị ứng phấn hoa", 
             dob="12/05/1990", gender="Nam", phone="0912345678", 
             address="123 Kim Mã, Hà Nội", cccd="001090000001", insurance="DN401..."
         )),
        
        # Thêm bệnh nhân khác
        ("bn_binh", pw_hash, "patient", "Trần Thị Bình",
         patient_info(
             history="Tiền sử cao huyết áp",
             dob="08/15/1985", gender="Nữ", phone="0987654321",
             address="456 Thanh Xuân, Hà Nội", cccd="001085000002", insurance="VN501..."
         )),
        
        ("bn_cuong", pw_hash, "patient", "Lý Văn Cường",
         patient_info(
             history="Không",
             dob="03/20/1995", gender="Nam", phone="0909999999",
             address="789 Ba Đình, Hà Nội", cccd="001095000003", insurance=""
         )),
    ]
    cursor.executemany("INSERT INTO users VALUES (?, ?, ?, ?, ?)", users)

    # 3. DỮ LIỆU THUỐC
    medicines = [
        ("Paracetamol", 500, "viên"),
        ("Amoxicillin", 200, "viên"),
        ("Vitamin C", 100, "lọ"),
        ("Aspirin", 150, "viên"),
        ("Omeprazole", 80, "viên"),
        ("Cetirizine", 120, "viên"),
    ]
    cursor.executemany("INSERT INTO medicines VALUES (?, ?, ?)", medicines)

    # 4. DỮ LIỆU LỊCH HẸN & LỊCH SỬ KHÁM (QUAN TRỌNG)
    
    # Mốc thời gian
    today = datetime.now()
    d_today = today.strftime("%Y-%m-%d")
    d_tomorrow = (today + timedelta(days=1)).strftime("%Y-%m-%d")
    
    # Quá khứ
    d_1_month_ago = (today - timedelta(days=30)).strftime("%Y-%m-%d")
    d_2_weeks_ago = (today - timedelta(days=14)).strftime("%Y-%m-%d")
    d_yesterday = (today - timedelta(days=1)).strftime("%Y-%m-%d")

    appointments = [
        # --- LỊCH SỬ ĐÃ KHÁM (Status = 'Hoan thanh' hoặc 'Paid') ---
        
        # 1. Khám Tim mạch (Cách đây 1 tháng) -> Để test đơn thuốc Tim mạch
        ("bn_an", d_1_month_ago, "09:00", 
         "[BK001] [CS1] [ThS.BS Trần Văn Hùng] Tức ngực, khó thở khi vận động mạnh. Chẩn đoán: Rối loạn nhịp tim nhẹ.", 
         "Hoan thanh"),

        # 2. Khám Da liễu (Cách đây 2 tuần) -> Để test đơn thuốc Da liễu
        ("bn_an", d_2_weeks_ago, "14:30", 
         "[BK002] [CS1] [BS. Lê Nhật Minh] Nổi mẩn đỏ vùng lưng, ngứa nhiều về đêm. Chẩn đoán: Viêm da cơ địa.", 
         "Hoan thanh"),

        # 3. Khám Nội tổng quát (Hôm qua) -> Để test đơn thuốc thông thường
        ("bn_an", d_yesterday, "08:00", 
         "[BK003] [CS2] [ThS.BS Phạm Thanh Thảo] Đau bụng vùng thượng vị, ợ chua. Chẩn đoán: Viêm dạ dày cấp.", 
         "Hoan thanh"),

        # --- LỊCH HẸN SẮP TỚI (Status = 'Da dat') ---
        ("bn_an", d_tomorrow, "10:00", 
         "[BK004] [CS1] [BS.CKII Nguyễn Thị Liên] [BN: Con trai] Khám ho sốt cho bé.", 
         "Da dat"),
        
        # Lịch hẹn của bệnh nhân khác
        ("bn_binh", d_today, "11:00",
         "[BK005] [CS2] [ThS.BS Phạm Thanh Thảo] Khám tư vấn sức khỏe tổng quát.",
         "Da dat"),
        
        ("bn_binh", (today - timedelta(days=3)).strftime("%Y-%m-%d"), "15:00",
         "[BK006] [CS1] [ThS.BS Trần Văn Hùng] Khám tim mạch định kỳ.",
         "Hoan thanh"),
        
        ("bn_cuong", d_tomorrow, "13:30",
         "[BK007] [CS1] [BS. Hoàng Văn Nam] Khám tiền phẫu thuật.",
         "Da dat"),
    ]
    
    cursor.executemany("INSERT INTO appointments (patient_username, date, time, reason, status) VALUES (?, ?, ?, ?, ?)", appointments)

    # 5. DỮ LIỆU HÓA ĐƠN
    invoices = [
        # Hóa đơn đã trả cho các lần khám cũ
        ("bn_an", "Phí khám tim mạch (BK001)", 500000, "Paid", d_1_month_ago),
        ("bn_an", "Phí khám da liễu (BK002)", 300000, "Paid", d_2_weeks_ago),
        
        # Hóa đơn chưa trả cho lịch sắp tới
        ("bn_an", "Phí khám Nhi (BK004)", 450000, "Unpaid", d_today),
        
        # Hóa đơn bệnh nhân khác
        ("bn_binh", "Phí khám tim mạch (BK006)", 500000, "Paid", (today - timedelta(days=3)).strftime("%Y-%m-%d")),
        ("bn_binh", "Phí khám tư vấn sức khỏe (BK005)", 250000, "Unpaid", d_today),
        
        ("bn_cuong", "Phí khám tiền phẫu thuật (BK007)", 750000, "Unpaid", d_today),
    ]
    cursor.executemany("INSERT INTO invoices (patient_username, service_name, amount, status, created_at) VALUES (?, ?, ?, ?, ?)", invoices)

    conn.commit()
    conn.close()
    print("\n=== ĐÃ CẬP NHẬT DỮ LIỆU LỊCH SỬ KHÁM ===")
    print("Tài khoản test: bn_an / 123456")

if __name__ == "__main__":
    create_sample_data()