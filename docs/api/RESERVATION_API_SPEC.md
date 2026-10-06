# 📋 Tài Liệu API Module Đặt Bàn (Reservation API Documentation for Frontend)

Tài liệu hướng dẫn kết nối API cho Module **Đặt Bàn (Reservation)** thuộc dự án `order_fast_api`.

---

## 🌐 Thông Tin Chung (General Info)

* **Base URL (Local)**: `http://localhost:8080/api/v1/reservations`
* **Base URL (Production)**: `https://order-fast-api.vercel.app/api/v1/reservations`
* **Authentication**: Phôi Token trong Header: `Authorization: Bearer <access_token>`
* **Content-Type**: `application/json`

---

## 📑 Các Trạng Thái Đặt Bàn (Reservation Status Enum)

| Status | Ý nghĩa |
|---|---|
| `PENDING` | Đang chờ nhà hàng xác nhận (Trạng thái mặc định khi mới tạo) |
| `CONFIRMED` | Đã xác nhận giữ chỗ (Có thể kèm gán `tableID`) |
| `COMPLETED` | Khách đã đến ăn & hoàn tất |
| `CANCELLED` | Đã hủy đặt bàn |

---

## 🚀 Danh Sách Endpoints (API Specification)

### 1. Tạo lượt đặt bàn (Public - Không cần đăng nhập)
Cho phép khách vãng lai đặt bàn trực tuyến.

* **Endpoint**: `POST /api/v1/reservations`
* **Auth Required**: ❌ No
* **Request Body**:
```json
{
  "fullName": "Nguyen Van A",
  "email": "nguyenvana@example.com",
  "phoneNumber": "0987654321",
  "numberOfGuests": 4,
  "reservationTime": "2026-10-10T19:00:00Z",
  "specialRequests": "Cho bàn gần cửa sổ, ghế trẻ em"
}
```
* **Response (201 Created)**:
```json
{
  "success": true,
  "message": "Reservation created successfully.",
  "data": {
    "id": 1,
    "fullName": "Nguyen Van A",
    "email": "nguyenvana@example.com",
    "phoneNumber": "0987654321",
    "numberOfGuests": 4,
    "reservationTime": "2026-10-10T19:00:00Z",
    "specialRequests": "Cho bàn gần cửa sổ, ghế trẻ em",
    "status": "PENDING",
    "userID": null,
    "tableID": null,
    "createdAt": "2026-10-06T08:00:00Z",
    "updatedAt": "2026-10-06T08:00:00Z"
  }
}
```

---

### 2. Tạo lượt đặt bàn cho User đã đăng nhập
Tự động gắn `userID` của tài khoản đang đăng nhập.

* **Endpoint**: `POST /api/v1/reservations/me`
* **Auth Required**: ✅ Yes (`Bearer token`)
* **Request Body**: *(Tương tự public endpoint, không cần truyền userID)*
```json
{
  "fullName": "Nguyen Van A",
  "email": "nguyenvana@example.com",
  "phoneNumber": "0987654321",
  "numberOfGuests": 2,
  "reservationTime": "2026-10-12T18:30:00Z",
  "specialRequests": "Kỷ niệm ngày cưới"
}
```
* **Response (201 Created)**:
```json
{
  "success": true,
  "message": "Reservation created successfully.",
  "data": {
    "id": 2,
    "fullName": "Nguyen Van A",
    "email": "nguyenvana@example.com",
    "phoneNumber": "0987654321",
    "numberOfGuests": 2,
    "reservationTime": "2026-10-12T18:30:00Z",
    "specialRequests": "Kỷ niệm ngày cưới",
    "status": "PENDING",
    "userID": 10,
    "tableID": null,
    "createdAt": "2026-10-06T08:05:00Z",
    "updatedAt": "2026-10-06T08:05:00Z"
  }
}
```

---

### 3. Lấy danh sách lượt đặt bàn (Phân trang & Lọc)
* Khách hàng: Chỉ xem được các đơn của chính họ.
* Admin / Staff: Xem được toàn bộ danh sách đơn đặt bàn.

* **Endpoint**: `GET /api/v1/reservations`
* **Auth Required**: ✅ Yes (`Bearer token`)
* **Query Parameters**:
  * `page` (int, default: 1): Số trang.
  * `limit` (int, default: 10, max: 100): Số bản ghi/trang.
  * `status` (string, optional): `PENDING` \| `CONFIRMED` \| `COMPLETED` \| `CANCELLED`
  * `email` (string, optional): Tìm kiếm theo email.
  * `phoneNumber` (string, optional): Tìm kiếm theo SĐT.
  * `startDate` (datetime, optional): `2026-10-01T00:00:00Z`
  * `endDate` (datetime, optional): `2026-10-31T23:59:59Z`

