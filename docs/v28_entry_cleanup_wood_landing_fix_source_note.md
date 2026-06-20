# v28 entry cleanup + wood landing fix source note

Gói này được xuất lại theo barem ZIP v22 và đồng bộ với GLB nâng cấp mới nhất.

- Source chính: `src/glb_forge/scenes/chua_cau_hoi_an.py`.
- Geometry tái dựng: `assets/geometry/chua_cau_hoi_an_v28_entry_cleanup_wood_landing_fix_geometry.npz`.
- Manifest vật liệu/texture: `assets/geometry/chua_cau_hoi_an_v28_entry_cleanup_wood_landing_fix_manifest.json`.
- Output chính: `output/chua_cau_hoi_an_textured_fixed_v28_entry_cleanup_wood_landing_fix.glb`.
- Output registry: `output/49_da_nang/chua_cau_hoi_an_textured_fixed_v28_entry_cleanup_wood_landing_fix.glb`.
- Output compatibility: `output/chua_cau_hoi_an_textured.glb` và `output/49_da_nang/chua_cau_hoi_an_textured.glb`.

Cách kiểm tra:

```bash
python3 main.py
```

Bản source này giữ đúng pipeline Python thuần của barem: dữ liệu SceneMesh được nạp từ NPZ/manifest rồi ghi ra GLB bằng `src/glb_forge/scene_writer.py`.
