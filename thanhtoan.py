from datetime import datetime
from typing import List


class ChiTietThanhToan:
    """Chi tiết từng khoản phí trong hóa đơn"""
    
    def __init__(self, loai_chi_phi: str, mo_ta: str, 
                 so_luong: int, don_gia: float):
        self.loai_chi_phi = loai_chi_phi  # "Khám bệnh", "Xét nghiệm", "Thuốc", "Dịch vụ khác"
        self.mo_ta = mo_ta
        self.so_luong = so_luong
        self.don_gia = don_gia
        self.thanh_tien = self.tinh_thanh_tien()
    
    def tinh_thanh_tien(self) -> float:
        """Tính thành tiền cho chi tiết này"""
        return self.so_luong * self.don_gia
    
    def cap_nhat_so_luong(self, so_luong_moi: int):
        """Cập nhật số lượng và tính lại thành tiền"""
        if so_luong_moi <= 0:
            raise ValueError("Số lượng phải lớn hơn 0")
        self.so_luong = so_luong_moi
        self.thanh_tien = self.tinh_thanh_tien()
    
    def __str__(self) -> str:
        return (f"{self.loai_chi_phi}: {self.mo_ta} - "
                f"SL: {self.so_luong} x {self.don_gia:,.0f} = "
                f"{self.thanh_tien:,.0f} VNĐ")


class HoaDon:
    """Hóa đơn thanh toán"""
    
    _ma_hoa_don_counter = 1000
    
    def __init__(self, ma_ho_so: str, ma_benh_nhan: str, 
                 ten_benh_nhan: str):
        self.ma_hoa_don = self._tao_ma_hoa_don()
        self.ma_ho_so = ma_ho_so
        self.ma_benh_nhan = ma_benh_nhan
        self.ten_benh_nhan = ten_benh_nhan
        self.ngay_tao = datetime.now()
        self.danh_sach_chi_tiet: List[ChiTietThanhToan] = []
        self.ghi_chu = ""
    
    @classmethod
    def _tao_ma_hoa_don(cls) -> str:
        """Tạo mã hóa đơn tự động"""
        ma = f"HD{cls._ma_hoa_don_counter:06d}"
        cls._ma_hoa_don_counter += 1
        return ma
    
    def them_chi_tiet(self, chi_tiet: ChiTietThanhToan):
        """Thêm chi tiết vào hóa đơn"""
        self.danh_sach_chi_tiet.append(chi_tiet)
    
    def xoa_chi_tiet(self, index: int):
        """Xóa chi tiết khỏi hóa đơn"""
        if 0 <= index < len(self.danh_sach_chi_tiet):
            self.danh_sach_chi_tiet.pop(index)
        else:
            raise IndexError("Index chi tiết không hợp lệ")
    
    def tinh_tong_tien(self) -> float:
        """Tính tổng tiền của hóa đơn"""
        return sum(ct.thanh_tien for ct in self.danh_sach_chi_tiet)
    
    def cap_nhat_ghi_chu(self, ghi_chu: str):
        """Cập nhật ghi chú cho hóa đơn"""
        self.ghi_chu = ghi_chu
    
    def in_hoa_don(self) -> str:
        """In hóa đơn ra định dạng text"""
        lines = [
            "=" * 60,
            "HÓA ĐƠN THANH TOÁN".center(60),
            "=" * 60,
            f"Mã hóa đơn: {self.ma_hoa_don}",
            f"Mã hồ sơ: {self.ma_ho_so}",
            f"Bệnh nhân: {self.ten_benh_nhan} (Mã: {self.ma_benh_nhan})",
            f"Ngày tạo: {self.ngay_tao.strftime('%d/%m/%Y %H:%M:%S')}",
            "-" * 60,
            "CHI TIẾT:",
        ]
        
        for i, ct in enumerate(self.danh_sach_chi_tiet, 1):
            lines.append(f"{i}. {ct}")
        
        lines.extend([
            "-" * 60,
            f"TỔNG CỘNG: {self.tinh_tong_tien():,.0f} VNĐ".rjust(60),
        ])
        
        if self.ghi_chu:
            lines.extend([
                "-" * 60,
                f"Ghi chú: {self.ghi_chu}",
            ])
        
        lines.append("=" * 60)
        return "\n".join(lines)


