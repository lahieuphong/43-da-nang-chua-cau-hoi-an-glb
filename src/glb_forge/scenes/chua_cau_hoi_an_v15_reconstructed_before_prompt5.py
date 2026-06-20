# -*- coding: utf-8 -*-
from __future__ import annotations

from pathlib import Path
from random import Random

import numpy as np

from glb_forge.scene import SceneMesh

# Scene dùng hệ trục Y-up:
# x = chiều dài cầu; y = chiều cao; z = chiều rộng / trước-sau.
# Bản v15 này được dựng lại từ GLB nâng cấp "variable_arches" người dùng gửi,
# giữ đúng buffer hình học của bản nâng cấp và vẫn dùng cùng hệ material/texture
# procedural của ZIP barem chuẩn.

MaterialMap = dict[str, int | list[int]]
PROJECT_ROOT = Path(__file__).resolve().parents[3]
TEXTURE_ROOT = PROJECT_ROOT / "assets" / "textures" / "chua_cau_hoi_an"
GEOMETRY_PATH = PROJECT_ROOT / "assets" / "geometry" / "chua_cau_hoi_an_v15_variable_arches_geometry.npz"

MATERIAL_TEXTURES: dict[str, dict[str, str]] = {
    "old dark bridge wood": {"basecolor": "old_wood_basecolor.png", "normal": "old_wood_normal.png", "roughness": "old_wood_roughness.png"},
    "weathered grey stone piers": {"basecolor": "weathered_stone_basecolor.png", "normal": "weathered_stone_normal.png", "roughness": "weathered_stone_roughness.png"},
    "old yin-yang roof tile base": {"basecolor": "old_roof_tile_basecolor.png", "normal": "old_roof_tile_normal.png", "roughness": "old_roof_tile_roughness.png"},
    "aged red lacquer gate and panels": {"basecolor": "aged_red_lacquer_basecolor.png", "normal": "aged_red_lacquer_normal.png", "roughness": "aged_red_lacquer_roughness.png"},
    "muted gold leaf lettering": {"basecolor": "aged_gold_leaf_basecolor.png", "normal": "aged_gold_leaf_normal.png", "roughness": "aged_gold_leaf_roughness.png"},
    "Hoi An yellow plaster wall": {"basecolor": "hoi_an_yellow_wall_basecolor.png", "normal": "hoi_an_yellow_wall_normal.png", "roughness": "hoi_an_yellow_wall_roughness.png"},
    "warm Hoi An street paving": {"basecolor": "warm_paving_brick_basecolor.png", "normal": "warm_paving_brick_normal.png", "roughness": "warm_paving_brick_roughness.png"},
    "blue white ceramic roof plates": {"basecolor": "blue_white_ceramic_basecolor.png", "normal": "blue_white_ceramic_normal.png", "roughness": "blue_white_ceramic_roughness.png"},
    "soft moss on old stone": {"basecolor": "soft_moss_basecolor.png", "normal": "soft_moss_normal.png", "roughness": "soft_moss_roughness.png"},
    "dark damp age stains": {"basecolor": "damp_stain_basecolor.png", "normal": "damp_stain_normal.png", "roughness": "damp_stain_roughness.png"},
    "shallow green canal water": {"basecolor": "canal_water_basecolor.png", "normal": "canal_water_normal.png", "roughness": "canal_water_roughness.png"},
    "old town green foliage": {"basecolor": "village_leaf_basecolor.png", "normal": "village_leaf_normal.png", "roughness": "village_leaf_roughness.png"},
    "warm red silk lantern": {"basecolor": "lantern_silk_basecolor.png", "normal": "lantern_silk_normal.png", "roughness": "lantern_silk_roughness.png"},
}


def _texture_path(filename: str | None) -> str | None:
    if filename is None:
        return None
    return str(TEXTURE_ROOT / filename)


