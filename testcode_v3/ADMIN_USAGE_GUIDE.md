# HƯỚNG DẪN SỬ DỤNG ADMIN FEATURES - CLINIC MANAGEMENT SYSTEM

## 🔑 ĐĂNG NHẬP
- **Username:** admin
- **Password:** 123456

---

## 📱 QUẢN LÝ BỆNH NHÂN (`manage_patients.py`)

### Tìm kiếm bệnh nhân
- Nhập tên hoặc username vào "Tìm kiếm"
- Kết quả cập nhật theo từng ký tự

### Xem chi tiết
1. Chọn một bệnh nhân từ danh sách
2. Nhấn "Xem chi tiết"
3. Popup hiển thị:
   - Họ tên, CCCD, ngày sinh
   - Giới tính, số điện thoại
   - Địa chỉ, lịch sử bệnh
   - Bảo hiểm

### Cập nhật thông tin
1. Chọn bệnh nhân
2. Nhấn "Cập nhật thông tin"
3. Sửa các trường cần thiết
4. Nhấn "Lưu"

### Tạo bệnh nhân mới
1. Nhấn "Tạo mới"
2. Điền đầy đủ: username, mật khẩu, họ tên
3. (Optional) Thêm số điện thoại, địa chỉ
4. Nhấn "Tạo"

### Xóa bệnh nhân
1. Chọn bệnh nhân
2. Nhấn "Xóa bệnh nhân"
3. Xác nhận: "Bạn chắc chắn muốn xóa...?"
4. Xóa thành công

---

## 👨‍⚕️ QUẢN LÝ BÁC SĨ (`manage_doctors.py`)

### Tìm kiếm bác sĩ
- Nhập tên hoặc username vào "Tìm kiếm"
- Hiển thị: Họ tên, chuyên khoa, chi nhánh

### Xem chi tiết bác sĩ
1. Chọn bác sĩ
2. Nhấn "Xem chi tiết"
3. Popup hiển thị:
   - Chuyên khoa, chi nhánh
   - Kinh nghiệm (năm), đánh giá (sao)
   - Giá khám, số điện thoại
   - Hình ảnh

### Cập nhật bác sĩ
1. Chọn bác sĩ
2. Nhấn "Cập nhật thông tin"
3. Sửa: Họ tên, chuyên khoa, chi nhánh, exp, rating, giá, SĐT, hình ảnh
4. Nhấn "Lưu"

### Tạo bác sĩ mới
1. Nhấn "Tạo mới"
2. Điền: username, mật khẩu, họ tên
3. Thêm: chuyên khoa, chi nhánh, kinh nghiệm, đánh giá, giá, SĐT
4. Nhấn "Tạo"

### Xóa bác sĩ
1. Chọn bác sĩ
2. Nhấn "Xóa bác sĩ"
3. Xác nhận
4. Xóa thành công

---

## 📅 QUẢN LÝ LỊCH HẸN (`manage_appointments.py`)

### Lọc theo trạng thái
- Dropdown: Tất cả / Đã đặt / Checked-in / Hoàn thành / Đã hủy
- Danh sách tự cập nhật khi chọn

### Xem chi tiết lịch hẹn
1. Chọn lịch hẹn
2. Nhấn "Xem chi tiết"
3. Popup hiển thị:
   - ID, bệnh nhân, ngày, giờ
   - Lý do/ghi chú, trạng thái

### Thay đổi trạng thái
1. Chọn lịch hẹn
2. Nhấn "Thay đổi trạng thái"
3. Chọn trạng thái mới từ dropdown
4. Nhấn "Lưu"

**Các trạng thái:**
- **Đã đặt** - Vừa tạo, chưa đến
- **Checked-in** - Bệnh nhân đã đến
- **Hoàn thành** - Đã khám xong
- **Đã hủy** - Hủy cuộc hẹn

### Xóa lịch hẹn
1. Chọn lịch hẹn
2. Nhấn "Xóa"
3. Xác nhận
4. Xóa thành công

---

## 💊 QUẢN LÝ KHO THUỐC (`manage_medicines.py`)

### Nhập thuốc vào kho
1. Điền: Tên thuốc, số lượng, đơn vị
2. Nhấn "Nhập kho"
3. Cập nhật thành công (hoặc thêm nếu chưa có)

### Tìm kiếm thuốc
- Nhập tên vào "Tìm kiếm"
- Danh sách lọc theo từng ký tự

### Xuất thuốc (trừ kho)
1. Chọn thuốc
2. Nhấn "Xuất thuốc"
3. Nhập số lượng cần xuất
4. Hệ thống kiểm tra đủ hàng
5. Nhấn "Xuất"

### Chỉnh sửa thuốc
1. Chọn thuốc
2. Nhấn "Chỉnh sửa"
3. Sửa: Số lượng, đơn vị
4. Nhấn "Lưu"

### Xóa loại thuốc
1. Chọn thuốc
2. Nhấn "Xóa"
3. Xác nhận
4. Xóa thành công

---

## 👤 QUẢN LÝ TÀI KHOẢN (`manage_users.py`)

