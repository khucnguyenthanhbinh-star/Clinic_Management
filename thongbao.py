from datetime import datetime, timedelta
from typing import List


class ThongBao:
    
    _ma_thong_bao_counter = 5000
    
    # Các loại thông báo
    LOAI_LICH_HEN = "Lịch hẹn"
    LOAI_KET_QUA = "Kết quả xét nghiệm"
    LOAI_DON_THUOC = "Đơn thuốc"
    LOAI_TAI_KHAM = "Tái khám"
    LOAI_THANH_TOAN = "Thanh toán"
    LOAI_HE_THONG = "Hệ thống"
    LOAI_KHUYEN_MAI = "Khuyến mãi"
    
    # Mức độ ưu tiên
    MUC_DO_THAP = "Thấp"
    MUC_DO_TRUNG_BINH = "Trung bình"
    MUC_DO_CAO = "Cao"
    MUC_DO_KHAN_CAP = "Khẩn cấp"
    
    def __init__(self, loai_thong_bao: str, tieu_de: str, 
                 noi_dung: str, muc_do_uu_tien: str = None):
        self.ma_thong_bao = self._tao_ma_thong_bao()
        self.loai_thong_bao = loai_thong_bao
        self.tieu_de = tieu_de
        self.noi_dung = noi_dung
        self.muc_do_uu_tien = muc_do_uu_tien or self.MUC_DO_TRUNG_BINH
        self.ngay_tao = datetime.now()
        self.da_doc = False
        self.ngay_doc = None
        self.lien_ket = ""  # Link đến chi tiết (mã hồ sơ, mã lịch hẹn...)
        self.hanh_dong = ""  # Hành động cần thực hiện
    
    @classmethod
    def _tao_ma_thong_bao(cls) -> str:
        """Tạo mã thông báo tự động"""
        ma = f"TB{cls._ma_thong_bao_counter:06d}"
        cls._ma_thong_bao_counter += 1
        return ma
    
    def danh_dau_da_doc(self):
        """Đánh dấu thông báo đã đọc"""
        if not self.da_doc:
            self.da_doc = True
            self.ngay_doc = datetime.now()
    
    def danh_dau_chua_doc(self):
        """Đánh dấu thông báo chưa đọc"""
        self.da_doc = False
        self.ngay_doc = None
    
    def them_lien_ket(self, lien_ket: str, hanh_dong: str = ""):
        """Thêm liên kết và hành động cho thông báo"""
        self.lien_ket = lien_ket
        self.hanh_dong = hanh_dong
    
    def la_khan_cap(self) -> bool:
        """Kiểm tra thông báo có khẩn cấp không"""
        return self.muc_do_uu_tien == self.MUC_DO_KHAN_CAP
    
    def thoi_gian_tu_khi_tao(self) -> str:
        """Tính thời gian từ khi tạo thông báo"""
        delta = datetime.now() - self.ngay_tao
        
        if delta.days > 0:
            return f"{delta.days} ngày trước"
        elif delta.seconds >= 3600:
            return f"{delta.seconds // 3600} giờ trước"
        elif delta.seconds >= 60:
            return f"{delta.seconds // 60} phút trước"
        else:
            return "Vừa xong"
    
    def __str__(self) -> str:
        trang_thai = "●" if not self.da_doc else "○"
        uu_tien = ""
        if self.muc_do_uu_tien == self.MUC_DO_CAO:
            uu_tien = " [!]"
        elif self.muc_do_uu_tien == self.MUC_DO_KHAN_CAP:
            uu_tien = " [!!]"
        
        return (f"{trang_thai} [{self.loai_thong_bao}]{uu_tien} {self.tieu_de}\n"
                f"   {self.thoi_gian_tu_khi_tao()}")
    
    def xem_chi_tiet(self) -> str:
        """Xem chi tiết thông báo"""
        lines = [
            "=" * 60,
            f"[{self.loai_thong_bao}] {self.tieu_de}",
            "=" * 60,
            f"Mức độ: {self.muc_do_uu_tien}",
            f"Thời gian: {self.ngay_tao.strftime('%d/%m/%Y %H:%M')}",
            f"Trạng thái: {'Đã đọc' if self.da_doc else 'Chưa đọc'}",
            "-" * 60,
            self.noi_dung,
        ]
        
        if self.lien_ket:
            lines.append(f"\nLiên kết: {self.lien_ket}")
        
        if self.hanh_dong:
            lines.append(f"Hành động: {self.hanh_dong}")
        
        lines.append("=" * 60)
        return "\n".join(lines)


