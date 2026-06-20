# V8 - Fix hiện tượng chớp/chớp ở mép đất - nước

Các thay đổi chính:

- Đổi mặt nước sang vật liệu opaque alpha 1.0 để tránh lỗi alpha sorting trong viewer GLB khi xoay/kéo camera.
- Tách vùng nước và vùng đất/lát thành các vùng hình học riêng, không còn overlap trực tiếp giữa mặt đất và mặt nước.
- Đường nối đất - nước được giấu dưới kè đá, nên nhìn vẫn kín nhưng không bị z-fighting.
- Mặt đáy và viền dày vẫn đồng bộ vật liệu như bản v7: phần bờ là đất/lát, phần kênh là nước.
- Các phần còn lại của mô hình được giữ nguyên.
