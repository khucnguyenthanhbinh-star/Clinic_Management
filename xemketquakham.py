from datetime import datetime
from typing import List


class KetQuaXetNghiem:
    """Kết quả xét nghiệm"""
    
    _ma_xet_nghiem_counter = 3000
    
    def __init__(self, loai_xet_nghiem: str, chi_tieu: str, 
                 ket_qua: str, don_vi: str, chi_so_binh_thuong: str):
        self.ma_xet_nghiem = self._tao_ma_xet_nghiem()
        self.loai_xet_nghiem = loai_xet_nghiem  # "Máu", "Nước tiểu", "Siêu âm"...
        self.chi_tieu = chi_tieu  # "Hồng cầu", "Bạch cầu"...
        self.ket_qua = ket_qua
        self.don_vi = don_vi
        self.chi_so_binh_thuong = chi_so_binh_thuong
        self.ngay_thuc_hien = datetime.now()
        self.ghi_chu = ""
    
    @classmethod
    def _tao_ma_xet_nghiem(cls) -> str:
        """Tạo mã xét nghiệm tự động"""
        ma = f"XN{cls._ma_xet_nghiem_counter:06d}"
        cls._ma_xet_nghiem_counter += 1
        return ma
    
    def kiem_tra_binh_thuong(self) -> bool:
        """Kiểm tra kết quả có nằm trong chỉ số bình thường không"""
        # Logic đơn giản, có thể mở rộng
        try:
            ket_qua_num = float(self.ket_qua)
            if "-" in self.chi_so_binh_thuong:
                min_val, max_val = map(float, self.chi_so_binh_thuong.split("-"))
                return min_val <= ket_qua_num <= max_val
        except:
            return True
        return True
    
    def cap_nhat_ghi_chu(self, ghi_chu: str):
        """Cập nhật ghi chú cho kết quả"""
        self.ghi_chu = ghi_chu
    
    def __str__(self) -> str:
        binh_thuong = "✓" if self.kiem_tra_binh_thuong() else "⚠"
        return (f"{binh_thuong} {self.chi_tieu}: {self.ket_qua} {self.don_vi} "
                f"(BT: {self.chi_so_binh_thuong})")


class DonThuoc:
    """Đơn thuốc"""
    
    def __init__(self, ten_thuoc: str, lieu_dung: str, 
                 cach_dung: str, so_luong: int):
        self.ten_thuoc = ten_thuoc
        self.lieu_dung = lieu_dung  # "500mg", "10ml"...
        self.cach_dung = cach_dung  # "Uống sau ăn, ngày 2 lần"
        self.so_luong = so_luong
        self.ghi_chu = ""
    
    def cap_nhat_ghi_chu(self, ghi_chu: str):
        """Cập nhật ghi chú cho thuốc"""
        self.ghi_chu = ghi_chu
    
    def __str__(self) -> str:
        result = f"• {self.ten_thuoc} ({self.lieu_dung})"
        result += f"\n  Liều dùng: {self.cach_dung}"
        result += f"\n  Số lượng: {self.so_luong}"
        if self.ghi_chu:
            result += f"\n  Ghi chú: {self.ghi_chu}"
        return result


