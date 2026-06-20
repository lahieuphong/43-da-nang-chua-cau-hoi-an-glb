# Prompt 8 / V19 – Three-segment bridge profile fix

Các chỉnh sửa theo feedback mới:

- Giữ nguyên nền, hai hông đỏ, mái ngói, hàng rào, nước và các phần đã duyệt ở V18.
- Chuyển các đường mặt tiền chính từ dạng một góc nhọn ở giữa thành bố cục **lên – ngang – xuống** như ảnh Chùa Cầu thật.
- Áp dụng chung cho các gờ/viền nhìn chính diện: mái, diềm mái, hàng rào, lan-can đá và gờ đá dưới.
- Thêm plateau trung tâm bằng hàm `_three_segment_crown()` để source vẫn procedural, dễ chỉnh tiếp.
- Nâng nhẹ các vertex gốc ở vùng giữa bằng `_apply_prompt8_three_segment_vertex_profile()` để phần cũ không còn đọc quá rõ thành chữ V.
- Thêm vài cột/khuôn nhỏ tại hai điểm gãy của đoạn ngang để mặt tiền đọc rõ ba mảnh nhưng không đổi phong cách vật liệu.

Output chính:

```text
output/chua_cau_hoi_an_textured_fixed_v19_three_segment_bridge_profile.glb
```
