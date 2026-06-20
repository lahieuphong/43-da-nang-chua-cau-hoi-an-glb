# Prompt 5 – material, roof, rail, bridge-slope fix

Các chỉnh sửa theo feedback ảnh mới:

1. **Chất liệu đá/mặt tiền**
   - `weathered_stone_*` được viết lại sáng hơn, khô hơn, giống đá vôi/vữa cũ ở mặt tiền.
   - Vật liệu `weathered grey stone piers` và `worn light stone trim` tăng base color để không còn bị xanh xám tối.
   - Thêm overlay gờ đá sáng ở mặt trước và mặt sau.

2. **Hàng rào mặt tiền**
   - Thêm lan-can đá dốc thẳng theo thân cầu.
   - Thêm hàng rào cao, thoáng bằng nhiều song đứng mảnh và thanh ngang gỗ.
   - Chia nhịp bằng cột gỗ, giữ các phần khác của v15.

3. **Mái ngói**
   - Texture `old_roof_tile_*` được viết lại theo pattern ngói âm-dương: nền cam đất nung, sống ngói kem sáng, rãnh tối.
   - Thêm overlay hàng ngói dọc ở mặt trước và một lớp nhẹ phía sau để khi xoay vẫn có chất ngói.
   - Thêm chấm/gờ sứ trắng ở mép mái.

4. **Độ dốc cầu/mái**
   - Tăng nhịp dốc tuyến tính cao ở giữa, thấp về hai đầu để bớt cảm giác tròn/thấp.
   - Giữ nguyên source geometry v15 gốc trong `assets/geometry/`, các chỉnh sửa nằm ở source procedural sau bước load.

Output mới: `chua_cau_hoi_an_textured_fixed_v16_material_roof_rail_slope.glb`.