class CaiDatThongBao:
    """Cài đặt thông báo của bệnh nhân"""
    
    def __init__(self):
        # Bật/tắt nhận thông báo theo loại
        self.nhan_thong_bao_lich_hen = True
        self.nhan_thong_bao_ket_qua = True
        self.nhan_thong_bao_don_thuoc = True
        self.nhan_thong_bao_tai_kham = True
        self.nhan_thong_bao_thanh_toan = True
        self.nhan_thong_bao_he_thong = True
        self.nhan_thong_bao_khuyen_mai = False
        
        # Kênh nhận thông báo
        self.nhan_thong_bao_email = True
        self.nhan_thong_bao_sms = True
        self.nhan_thong_bao_app = True
    
    def bat_tat_thong_bao(self, loai: str, trang_thai: bool):
        """Bật/tắt nhận thông báo theo loại"""
        loai_mapping = {
            ThongBao.LOAI_LICH_HEN: "nhan_thong_bao_lich_hen",
            ThongBao.LOAI_KET_QUA: "nhan_thong_bao_ket_qua",
            ThongBao.LOAI_DON_THUOC: "nhan_thong_bao_don_thuoc",
            ThongBao.LOAI_TAI_KHAM: "nhan_thong_bao_tai_kham",
            ThongBao.LOAI_THANH_TOAN: "nhan_thong_bao_thanh_toan",
            ThongBao.LOAI_HE_THONG: "nhan_thong_bao_he_thong",
            ThongBao.LOAI_KHUYEN_MAI: "nhan_thong_bao_khuyen_mai",
        }
        
        if loai in loai_mapping:
            setattr(self, loai_mapping[loai], trang_thai)
    
    def kiem_tra_cho_phep(self, loai: str) -> bool:
        """Kiểm tra có cho phép nhận thông báo loại này không"""
        loai_mapping = {
            ThongBao.LOAI_LICH_HEN: self.nhan_thong_bao_lich_hen,
            ThongBao.LOAI_KET_QUA: self.nhan_thong_bao_ket_qua,
            ThongBao.LOAI_DON_THUOC: self.nhan_thong_bao_don_thuoc,
            ThongBao.LOAI_TAI_KHAM: self.nhan_thong_bao_tai_kham,
            ThongBao.LOAI_THANH_TOAN: self.nhan_thong_bao_thanh_toan,
            ThongBao.LOAI_HE_THONG: self.nhan_thong_bao_he_thong,
            ThongBao.LOAI_KHUYEN_MAI: self.nhan_thong_bao_khuyen_mai,
        }
        return loai_mapping.get(loai, True)
    
    def hien_thi_cai_dat(self) -> str:
        """Hiển thị cài đặt thông báo"""
        lines = [
            "=" * 60,
            "CÀI ĐẶT THÔNG BÁO",
            "=" * 60,
            "\nLOẠI THÔNG BÁO:",
            f"  1. Lịch hẹn: {'✓ Bật' if self.nhan_thong_bao_lich_hen else '✗ Tắt'}",
            f"  2. Kết quả XN: {'✓ Bật' if self.nhan_thong_bao_ket_qua else '✗ Tắt'}",
            f"  3. Đơn thuốc: {'✓ Bật' if self.nhan_thong_bao_don_thuoc else '✗ Tắt'}",
            f"  4. Tái khám: {'✓ Bật' if self.nhan_thong_bao_tai_kham else '✗ Tắt'}",
            f"  5. Thanh toán: {'✓ Bật' if self.nhan_thong_bao_thanh_toan else '✗ Tắt'}",
            f"  6. Hệ thống: {'✓ Bật' if self.nhan_thong_bao_he_thong else '✗ Tắt'}",
            f"  7. Khuyến mãi: {'✓ Bật' if self.nhan_thong_bao_khuyen_mai else '✗ Tắt'}",
            "",
            "KÊNH NHẬN THÔNG BÁO:",
            f"  8. Email: {'✓ Bật' if self.nhan_thong_bao_email else '✗ Tắt'}",
            f"  9. SMS: {'✓ Bật' if self.nhan_thong_bao_sms else '✗ Tắt'}",
            f"  10. App: {'✓ Bật' if self.nhan_thong_bao_app else '✗ Tắt'}",
            "=" * 60,
        ]
        return "\n".join(lines)


