import bcrypt

class PasswordHasher:
    @staticmethod
    def hash_password(plain_password):
        # Chuyển password sang bytes và mã hóa
        return bcrypt.hashpw(plain_password.encode('utf-8'), bcrypt.gensalt())

    @staticmethod
    def verify_password(plain_password, hashed_password):
        # Kiểm tra password
        # Lưu ý: hashed_password từ DB có thể là string, cần encode lại sang bytes
        if isinstance(hashed_password, str):
            hashed_password = hashed_password.encode('utf-8')
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password)