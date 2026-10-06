# 📋 Tài Liệu Tổng Hợp Full API Backend (Cập Nhật 06/10/2026)

Tài liệu chi tiết toàn bộ các API Backend của dự án `order_fast_api` đáp ứng 100% yêu cầu tích hợp từ đội ngũ Frontend.

---

## 🌐 Baseline Info

* **Base URL (Local):** `http://localhost:8080/api/v1`
* **Base URL (Production):** `https://order-fast-api.vercel.app/api/v1`
* **Header:** `Authorization: Bearer <access_token>`
* **Content-Type:** `application/json`

---

## 📋 Response Contract Standard

**Thành công (200 / 201):**
```json
{
  "success": true,
  "message": "Thông báo thành công",
  "data": { ... },
  "meta": {
    "page": 1,
    "limit": 10,
    "total": 100
  }
}
```

**Thất bại (4xx / 5xx):**
```json
{
  "success": false,
  "message": "Mô tả lỗi dễ hiểu"
}
```

---

## 🛠️ Danh Sách Chi Tiết API Mới Đã Bổ Sung

### 1. Phân Hệ Đăng Ký, Đăng Nhập & Quên Mật Khẩu (Auth)

| Method | Endpoint | Mô tả | Authorization |
|---|---|---|---|
| `POST` | `/auth/login` | Đăng nhập hệ thống | Public |
| `POST` | `/auth/register` | Đăng ký tài khoản người dùng mới | Public |
| `POST` | `/auth/refresh-token` | Làm mới Access Token | Public |
| `POST` | `/auth/logout` | Đăng xuất tài khoản | Bearer Token |
| `POST` | `/auth/forgot-password/send-otp` | Bước 1: Gửi mã OTP khôi phục mật khẩu | Public |
| `POST` | `/auth/forgot-password/verify-otp` | Bước 2: Xác thực mã OTP | Public |
| `POST` | `/auth/forgot-password/reset-password` | Bước 3: Đặt lại mật khẩu mới | Public |

#### Mẫu Request Quên Mật Khẩu OTP:

* **Send OTP:** `POST /api/v1/auth/forgot-password/send-otp`
```json
{ "email": "nguyenvana@example.com" }
```

* **Verify OTP:** `POST /api/v1/auth/forgot-password/verify-otp`
```json
{ "email": "nguyenvana@example.com", "otp": "123456" }
```

* **Reset Password:** `POST /api/v1/auth/forgot-password/reset-password`
```json
{
  "email": "nguyenvana@example.com",
  "otp": "123456",
  "newPassword": "NewPassword123!"
}
```

---

### 2. Phân Hệ Cá Nhân & Quản Lý User (User & Admin User Management)

| Method | Endpoint | Mô tả | Authorization |
|---|---|---|---|
| `GET` | `/users/me` | Lấy thông tin tài khoản hiện tại | Bearer Token |
| `PUT` | `/users/me` | Cập nhật thông tin cá nhân (`name`, `email`, `phoneNumber`, `address`) | Bearer Token |
| `GET` | `/users` | Admin xem danh sách tất cả tài khoản (Phân trang, search `name`/`email`/`phone`, filter `roleID`/`status`) | Admin Token |
| `POST` | `/users` | Admin tạo tài khoản mới (Có thể gán roleID & status) | Admin Token |
| `GET` | `/users/{id}` | Admin xem chi tiết 1 tài khoản | Admin Token |
| `PATCH` | `/users/{id}` | Admin cập nhật vai trò `roleID`, trạng thái `status` hoặc thông tin tài khoản | Admin Token |
| `DELETE` | `/users/{id}` | Admin xóa / vô hiệu hóa tài khoản | Admin Token |

#### Mẫu Request Cập Nhật Cá Nhân (`PUT /api/v1/users/me`):
```json
{
  "name": "Nguyen Van A",
  "email": "nguyenvana@example.com",
  "phoneNumber": "0987654321",
  "address": "123 District 1, HCMC"
}
```

---

### 3. Phân Hệ Danh Mục Món Ăn (Category CRUD)

| Method | Endpoint | Mô tả | Authorization |
|---|---|---|---|
| `GET` | `/categories` | Lấy danh sách danh mục (Lọc & Phân trang) | Public |
| `POST` | `/categories` | Tạo danh mục món ăn mới | Admin/Staff Token |
| `PUT` | `/categories/{id}` | Cập nhật tên danh mục | Admin/Staff Token |
| `DELETE` | `/categories/{id}` | Xóa danh mục | Admin/Staff Token |

---

### 4. Phân Hệ Bàn Ăn (Table CRUD)

| Method | Endpoint | Mô tả | Authorization |
|---|---|---|---|
| `GET` | `/tables` | Lấy danh sách bàn ăn (Phân trang, lọc status/capacity) | Public |
| `GET` | `/tables/{id}` | Chi tiết 1 bàn ăn | Public |
| `POST` | `/tables` | Thêm bàn ăn mới (`number`, `minCapacity`, `maxCapacity`, `status`) | Admin/Staff Token |
| `PATCH` | `/tables/{id}/status` | Nhanh chóng đổi trạng thái bàn (`EMPTY`, `OCCUPIED`, `RESERVED`) | Admin/Staff Token |
| `PATCH` | `/tables/{id}` | Cập nhật thông tin sức chứa / số bàn | Admin/Staff Token |
| `DELETE` | `/tables/{id}` | Xóa bàn ăn khỏi hệ thống | Admin/Staff Token |

---

### 5. Phân Hệ Đặt Bàn (Reservation Module)

| Method | Endpoint | Mô tả | Authorization |
|---|---|---|---|
| `POST` | `/reservations` | Đặt bàn vãng lai (Public) | Public |
| `POST` | `/reservations/me` | Đặt bàn cho User đang đăng nhập | Bearer Token |
| `GET` | `/reservations` | Danh sách đặt bàn (Phân trang & Lọc) | Bearer Token |
| `GET` | `/reservations/{id}` | Chi tiết 1 đơn đặt bàn | Bearer Token |
| `PATCH` | `/reservations/{id}` | Xác nhận đơn / Gán bàn (`tableID`) | Admin/Staff Token |
| `POST` | `/reservations/{id}/cancel` | Hủy đơn đặt bàn (Tự động giải phóng bàn về `EMPTY`) | Bearer Token |
| `DELETE` | `/reservations/{id}` | Xóa đơn đặt bàn | Admin Token |

---

### 6. Phân Hệ Đơn Hàng (Order & POS Module)

| Method | Endpoint | Mô tả | Authorization |
|---|---|---|---|
| `POST` | `/orders` | Tạo đơn hàng mới | Bearer Token |
| `GET` | `/orders` | Lấy danh sách đơn hàng (Phân trang & Lọc) | Bearer Token |
| `GET` | `/orders/{id}` | Lấy chi tiết đơn hàng (Phục vụ in hóa đơn K80) | Bearer Token |
| `PATCH` | `/orders/{id}/status` | Cập nhật trạng thái đơn (`PENDING`, `PREPARING`, `COMPLETED`, v.v.) | Staff/Admin Token |