class ThanhToan:
    """Lớp quản lý thanh toán"""
    
    _ma_thanh_toan_counter = 2000
    
    # Các trạng thái thanh toán
    TRANG_THAI_CHO = "Chờ thanh toán"
    TRANG_THAI_DA_THANH_TOAN = "Đã thanh toán"
    TRANG_THAI_DA_HUY = "Đã hủy"
    TRANG_THAI_HOAN_TIEN = "Hoàn tiền"
    
    # Các phương thức thanh toán
    PHUONG_THUC_TIEN_MAT = "Tiền mặt"
    PHUONG_THUC_CHUYEN_KHOAN = "Chuyển khoản"
    PHUONG_THUC_THE_ATM = "Thẻ ATM"
    PHUONG_THUC_THE_TIN_DUNG = "Thẻ tín dụng"
    PHUONG_THUC_VI_DIEN_TU = "Ví điện tử"
    
    def __init__(self, hoa_don: HoaDon):
        self.ma_thanh_toan = self._tao_ma_thanh_toan()
        self.hoa_don = hoa_don
        self.tong_tien = hoa_don.tinh_tong_tien()
        self.tien_benh_nhan_tra = 0.0
        self.tien_thua = 0.0
        self.phuong_thuc_thanh_toan = None
        self.trang_thai = self.TRANG_THAI_CHO
        self.ngay_thanh_toan = None
        self.nguoi_thu_tien = ""
        self.ma_giao_dich = ""
    
    @classmethod
    def _tao_ma_thanh_toan(cls) -> str:
        """Tạo mã thanh toán tự động"""
        ma = f"TT{cls._ma_thanh_toan_counter:06d}"
        cls._ma_thanh_toan_counter += 1
        return ma
    
    def xac_nhan_thanh_toan(self, phuong_thuc: str, tien_tra: float, 
                           nguoi_thu: str, ma_giao_dich: str = "") -> dict:
        """Xác nhận thanh toán"""
        if self.trang_thai == self.TRANG_THAI_DA_THANH_TOAN:
            raise Exception("Hóa đơn đã được thanh toán")
        
        if tien_tra < self.tong_tien:
            raise ValueError(
                f"Số tiền thanh toán không đủ. "
                f"Cần: {self.tong_tien:,.0f} VNĐ, "
                f"Nhận: {tien_tra:,.0f} VNĐ"
            )
        
        self.phuong_thuc_thanh_toan = phuong_thuc
        self.tien_benh_nhan_tra = tien_tra
        self.tien_thua = tien_tra - self.tong_tien
        self.trang_thai = self.TRANG_THAI_DA_THANH_TOAN
        self.ngay_thanh_toan = datetime.now()
        self.nguoi_thu_tien = nguoi_thu
        self.ma_giao_dich = ma_giao_dich
        
        return {
            "thanh_cong": True,
            "ma_thanh_toan": self.ma_thanh_toan,
            "tong_tien": self.tong_tien,
            "tien_nhan": self.tien_benh_nhan_tra,
            "tien_thua": self.tien_thua,
            "phuong_thuc": self.phuong_thuc_thanh_toan,
            "ngay_thanh_toan": self.ngay_thanh_toan
        }
    
    def huy_thanh_toan(self, ly_do: str):
        """Hủy thanh toán"""
        if self.trang_thai == self.TRANG_THAI_DA_THANH_TOAN:
            # Nếu đã thanh toán, chuyển sang trạng thái hoàn tiền
            self.trang_thai = self.TRANG_THAI_HOAN_TIEN
        else:
            self.trang_thai = self.TRANG_THAI_DA_HUY
        
        self.hoa_don.cap_nhat_ghi_chu(
            f"{self.hoa_don.ghi_chu}\nĐã hủy: {ly_do}"
        )
    
    def kiem_tra_trang_thai(self) -> str:
        """Kiểm tra trạng thái thanh toán"""
        return self.trang_thai
    
    def xuat_bien_lai(self) -> str:
        """Xuất biên lai thanh toán"""
        if self.trang_thai != self.TRANG_THAI_DA_THANH_TOAN:
            raise Exception("Chưa thể xuất biên lai - chưa thanh toán")
        
        lines = [
            "=" * 60,
            "BIÊN LAI THANH TOÁN".center(60),
            "=" * 60,
            f"Mã thanh toán: {self.ma_thanh_toan}",
            f"Mã hóa đơn: {self.hoa_don.ma_hoa_don}",
            f"Bệnh nhân: {self.hoa_don.ten_benh_nhan}",
            f"Ngày thanh toán: {self.ngay_thanh_toan.strftime('%d/%m/%Y %H:%M:%S')}",
            "-" * 60,
            f"Tổng tiền: {self.tong_tien:,.0f} VNĐ",
            f"Tiền nhận: {self.tien_benh_nhan_tra:,.0f} VNĐ",
            f"Tiền thừa: {self.tien_thua:,.0f} VNĐ",
            f"Phương thức: {self.phuong_thuc_thanh_toan}",
        ]
        
        if self.ma_giao_dich:
            lines.append(f"Mã giao dịch: {self.ma_giao_dich}")
        
        lines.extend([
            f"Người thu tiền: {self.nguoi_thu_tien}",
            "=" * 60,
            "Cảm ơn quý khách!".center(60),
            "=" * 60,
        ])
        
        return "\n".join(lines)
    
    def __str__(self) -> str:
        return (f"Thanh toán {self.ma_thanh_toan} - "
                f"Hóa đơn {self.hoa_don.ma_hoa_don} - "
                f"Tổng: {self.tong_tien:,.0f} VNĐ - "
                f"Trạng thái: {self.trang_thai}")


