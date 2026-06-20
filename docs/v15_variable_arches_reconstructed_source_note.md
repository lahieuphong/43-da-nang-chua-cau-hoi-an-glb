# V15 variable arches – source phục dựng từ GLB nâng cấp

Bản ZIP này được tạo lại theo barem chuẩn của project cũ, nhưng dùng GLB nâng cấp `chua_cau_hoi_an_textured_fixed_v15_variable_arches.glb` làm nguồn phục dựng.

Các điểm chính:

- Giữ nguyên pipeline Python `glb_forge` và `scene_writer.py` của ZIP chuẩn.
- Giữ nguyên 39 texture procedural PBR nhúng vào GLB.
- Hình học v15 được giải mã từ buffer GLB nâng cấp thành `assets/geometry/chua_cau_hoi_an_v15_variable_arches_geometry.npz`.
- `src/glb_forge/scenes/chua_cau_hoi_an.py` nạp lại vertex, normal, UV và index theo từng material để xuất GLB nâng cấp.
- File procedural v10 gốc được giữ lại ở `src/glb_forge/scenes/chua_cau_hoi_an_v10_procedural_reference.py` để tham khảo.

Thông số phục dựng:

- Vertex: 126,760
- Materials: 30
- Mesh primitives có geometry: 29
- Bounds min: [-7.960000038146973, -0.5849999785423279, -4.616000175476074]
- Bounds max: [7.960000038146973, 5.380000114440918, 5.315999984741211]
- SHA-256 GLB đầu vào: `b8da5f6f16d0b12519bcfa292b0716dec27fabdf6db6e0070cbebb916eeed4af`

Cách chạy:

```bash
python3 main.py
```

Output chính:

```text
output/chua_cau_hoi_an_textured_fixed_v15_variable_arches.glb
```