def create_chua_cau_hoi_an(seed: int = 1719) -> SceneMesh:
    """Tạo lại mô hình Chùa Cầu Hội An / Lai Viễn Kiều bản v15 variable arches.

    Source gốc của bản v15 không có trong ZIP ban đầu, nên file này phục dựng từ
    GLB nâng cấp đã có: giữ nguyên vertex, normal, UV và index theo từng material.
    Nhờ vậy project vẫn chạy bằng cùng pipeline Python GLB Forge và xuất lại GLB
    nâng cấp có cùng hình học, texture và vật liệu với file v15 đã gửi.
    """
    # Seed được giữ để API tương thích với bản procedural v10, dù geometry v15 đã cố định.
    _ = Random(seed)
    scene = SceneMesh("Chua_Cau_Hoi_An_Lai_Vien_Kieu")
    _make_materials(scene)
    _load_reconstructed_geometry(scene)
    return scene


def _make_materials(scene: SceneMesh) -> MaterialMap:
    materials: MaterialMap = {}

    wood_tex = _texture_path("old_wood_basecolor.png")
    wood_nrm = _texture_path("old_wood_normal.png")
    wood_rgh = _texture_path("old_wood_roughness.png")
    stone_tex = _texture_path("weathered_stone_basecolor.png")
    stone_nrm = _texture_path("weathered_stone_normal.png")
    stone_rgh = _texture_path("weathered_stone_roughness.png")
    roof_tex = _texture_path("old_roof_tile_basecolor.png")
    roof_nrm = _texture_path("old_roof_tile_normal.png")
    roof_rgh = _texture_path("old_roof_tile_roughness.png")
    red_tex = _texture_path("aged_red_lacquer_basecolor.png")
    red_nrm = _texture_path("aged_red_lacquer_normal.png")
    red_rgh = _texture_path("aged_red_lacquer_roughness.png")
    yellow_tex = _texture_path("hoi_an_yellow_wall_basecolor.png")
    yellow_nrm = _texture_path("hoi_an_yellow_wall_normal.png")
    yellow_rgh = _texture_path("hoi_an_yellow_wall_roughness.png")
    paving_tex = _texture_path("warm_paving_brick_basecolor.png")
    paving_nrm = _texture_path("warm_paving_brick_normal.png")
    paving_rgh = _texture_path("warm_paving_brick_roughness.png")
    ceramic_tex = _texture_path("blue_white_ceramic_basecolor.png")
    ceramic_nrm = _texture_path("blue_white_ceramic_normal.png")
    ceramic_rgh = _texture_path("blue_white_ceramic_roughness.png")
    moss_tex = _texture_path("soft_moss_basecolor.png")
    moss_nrm = _texture_path("soft_moss_normal.png")
    moss_rgh = _texture_path("soft_moss_roughness.png")
    water_tex = _texture_path("canal_water_basecolor.png")
    water_nrm = _texture_path("canal_water_normal.png")
    water_rgh = _texture_path("canal_water_roughness.png")
    leaf_tex = _texture_path("village_leaf_basecolor.png")
    leaf_nrm = _texture_path("village_leaf_normal.png")
    leaf_rgh = _texture_path("village_leaf_roughness.png")
    gold_tex = _texture_path("aged_gold_leaf_basecolor.png")
    gold_nrm = _texture_path("aged_gold_leaf_normal.png")
    gold_rgh = _texture_path("aged_gold_leaf_roughness.png")
    damp_tex = _texture_path("damp_stain_basecolor.png")
    damp_nrm = _texture_path("damp_stain_normal.png")
    damp_rgh = _texture_path("damp_stain_roughness.png")
    silk_tex = _texture_path("lantern_silk_basecolor.png")
    silk_nrm = _texture_path("lantern_silk_normal.png")
    silk_rgh = _texture_path("lantern_silk_roughness.png")

    materials["display_base"] = scene.add_material("matte warm stone display base", (0.48, 0.44, 0.38, 1.0), roughness=0.95, base_color_texture=stone_tex, normal_texture=stone_nrm, normal_scale=0.30, roughness_texture=stone_rgh)
    materials["earth"] = scene.add_material("old town dusty earth", (0.54, 0.43, 0.32, 1.0), roughness=0.96, base_color_texture=paving_tex, normal_texture=paving_nrm, normal_scale=0.25, roughness_texture=paving_rgh)
    materials["paving"] = scene.add_material("warm Hoi An street paving", (0.74, 0.57, 0.43, 1.0), roughness=0.94, base_color_texture=paving_tex, normal_texture=paving_nrm, normal_scale=0.48, roughness_texture=paving_rgh)
    materials["water"] = scene.add_material("shallow green canal water", (0.05, 0.28, 0.30, 1.0), metallic=0.0, roughness=0.22, base_color_texture=water_tex, normal_texture=water_nrm, normal_scale=0.20, roughness_texture=water_rgh)
    materials["water_edge"] = scene.add_material("opaque canal water vertical edge", (0.05, 0.28, 0.30, 1.0), metallic=0.0, roughness=0.24, base_color_texture=water_tex, normal_texture=water_nrm, normal_scale=0.18, roughness_texture=water_rgh)

    materials["stone"] = scene.add_material("weathered grey stone piers", (0.58, 0.56, 0.50, 1.0), roughness=0.96, base_color_texture=stone_tex, normal_texture=stone_nrm, normal_scale=0.62, roughness_texture=stone_rgh)
    materials["stone_dark"] = scene.add_material("dark shadow inside stone arch", (0.12, 0.13, 0.12, 1.0), roughness=1.0, base_color_texture=damp_tex, normal_texture=damp_nrm, normal_scale=0.25, roughness_texture=damp_rgh)
    materials["stone_light"] = scene.add_material("worn light stone trim", (0.74, 0.72, 0.64, 1.0), roughness=0.94, base_color_texture=stone_tex, normal_texture=stone_nrm, normal_scale=0.45, roughness_texture=stone_rgh)

    materials["wood_dark"] = scene.add_material("old dark bridge wood", (0.33, 0.20, 0.13, 1.0), roughness=0.90, base_color_texture=wood_tex, normal_texture=wood_nrm, normal_scale=0.72, roughness_texture=wood_rgh)
    materials["wood"] = scene.add_material("aged brown structural wood", (0.55, 0.34, 0.20, 1.0), roughness=0.86, base_color_texture=wood_tex, normal_texture=wood_nrm, normal_scale=0.60, roughness_texture=wood_rgh)
    materials["wood_light"] = scene.add_material("worn golden brown wood edge", (0.78, 0.51, 0.30, 1.0), roughness=0.84, base_color_texture=wood_tex, normal_texture=wood_nrm, normal_scale=0.44, roughness_texture=wood_rgh)
    materials["interior_shadow"] = scene.add_material("deep covered bridge interior", (0.025, 0.019, 0.014, 1.0), roughness=1.0)

    materials["red"] = scene.add_material("aged red lacquer gate and panels", (0.70, 0.14, 0.10, 1.0), roughness=0.78, base_color_texture=red_tex, normal_texture=red_nrm, normal_scale=0.42, roughness_texture=red_rgh)
    materials["red_dark"] = scene.add_material("dark oxidized red lacquer", (0.37, 0.06, 0.04, 1.0), roughness=0.86, base_color_texture=red_tex, normal_texture=red_nrm, normal_scale=0.50, roughness_texture=red_rgh)
    materials["gold"] = scene.add_material("muted gold leaf lettering", (1.0, 0.72, 0.20, 1.0), metallic=0.35, roughness=0.38, base_color_texture=gold_tex, normal_texture=gold_nrm, normal_scale=0.18, roughness_texture=gold_rgh)
    materials["black"] = scene.add_material("blackened doorway shadow", (0.015, 0.011, 0.008, 1.0), roughness=1.0)

    materials["roof_base"] = scene.add_material("old yin-yang roof tile base", (0.57, 0.28, 0.18, 1.0), roughness=0.93, base_color_texture=roof_tex, normal_texture=roof_nrm, normal_scale=0.68, roughness_texture=roof_rgh)
    roof_tiles: list[int] = []
    roof_tints = [
        (0.62, 0.31, 0.20, 1.0),
        (0.72, 0.38, 0.24, 1.0),
        (0.50, 0.24, 0.17, 1.0),
        (0.78, 0.45, 0.30, 1.0),
        (0.43, 0.21, 0.15, 1.0),
    ]
    for i, tint in enumerate(roof_tints):
        roof_tiles.append(scene.add_material(f"individual muted roof tile {i + 1}", tint, roughness=0.95, base_color_texture=roof_tex, normal_texture=roof_nrm, normal_scale=0.74, roughness_texture=roof_rgh))
    materials["roof_tiles"] = roof_tiles

    materials["ceramic"] = scene.add_material("blue white ceramic roof plates", (0.92, 0.92, 0.86, 1.0), roughness=0.42, base_color_texture=ceramic_tex, normal_texture=ceramic_nrm, normal_scale=0.25, roughness_texture=ceramic_rgh)
    materials["ceramic_blue"] = scene.add_material("cobalt blue ceramic accents", (0.10, 0.33, 0.66, 1.0), roughness=0.55, base_color_texture=ceramic_tex, normal_texture=ceramic_nrm, normal_scale=0.18, roughness_texture=ceramic_rgh)
    materials["moss"] = scene.add_material("soft moss on old stone", (0.40, 0.56, 0.28, 1.0), roughness=0.98, base_color_texture=moss_tex, normal_texture=moss_nrm, normal_scale=0.46, roughness_texture=moss_rgh)

    materials["yellow_wall"] = scene.add_material("Hoi An yellow plaster wall", (0.86, 0.63, 0.28, 1.0), roughness=0.92, base_color_texture=yellow_tex, normal_texture=yellow_nrm, normal_scale=0.30, roughness_texture=yellow_rgh)
    materials["leaf"] = scene.add_material("old town green foliage", (0.33, 0.58, 0.24, 1.0), roughness=0.94, base_color_texture=leaf_tex, normal_texture=leaf_nrm, normal_scale=0.36, roughness_texture=leaf_rgh)
    materials["lantern_red"] = scene.add_material("warm red silk lantern", (0.88, 0.10, 0.06, 1.0), roughness=0.58, base_color_texture=silk_tex, normal_texture=silk_nrm, normal_scale=0.18, roughness_texture=silk_rgh)
    materials["lantern_yellow"] = scene.add_material("warm yellow silk lantern", (1.0, 0.67, 0.22, 1.0), roughness=0.55, base_color_texture=silk_tex, normal_texture=silk_nrm, normal_scale=0.16, roughness_texture=silk_rgh)
    materials["lantern_glow"] = scene.add_material("soft lantern glow", (1.0, 0.82, 0.42, 0.72), roughness=0.35)

    return materials