### Tìm kiếm tài khoản
- Nhập username hoặc họ tên
- Hiển thị: Username, Họ tên, Vai trò

### Xem chi tiết tài khoản
1. Chọn tài khoản
2. Nhấn "Xem chi tiết"
3. Hiển thị role và thông tin bổ sung

### Đổi mật khẩu
1. Chọn tài khoản
2. Nhấn "Đổi mật khẩu"
3. Nhập mật khẩu mới 2 lần
4. Nhấn "Lưu"
- ⚠️ Admin không thể đổi mật khẩu của chính mình từ đây

### Tạo tài khoản mới
1. Nhấn "Tạo tài khoản"
2. Chọn vai trò: Patient / Doctor / Receptionist / Admin
3. Điền: Username, Mật khẩu, Họ tên
4. (Optional) Chi nhánh/chuyên khoa
5. Nhấn "Tạo"

### Xóa tài khoản
1. Chọn tài khoản (không thể xóa admin)
2. Nhấn "Xóa tài khoản"
3. Xác nhận
4. Xóa thành công

---

## 📊 BÁO CÁO THỐNG KÊ (`reports.py`)

### Bảng điều khiển chính (Dashboard)
Hiển thị 8 KPI:
- **👥 Tổng bệnh nhân** - Số bệnh nhân đã đăng ký
- **👨‍⚕️ Tổng bác sĩ** - Số bác sĩ trong hệ thống
- **📅 Tổng lịch hẹn** - Tất cả lịch hẹn
- **✅ Lịch hẹn hoàn thành** - Lịch hẹn đã khám xong
- **💊 Loại thuốc** - Số loại thuốc trong kho
- **💰 Hóa đơn chưa thanh toán** - Số hóa đơn chưa paid
- **💵 Tổng doanh thu** - Tổng tiền đã thanh toán
- **📊 Tỷ lệ hoàn thành** - % lịch hẹn hoàn thành / tổng

### Lọc theo ngày
1. Nhập "Từ ngày" (YYYY-MM-DD)
2. Nhập "Đến ngày" (YYYY-MM-DD)
3. Nhấn "Tìm"

### Xem lịch hẹn theo ngày
- Bảng hiển thị:
  - Ngày
  - Tổng lịch hẹn hôm đó
  - Số lịch hẹn hoàn thành
- Sắp xếp theo ngày mới nhất trước

### Xem doanh thu theo ngày
- Bảng hiển thị:
  - Ngày
  - Tổng hóa đơn (đ)
  - Đã thanh toán (đ)
- Định dạng tiền tệ: 1,234,567 đ
- Sắp xếp theo ngày mới nhất trước

---

## 🎨 TIPS & TRICKS

### Cách sử dụng nhanh
- Các bảng có **scrollbar** → Cuộn để xem thêm
- **Search real-time** → Không cần nhấn nút "Tìm"
- **Double-click** → Không cần (dùng nút bấm)
- **Escape** → Đóng cửa sổ popup

### Lỗi thường gặp
| Lỗi | Giải pháp |
|-----|----------|
| "Vui lòng chọn một..." | Chọn hàng trong bảng trước |
| "Tên đăng nhập đã tồn tại" | Dùng username khác khi tạo mới |
| "Mật khẩu không khớp" | Điền lại 2 lần mật khẩu giống nhau |
| "Không đủ số lượng" | Số lượng xuất > tồn kho |
| "Định dạng ngày không hợp lệ" | Dùng định dạng YYYY-MM-DD |

---

## 🔒 CẤU TRÚC DỮ LIỆU

### Bảng Users (clinic.db)
| Trường | Kiểu | Mô tả |
|-------|-----|------|
| username | TEXT (PK) | Tên đăng nhập |
| password | TEXT | Hash mật khẩu |
| role | TEXT | patient/doctor/admin/receptionist |
| name | TEXT | Họ tên |
| info | JSON | Thông tin bổ sung (JSON) |

### Bảng Appointments (clinic.db)
| Trường | Kiểu | Mô tả |
|-------|-----|------|
| id | INT (PK) | ID lịch hẹn |
| patient_username | TEXT (FK) | Username bệnh nhân |
| date | TEXT | Ngày (YYYY-MM-DD) |
| time | TEXT | Giờ (HH:MM) |
| reason | TEXT | Lý do/ghi chú |
| status | TEXT | Đã đặt/Checked-in/Hoàn thành/Đã hủy |

### Bảng Medicines (clinic.db)
| Trường | Kiểu | Mô tả |
|-------|-----|------|
| name | TEXT (PK) | Tên thuốc |
| quantity | INT | Số lượng tồn |
| unit | TEXT | Đơn vị (Viên/Chai/Lọ/Gói/Tuýp) |

---

## 📞 LIÊN HỆ & HỖ TRỢ
- Kiểm tra file ADMIN_UPDATES_SUMMARY.md để biết chi tiết nâng cấp
- Tất cả chức năng đã được test lỗi cú pháp ✅
- Không sửa đổi schema database, chỉ CRUD data

---

**Cập nhật lần cuối: 27/11/2025**