class QuanLyThanhToan:
    """Quản lý toàn bộ thanh toán trong hệ thống"""
    
    def __init__(self):
        self.danh_sach_thanh_toan: List[ThanhToan] = []
    
    def tao_hoa_don(self, ma_ho_so: str, ma_benh_nhan: str,
                    ten_benh_nhan: str) -> HoaDon:
        """Tạo hóa đơn mới"""
        return HoaDon(ma_ho_so, ma_benh_nhan, ten_benh_nhan)
    
    def tao_thanh_toan(self, hoa_don: HoaDon) -> ThanhToan:
        """Tạo thanh toán từ hóa đơn"""
        thanh_toan = ThanhToan(hoa_don)
        self.danh_sach_thanh_toan.append(thanh_toan)
        return thanh_toan
    
    def tim_thanh_toan_theo_ma(self, ma_thanh_toan: str):
        """Tìm thanh toán theo mã"""
        for tt in self.danh_sach_thanh_toan:
            if tt.ma_thanh_toan == ma_thanh_toan:
                return tt
        return None
    
    def lay_danh_sach_theo_trang_thai(self, trang_thai: str) -> List[ThanhToan]:
        """Lấy danh sách thanh toán theo trạng thái"""
        return [tt for tt in self.danh_sach_thanh_toan 
                if tt.trang_thai == trang_thai]
    
    def thong_ke_doanh_thu(self, tu_ngay: datetime, den_ngay: datetime) -> dict:
        """Thống kê doanh thu theo khoảng thời gian"""
        doanh_thu_theo_phuong_thuc = {
            ThanhToan.PHUONG_THUC_TIEN_MAT: 0.0,
            ThanhToan.PHUONG_THUC_CHUYEN_KHOAN: 0.0,
            ThanhToan.PHUONG_THUC_THE_ATM: 0.0,
            ThanhToan.PHUONG_THUC_THE_TIN_DUNG: 0.0,
            ThanhToan.PHUONG_THUC_VI_DIEN_TU: 0.0
        }
        tong_doanh_thu = 0.0
        so_giao_dich = 0
        
        for tt in self.danh_sach_thanh_toan:
            if (tt.trang_thai == ThanhToan.TRANG_THAI_DA_THANH_TOAN and
                tt.ngay_thanh_toan and
                tu_ngay <= tt.ngay_thanh_toan <= den_ngay):
                
                tong_doanh_thu += tt.tong_tien
                so_giao_dich += 1
                if tt.phuong_thuc_thanh_toan in doanh_thu_theo_phuong_thuc:
                    doanh_thu_theo_phuong_thuc[tt.phuong_thuc_thanh_toan] += tt.tong_tien
        
        return {
            "tu_ngay": tu_ngay,
            "den_ngay": den_ngay,
            "tong_doanh_thu": tong_doanh_thu,
            "so_giao_dich": so_giao_dich,
            "doanh_thu_theo_phuong_thuc": doanh_thu_theo_phuong_thuc
        }