def _load_reconstructed_geometry(scene: SceneMesh) -> None:
    if not GEOMETRY_PATH.exists():
        raise FileNotFoundError(f"Không tìm thấy geometry phục dựng: {GEOMETRY_PATH}")

    data = np.load(GEOMETRY_PATH)
    positions = data["positions"].astype(np.float32, copy=False)
    normals = data["normals"].astype(np.float32, copy=False)
    texcoords = data["texcoords"].astype(np.float32, copy=False)

    if not (len(positions) == len(normals) == len(texcoords)):
        raise ValueError("Geometry v15 không hợp lệ: positions/normals/texcoords không cùng số lượng")
    if len(scene.materials) != 30:
        raise ValueError(f"Sai số material, cần 30 nhưng đang có {len(scene.materials)}")

    # Một số giá trị biên được trả về dạng float32 dài khi đọc từ GLB.
    # Gán lại theo float Python của source gốc để JSON accessor min/max khớp
    # file GLB v15 đầu vào, trong khi bytes float32 khi pack vẫn giữ nguyên.
    bound_value_map = {
        -7.960000038146973: -7.96,
        7.960000038146973: 7.96,
        -0.5849999785423279: -0.585,
        5.380000114440918: 5.380000000000001,
        -4.616000175476074: -4.6160000000000005,
        5.315999984741211: 5.316,
    }

    def _restore_source_float(value: float) -> float:
        return bound_value_map.get(float(value), float(value))

    scene.positions = [tuple(_restore_source_float(v) for v in row) for row in positions]
    scene.normals = [tuple(map(float, row)) for row in normals]
    scene.texcoords = [tuple(map(float, row)) for row in texcoords]

    for material_index in range(len(scene.materials)):
        key = f"indices_{material_index:02d}"
        values = data[key].astype(np.uint32, copy=False)
        scene.indices_by_material[material_index] = [int(v) for v in values]
