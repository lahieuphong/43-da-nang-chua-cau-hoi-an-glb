# V32 – inner tan/cream horizontal plank fix

Bản này kế thừa v31 và chỉ focus vào vùng người dùng chỉ trong ảnh: các dải **màu da / kem nhạt** bên trong khuôn viên, sát sàn gỗ nâu.

## Thay đổi

- Target chính: material 7 `worn light stone trim`.
- Target phụ: một số mép đá sáng material 5 trong cùng vùng nhìn.
- Trước: các dải kem vẫn đọc như **lên xuống / gãy W** theo trục X.
- Sau: profile được ép lại thành các hàng **ngang như tấm gỗ / miếng ván**.
- Cách sửa: dịch từng cột X theo trục Y, giữ nguyên UV, texture, chỉ số material và độ dày cục bộ của từng dải.

## Output

```text
output/chua_cau_hoi_an_textured_fixed_v32_inner_tan_horizontal_plank_fix.glb
output/chua_cau_hoi_an_textured.glb
output/49_da_nang/chua_cau_hoi_an_textured_fixed_v32_inner_tan_horizontal_plank_fix.glb
output/49_da_nang/chua_cau_hoi_an_textured.glb
```
