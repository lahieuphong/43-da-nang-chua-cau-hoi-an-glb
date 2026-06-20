# Implementation notes - Chùa Cầu Hội An GLB

## Phần chính trong scene

1. `create_chua_cau_hoi_an()` là hàm scene factory chính.
2. `_add_scene_base()` dựng đế sa bàn, kênh nước xanh rêu, bờ kè và lối lát đá.
3. `_add_bridge_foundation()` dựng móng/trụ đá và 5 nhịp/vòm dưới cầu.
4. `_add_bridge_deck_body_and_railings()` dựng thân cầu gỗ, sàn, vách nửa kín và song lan can.
5. `_add_end_gates_and_signage()` dựng cổng đỏ, biển `LAI VIỄN KIỀU` và mắt cửa.
6. `_add_columns_and_frame()` dựng cột, dầm, kèo gỗ theo nhịp.
7. `_add_shrine_wing()` dựng khối miếu phụ nhô ra một bên để gợi mặt bằng chữ T/Đinh.
8. `_add_main_roof()` dựng mái chính cong nhẹ, mái ngói âm dương và hồi tam giác.
9. `_add_ceramics_dragons_and_roof_details()` dựng gốm men lam, đĩa trang trí, lưỡng long tranh châu cách điệu.
10. `_add_guardian_animals()` dựng tượng chó/khỉ low-poly.
11. `_add_hoi_an_context()` dựng nhà vàng Hội An, đèn lồng, cây xanh và nền phố cổ.

## Ưu tiên nhận diện

Silhouette mái cong + cầu có trụ/vòm đá + lan can gỗ + cổng đỏ + biển Lai Viễn Kiều + đĩa gốm men lam là bộ nhận diện quan trọng nhất. Các chi tiết môi trường chỉ dùng để hỗ trợ, không để lấn át công trình chính.

## Tỷ lệ

Model không dùng đơn vị mét tuyệt đối. Tỷ lệ quy đổi khoảng 1 đơn vị = 1.7m, giữ cảm giác cầu chính dài khoảng 18-20m, hẹp khoảng 3m, cao khoảng 5-6m trong thực tế. Các tỷ lệ này được chọn để mô hình đẹp trong trình xem GLB, không phải hồ sơ đo vẽ bảo tồn.

## Water-channel focus fix

- Updated `_add_scene_base()` so the canal runs through the center of the model along the front-back axis, matching the reference photo: water in the middle, land/paving only on the two side banks.
- Split the foreground paving slab into left and right sections so it no longer covers the central water channel.
- Added low stone canal edges and moss strips along the waterline.
- Kept roof, bridge body, signage, animals, materials and other geometry unchanged except for making the central lower arch openings read as water/dark canal rather than solid land.

## Water fix 2 - đủ 5 ô vòm và tiền cảnh là nước

Cập nhật theo phản hồi: mặt nước kênh đã được mở rộng theo trục X để xuất hiện dưới toàn bộ 5 ô/vòm đá của Chùa Cầu, bao gồm cả 2 ô ngoài cùng. Phần nước cũng được kéo ra sát mép tiền cảnh phía trước cầu; nền lát chỉ còn ở hai bên ngoài kênh. Các khối mái, thân cầu, bảng chữ, lan can, cổng đỏ và texture chính được giữ nguyên.
## Water/sign fix 3 - mở rộng mặt nước và sửa biển chữ

- Thêm một lớp mặt nước nông phủ gần hết mặt sa bàn, đặt thấp hơn nền lát để nước tràn ra ở các góc nhìn nhưng không che lối gạch, cây, nhà cổ và các chi tiết hiện có.
- Giữ lớp nước chính trong lòng kênh để 5 ô/vòm dưới cầu vẫn đọc rõ là nước.
- Biển chính được đổi từ `LAI VIEN KIEU` sang `LAI VIỄN KIỀU` bằng chữ khối UTF-8 có dấu; thêm hỗ trợ dấu mũ, dấu ngã và dấu huyền cho glyph tiếng Việt.
- Thêm lớp chữ phụ đảo chiều ở mặt sau biển để khi xoay model không còn thấy chữ bị ngược.

