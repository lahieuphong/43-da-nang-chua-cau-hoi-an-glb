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
    """Tạo mô hình Chùa Cầu Hội An / Lai Viễn Kiều bản v18 shorter bridge + extended side land.

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
    _apply_prompt5_reference_fixes(scene)
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

    materials["stone"] = scene.add_material("weathered grey stone piers", (0.86, 0.84, 0.76, 1.0), roughness=0.98, base_color_texture=stone_tex, normal_texture=stone_nrm, normal_scale=0.46, roughness_texture=stone_rgh)
    materials["stone_dark"] = scene.add_material("dark shadow inside stone arch", (0.12, 0.13, 0.12, 1.0), roughness=1.0, base_color_texture=damp_tex, normal_texture=damp_nrm, normal_scale=0.25, roughness_texture=damp_rgh)
    materials["stone_light"] = scene.add_material("worn light stone trim", (0.96, 0.94, 0.86, 1.0), roughness=0.97, base_color_texture=stone_tex, normal_texture=stone_nrm, normal_scale=0.34, roughness_texture=stone_rgh)

    materials["wood_dark"] = scene.add_material("old dark bridge wood", (0.33, 0.20, 0.13, 1.0), roughness=0.90, base_color_texture=wood_tex, normal_texture=wood_nrm, normal_scale=0.72, roughness_texture=wood_rgh)
    materials["wood"] = scene.add_material("aged brown structural wood", (0.55, 0.34, 0.20, 1.0), roughness=0.86, base_color_texture=wood_tex, normal_texture=wood_nrm, normal_scale=0.60, roughness_texture=wood_rgh)
    materials["wood_light"] = scene.add_material("worn golden brown wood edge", (0.78, 0.51, 0.30, 1.0), roughness=0.84, base_color_texture=wood_tex, normal_texture=wood_nrm, normal_scale=0.44, roughness_texture=wood_rgh)
    materials["interior_shadow"] = scene.add_material("deep covered bridge interior", (0.025, 0.019, 0.014, 1.0), roughness=1.0)

    materials["red"] = scene.add_material("aged red lacquer gate and panels", (0.70, 0.14, 0.10, 1.0), roughness=0.78, base_color_texture=red_tex, normal_texture=red_nrm, normal_scale=0.42, roughness_texture=red_rgh)
    materials["red_dark"] = scene.add_material("dark oxidized red lacquer", (0.37, 0.06, 0.04, 1.0), roughness=0.86, base_color_texture=red_tex, normal_texture=red_nrm, normal_scale=0.50, roughness_texture=red_rgh)
    materials["gold"] = scene.add_material("muted gold leaf lettering", (1.0, 0.72, 0.20, 1.0), metallic=0.35, roughness=0.38, base_color_texture=gold_tex, normal_texture=gold_nrm, normal_scale=0.18, roughness_texture=gold_rgh)
    materials["black"] = scene.add_material("blackened doorway shadow", (0.015, 0.011, 0.008, 1.0), roughness=1.0)

    materials["roof_base"] = scene.add_material("old yin-yang roof tile base", (0.93, 0.68, 0.45, 1.0), roughness=0.94, base_color_texture=roof_tex, normal_texture=roof_nrm, normal_scale=0.82, roughness_texture=roof_rgh)
    roof_tiles: list[int] = []
    # Prompt 5: mái ngói chuyển sang gam đất nung cũ + viền ngói vàng nhạt,
    # gần ảnh tham chiếu hơn thay vì mái nâu phẳng của bản trước.
    roof_tints = [
        (0.96, 0.78, 0.58, 1.0),
        (0.84, 0.42, 0.24, 1.0),
        (0.98, 0.88, 0.72, 1.0),
        (0.76, 0.34, 0.20, 1.0),
        (0.90, 0.60, 0.38, 1.0),
    ]
    for i, tint in enumerate(roof_tints):
        roof_tiles.append(scene.add_material(f"individual muted roof tile {i + 1}", tint, roughness=0.96, base_color_texture=roof_tex, normal_texture=roof_nrm, normal_scale=0.92, roughness_texture=roof_rgh))
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


# -----------------------------------------------------------------------------
# Prompt 5 reference fixes
# -----------------------------------------------------------------------------
# Các hằng số material giữ nguyên thứ tự 30 material của bản v15 phục dựng.
# Không xóa chi tiết cũ; chỉ chỉnh vật liệu, nâng nhịp mái/cầu và phủ thêm các
# chi tiết nhìn mặt tiền giống ảnh tham chiếu hơn: đá sáng, hàng rào cao thoáng,
# mái ngói sáng có hàng ngói dọc, dốc cầu/mái dạng gãy thẳng thay vì quá tròn.
MAT_EARTH = 1
MAT_PAVING = 2
MAT_STONE = 5
MAT_STONE_DARK = 6
MAT_STONE_LIGHT = 7
MAT_WOOD_DARK = 8
MAT_WOOD = 9
MAT_WOOD_LIGHT = 10
MAT_INTERIOR_SHADOW = 11
MAT_RED = 12
MAT_RED_DARK = 13
MAT_GOLD = 14
MAT_ROOF_BASE = 16
MAT_ROOF_TILES = (17, 18, 19, 20, 21)
MAT_CERAMIC = 22
MAT_CERAMIC_BLUE = 23
MAT_MOSS = 24
MAT_YELLOW_WALL = 25
MAT_LEAF = 26
MAT_LANTERN_RED = 27
MAT_LANTERN_GLOW = 29


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))


def _linear_crown(x: float, *, half: float, edge: float, center: float) -> float:
    """Đường dốc thẳng 2 bên: cao ở giữa, hạ dần về hai đầu cầu."""
    t = 1.0 - min(abs(x) / half, 1.0)
    return edge + (center - edge) * t


def _apply_prompt5_reference_fixes(scene: SceneMesh) -> None:
    """Áp dụng các chỉnh sửa theo ảnh feedback mà vẫn giữ phần còn lại."""
    # Prompt 7/V18: dọn 4 cây, bỏ 2 nhà phụ phía sau, rút ngắn thân cầu chính
    # để hai mảng đất liền/tường đỏ hai bên có cảm giác dài hơn như ảnh gốc.
    _remove_prompt7_trees_side_houses_and_spikes(scene)
    _shrink_main_bridge_width_for_extended_sides(scene)
    _make_roof_pitch_more_angular(scene)
    _raise_lower_stone_arch_height(scene)
    _flatten_side_land_colored_frames(scene)
    _add_front_and_back_high_open_railings(scene)
    _add_reference_roof_tile_overlay(scene)
    _add_light_stone_material_overlays(scene)
    _add_prompt6_side_red_wall_land_fixes(scene)
    _remove_prompt7_residual_back_spikes(scene)


def _iter_vertices_for_materials(scene: SceneMesh, material_indices: set[int]) -> set[int]:
    vertices: set[int] = set()
    for material_index in material_indices:
        vertices.update(scene.indices_by_material.get(material_index, []))
    return vertices


def _filter_triangles(scene: SceneMesh, material_indices: set[int], predicate) -> None:
    """Xóa tam giác theo tâm tam giác; vertex thừa được giữ để writer đơn giản."""
    for material_index in material_indices:
        old_indices = scene.indices_by_material.get(material_index, [])
        if not old_indices:
            continue
        kept: list[int] = []
        for i in range(0, len(old_indices), 3):
            tri = old_indices[i:i + 3]
            if len(tri) < 3:
                continue
            pts = [scene.positions[v] for v in tri]
            cx = (pts[0][0] + pts[1][0] + pts[2][0]) / 3.0
            cy = (pts[0][1] + pts[1][1] + pts[2][1]) / 3.0
            cz = (pts[0][2] + pts[1][2] + pts[2][2]) / 3.0
            if not predicate(cx, cy, cz, pts):
                kept.extend(tri)
        scene.indices_by_material[material_index] = kept


def _remove_prompt7_trees_side_houses_and_spikes(scene: SceneMesh) -> None:
    """Dọn các chi tiết người dùng muốn bỏ ở bản V18.

    - Xóa 4 cây ở bốn góc.
    - Xóa hai nhà phụ mái cam phía sau/trên bản v17.
    - Xóa các thanh/chống chéo bị chỉa ra ở vùng mái phụ phía sau.
    """
    # Lá cây nằm gọn trong material foliage; người dùng muốn bỏ cả 4 cây nên clear hẳn.
    scene.indices_by_material[MAT_LEAF] = []

    # Thân cây là các trụ gỗ nhỏ ở 4 góc, tránh chạm gỗ cầu bằng bounding box góc ngoài.
    _filter_triangles(
        scene,
        {MAT_WOOD_DARK, MAT_WOOD, MAT_WOOD_LIGHT},
        lambda x, y, z, pts: abs(x) > 6.35 and abs(z) > 3.20 and -0.05 <= y <= 2.25,
    )

    # Hai nhà phụ phía sau: toàn bộ tường vàng và các mái/gỗ ở hai bên phía sau.
    scene.indices_by_material[MAT_YELLOW_WALL] = []
    side_house_materials = {
        MAT_WOOD_DARK, MAT_WOOD, MAT_WOOD_LIGHT, MAT_RED, MAT_RED_DARK,
        MAT_ROOF_BASE, *MAT_ROOF_TILES, MAT_CERAMIC, MAT_CERAMIC_BLUE, MAT_MOSS,
    }
    _filter_triangles(
        scene,
        side_house_materials,
        # Dùng max theo từng đỉnh để bắt cả các tam giác mái rất lớn của 2 nhà phụ.
        lambda x, y, z, pts: (
            max(p[2] for p in pts) > 2.92
            and max(abs(p[0]) for p in pts) > 3.62
            and max(p[1] for p in pts) > 0.80
        ),
    )

    # Một số chống chéo/thanh mảnh còn nằm ở vùng sau mái, nhìn như bị chỉa ra từ trên xuống.
    _filter_triangles(
        scene,
        {MAT_WOOD_DARK, MAT_WOOD, MAT_WOOD_LIGHT, MAT_MOSS, *MAT_ROOF_TILES},
        lambda x, y, z, pts: (
            max(p[2] for p in pts) > 2.55
            and max(p[1] for p in pts) > 0.45
            and max(abs(p[0]) for p in pts) > 2.95
        ),
    )



def _remove_prompt7_residual_back_spikes(scene: SceneMesh) -> None:
    """Dọn nốt vài thanh cũ lộ ở vùng sau sau khi đã thêm hông đỏ V18."""
    back_spike_materials = {
        MAT_WOOD_DARK, MAT_WOOD, MAT_WOOD_LIGHT, MAT_RED, MAT_RED_DARK,
        *MAT_ROOF_TILES, MAT_CERAMIC, MAT_CERAMIC_BLUE, MAT_MOSS,
    }
    _filter_triangles(
        scene,
        back_spike_materials,
        lambda x, y, z, pts: (
            z > 2.34
            and y > 0.05
            and 1.65 < abs(x) < 5.80
        ),
    )


def _shrink_main_bridge_width_for_extended_sides(scene: SceneMesh) -> None:
    """Rút ngắn bề ngang thân/mái cầu chính, dành chỗ cho hai hông đỏ dài hơn."""
    central_materials = {
        MAT_STONE, MAT_STONE_DARK, MAT_STONE_LIGHT,
        MAT_WOOD_DARK, MAT_WOOD, MAT_WOOD_LIGHT, MAT_INTERIOR_SHADOW,
        MAT_RED, MAT_RED_DARK, MAT_GOLD, MAT_ROOF_BASE, *MAT_ROOF_TILES,
        MAT_CERAMIC, MAT_CERAMIC_BLUE, MAT_MOSS, MAT_LANTERN_RED, MAT_LANTERN_GLOW,
    }
    scale = 0.895
    for vertex_index in _iter_vertices_for_materials(scene, central_materials):
        x, y, z = scene.positions[vertex_index]
        # Chỉ rút phần cầu/mái chính; giữ nguyên nền, nước và bờ ngoài.
        if abs(x) <= 6.18 and y > 0.04 and z < 3.35:
            scene.positions[vertex_index] = (x * scale, y, z)


def _raise_lower_stone_arch_height(scene: SceneMesh) -> None:
    """Nâng nhẹ chiều cao phần vòm/trụ đá dưới cầu theo ảnh feedback."""
    stone_vertices = _iter_vertices_for_materials(scene, {MAT_STONE, MAT_STONE_DARK, MAT_STONE_LIGHT})
    for vertex_index in stone_vertices:
        x, y, z = scene.positions[vertex_index]
        if abs(x) <= 5.38 and abs(z) <= 2.10 and 0.20 < y < 1.86:
            # Giữ chân trụ sát nước, kéo phần vòm/lan-can đá phía trên cao thêm vừa phải.
            lifted = 0.20 + (y - 0.20) * 1.105
            scene.positions[vertex_index] = (x, lifted, z)


def _flatten_side_land_colored_frames(scene: SceneMesh) -> None:
    """Hạ hai khối bờ đất màu nâu ở hai bên xuống thành mặt đất liền thấp.

    Ảnh tham chiếu mới cho thấy hai hông chùa đặt trên nền đất/đường phẳng,
    không có hai khối bờ cao màu nâu kiểu "khung" ở hai đầu. Ở geometry v15,
    phần này nằm trong material earth/paving với các đỉnh cao khoảng 0.82.
    Ta chỉ hạ các đỉnh bờ ngoài kênh, giữ nguyên nước, vòm đá và thân cầu.
    """
    side_vertices = _iter_vertices_for_materials(scene, {MAT_EARTH, MAT_PAVING})
    for vertex_index in side_vertices:
        x, y, z = scene.positions[vertex_index]
        # Chỉ tác động hai mảng đất liền ngoài kênh; không chạm canal/water ở giữa.
        if abs(x) < 5.72 or y <= 0.19:
            continue
        # Mặt nền phẳng thấp, có chênh nhẹ giữa paving và gân lát để không z-fighting.
        if y >= 0.82:
            new_y = 0.158 + min(0.032, max(0.0, y - 0.82) * 0.85)
        else:
            new_y = min(y, 0.165)
        scene.positions[vertex_index] = (x, new_y, z)


def _make_roof_pitch_more_angular(scene: SceneMesh) -> None:
    """Tăng dốc mái/cầu dạng thẳng ở hai bên, tránh cảm giác vòm quá tròn/thấp."""
    roof_like = set(range(13, 24)) | set(range(27, 30))
    for vertex_index in _iter_vertices_for_materials(scene, roof_like):
        x, y, z = scene.positions[vertex_index]
        # Chỉ chỉnh phần mái và khung trang trí phía trên; không chạm nền/cây/nước.
        if y < 2.55 or abs(x) > 6.35:
            continue
        span_t = 1.0 - min(abs(x) / 6.15, 1.0)
        height_t = _clamp01((y - 2.55) / 2.65)
        # Hàm tuyến tính theo |x| tạo cạnh gãy thẳng hơn ở hai mái, đồng thời nhấn
        # đỉnh giữa cao hơn giống mái thật trong ảnh tham chiếu.
        delta = (0.10 + 0.24 * height_t) * span_t
        # Hai đầu eave hạ nhẹ để dốc nhìn rõ hơn, nhưng giữ biên tổng thể.
        edge_drop = 0.035 * _clamp01((abs(x) - 4.9) / 1.25) * height_t
        scene.positions[vertex_index] = (x, y + delta - edge_drop, z)


def _add_sloped_band(
    scene: SceneMesh,
    *,
    z: float,
    material: int,
    x_values: list[float],
    bottom_offset: float,
    top_offset: float,
    normal_z: float,
) -> None:
    for x0, x1 in zip(x_values, x_values[1:]):
        y0 = _linear_crown(x0, half=4.98, edge=1.34, center=1.74)
        y1 = _linear_crown(x1, half=4.98, edge=1.34, center=1.74)
        scene.add_quad(
            (x0, y0 + bottom_offset, z),
            (x1, y1 + bottom_offset, z),
            (x1, y1 + top_offset, z),
            (x0, y0 + top_offset, z),
            material,
            normal=(0.0, 0.0, normal_z),
        )


def _add_sloped_rail(scene: SceneMesh, *, z: float, y_offset: float, material: int, normal_z: float) -> None:
    x_values = [-4.82, -3.92, -2.92, -1.93, -0.94, 0.0, 0.94, 1.93, 2.92, 3.92, 4.82]
    for x0, x1 in zip(x_values, x_values[1:]):
        y0 = _linear_crown(x0, half=4.82, edge=1.68, center=2.02) + y_offset
        y1 = _linear_crown(x1, half=4.82, edge=1.68, center=2.02) + y_offset
        scene.add_box_between((x0, y0, z), (x1, y1, z), 0.055, material, width=0.060)


def _add_front_and_back_high_open_railings(scene: SceneMesh) -> None:
    """Thêm hàng rào cao, thoáng ở mặt tiền giống ảnh thật."""
    # Hai mặt được thêm đối xứng để khi xoay GLB vẫn không bị hụt chi tiết.
    for z, normal_z in [(-1.935, -1.0), (1.935, 1.0)]:
        x_values = [-5.02, -4.16, -3.12, -2.08, -1.04, 0.0, 1.04, 2.08, 3.12, 4.16, 5.02]
        # Lan-can đá sáng bên dưới, dốc gãy thẳng theo thân cầu.
        _add_sloped_band(scene, z=z, material=MAT_STONE_LIGHT, x_values=x_values, bottom_offset=-0.11, top_offset=0.22, normal_z=normal_z)
        _add_sloped_band(scene, z=z - 0.010 * normal_z, material=MAT_STONE, x_values=x_values, bottom_offset=-0.20, top_offset=-0.12, normal_z=normal_z)

        # Gờ chỉ đá mảnh để vật liệu nhìn giống code gốc/ảnh thật hơn.
        for yoff in (0.25, -0.13):
            for x0, x1 in zip(x_values, x_values[1:]):
                y0 = _linear_crown(x0, half=4.98, edge=1.34, center=1.74) + yoff
                y1 = _linear_crown(x1, half=4.98, edge=1.34, center=1.74) + yoff
                scene.add_box_between((x0, y0, z + 0.018 * normal_z), (x1, y1, z + 0.018 * normal_z), 0.045, MAT_STONE_LIGHT, width=0.070)

        # Hàng rào gỗ cao và thoáng: nhiều song đứng nhỏ, chừa khe đen rõ.
        for rail_offset in (0.00, 0.36, 0.74):
            _add_sloped_rail(scene, z=z + 0.055 * normal_z, y_offset=rail_offset, material=MAT_WOOD_DARK, normal_z=normal_z)

        baluster_count = 52
        for i in range(baluster_count):
            x = -4.66 + i * (9.32 / (baluster_count - 1))
            base = _linear_crown(x, half=4.82, edge=1.68, center=2.02)
            y0 = base + 0.06
            y1 = base + 0.70
            radius = 0.018 if i % 3 else 0.022
            scene.add_frustum_between((x, y0, z + 0.080 * normal_z), (x, y1, z + 0.080 * normal_z), radius, radius * 0.82, MAT_WOOD_DARK, segments=7, cap_ends=True)

        # Cột chia nhịp lớn, giúp hàng rào cao nhưng không bị rối.
        for x in (-4.80, -3.22, -1.62, 0.0, 1.62, 3.22, 4.80):
            base = _linear_crown(x, half=4.82, edge=1.68, center=2.02)
            scene.add_box((x, base + 0.43, z + 0.095 * normal_z), (0.085, 0.92, 0.095), MAT_WOOD_LIGHT)

        # Bảng tên nhỏ trên lan-can đá ở giữa, giống ảnh chùa thật.
        y_mid = _linear_crown(0.0, half=4.98, edge=1.34, center=1.74) + 0.01
        scene.add_box((0.0, y_mid, z + 0.130 * normal_z), (1.05, 0.105, 0.035), MAT_RED_DARK)
        scene.add_box((0.0, y_mid + 0.002, z + 0.155 * normal_z), (0.84, 0.020, 0.040), MAT_GOLD)


def _add_reference_roof_tile_overlay(scene: SceneMesh) -> None:
    """Phủ thêm hàng ngói dọc sáng/cũ để mái gần ảnh thật hơn."""
    # Hàng ngói mặt trước: chạy từ mép mái lên đỉnh, hơi tụ vào giữa như phối cảnh ảnh gốc.
    count = 58
    xs = [-5.08 + i * (10.16 / (count - 1)) for i in range(count)]
    for i, x in enumerate(xs):
        span_t = 1.0 - min(abs(x) / 5.18, 1.0)
        x_top = x * 0.84
        y_eave = 3.14 + 0.18 * span_t
        y_ridge = 4.62 + 0.38 * span_t
        z_eave = -2.455
        z_ridge = -0.92
        material = MAT_ROOF_TILES[i % len(MAT_ROOF_TILES)]
        radius = 0.025 if i % 2 else 0.032
        scene.add_frustum_between((x, y_eave, z_eave), (x_top, y_ridge, z_ridge), radius, radius * 0.92, material, segments=8, cap_ends=True)
        # Gờ sáng cạnh viên ngói giúp giống mái âm-dương cũ, không còn là mảng nâu phẳng.
        if i % 2 == 0:
            scene.add_frustum_between((x + 0.045, y_eave + 0.015, z_eave - 0.012), (x_top + 0.025, y_ridge + 0.018, z_ridge - 0.010), 0.010, 0.009, MAT_CERAMIC, segments=6, cap_ends=True)

    # Hàng chấm/gờ sứ trắng dưới diềm mái, mô phỏng mép ngói trong ảnh thật.
    dot_count = 34
    for i in range(dot_count):
        x = -5.00 + i * (10.00 / (dot_count - 1))
        span_t = 1.0 - min(abs(x) / 5.00, 1.0)
        y = 3.08 + 0.16 * span_t
        scene.add_frustum((x, y, -2.505), 0.042, 0.038, 0.040, MAT_CERAMIC, segments=10, cap_bottom=True, cap_top=True)

    # V18: bỏ lớp ngói/chống chéo phía sau vì khi nhìn top-view tạo cảm giác nhiều thanh chỉa ra.


def _add_light_stone_material_overlays(scene: SceneMesh) -> None:
    """Thêm mảng/đường chỉ đá sáng để phần dưới không còn xanh xám đậm."""
    # Mặt đá chính phía trước và gờ trên dưới sáng hơn như bản code gốc / ảnh chùa thật.
    z = -1.975
    x_values = [-5.18, -3.66, -2.02, 0.0, 2.02, 3.66, 5.18]
    for x0, x1 in zip(x_values, x_values[1:]):
        y0 = _linear_crown(x0, half=5.18, edge=1.08, center=1.48)
        y1 = _linear_crown(x1, half=5.18, edge=1.08, center=1.48)
        scene.add_quad((x0, y0, z), (x1, y1, z), (x1, y1 + 0.16, z), (x0, y0 + 0.16, z), MAT_STONE_LIGHT, normal=(0.0, 0.0, -1.0))
        scene.add_box_between((x0, y0 + 0.19, z - 0.035), (x1, y1 + 0.19, z - 0.035), 0.055, MAT_STONE_LIGHT, width=0.065)

    # Gờ chân đá nhỏ phía sau, chỉ sửa vật liệu chứ không đè lên kiến trúc chính.
    z_back = 1.975
    for x0, x1 in zip(x_values, x_values[1:]):
        y0 = _linear_crown(x0, half=5.18, edge=1.08, center=1.48)
        y1 = _linear_crown(x1, half=5.18, edge=1.08, center=1.48)
        scene.add_quad((x1, y1, z_back), (x0, y0, z_back), (x0, y0 + 0.14, z_back), (x1, y1 + 0.14, z_back), MAT_STONE_LIGHT, normal=(0.0, 0.0, 1.0))


# -----------------------------------------------------------------------------
# Prompt 6 side red wall + flat land fixes
# -----------------------------------------------------------------------------

def _add_wall_relief_frame(scene: SceneMesh, *, x_face: float, sign: float, z_center: float, y_center: float) -> None:
    """Khung phù điêu nổi trên mặt hông đỏ, mô phỏng chi tiết ảnh tham chiếu."""
    x = x_face + sign * 0.030
    # Khung chữ nhật nổi: dùng các thanh mảnh nằm sát mặt x.
    frame_w_z = 0.92
    frame_h_y = 1.28
    scene.add_box((x, y_center + frame_h_y / 2.0, z_center), (0.060, 0.080, frame_w_z), MAT_RED_DARK)
    scene.add_box((x, y_center - frame_h_y / 2.0, z_center), (0.060, 0.080, frame_w_z), MAT_RED_DARK)
    scene.add_box((x, y_center, z_center - frame_w_z / 2.0), (0.060, frame_h_y, 0.070), MAT_RED_DARK)
    scene.add_box((x, y_center, z_center + frame_w_z / 2.0), (0.060, frame_h_y, 0.070), MAT_RED_DARK)

    # Phù điêu đất nung đơn giản hóa: các nét cong/nổi trong ô khung, cùng màu đỏ sẫm.
    scene.add_frustum_between((x + sign * 0.012, y_center - 0.25, z_center - 0.22), (x + sign * 0.012, y_center + 0.18, z_center + 0.18), 0.060, 0.040, MAT_RED, segments=8, cap_ends=True)
    scene.add_frustum_between((x + sign * 0.014, y_center - 0.16, z_center + 0.10), (x + sign * 0.014, y_center + 0.24, z_center - 0.30), 0.040, 0.030, MAT_RED_DARK, segments=8, cap_ends=True)
    scene.add_frustum_between((x + sign * 0.016, y_center - 0.42, z_center - 0.34), (x + sign * 0.016, y_center - 0.42, z_center + 0.34), 0.030, 0.030, MAT_RED_DARK, segments=8, cap_ends=True)
    for z in (z_center - 0.24, z_center, z_center + 0.24):
        scene.add_frustum((x + sign * 0.018, y_center + 0.42, z), 0.040, 0.030, 0.055, MAT_RED, segments=8, cap_bottom=True, cap_top=True)


def _add_blue_white_side_ceramic_cap(scene: SceneMesh, *, x_center: float, sign: float) -> None:
    """Mép tường hông trắng xanh phía dưới diềm mái như ảnh thật."""
    # Nẹp trắng chạy quanh đỉnh tường đỏ.
    scene.add_box((x_center, 3.135, 0.18), (2.78, 0.135, 5.04), MAT_CERAMIC)
    scene.add_box((x_center, 3.245, -2.36), (2.70, 0.080, 0.135), MAT_CERAMIC)
    scene.add_box((x_center, 3.245, 2.73), (2.70, 0.080, 0.135), MAT_CERAMIC)
    x_face = x_center + sign * 1.395
    scene.add_box((x_face, 3.240, 0.18), (0.065, 0.080, 5.06), MAT_CERAMIC)

    # Chỉ xanh lam mảnh trên nẹp trắng và các nhịp trang trí nhỏ.
    scene.add_box((x_center, 3.312, -2.36), (2.42, 0.030, 0.055), MAT_CERAMIC_BLUE)
    scene.add_box((x_center, 3.312, 2.73), (2.42, 0.030, 0.055), MAT_CERAMIC_BLUE)
    scene.add_box((x_face + sign * 0.010, 3.315, 0.18), (0.034, 0.030, 4.65), MAT_CERAMIC_BLUE)
    for z in (-1.78, -0.88, 0.02, 0.92, 1.82):
        scene.add_frustum((x_face + sign * 0.028, 3.39, z), 0.080, 0.050, 0.050, MAT_CERAMIC_BLUE, segments=9, cap_bottom=True, cap_top=True)
        scene.add_frustum_between((x_face + sign * 0.020, 3.34, z - 0.16), (x_face + sign * 0.020, 3.48, z + 0.16), 0.018, 0.014, MAT_CERAMIC_BLUE, segments=6, cap_ends=True)


def _add_side_door_and_pilasters(scene: SceneMesh, *, x_face: float, sign: float) -> None:
    """Cửa/hốc bên hông và cột đỏ theo ảnh mặt bên."""
    x = x_face + sign * 0.040
    # Hốc tối bên hông nằm dưới mái, chừa cảm giác có lối vào/hiên sâu.
    scene.add_box((x, 1.72, 1.55), (0.070, 1.72, 0.70), MAT_INTERIOR_SHADOW)
    scene.add_box((x + sign * 0.012, 1.72, 1.55), (0.040, 1.52, 0.52), MAT_INTERIOR_SHADOW)
    # Khung cột/viền cửa đỏ sẫm.
    scene.add_box((x + sign * 0.030, 1.72, 1.15), (0.080, 1.86, 0.090), MAT_RED_DARK)
    scene.add_box((x + sign * 0.030, 1.72, 1.95), (0.080, 1.86, 0.090), MAT_RED_DARK)
    scene.add_box((x + sign * 0.030, 2.64, 1.55), (0.080, 0.105, 0.88), MAT_RED_DARK)
    scene.add_box((x + sign * 0.030, 0.81, 1.55), (0.080, 0.105, 0.88), MAT_RED_DARK)
    # Vài chữ/gốm xanh trắng xếp dọc giống mảng chữ bên hông, không dùng text thật để nhẹ file.
    for k in range(6):
        yy = 0.96 + k * 0.26
        scene.add_box((x + sign * 0.055, yy, 0.82), (0.032, 0.095, 0.035), MAT_CERAMIC)
        scene.add_box((x + sign * 0.072, yy, 0.82), (0.034, 0.030, 0.115), MAT_CERAMIC_BLUE)


def _add_prompt6_side_red_wall_land_fixes(scene: SceneMesh) -> None:
    """Thêm hai tường hông đỏ nằm trên đất liền và xóa cảm giác bờ hộp màu nâu."""
    # Phủ lại mặt đất liền thấp ở hai bên bằng lớp lát mỏng sáng hơn, không còn khối hộp cao màu nâu.
    for sign in (-1.0, 1.0):
        x0, x1 = ((-7.92, -5.04) if sign < 0 else (5.04, 7.92))
        # Mặt đất/đường phẳng thấp, phủ trên bank đã hạ để nhìn đúng "nằm trên đất liền".
        scene.add_quad(
            (x0, 0.172, -4.53),
            (x1, 0.172, -4.53),
            (x1, 0.172, 5.23),
            (x0, 0.172, 5.23),
            MAT_PAVING,
            normal=(0.0, 1.0, 0.0),
            uv=((0.0, 0.0), (2.0, 0.0), (2.0, 8.0), (0.0, 8.0)),
        )
        # Kè đá thấp sát mặt trước và hai đầu, thay thế cảm giác khung nâu cao.
        # Các mặt đá được đặt hơi trồi ra ngoài để che toàn bộ mảng đứng màu đất cũ.
        scene.add_box(((x0 + x1) / 2.0, 0.075, -4.56), (abs(x1 - x0), 0.18, 0.085), MAT_STONE)
        scene.add_box(((x0 + x1) / 2.0, 0.075, 5.26), (abs(x1 - x0), 0.18, 0.085), MAT_STONE)
        scene.add_box((x0, 0.075, 0.35), (0.075, 0.18, 9.65), MAT_STONE)
        scene.add_box((x1, 0.075, 0.35), (0.075, 0.18, 9.65), MAT_STONE)
        scene.add_quad((x0, -0.595, -4.676), (x1, -0.595, -4.676), (x1, 0.190, -4.676), (x0, 0.190, -4.676), MAT_STONE, normal=(0.0, 0.0, -1.0), uv=((0.0, 0.0), (2.2, 0.0), (2.2, 1.0), (0.0, 1.0)))
        scene.add_quad((x1, -0.595, 5.356), (x0, -0.595, 5.356), (x0, 0.190, 5.356), (x1, 0.190, 5.356), MAT_STONE, normal=(0.0, 0.0, 1.0), uv=((0.0, 0.0), (2.2, 0.0), (2.2, 1.0), (0.0, 1.0)))
        outer_x = x0 if sign < 0 else x1
        side_normal = -1.0 if sign < 0 else 1.0
        scene.add_quad((outer_x + side_normal * 0.010, -0.595, -4.58), (outer_x + side_normal * 0.010, -0.595, 5.28), (outer_x + side_normal * 0.010, 0.190, 5.28), (outer_x + side_normal * 0.010, 0.190, -4.58), MAT_STONE, normal=(side_normal, 0.0, 0.0), uv=((0.0, 0.0), (8.5, 0.0), (8.5, 1.0), (0.0, 1.0)))
        # Chia ô đá mỏng để phần kè không thành một mảng phẳng.
        for kk in range(4):
            y_line = -0.47 + kk * 0.16
            scene.add_box_between((x0 + 0.08, y_line, -4.688), (x1 - 0.08, y_line, -4.688), 0.012, MAT_STONE_DARK, width=0.020)

        # Khối tường đỏ hông chùa. Hình thật có hai mảng tường đỏ lớn ở hai đầu,
        # đặt trên đất/đường, không phải bờ hộp nâu.
        x_center = sign * 6.50
        scene.add_box((x_center, 1.62, 0.18), (2.72, 2.88, 5.02), MAT_RED)
        # Mảng mặt trước/sau hơi lồi để che triệt để phần bờ nâu cũ khi nhìn chính diện.
        scene.add_box((x_center, 1.63, -2.42), (2.74, 2.70, 0.105), MAT_RED)
        scene.add_box((x_center, 1.63, 2.78), (2.74, 2.70, 0.105), MAT_RED)

        # Chân tường đỏ dày hơn và có bậc như ảnh hông thật.
        scene.add_box((x_center, 0.33, 0.18), (2.92, 0.34, 5.18), MAT_RED_DARK)
        scene.add_box((x_center, 0.56, 0.18), (2.80, 0.16, 5.10), MAT_RED)
        scene.add_box((x_center, 0.22, 0.18), (3.04, 0.10, 5.28), MAT_RED_DARK)

        # Cột/viền đỏ tại các góc để khối hông giống tường chùa thật, không phải hộp trơn.
        for z in (-2.25, 2.58):
            scene.add_box((x_center - sign * 1.20, 1.70, z), (0.135, 2.82, 0.135), MAT_RED_DARK)
            scene.add_box((x_center + sign * 1.20, 1.70, z), (0.135, 2.82, 0.135), MAT_RED_DARK)
        scene.add_box((x_center, 2.98, 0.18), (2.86, 0.18, 5.15), MAT_RED_DARK)

        _add_blue_white_side_ceramic_cap(scene, x_center=x_center, sign=sign)

        # Trang trí mặt ngoài hông: ô phù điêu, cửa/hốc, chữ gốm xanh trắng.
        x_face = x_center + sign * 1.395
        _add_wall_relief_frame(scene, x_face=x_face, sign=sign, z_center=-0.72, y_center=1.62)
        _add_side_door_and_pilasters(scene, x_face=x_face, sign=sign)

        # Mặt trước của hai khối hông có mảng đá trắng bên dưới giống ảnh tổng quan.
        scene.add_box((x_center, 0.92, -2.485), (2.80, 0.18, 0.085), MAT_STONE_LIGHT)
        scene.add_box((x_center, 1.08, -2.495), (2.62, 0.08, 0.080), MAT_STONE)
        scene.add_box((x_center, 2.94, -2.495), (2.50, 0.10, 0.080), MAT_CERAMIC)
        scene.add_box((x_center, 3.03, -2.515), (2.05, 0.035, 0.055), MAT_CERAMIC_BLUE)

        # Một vài vệt loang/miếng vá cùng material đá/đỏ sẫm giúp tường bớt phẳng.
        for j, (zz, yy, ww) in enumerate([(-1.75, 1.20, 0.34), (-0.20, 2.15, 0.42), (0.95, 1.05, 0.26), (2.05, 2.32, 0.30)]):
            scene.add_box((x_face + sign * 0.036, yy, zz), (0.035, 0.035 + 0.008 * (j % 2), ww), MAT_RED_DARK)
            scene.add_box((x_face + sign * 0.038, yy + 0.09, zz + 0.08), (0.030, 0.028, ww * 0.54), MAT_RED)