class HoSoKham:
    """Hồ sơ một lần khám bệnh"""
    
    _ma_ho_so_counter = 4000
    
    def __init__(self, ma_benh_nhan: str, ten_benh_nhan: str,
                 ma_bac_si: str, ten_bac_si: str, chuyen_khoa: str):
        self.ma_ho_so = self._tao_ma_ho_so()
        self.ma_benh_nhan = ma_benh_nhan
        self.ten_benh_nhan = ten_benh_nhan
        self.ma_bac_si = ma_bac_si
        self.ten_bac_si = ten_bac_si
        self.chuyen_khoa = chuyen_khoa
        self.ngay_kham = datetime.now()
        
        # Thông tin khám
        self.ly_do_kham = ""
        self.trieu_chung = ""
        self.chan_doan = ""
        self.huyet_ap = ""  # "120/80"
        self.nhip_tim = ""  # "75 nhịp/phút"
        self.nhiet_do = ""  # "37°C"
        self.can_nang = ""  # "65kg"
        self.chieu_cao = ""  # "170cm"
        
        # Danh sách kết quả và đơn thuốc
        self.danh_sach_xet_nghiem: List[KetQuaXetNghiem] = []
        self.danh_sach_thuoc: List[DonThuoc] = []
        
        self.loi_dan_bac_si = ""
        self.ngay_tai_kham = None
        self.ghi_chu = ""
    
    @classmethod
    def _tao_ma_ho_so(cls) -> str:
        """Tạo mã hồ sơ tự động"""
        ma = f"HS{cls._ma_ho_so_counter:06d}"
        cls._ma_ho_so_counter += 1
        return ma
    
    def cap_nhat_thong_tin_kham(self, ly_do_kham: str, trieu_chung: str,
                                chan_doan: str, **chi_so_sinh_ton):
        """Cập nhật thông tin khám bệnh"""
        self.ly_do_kham = ly_do_kham
        self.trieu_chung = trieu_chung
        self.chan_doan = chan_doan
        
        # Cập nhật các chỉ số sinh tồn nếu có
        if "huyet_ap" in chi_so_sinh_ton:
            self.huyet_ap = chi_so_sinh_ton["huyet_ap"]
        if "nhip_tim" in chi_so_sinh_ton:
            self.nhip_tim = chi_so_sinh_ton["nhip_tim"]
        if "nhiet_do" in chi_so_sinh_ton:
            self.nhiet_do = chi_so_sinh_ton["nhiet_do"]
        if "can_nang" in chi_so_sinh_ton:
            self.can_nang = chi_so_sinh_ton["can_nang"]
        if "chieu_cao" in chi_so_sinh_ton:
            self.chieu_cao = chi_so_sinh_ton["chieu_cao"]
    
    def them_ket_qua_xet_nghiem(self, ket_qua: KetQuaXetNghiem):
        """Thêm kết quả xét nghiệm"""
        self.danh_sach_xet_nghiem.append(ket_qua)
    
    def them_don_thuoc(self, thuoc: DonThuoc):
        """Thêm thuốc vào đơn"""
        self.danh_sach_thuoc.append(thuoc)
    
    def cap_nhat_loi_dan(self, loi_dan: str, ngay_tai_kham: datetime = None):
        """Cập nhật lời dặn của bác sĩ"""
        self.loi_dan_bac_si = loi_dan
        self.ngay_tai_kham = ngay_tai_kham
    
    def in_ho_so(self) -> str:
        """In hồ sơ khám bệnh"""
        lines = [
            "=" * 70,
            "HỒ SƠ KHÁM BỆNH".center(70),
            "=" * 70,
            f"Mã hồ sơ: {self.ma_ho_so}",
            f"Ngày khám: {self.ngay_kham.strftime('%d/%m/%Y %H:%M')}",
            "",
            "THÔNG TIN BỆNH NHÂN:",
            f"  Họ tên: {self.ten_benh_nhan}",
            f"  Mã BN: {self.ma_benh_nhan}",
            "",
            "BÁC SĨ KHÁM:",
            f"  BS. {self.ten_bac_si}",
            f"  Chuyên khoa: {self.chuyen_khoa}",
            "-" * 70,
        ]
        
        # Thông tin khám
        lines.extend([
            "THÔNG TIN KHÁM:",
            f"  Lý do khám: {self.ly_do_kham}",
            f"  Triệu chứng: {self.trieu_chung}",
        ])
        
        # Chỉ số sinh tồn
        if any([self.huyet_ap, self.nhip_tim, self.nhiet_do, self.can_nang, self.chieu_cao]):
            lines.append("\nCHỈ SỐ SINH TỒN:")
            if self.huyet_ap:
                lines.append(f"  Huyết áp: {self.huyet_ap}")
            if self.nhip_tim:
                lines.append(f"  Nhịp tim: {self.nhip_tim}")
            if self.nhiet_do:
                lines.append(f"  Nhiệt độ: {self.nhiet_do}")
            if self.can_nang:
                lines.append(f"  Cân nặng: {self.can_nang}")
            if self.chieu_cao:
                lines.append(f"  Chiều cao: {self.chieu_cao}")
        
        lines.extend([
            "",
            f"CHẨN ĐOÁN: {self.chan_doan}",
            "-" * 70,
        ])
        
        # Kết quả xét nghiệm
        if self.danh_sach_xet_nghiem:
            lines.append("\nKẾT QUẢ XÉT NGHIỆM:")
            loai_current = None
            for xn in self.danh_sach_xet_nghiem:
                if xn.loai_xet_nghiem != loai_current:
                    lines.append(f"\n  [{xn.loai_xet_nghiem}]")
                    loai_current = xn.loai_xet_nghiem
                lines.append(f"    {xn}")
                if xn.ghi_chu:
                    lines.append(f"      Ghi chú: {xn.ghi_chu}")
        
        # Đơn thuốc
        if self.danh_sach_thuoc:
            lines.append("\n" + "-" * 70)
            lines.append("ĐỚN THUỐC:")
            for i, thuoc in enumerate(self.danh_sach_thuoc, 1):
                lines.append(f"\n{i}. {thuoc}")
        
        # Lời dặn
        if self.loi_dan_bac_si:
            lines.append("\n" + "-" * 70)
            lines.append("LỜI DẶN CỦA BÁC SĨ:")
            lines.append(f"  {self.loi_dan_bac_si}")
        
        if self.ngay_tai_kham:
            lines.append(f"\n  Tái khám: {self.ngay_tai_kham.strftime('%d/%m/%Y')}")
        
        if self.ghi_chu:
            lines.append(f"\nGhi chú: {self.ghi_chu}")
        
        lines.append("=" * 70)
        return "\n".join(lines)
    
    def tom_tat_ho_so(self) -> str:
        """Tóm tắt hồ sơ (dùng cho danh sách)"""
        return (f"[{self.ma_ho_so}] {self.ngay_kham.strftime('%d/%m/%Y')} - "
                f"BS. {self.ten_bac_si} ({self.chuyen_khoa})\n"
                f"    Chẩn đoán: {self.chan_doan}")


