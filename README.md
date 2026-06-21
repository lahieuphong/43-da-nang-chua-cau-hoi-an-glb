# 43 - Đà Nẵng / Hội An - Chùa Cầu Hội An - GLB
Project Python thuần để tạo file .glb cho Chùa Cầu Hội An (Cầu Nhật Bản / Lai Viễn Kiều), Hội An.

## Output hiện tại

```
output/43_da_nang/chua_cau_hoi_an.glb
```

## Thông Số Model

| | |
|---|---|
| Scene | `Chua_Cau_Hoi_An_Lai_Vien_Kieu` |
| Vertices | 246,501 |
| Materials | 30 |
| Primitives | 25 |
| UV/TEXCOORD | có, kèm theo geometry NPZ |
| Images | 39 PNG nhúng trong GLB |
| Textures | 39 texture slots (basecolor + normal + roughness) |
| Registry key | `43-da-nang/chua-cau-hoi-an` |

## Cấu Trúc Chính

```
assets/
├── geometry/
│   ├── chua_cau_hoi_an_geometry.npz     # vertex positions, normals, UVs, indices
│   └── chua_cau_hoi_an_manifest.json    # danh sách material + metadata
└── textures/
    └── chua_cau_hoi_an/
        ├── old_wood_basecolor.png
        ├── old_wood_normal.png
        ├── old_wood_roughness.png
        ├── weathered_stone_basecolor.png
        ├── weathered_stone_normal.png
        ├── weathered_stone_roughness.png
        ├── old_roof_tile_basecolor.png
        ├── old_roof_tile_normal.png
        ├── old_roof_tile_roughness.png
        ├── aged_red_lacquer_basecolor.png
        ├── aged_red_lacquer_normal.png
        ├── aged_red_lacquer_roughness.png
        ├── hoi_an_yellow_wall_basecolor.png
        ├── hoi_an_yellow_wall_normal.png
        ├── hoi_an_yellow_wall_roughness.png
        ├── warm_paving_brick_basecolor.png
        ├── warm_paving_brick_normal.png
        ├── warm_paving_brick_roughness.png
        ├── blue_white_ceramic_basecolor.png
        ├── blue_white_ceramic_normal.png
        ├── blue_white_ceramic_roughness.png
        ├── soft_moss_basecolor.png
        ├── soft_moss_normal.png
        ├── soft_moss_roughness.png
        ├── canal_water_basecolor.png
        ├── canal_water_normal.png
        ├── canal_water_roughness.png
        ├── village_leaf_basecolor.png
        ├── village_leaf_normal.png
        ├── village_leaf_roughness.png
        ├── aged_gold_leaf_basecolor.png
        ├── aged_gold_leaf_normal.png
        ├── aged_gold_leaf_roughness.png
        ├── damp_stain_basecolor.png
        ├── damp_stain_normal.png
        ├── damp_stain_roughness.png
        ├── lantern_silk_basecolor.png
        ├── lantern_silk_normal.png
        └── lantern_silk_roughness.png

src/glb_forge/
├── scene.py                         # SceneMesh + Material, hệ Y-up
├── scene_writer.py                  # ghi GLB, nhúng PNG texture vào BIN chunk
├── build.py                         # luồng generate dùng chung
├── scenes/
│   └── chua_cau_hoi_an.py           # load geometry NPZ + manifest, tạo SceneMesh
└── sites/
    ├── models.py
    ├── registry.py
    └── provinces/
        └── da_nang.py

scripts/
├── generate_all.py                  # generate toàn bộ di tích đã đăng ký
├── generate_site.py                 # generate theo registry key
└── generate_textures.py             # sinh lại toàn bộ texture PNG procedural
```

## Chạy Code

Vào thư mục project:

```bash
cd 43-da-nang-chua-cau-hoi-an-glb
```

Generate file GLB:

```bash
python main.py
```

Hoặc generate theo registry key:

```bash
python scripts/generate_site.py 43-da-nang/chua-cau-hoi-an
```

Hoặc generate toàn bộ di tích đã đăng ký:

```bash
python scripts/generate_all.py
```

Kết quả nằm tại:

```
output/43_da_nang/chua_cau_hoi_an.glb
```

## Sinh Lại Texture

Texture đã được tạo sẵn trong `assets/textures/chua_cau_hoi_an/`. Nếu muốn sinh lại:

```bash
python scripts/generate_textures.py
```

Texture là ảnh procedural tạo bằng NumPy + Pillow, mỗi bộ gồm 3 map: `basecolor`, `normal`, `roughness`.

## Cách Map Texture

Trong `src/glb_forge/scenes/chua_cau_hoi_an.py`, geometry và material được load từ NPZ + manifest JSON. Mapping texture theo material:

```python
MATERIAL_TEXTURES = {
    "matte warm stone display base":      "weathered_stone",
    "old town dusty earth":               "warm_paving_brick",
    "warm Hoi An street paving":          "warm_paving_brick",
    "shallow green canal water":          "canal_water",
    "opaque canal water vertical edge":   "canal_water",
    "weathered grey stone piers":         "weathered_stone",
    "dark shadow inside stone arch":      "damp_stain",
    "worn light stone trim":              "weathered_stone",
    "old dark bridge wood":               "old_wood",
    "aged brown structural wood":         "old_wood",
    "worn golden brown wood edge":        "old_wood",
    "aged red lacquer gate and panels":   "aged_red_lacquer",
    "dark oxidized red lacquer":          "aged_red_lacquer",
    "muted gold leaf lettering":          "aged_gold_leaf",
    "old yin-yang roof tile base":        "old_roof_tile",
    "individual muted roof tile 1-5":     "old_roof_tile",
    "blue white ceramic roof plates":     "blue_white_ceramic",
    "cobalt blue ceramic accents":        "blue_white_ceramic",
    "soft moss on old stone":             "soft_moss",
    "Hoi An yellow plaster wall":         "hoi_an_yellow_wall",
    "old town green foliage":             "village_leaf",
    "warm red silk lantern":              "lantern_silk",
    "warm yellow silk lantern":           "lantern_silk",
}
```

Geometry lưu sẵn UV trong NPZ (TEXCOORD_0), không cần planar mapping runtime.