class BenhNhanThongBao:
    """
    CHỨC NĂNG NHẬN VÀ HIỂN THỊ THÔNG BÁO CỦA BỆNH NHÂN
    Đây là class chính mà bệnh nhân sử dụng để:
    - Xem thông báo
    - Đọc thông báo
    - Quản lý thông báo
    - Cài đặt nhận thông báo
    """
    
    def __init__(self, ma_benh_nhan: str, ten_benh_nhan: str):
        self.ma_benh_nhan = ma_benh_nhan
        self.ten_benh_nhan = ten_benh_nhan
        self.danh_sach_thong_bao: List[ThongBao] = []
        self.cai_dat = CaiDatThongBao()
    
    # ===== CHỨC NĂNG XEM THÔNG BÁO =====
    
    def xem_trang_chu(self) -> str:
        """Màn hình chính - hiển thị tổng quan thông báo"""
        chua_doc = self.dem_chua_doc()
        khan_cap = len(self.lay_thong_bao_khan_cap())
        
        lines = [
            "=" * 60,
            f"THÔNG BÁO - {self.ten_benh_nhan}".center(60),
            "=" * 60,
            f"📬 Tổng số thông báo: {len(self.danh_sach_thong_bao)}",
            f"🔴 Chưa đọc: {chua_doc}",
            f"⚠️  Khẩn cấp: {khan_cap}",
            "=" * 60,
            "\nMENU:",
            "  1. Xem tất cả thông báo",
            "  2. Xem thông báo chưa đọc",
            "  3. Xem theo loại",
            "  4. Tìm kiếm thông báo",
            "  5. Cài đặt thông báo",
            "=" * 60,
        ]
        return "\n".join(lines)
    
    def xem_tat_ca_thong_bao(self, trang: int = 1, so_luong_trang: int = 10) -> str:
        """Xem tất cả thông báo (có phân trang)"""
        bat_dau = (trang - 1) * so_luong_trang
        ket_thuc = bat_dau + so_luong_trang
        danh_sach = self.danh_sach_thong_bao[bat_dau:ket_thuc]
        tong_trang = (len(self.danh_sach_thong_bao) + so_luong_trang - 1) // so_luong_trang
        
        lines = [
            "=" * 60,
            f"TẤT CẢ THÔNG BÁO (Trang {trang}/{tong_trang})".center(60),
            "=" * 60,
        ]
        
        if not danh_sach:
            lines.append("\n📭 Không có thông báo nào.")
        else:
            for i, tb in enumerate(danh_sach, bat_dau + 1):
                lines.append(f"\n{i}. {tb}")
        
        lines.append("\n" + "=" * 60)
        return "\n".join(lines)
    
    def xem_thong_bao_chua_doc(self) -> str:
        """Xem chỉ thông báo chưa đọc"""
        danh_sach = [tb for tb in self.danh_sach_thong_bao if not tb.da_doc]
        
        lines = [
            "=" * 60,
            f"THÔNG BÁO CHƯA ĐỌC ({len(danh_sach)})".center(60),
            "=" * 60,
        ]
        
        if not danh_sach:
            lines.append("\n✅ Bạn đã đọc hết thông báo!")
        else:
            for i, tb in enumerate(danh_sach, 1):
                lines.append(f"\n{i}. {tb}")
        
        lines.append("\n" + "=" * 60)
        return "\n".join(lines)
    
    def xem_theo_loai(self, loai: str) -> str:
        """Xem thông báo theo loại"""
        danh_sach = [tb for tb in self.danh_sach_thong_bao 
                     if tb.loai_thong_bao == loai]
        
        lines = [
            "=" * 60,
            f"THÔNG BÁO: {loai.upper()} ({len(danh_sach)})".center(60),
            "=" * 60,
        ]
        
        if not danh_sach:
            lines.append(f"\n📭 Không có thông báo {loai}.")
        else:
            for i, tb in enumerate(danh_sach, 1):
                lines.append(f"\n{i}. {tb}")
        
        lines.append("\n" + "=" * 60)
        return "\n".join(lines)
    
    def xem_chi_tiet_thong_bao(self, so_thu_tu: int) -> str:
        """Xem chi tiết thông báo theo số thứ tự"""
        if 1 <= so_thu_tu <= len(self.danh_sach_thong_bao):
            tb = self.danh_sach_thong_bao[so_thu_tu - 1]
            tb.danh_dau_da_doc()  # Tự động đánh dấu đã đọc khi xem
            return tb.xem_chi_tiet()
        return "❌ Không tìm thấy thông báo."
    
    def tim_kiem_thong_bao(self, tu_khoa: str) -> str:
        """Tìm kiếm thông báo"""
        tu_khoa_lower = tu_khoa.lower()
        ket_qua = [tb for tb in self.danh_sach_thong_bao 
                   if (tu_khoa_lower in tb.tieu_de.lower() or 
                       tu_khoa_lower in tb.noi_dung.lower())]
        
        lines = [
            "=" * 60,
            f"KẾT QUẢ TÌM KIẾM: '{tu_khoa}' ({len(ket_qua)})".center(60),
            "=" * 60,
        ]
        
        if not ket_qua:
            lines.append(f"\n🔍 Không tìm thấy thông báo chứa '{tu_khoa}'.")
        else:
            for i, tb in enumerate(ket_qua, 1):
                lines.append(f"\n{i}. {tb}")
        
        lines.append("\n" + "=" * 60)
        return "\n".join(lines)
    
    # ===== CHỨC NĂNG QUẢN LÝ THÔNG BÁO =====
    
    def danh_dau_da_doc(self, so_thu_tu: int) -> str:
        """Đánh dấu một thông báo là đã đọc"""
        if 1 <= so_thu_tu <= len(self.danh_sach_thong_bao):
            tb = self.danh_sach_thong_bao[so_thu_tu - 1]
            tb.danh_dau_da_doc()
            return f"✓ Đã đánh dấu thông báo '{tb.tieu_de}' là đã đọc."
        return "❌ Không tìm thấy thông báo."
    
    def danh_dau_chua_doc(self, so_thu_tu: int) -> str:
        """Đánh dấu một thông báo là chưa đọc"""
        if 1 <= so_thu_tu <= len(self.danh_sach_thong_bao):
            tb = self.danh_sach_thong_bao[so_thu_tu - 1]
            tb.danh_dau_chua_doc()
            return f"✓ Đã đánh dấu thông báo '{tb.tieu_de}' là chưa đọc."
        return "❌ Không tìm thấy thông báo."
    
    def danh_dau_tat_ca_da_doc(self):
        """Đánh dấu tất cả thông báo là đã đọc"""
        for tb in self.danh_sach_thong_bao:
            tb.danh_dau_da_doc()
        return f"✓ Đã đánh dấu tất cả {len(self.danh_sach_thong_bao)} thông báo là đã đọc."
    
    def xoa_thong_bao(self, so_thu_tu: int) -> str:
        """Xóa một thông báo"""
        if 1 <= so_thu_tu <= len(self.danh_sach_thong_bao):
            tb = self.danh_sach_thong_bao.pop(so_thu_tu - 1)
            return f"✓ Đã xóa thông báo '{tb.tieu_de}'."
        return "❌ Không tìm thấy thông báo."
    
    def xoa_tat_ca_da_doc(self):
        """Xóa tất cả thông báo đã đọc"""
        so_luong_truoc = len(self.danh_sach_thong_bao)
        self.danh_sach_thong_bao = [tb for tb in self.danh_sach_thong_bao 
                                     if not tb.da_doc]
        so_luong_xoa = so_luong_truoc - len(self.danh_sach_thong_bao)
        return f"✓ Đã xóa {so_luong_xoa} thông báo đã đọc."
    
    # ===== CHỨC NĂNG CÀI ĐẶT =====
    
    def xem_cai_dat(self) -> str:
        """Xem cài đặt thông báo hiện tại"""
        return self.cai_dat.hien_thi_cai_dat()
    
    def thay_doi_cai_dat(self, loai_thong_bao: str, bat_tat: bool) -> str:
        """Thay đổi cài đặt nhận thông báo"""
        self.cai_dat.bat_tat_thong_bao(loai_thong_bao, bat_tat)
        trang_thai = "bật" if bat_tat else "tắt"
        return f"✓ Đã {trang_thai} thông báo {loai_thong_bao}."
    
    # ===== CHỨC NĂNG HỖ TRỢ =====
    
    def dem_chua_doc(self) -> int:
        """Đếm số thông báo chưa đọc"""
        return sum(1 for tb in self.danh_sach_thong_bao if not tb.da_doc)
    
    def lay_thong_bao_khan_cap(self) -> List[ThongBao]:
        """Lấy danh sách thông báo khẩn cấp chưa đọc"""
        return [tb for tb in self.danh_sach_thong_bao 
                if not tb.da_doc and tb.la_khan_cap()]
    
    def thong_ke_theo_loai(self) -> dict:
        """Thống kê số lượng thông báo theo loại"""
        thong_ke = {}
        for tb in self.danh_sach_thong_bao:
            loai = tb.loai_thong_bao
            thong_ke[loai] = thong_ke.get(loai, 0) + 1
        return thong_ke
    
    # ===== CHỨC NĂNG NHẬN THÔNG BÁO (Từ hệ thống) =====
    
    def nhan_thong_bao_moi(self, thong_bao: ThongBao) -> bool:
        """Nhận thông báo mới từ hệ thống"""
        # Kiểm tra cài đặt có cho phép không
        if not self.cai_dat.kiem_tra_cho_phep(thong_bao.loai_thong_bao):
            return False
        
        self.danh_sach_thong_bao.insert(0, thong_bao)  # Thêm vào đầu danh sách
        return True