class LichSuKhamBenh:
    """Quản lý lịch sử khám bệnh của bệnh nhân"""
    
    def __init__(self, ma_benh_nhan: str, ten_benh_nhan: str,
                 ngay_sinh: str, gioi_tinh: str):
        self.ma_benh_nhan = ma_benh_nhan
        self.ten_benh_nhan = ten_benh_nhan
        self.ngay_sinh = ngay_sinh
        self.gioi_tinh = gioi_tinh
        self.danh_sach_ho_so: List[HoSoKham] = []
    
    def them_ho_so(self, ho_so: HoSoKham):
        """Thêm hồ sơ khám mới"""
        if ho_so.ma_benh_nhan != self.ma_benh_nhan:
            raise ValueError("Mã bệnh nhân không khớp")
        self.danh_sach_ho_so.append(ho_so)
    
    def xem_lich_su_day_du(self) -> str:
        """Xem toàn bộ lịch sử khám bệnh"""
        lines = [
            "=" * 70,
            "LỊCH SỬ KHÁM BỆNH".center(70),
            "=" * 70,
            f"Bệnh nhân: {self.ten_benh_nhan}",
            f"Mã BN: {self.ma_benh_nhan}",
            f"Ngày sinh: {self.ngay_sinh}",
            f"Giới tính: {self.gioi_tinh}",
            f"Tổng số lần khám: {len(self.danh_sach_ho_so)}",
            "=" * 70,
        ]
        
        if not self.danh_sach_ho_so:
            lines.append("\nChưa có lịch sử khám bệnh.")
        else:
            for i, ho_so in enumerate(reversed(self.danh_sach_ho_so), 1):
                lines.append(f"\nLần khám {i}:")
                lines.append(ho_so.tom_tat_ho_so())
        
        lines.append("=" * 70)
        return "\n".join(lines)
    
    def tim_ho_so_theo_ma(self, ma_ho_so: str):
        """Tìm hồ sơ theo mã"""
        for ho_so in self.danh_sach_ho_so:
            if ho_so.ma_ho_so == ma_ho_so:
                return ho_so
        return None
    
    def tim_ho_so_theo_bac_si(self, ma_bac_si: str) -> List[HoSoKham]:
        """Tìm tất cả hồ sơ khám với bác sĩ cụ thể"""
        return [hs for hs in self.danh_sach_ho_so if hs.ma_bac_si == ma_bac_si]
    
    def tim_ho_so_theo_chan_doan(self, tu_khoa: str) -> List[HoSoKham]:
        """Tìm hồ sơ theo từ khóa trong chẩn đoán"""
        tu_khoa_lower = tu_khoa.lower()
        return [hs for hs in self.danh_sach_ho_so 
                if tu_khoa_lower in hs.chan_doan.lower()]
    
    def lay_ho_so_gan_nhat(self):
        """Lấy hồ sơ khám gần nhất"""
        if not self.danh_sach_ho_so:
            return None
        return max(self.danh_sach_ho_so, key=lambda hs: hs.ngay_kham)
    
    def lay_ho_so_theo_khoang_thoi_gian(self, tu_ngay: datetime, 
                                        den_ngay: datetime) -> List[HoSoKham]:
        """Lấy hồ sơ trong khoảng thời gian"""
        return [hs for hs in self.danh_sach_ho_so 
                if tu_ngay <= hs.ngay_kham <= den_ngay]
    
    def thong_ke_benh(self) -> dict:
        """Thống kê các bệnh đã khám"""
        thong_ke = {}
        for ho_so in self.danh_sach_ho_so:
            chan_doan = ho_so.chan_doan
            if chan_doan:
                thong_ke[chan_doan] = thong_ke.get(chan_doan, 0) + 1
        return thong_ke


