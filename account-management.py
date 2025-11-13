# account_manager.py
from datetime import datetime
import os

# Dữ liệu giả lập (thay cho database)
users = [
    {"id": 1, "username": "admin", "email": "admin@clinic.com", "role": "admin", "is_active": True, "created_at": "2025-01-01"},
    {"id": 2, "username": "bs_binh", "email": "binh@doctor.com", "role": "doctor", "is_active": True, "created_at": "2025-02-15"},
    {"id": 3, "username": "bn_hung", "email": "hung@gmail.com", "role": "patient", "is_active": True, "created_at": "2025-03-10"},
    {"id": 4, "username": "bs_dat", "email": "dat@gmail.com", "role": "doctor", "is_active": False, "created_at": "2025-04-05"},
]

# Hàm hỗ trợ
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    print("="*60)
    print("     QUẢN LÝ TÀI KHOẢN NGƯỜI DÙNG - PHÒNG KHÁM")
    print("="*60)

def display_users():
    print("\nDANH SÁCH TÀI KHOẢN:")
    print("-" * 100)
    print(f"{'ID':<4} {'Tên đăng nhập':<15} {'Email':<25} {'Vai trò':<10} {'Trạng thái':<12} {'Ngày tạo':<12}")
    print("-" * 100)
    for user in users:
        status = "Hoạt động" if user["is_active"] else "Vô hiệu"
        role_vn = {"admin": "Quản trị", "doctor": "Bác sĩ", "patient": "Bệnh nhân"}
        print(f"{user['id']:<4} {user['username']:<15} {user['email']:<25} {role_vn[user['role']]:<10} {status:<12} {user['created_at']}")
    print("-" * 100)
    

def find_user_by_id(user_id):
    for user in users:
        if user["id"] == user_id:
            return user
    return None

# === CHỨC NĂNG QUẢN LÝ ===
def delete_user():
    display_users()
    try:
        uid = int(input("\nNhập ID tài khoản cần XÓA: "))
        user = find_user_by_id(uid)
        if not user:
            print("Không tìm thấy tài khoản!")
            input("Nhấn Enter để tiếp tục...")
            return
        
        if user["role"] == "admin":
            print("Cảnh báo: Không nên xóa tài khoản Quản trị viên!")
            confirm = input("Bạn có chắc muốn xóa? (y/N): ")
            if confirm.lower() != 'y':
                return

        users.remove(user)
        print(f"ĐÃ XÓA tài khoản: {user['username']}")
    except:
        print("ID không hợp lệ!")
    input("Nhấn Enter để tiếp tục...")

def toggle_user_status():
    display_users()
    try:
        uid = int(input("\nNhập ID tài khoản cần thay đổi trạng thái: "))
        user = find_user_by_id(uid)
        if not user:
            print("Không tìm thấy tài khoản!")
            input("Nhấn Enter để tiếp tục...")
            return

        user["is_active"] = not user["is_active"]
        status = "KÍCH HOẠT" if user["is_active"] else "VÔ HIỆU HÓA"
        print(f"ĐÃ {status} tài khoản: {user['username']}")
    except:
        print("ID không hợp lệ!")
    input("Nhấn Enter để tiếp tục...")

def edit_user():
    display_users()
    try:
        uid = int(input("\nNhập ID tài khoản cần CHỈNH SỬA: "))
        user = find_user_by_id(uid)
        if not user:
            print("Không tìm thấy tài khoản!")
            input("Nhấn Enter để tiếp tục...")
            return

        print(f"\nChỉnh sửa tài khoản ID={uid}")
        print(f"Hiện tại: {user['username']} | {user['email']} | {user['role']}")

        new_username = input(f"Tên đăng nhập mới (Enter để giữ): ").strip()
        new_email = input(f"Email mới (Enter để giữ): ").strip()
        new_role = input(f"Vai trò mới (admin/doctor/patient, Enter để giữ): ").strip().lower()

        if new_username:
            user["username"] = new_username
        if new_email:
            user["email"] = new_email
        if new_role in ["admin", "doctor", "patient"]:
            user["role"] = new_role

        print("ĐÃ CẬP NHẬT tài khoản thành công!")
    except:
        print("Lỗi nhập liệu!")
    input("Nhấn Enter để tiếp tục...")


def admin_menu():
    while True:
        clear_screen()
        print_header()
        display_users()

        print("\nCHỌN CHỨC NĂNG:")
        print("1. Xóa tài khoản")
        print("2. Vô hiệu hóa / Kích hoạt tài khoản")
        print("3. Chỉnh sửa tài khoản")
        print("4. Thoát")

        choice = input("\nNhập lựa chọn (1-5): ").strip()

        if choice == '1':
            delete_user()
        elif choice == '2':
            toggle_user_status()
        elif choice == '3':
            edit_user()
        elif choice == '4':
            print("Tạm biệt Admin!")
            break
        else:
            print("Lựa chọn không hợp lệ!")
            input("Nhấn Enter để tiếp tục...")

if __name__ == "__main__":
    print("Đăng nhập thành công với vai trò: QUẢN TRỊ VIÊN")
    input("Nhấn Enter để vào hệ thống quản lý...")
    admin_menu()