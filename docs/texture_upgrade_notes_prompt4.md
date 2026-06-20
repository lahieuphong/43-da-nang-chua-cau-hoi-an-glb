# Ghi chú nâng cấp texture - Prompt 4

## Texture cần thiết và lý do

1. **Gỗ cũ**: dùng cho thân cầu, sàn, lan can, cột, khung. Vân gỗ và normal map giúp bề mặt bớt phẳng, gần cảm giác gỗ cổ.
2. **Đá xám phong hóa**: dùng cho trụ, vòm, bờ kè, đế sa bàn. Noise và vệt nứt nhẹ giúp đá có tuổi đời.
3. **Mái ngói âm dương cũ**: dùng cho mái cong và từng hàng ngói. Texture nâu đỏ không đều giúp mái giống ngói đất nung đã cũ.
4. **Sơn son đỏ cũ**: dùng cho cổng, mảng tường/cửa, bảng tên. Màu loang nhẹ tránh cảm giác công trình quá mới.
5. **Gốm men lam xanh-trắng**: dùng cho đĩa trang trí trên mái, giúp gợi đúng chi tiết nhận diện Chùa Cầu.
6. **Rêu mềm**: dùng cho mép đá, chân tường/kè nước. Rêu tăng cảm giác ẩm và cổ kính nhưng được tiết chế để không làm sai hiện trạng sau trùng tu.
7. **Nước kênh xanh rêu**: dùng cho lạch nước dưới cầu, bổ sung normal map sóng nhẹ.
8. **Tường vàng Hội An**: dùng cho nhà cổ bối cảnh, giúp người xem nhận ra không gian phố cổ.
9. **Nền lát gạch/đá**: dùng cho lối đi hai đầu cầu và nền cảnh quan.
10. **Lá cây**: dùng cho cây xanh bối cảnh.

## UV mapping

Scene writer xuất `TEXCOORD_0`; các primitive/hình khối trong scene có UV mặc định hoặc UV thủ công ở phần mái để texture lặp. Các hàng ngói và bề mặt mái được chia module để normal/basecolor hiển thị rõ hơn.

## Bản quyền

Tất cả texture trong project được tạo procedural bằng Pillow, không sao chép từ ảnh báo/web.
