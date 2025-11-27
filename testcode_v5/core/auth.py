import re
from core.password_hasher import PasswordHasher

class AuthManager:
    def __init__(self, db):
        self.db = db
        self.current_user = None
        self.current_role = None

    def login(self, username, password):
        user = self.db.get_user(username)
        if user and PasswordHasher.verify_password(password, user['password']):
            self.current_user = username
            self.current_role = user['role']
            return True, user
        return False, None

    def validate_password(self, password):
        """
        Kiểm tra mật khẩu tiêu chuẩn:
        - Ít nhất 6 ký tự
        - Có ít nhất 1 chữ cái
        - Có ít nhất 1 số
        """
        if len(password) < 6:
            return False, "Mật khẩu phải có ít nhất 6 ký tự!"
        if not re.search(r"[a-zA-Z]", password):
            return False, "Mật khẩu phải chứa ít nhất 1 chữ cái!"
        if not re.search(r"\d", password):
            return False, "Mật khẩu phải chứa ít nhất 1 số!"
        return True, ""

    def register(self, username, password, confirm_password):
        # 1. Kiểm tra dữ liệu đầu vào
        if not username or not password:
            return False, "Vui lòng nhập đầy đủ thông tin!"
            
        if " " in username:
            return False, "Tên đăng nhập không được chứa khoảng trắng!"

        # 2. Kiểm tra khớp mật khẩu
        if password != confirm_password:
            return False, "Mật khẩu nhập lại không khớp!"

        # 3. Kiểm tra độ mạnh mật khẩu
        is_valid, msg = self.validate_password(password)
        if not is_valid:
            return False, msg

        # 4. Đăng ký (Tự động lấy username làm Tên hiển thị)
        success, db_msg = self.db.add_user(username, password, "patient", name=username)
        return success, db_msg

    def logout(self):
        self.current_user = None
        self.current_role = None