# ===== DEMO SỬ DỤNG - QUAN ĐIỂM BỆNH NHÂN =====
if __name__ == "__main__":
    print("=== DEMO: BỆNH NHÂN SỬ DỤNG CHỨC NĂNG THÔNG BÁO ===\n")
    
    # Giả lập: Bệnh nhân đăng nhập vào hệ thống
    benh_nhan = BenhNhanThongBao("BN12345", "Nguyễn Văn A")
    
    # Giả lập: Hệ thống gửi một số thông báo cho bệnh nhân
    print("📩 Hệ thống đang gửi thông báo...\n")
    
    # Thông báo 1: Lịch hẹn
    tb1 = ThongBao(
        ThongBao.LOAI_LICH_HEN,
        "Nhắc nhở lịch hẹn khám bệnh",
        f"Bạn có lịch hẹn khám bệnh:\n"
        f"  - Thời gian: {(datetime.now() + timedelta(days=2)).strftime('%d/%m/%Y %H:%M')}\n"
        f"  - Bác sĩ: BS. Trần Thị B\n"
        f"  - Phòng khám: Phòng số 3",
        ThongBao.MUC_DO_CAO
    )
    tb1.them_lien_ket("LH001", "Xem chi tiết lịch hẹn")
    benh_nhan.nhan_thong_bao_moi(tb1)
    
    # Thông báo 2: Kết quả
    tb2 = ThongBao(
        ThongBao.LOAI_KET_QUA,
        "Kết quả xét nghiệm máu đã có",
        "Kết quả xét nghiệm máu của bạn đã có.\n"
        "Vui lòng truy cập hệ thống để xem chi tiết.",
        ThongBao.MUC_DO_CAO
    )
    tb2.them_lien_ket("HS001", "Xem kết quả")
    benh_nhan.nhan_thong_bao_moi(tb2)
    
    # Thông báo 3: Thanh toán
    tb3 = ThongBao(
        ThongBao.LOAI_THANH_TOAN,
        "Hóa đơn chờ thanh toán",
        "Bạn có hóa đơn chờ thanh toán:\n"
        "  - Mã hóa đơn: HD001\n"
        "  - Số tiền: 380,000 VNĐ",
        ThongBao.MUC_DO_TRUNG_BINH
    )
    tb3.them_lien_ket("HD001", "Xem hóa đơn")
    benh_nhan.nhan_thong_bao_moi(tb3)
    
    # Thông báo 4: Tái khám
    tb4 = ThongBao(
        ThongBao.LOAI_TAI_KHAM,
        "Nhắc nhở tái khám",
        f"Bác sĩ BS. Trần Thị B đã lên lịch tái khám cho bạn:\n"
        f"  - Ngày: {(datetime.now() + timedelta(days=30)).strftime('%d/%m/%Y')}",
        ThongBao.MUC_DO_CAO
    )
    benh_nhan.nhan_thong_bao_moi(tb4)
    
    # Thông báo 5: Hệ thống
    tb5 = ThongBao(
        ThongBao.LOAI_HE_THONG,
        "Bảo trì hệ thống",
        "Hệ thống sẽ bảo trì vào 02:00 - 04:00 ngày 20/11/2024.",
        ThongBao.MUC_DO_THAP
    )
    benh_nhan.nhan_thong_bao_moi(tb5)
    
    print("✓ Đã nhận 5 thông báo từ hệ thống\n")
    print("="*60)
    input("\nNhấn Enter để tiếp tục...")
    
    # ===== BỆNH NHÂN BẮT ĐẦU SỬ DỤNG =====
    
    # 1. Xem trang chủ
    print("\n\n📱 BỆNH NHÂN MỞ ỨNG DỤNG")
    print(benh_nhan.xem_trang_chu())
    input("\nNhấn Enter để tiếp tục...")
    
    # 2. Xem tất cả thông báo
    print("\n\n📋 CHỌN: Xem tất cả thông báo")
    print(benh_nhan.xem_tat_ca_thong_bao())
    input("\nNhấn Enter để tiếp tục...")
    
    # 3. Xem chi tiết một thông báo
    print("\n\n👁️  CHỌN: Xem chi tiết thông báo số 1")
    print(benh_nhan.xem_chi_tiet_thong_bao(1))
    input("\nNhấn Enter để tiếp tục...")
    
    # 4. Xem thông báo chưa đọc
    print("\n\n🔴 CHỌN: Xem thông báo chưa đọc")
    print(benh_nhan.xem_thong_bao_chua_doc())
    input("\nNhấn Enter để tiếp tục...")
    
    # 5. Xem theo loại
    print("\n\n📂 CHỌN: Xem thông báo 'Lịch hẹn'")
    print(benh_nhan.xem_theo_loai(ThongBao.LOAI_LICH_HEN))
    input("\nNhấn Enter để tiếp tục...")
    
    # 6. Tìm kiếm
    print("\n\n🔍 CHỌN: Tìm kiếm 'kết quả'")
    print(benh_nhan.tim_kiem_thong_bao("kết quả"))
    input("\nNhấn Enter để tiếp tục...")
    
    # 7. Đánh dấu đã đọc
    print("\n\n✅ CHỌN: Đánh dấu thông báo số 2 là đã đọc")
    print(benh_nhan.danh_dau_da_doc(2))
    print("\nTrạng thái hiện tại:")
    print(f"  Chưa đọc: {benh_nhan.dem_chua_doc()}")
    input("\nNhấn Enter để tiếp tục...")
    
    # 8. Xóa thông báo
    print("\n\n🗑️  CHỌN: Xóa thông báo số 5")
    print(benh_nhan.xoa_thong_bao(5))
    print(f"\nCòn lại: {len(benh_nhan.danh_sach_thong_bao)} thông báo")
    input("\nNhấn Enter để tiếp tục...")
    
    # 9. Đánh dấu tất cả đã đọc
    print("\n\n✅ CHỌN: Đánh dấu tất cả là đã đọc")
    print(benh_nhan.danh_dau_tat_ca_da_doc())
    print(benh_nhan.xem_thong_bao_chua_doc())
    input("\nNhấn Enter để tiếp tục...")
    
    # 10. Xem cài đặt
    print("\n\n⚙️  CHỌN: Xem cài đặt thông báo")
    print(benh_nhan.xem_cai_dat())
    input("\nNhấn Enter để tiếp tục...")
    
    # 11. Thay đổi cài đặt
    print("\n\n⚙️  CHỌN: Tắt thông báo Khuyến mãi")
    print(benh_nhan.thay_doi_cai_dat(ThongBao.LOAI_KHUYEN_MAI, False))
    
    print("\n⚙️  CHỌN: Bật thông báo Khuyến mãi")
    print(benh_nhan.thay_doi_cai_dat(ThongBao.LOAI_KHUYEN_MAI, True))
    print("\nCài đặt hiện tại:")
    print(benh_nhan.xem_cai_dat())
    input("\nNhấn Enter để tiếp tục...")
    
    # 12. Thống kê
    print("\n\n📊 THỐNG KÊ THÔNG BÁO")
    print("="*60)
    print(f"Tổng số: {len(benh_nhan.danh_sach_thong_bao)}")
    print(f"Chưa đọc: {benh_nhan.dem_chua_doc()}")
    print(f"Khẩn cấp: {len(benh_nhan.lay_thong_bao_khan_cap())}")
    
    print("\nPhân loại:")
    thong_ke = benh_nhan.thong_ke_theo_loai()
    for loai, so_luong in thong_ke.items():
        print(f"  {loai}: {so_luong}")
    
    print("\n" + "="*60)
    print("\n✅ DEMO HOÀN TẤT!")
