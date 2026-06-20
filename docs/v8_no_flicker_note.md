# FIX v8 - chống chớp chớp / z-fighting

Các phần đã chỉnh:

- Tách mặt nước và mặt đất thành các vùng hình học riêng, không còn để 2 mặt phẳng trùng nhau ở ranh đất-nước.
- Mặt nước chính chuyển thành quad phẳng riêng, không dùng khối box dày chồng vào bờ.
- Hai bờ lát/đất dừng trước vùng nước; seam được kè đá che nên nhìn vẫn kín nhưng không bị flicker.
- Các mảng vật liệu cho thành dày và mặt đáy được đặt lệch ra ngoài, không còn coplanar với đế xám.
- Các vùng mặt đáy vẫn đồng bộ: bờ là đất/lát, lòng kênh là nước.

Các phần còn lại giữ nguyên.