class QuanLyKetQua:
    """Quản lý toàn bộ kết quả và lịch sử khám bệnh"""
    
    def __init__(self):
        self.danh_sach_lich_su: List[LichSuKhamBenh] = []
    
    def tao_lich_su_benh_nhan(self, ma_benh_nhan: str, ten_benh_nhan: str,
                              ngay_sinh: str, gioi_tinh: str) -> LichSuKhamBenh:
        """Tạo lịch sử khám bệnh cho bệnh nhân mới"""
        lich_su = LichSuKhamBenh(ma_benh_nhan, ten_benh_nhan, ngay_sinh, gioi_tinh)
        self.danh_sach_lich_su.append(lich_su)
        return lich_su
    
    def tim_lich_su_benh_nhan(self, ma_benh_nhan: str):
        """Tìm lịch sử khám bệnh của bệnh nhân"""
        for lich_su in self.danh_sach_lich_su:
            if lich_su.ma_benh_nhan == ma_benh_nhan:
                return lich_su
        return None
    
    def tao_ho_so_kham(self, ma_benh_nhan: str, ten_benh_nhan: str,
                       ma_bac_si: str, ten_bac_si: str, 
                       chuyen_khoa: str) -> HoSoKham:
        """Tạo hồ sơ khám mới"""
        ho_so = HoSoKham(ma_benh_nhan, ten_benh_nhan, 
                        ma_bac_si, ten_bac_si, chuyen_khoa)
        
        # Tự động thêm vào lịch sử nếu đã có
        lich_su = self.tim_lich_su_benh_nhan(ma_benh_nhan)
        if lich_su:
            lich_su.them_ho_so(ho_so)
        
        return ho_so


