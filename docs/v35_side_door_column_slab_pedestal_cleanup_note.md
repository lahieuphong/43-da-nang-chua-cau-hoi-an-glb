# V35 – side-door column/slab/pedestal cleanup

Bản này kế thừa v34 và chỉ xóa các phần được đánh dấu trong feedback mới.

## Thay đổi

1. Xóa cụm thanh/cột đứng gỗ màu nâu ở vùng cửa bên hông.
   - Target material: 9 `aged brown structural wood`.
   - Xóa các cột gần cửa bên hông và cột liền phía trong cùng hàng nhìn, xử lý đối xứng hai đầu để khi xoay model không bị lặp lỗi.

2. Xóa thanh ngang/miếng gỗ dạng kệ nhô trên tường bên.
   - Target material: 8 `old dark bridge wood`.
   - Chỉ xóa slab cũ của v33, giữ nguyên miếng gỗ lót sàn đỏ đã duyệt ở v34.

3. Xóa 4 khối bệ tối/đen trong khu vực bên trong.
   - Target material: 6 `dark shadow inside stone arch`.
   - Xóa 4 khối tại các vị trí đối xứng x≈±4.37, z≈±0.88.

## Output

```text
output/chua_cau_hoi_an_textured_fixed_v35_side_door_column_slab_pedestal_cleanup.glb
output/chua_cau_hoi_an_textured.glb
output/49_da_nang/chua_cau_hoi_an_textured_fixed_v35_side_door_column_slab_pedestal_cleanup.glb
output/49_da_nang/chua_cau_hoi_an_textured.glb
```