* **Response (200 OK)**:
```json
{
  "success": true,
  "message": "Get reservation list successfully.",
  "data": [
    {
      "id": 1,
      "fullName": "Nguyen Van A",
      "email": "nguyenvana@example.com",
      "phoneNumber": "0987654321",
      "numberOfGuests": 4,
      "reservationTime": "2026-10-10T19:00:00Z",
      "specialRequests": "Cho bàn gần cửa sổ, ghế trẻ em",
      "status": "PENDING",
      "userID": null,
      "tableID": null,
      "createdAt": "2026-10-06T08:00:00Z",
      "updatedAt": "2026-10-06T08:00:00Z"
    }
  ],
  "meta": {
    "page": 1,
    "limit": 10,
    "total": 1
  }
}
```

---

### 4. Xem chi tiết 1 lượt đặt bàn
* **Endpoint**: `GET /api/v1/reservations/{id}`
* **Auth Required**: ✅ Yes (`Bearer token`)
* **Response (200 OK)**:
```json
{
  "success": true,
  "message": "Get reservation details successfully.",
  "data": {
    "id": 1,
    "fullName": "Nguyen Van A",
    "email": "nguyenvana@example.com",
    "phoneNumber": "0987654321",
    "numberOfGuests": 4,
    "reservationTime": "2026-10-10T19:00:00Z",
    "specialRequests": "Cho bàn gần cửa sổ, ghế trẻ em",
    "status": "CONFIRMED",
    "userID": null,
    "tableID": 5,
    "createdAt": "2026-10-06T08:00:00Z",
    "updatedAt": "2026-10-06T08:10:00Z"
  }
}
```

---

### 5. Cập nhật thông tin / Xác nhận / Gán bàn
Cho phép cập nhật thông tin đơn, thay đổi trạng thái hoặc gán bàn ăn (`tableID`).
*(Lưu ý: Khi đổi trạng thái thành `CONFIRMED` và gán `tableID`, trạng thái của bàn đó sẽ tự động chuyển thành `RESERVED`)*.

* **Endpoint**: `PATCH /api/v1/reservations/{id}`
* **Auth Required**: ✅ Yes (`Bearer token`)
* **Request Body** *(Tùy chọn truyền các trường cần cập nhật)*:
```json
{
  "status": "CONFIRMED",
  "tableID": 5
}
```
* **Response (200 OK)**:
```json
{
  "success": true,
  "message": "Update reservation successfully.",
  "data": {
    "id": 1,
    "fullName": "Nguyen Van A",
    "email": "nguyenvana@example.com",
    "phoneNumber": "0987654321",
    "numberOfGuests": 4,
    "reservationTime": "2026-10-10T19:00:00Z",
    "specialRequests": "Cho bàn gần cửa sổ, ghế trẻ em",
    "status": "CONFIRMED",
    "userID": null,
    "tableID": 5,
    "createdAt": "2026-10-06T08:00:00Z",
    "updatedAt": "2026-10-06T08:10:00Z"
  }
}
```

---

### 6. Hủy lượt đặt bàn (Cancel Reservation)
Hủy lịch đặt bàn. *(Nếu đơn đã được gán bàn ăn trước đó, bàn ăn đó sẽ tự động chuyển trạng thái về `EMPTY`)*.

* **Endpoint**: `POST /api/v1/reservations/{id}/cancel`
* **Auth Required**: ✅ Yes (`Bearer token`)
* **Response (200 OK)**:
```json
{
  "success": true,
  "message": "Reservation cancelled successfully.",
  "data": {
    "id": 1,
    "fullName": "Nguyen Van A",
    "email": "nguyenvana@example.com",
    "phoneNumber": "0987654321",
    "numberOfGuests": 4,
    "reservationTime": "2026-10-10T19:00:00Z",
    "specialRequests": "Cho bàn gần cửa sổ, ghế trẻ em",
    "status": "CANCELLED",
    "userID": null,
    "tableID": 5,
    "createdAt": "2026-10-06T08:00:00Z",
    "updatedAt": "2026-10-06T08:15:00Z"
  }
}
```

---

### 7. Xóa lượt đặt bàn (Delete Reservation - Admin only)
Xóa hoàn toàn lượt đặt bàn khỏi cơ sở dữ liệu.

* **Endpoint**: `DELETE /api/v1/reservations/{id}`
* **Auth Required**: ✅ Yes (`Admin / Staff Token`)
* **Response (200 OK)**:
```json
{
  "success": true,
  "message": "Reservation deleted successfully.",
  "data": {
    "id": 1,
    "fullName": "Nguyen Van A",
    "email": "nguyenvana@example.com",
    "phoneNumber": "0987654321",
    "numberOfGuests": 4,
    "reservationTime": "2026-10-10T19:00:00Z",
    "specialRequests": "Cho bàn gần cửa sổ, ghế trẻ em",
    "status": "CANCELLED",
    "userID": null,
    "tableID": 5,
    "createdAt": "2026-10-06T08:00:00Z",
    "updatedAt": "2026-10-06T08:15:00Z"
  }
}
```
