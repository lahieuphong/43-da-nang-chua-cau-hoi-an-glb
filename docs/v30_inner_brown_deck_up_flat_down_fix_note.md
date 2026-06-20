# V31 inner brown deck up-flat-down fix

Bản này kế thừa v29 và chỉ sửa phần miếng sàn/thanh gỗ nâu đậm bên trong lan-can mặt tiền.

## Thay đổi

- Target: material 8 `old dark bridge wood`.
- Vùng sửa: 300 triangle đầu của material 8, chính là khối sàn/thanh gỗ nâu đậm bên trong mặt tiền.
- Trước: profile bị gãy kiểu **lên – xuống – lên – xuống** ở giữa.
- Sau: profile **lên – ngang – xuống**, phần giữa phẳng theo plateau.
- Cách sửa: dịch từng cột theo trục X, giữ nguyên độ dày, UV, texture và segmentation của các ván.

## Thống kê

```text
inner_brown_deck_triangles_reprofiled: 300
inner_brown_deck_vertices_reprofiled: 604
inner_brown_deck_x_columns_shifted: 72
center_y_before: 1.599123
center_y_after: 1.683198
flat_center_y_min_after: 1.683198
flat_center_y_max_after: 1.683198
```

## Output

```text
output/chua_cau_hoi_an_textured_fixed_v31_inner_brown_floor_profile_final_fix.glb
output/chua_cau_hoi_an_textured.glb
output/49_da_nang/chua_cau_hoi_an_textured_fixed_v31_inner_brown_floor_profile_final_fix.glb
output/49_da_nang/chua_cau_hoi_an_textured.glb
```