# ===== DEMO SỬ DỤNG =====
if __name__ == "__main__":
    print("=== HỆ THỐNG THANH TOÁN PHÒNG KHÁM ===\n")
    
    # Khởi tạo hệ thống quản lý
    ql_thanh_toan = QuanLyThanhToan()
    
    # 1. Tạo hóa đơn
    print("1. TẠO HÓA ĐƠN")
    hoa_don = ql_thanh_toan.tao_hoa_don(
        ma_ho_so="HS001",
        ma_benh_nhan="BN12345",
        ten_benh_nhan="Nguyễn Văn A"
    )
    
    # Thêm chi tiết vào hóa đơn
    hoa_don.them_chi_tiet(ChiTietThanhToan(
        "Khám bệnh",
        "Khám nội tổng quát",
        1,
        200000
    ))
    
    hoa_don.them_chi_tiet(ChiTietThanhToan(
        "Xét nghiệm",
        "Xét nghiệm máu tổng quát",
        1,
        150000
    ))
    
    hoa_don.them_chi_tiet(ChiTietThanhToan(
        "Thuốc",
        "Paracetamol 500mg",
        20,
        1000
    ))
    
    hoa_don.them_chi_tiet(ChiTietThanhToan(
        "Thuốc",
        "Amoxicillin 500mg",
        10,
        3000
    ))
    
    print(hoa_don.in_hoa_don())
    print()
    
    # 2. Tạo thanh toán
    print("\n2. TẠO THANH TOÁN")
    thanh_toan = ql_thanh_toan.tao_thanh_toan(hoa_don)
    print(f"Đã tạo: {thanh_toan}")
    print()
    
    # 3. Xác nhận thanh toán
    print("\n3. XÁC NHẬN THANH TOÁN")
    try:
        ket_qua = thanh_toan.xac_nhan_thanh_toan(
            phuong_thuc=ThanhToan.PHUONG_THUC_TIEN_MAT,
            tien_tra=500000,
            nguoi_thu="Lê Thị B - Lễ tân",
            ma_giao_dich=""
        )
        print("Thanh toán thành công!")
        print(f"- Tổng tiền: {ket_qua['tong_tien']:,.0f} VNĐ")
        print(f"- Tiền nhận: {ket_qua['tien_nhan']:,.0f} VNĐ")
        print(f"- Tiền thừa: {ket_qua['tien_thua']:,.0f} VNĐ")
    except Exception as e:
        print(f"Lỗi: {e}")
    print()
    
    # 4. In biên lai
    print("\n4. BIÊN LAI THANH TOÁN")
    print(thanh_toan.xuat_bien_lai())
    print()
    
    # 5. Tạo thêm các giao dịch khác
    print("\n5. TẠO THÊM CÁC GIAO DỊCH")
    
    # Giao dịch 2
    hoa_don2 = ql_thanh_toan.tao_hoa_don("HS002", "BN12346", "Trần Thị C")
    hoa_don2.them_chi_tiet(ChiTietThanhToan(
        "Khám bệnh", "Khám tai mũi họng", 1, 150000
    ))
    thanh_toan2 = ql_thanh_toan.tao_thanh_toan(hoa_don2)
    thanh_toan2.xac_nhan_thanh_toan(
        ThanhToan.PHUONG_THUC_CHUYEN_KHOAN,
        150000,
        "Lê Thị B - Lễ tân",
        "CK20241113001"
    )
    
    # Giao dịch 3
    hoa_don3 = ql_thanh_toan.tao_hoa_don("HS003", "BN12347", "Phạm Văn D")
    hoa_don3.them_chi_tiet(ChiTietThanhToan(
        "Xét nghiệm", "Siêu âm bụng", 1, 300000
    ))
    thanh_toan3 = ql_thanh_toan.tao_thanh_toan(hoa_don3)
    thanh_toan3.xac_nhan_thanh_toan(
        ThanhToan.PHUONG_THUC_THE_ATM,
        300000,
        "Lê Thị B - Lễ tân",
        "ATM20241113001"
    )
    
    print(f"Đã tạo thêm 2 giao dịch")
    print()
    
    # 6. Thống kê doanh thu
    print("\n6. THỐNG KÊ DOANH THU")
    tu_ngay = datetime(2024, 11, 1)
    den_ngay = datetime(2024, 11, 30)
    thong_ke = ql_thanh_toan.thong_ke_doanh_thu(tu_ngay, den_ngay)
    
    print(f"Từ ngày: {thong_ke['tu_ngay'].strftime('%d/%m/%Y')}")
    print(f"Đến ngày: {thong_ke['den_ngay'].strftime('%d/%m/%Y')}")
    print(f"Tổng doanh thu: {thong_ke['tong_doanh_thu']:,.0f} VNĐ")
    print(f"Số giao dịch: {thong_ke['so_giao_dich']}")
    print("\nDoanh thu theo phương thức:")
    for pt, so_tien in thong_ke['doanh_thu_theo_phuong_thuc'].items():
        if so_tien > 0:
            print(f"  - {pt}: {so_tien:,.0f} VNĐ")
    
    # 7. Danh sách thanh toán theo trạng thái
    print("\n7. DANH SÁCH THANH TOÁN ĐÃ HOÀN THÀNH")
    ds_da_thanh_toan = ql_thanh_toan.lay_danh_sach_theo_trang_thai(
        ThanhToan.TRANG_THAI_DA_THANH_TOAN
    )
    for tt in ds_da_thanh_toan:
        print(f"  - {tt}")
