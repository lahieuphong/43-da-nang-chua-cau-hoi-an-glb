# FIX v8 - No Flicker / Z-fighting Cleanup

Các chỉnh sửa chính:

- Tách hình học mặt nước và bờ đất/lát để không còn các mặt phẳng đồng phẳng bị chồng lên nhau.
- Đổi vật liệu nước chính sang alpha 1.0 để tránh lỗi alpha sorting trong một số GLB viewer khi xoay/kéo mô hình.
- Mặt nước chuyển thành một quad riêng nằm trong lòng kênh, không còn dùng khối nước dày chồng vào bờ.
- Thành dày trước/sau và mặt đáy được chia thành các dải vật liệu không overlap: đất/lát - kè đá - nước - kè đá - đất/lát.
- Hai dải seam cực nhỏ giữa đất và nước dùng vật liệu kè đá để che kín, không để lộ nền xám và không gây z-fighting.

Các phần còn lại giữ nguyên.
