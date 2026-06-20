# V31 – final inner brown floor/rail profile fix

Bản này sửa đúng phần bạn chỉ ở hình crop: dải/miếng màu nâu bên trong mặt tiền còn nhìn như **lên – xuống – lên – xuống**.

Cách fix:

- Nền giữ nguyên từ v30.
- Chỉnh trực tiếp material 8 theo từng cột X, không chỉ dịch nguyên cụm.
- Ba vùng material 8 được chỉnh:
  1. Main inner brown floor/deck panel: group range `0..22`.
  2. Inner lower brown rail segments: group range `463..475`.
  3. Dark brown landing/fascia strip visible in the focus crop: group range `477..484`.
- Profile sau fix: **lên → ngang → xuống**.

Thống kê:

```text
Triangles adjusted: 528
Unique vertices shifted: 614
Vertices: 156736
Materials: 30
Textures PNG: 39
```

Source chính nạp geometry từ:

```text
assets/geometry/chua_cau_hoi_an_v31_inner_brown_floor_profile_final_fix_geometry.npz
```