# ===== DEMO SỬ DỤNG =====
if __name__ == "__main__":
    print("=== HỆ THỐNG XEM KẾT QUẢ VÀ LỊCH SỬ KHÁM BỆNH ===\n")
    
    # Khởi tạo hệ thống
    ql_ket_qua = QuanLyKetQua()
    
    # 1. Tạo lịch sử cho bệnh nhân
    print("1. TẠO LỊCH SỬ BỆNH NHÂN")
    lich_su_bn = ql_ket_qua.tao_lich_su_benh_nhan(
        ma_benh_nhan="BN12345",
        ten_benh_nhan="Nguyễn Văn A",
        ngay_sinh="15/05/1985",
        gioi_tinh="Nam"
    )
    print(f"Đã tạo lịch sử cho bệnh nhân: {lich_su_bn.ten_benh_nhan}\n")
    
    # 2. Tạo hồ sơ khám lần 1
    print("2. KHÁM BỆNH LẦN 1 (3 tháng trước)")
    ho_so1 = ql_ket_qua.tao_ho_so_kham(
        ma_benh_nhan="BN12345",
        ten_benh_nhan="Nguyễn Văn A",
        ma_bac_si="BS001",
        ten_bac_si="Trần Thị B",
        chuyen_khoa="Nội tổng quát"
    )
    
    # Giả lập ngày khám 3 tháng trước
    from datetime import timedelta
    ho_so1.ngay_kham = datetime.now() - timedelta(days=90)
    
    # Cập nhật thông tin khám
    ho_so1.cap_nhat_thong_tin_kham(
        ly_do_kham="Đau đầu, chóng mặt",
        trieu_chung="Đau đầu nhiều, mệt mỏi, ăn uống kém",
        chan_doan="Tăng huyết áp độ 1",
        huyet_ap="145/95 mmHg",
        nhip_tim="88 nhịp/phút",
        nhiet_do="37°C",
        can_nang="72kg",
        chieu_cao="168cm"
    )
    
    # Thêm kết quả xét nghiệm
    xn1 = KetQuaXetNghiem("Xét nghiệm máu", "Hồng cầu", "4.8", "triệu/mm³", "4.5-5.5")
    xn2 = KetQuaXetNghiem("Xét nghiệm máu", "Bạch cầu", "7.2", "nghìn/mm³", "4.0-10.0")
    xn3 = KetQuaXetNghiem("Xét nghiệm máu", "Glucose", "110", "mg/dL", "70-100")
    xn3.cap_nhat_ghi_chu("Glucose hơi cao, cần theo dõi")
    
    ho_so1.them_ket_qua_xet_nghiem(xn1)
    ho_so1.them_ket_qua_xet_nghiem(xn2)
    ho_so1.them_ket_qua_xet_nghiem(xn3)
    
    # Kê đơn thuốc
    thuoc1 = DonThuoc("Amlodipine", "5mg", "Uống 1 viên/ngày vào buổi sáng", 30)
    thuoc2 = DonThuoc("Vitamin B", "100mg", "Uống 1 viên/ngày sau ăn sáng", 30)
    
    ho_so1.them_don_thuoc(thuoc1)
    ho_so1.them_don_thuoc(thuoc2)
    
    # Lời dặn
    ho_so1.cap_nhat_loi_dan(
        "Uống thuốc đều đặn, hạn chế muối, tăng vận động nhẹ nhàng. Theo dõi huyết áp tại nhà.",
        ngay_tai_kham=datetime.now() - timedelta(days=60)
    )
    
    print(ho_so1.in_ho_so())
    print("\n" + "="*70 + "\n")
    
    # 3. Tạo hồ sơ khám lần 2
    print("3. KHÁM BỆNH LẦN 2 (1 tháng trước)")
    ho_so2 = ql_ket_qua.tao_ho_so_kham(
        ma_benh_nhan="BN12345",
        ten_benh_nhan="Nguyễn Văn A",
        ma_bac_si="BS001",
        ten_bac_si="Trần Thị B",
        chuyen_khoa="Nội tổng quát"
    )
    
    ho_so2.ngay_kham = datetime.now() - timedelta(days=30)
    
    ho_so2.cap_nhat_thong_tin_kham(
        ly_do_kham="Tái khám theo lịch hẹn",
        trieu_chung="Tình trạng ổn định hơn, đau đầu giảm",
        chan_doan="Tăng huyết áp độ 1 - đang kiểm soát tốt",
        huyet_ap="130/85 mmHg",
        nhip_tim="76 nhịp/phút",
        nhiet_do="36.8°C",
        can_nang="70kg"
    )
    
    # Kết quả xét nghiệm lần 2
    xn4 = KetQuaXetNghiem("Xét nghiệm máu", "Glucose", "95", "mg/dL", "70-100")
    ho_so2.them_ket_qua_xet_nghiem(xn4)
    
    # Tiếp tục đơn thuốc
    thuoc3 = DonThuoc("Amlodipine", "5mg", "Uống 1 viên/ngày vào buổi sáng", 30)
    ho_so2.them_don_thuoc(thuoc3)
    
    ho_so2.cap_nhat_loi_dan(
        "Tình trạng khá hơn, tiếp tục duy trì thuốc và chế độ ăn uống.",
        ngay_tai_kham=datetime.now() + timedelta(days=60)
    )
    
    print(ho_so2.in_ho_so())
    print("\n" + "="*70 + "\n")
    
    # 4. Xem lịch sử đầy đủ
    print("4. XEM LỊCH SỬ KHÁM BỆNH ĐẦY ĐỦ")
    print(lich_su_bn.xem_lich_su_day_du())
    print()
    
    # 5. Tìm kiếm và thống kê
    print("\n5. TÌM KIẾM VÀ THỐNG KÊ")
    
    # Hồ sơ gần nhất
    ho_so_moi = lich_su_bn.lay_ho_so_gan_nhat()
    print(f"Hồ sơ khám gần nhất: {ho_so_moi.ma_ho_so} - {ho_so_moi.ngay_kham.strftime('%d/%m/%Y')}")
    
    # Thống kê bệnh
    print("\nThống kê các bệnh đã khám:")
    thong_ke = lich_su_bn.thong_ke_benh()
    for benh, so_lan in thong_ke.items():
        print(f"  - {benh}: {so_lan} lần")
    
    # Tìm theo chẩn đoán
    print("\nTìm hồ sơ có chứa 'tăng huyết áp':")
    ket_qua_tim = lich_su_bn.tim_ho_so_theo_chan_doan("tăng huyết áp")
    for hs in ket_qua_tim:
        print(f"  - {hs.ma_ho_so}: {hs.chan_doan}")
    
    print("\n" + "="*70)
