# -*- coding: utf-8 -*-
from __future__ import annotations

import math
from pathlib import Path
from random import Random

from glb_forge.scene import SceneMesh, Vec3, v_add, v_cross, v_len, v_mul, v_norm, v_sub

# Scene dùng hệ trục Y-up:
# x = chiều dài cầu; y = chiều cao; z = chiều rộng / trước-sau.
# Mặt trước dễ nhận diện được đặt ở z âm, khối miếu phụ nhô ra ở z dương.

MaterialMap = dict[str, int | list[int]]
TEXTURE_ROOT = Path(__file__).resolve().parents[3] / "assets" / "textures" / "chua_cau_hoi_an"

# Bảng map texture chính dùng cho Prompt 4: giữ tên material quan trọng,
# bổ sung base color, normal và roughness map procedural.
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
    """Tạo mô hình procedural Chùa Cầu Hội An / Cầu Nhật Bản / Lai Viễn Kiều.

    Mục tiêu model:
    - Nhận diện nhanh: cầu có mái ngói cong, trụ đá/vòm dưới cầu, gỗ nâu sẫm,
      mảng cổng đỏ, biển Lai Viễn Kiều, mắt cửa, gốm men lam, tượng khỉ/chó.
    - Tỷ lệ dựa trên tư liệu Prompt 2: phần cầu chính dài-hẹp, khoảng 18-20m
      ngoài thực tế; mô hình dùng tỷ lệ quy đổi 1 đơn vị ~ 1.7m để giữ scene gọn.
    - Một số chi tiết nhỏ như chữ Hán, tượng thờ, lưỡng long được cách điệu low-poly
      vì chưa có bản vẽ/scan chính xác trong đầu vào.
    """
    rng = Random(seed)
    scene = SceneMesh("Chua_Cau_Hoi_An_Lai_Vien_Kieu")
    mat = _make_materials(scene)

    _add_scene_base(scene, mat, rng)
    _add_bridge_foundation(scene, mat, rng)
    _add_bridge_deck_body_and_railings(scene, mat, rng)
    _add_end_gates_and_signage(scene, mat, rng)
    _add_columns_and_frame(scene, mat, rng)
    _add_shrine_wing(scene, mat, rng)
    _add_main_roof(scene, mat, rng)
    _add_ceramics_dragons_and_roof_details(scene, mat, rng)
    _add_guardian_animals(scene, mat, rng)
    _add_hoi_an_context(scene, mat, rng)

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
    # FIX 8: dùng nước dạng opaque để tránh lỗi alpha sorting / nhấp nháy trong
    # các trình xem GLB khi xoay mô hình. Màu/texture nước giữ như cũ, chỉ bỏ
    # trạng thái trong suốt vì trước đó nó chồng lên bờ và gây chớp chớp.
    materials["water"] = scene.add_material(
        "shallow green canal water",
        (0.05, 0.28, 0.30, 1.0),
        metallic=0.0,
        roughness=0.22,
        base_color_texture=water_tex,
        normal_texture=water_nrm,
        normal_scale=0.20,
        roughness_texture=water_rgh,
    )
    # Vật liệu riêng cho mặt đứng/mặt đáy của phần kênh nước.
    # Dùng alpha 1.0 để che hẳn lớp đế xám phía sau và tránh z-sorting ở viewer GLB.
    materials["water_edge"] = scene.add_material(
        "opaque canal water vertical edge",
        (0.05, 0.28, 0.30, 1.0),
        metallic=0.0,
        roughness=0.24,
        base_color_texture=water_tex,
        normal_texture=water_nrm,
        normal_scale=0.18,
        roughness_texture=water_rgh,
    )

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


def _mat(materials: MaterialMap, name: str) -> int:
    value = materials[name]
    if isinstance(value, list):
        raise TypeError(f"Material {name!r} là list, không phải int")
    return value


def _mat_list(materials: MaterialMap, name: str) -> list[int]:
    value = materials[name]
    if not isinstance(value, list):
        raise TypeError(f"Material {name!r} là int, không phải list")
    return value


def _rand(rng: Random, lo: float, hi: float) -> float:
    return rng.uniform(lo, hi)


# -----------------------------------------------------------------------------
# Nền cảnh quan, kênh nước và bờ đá
# -----------------------------------------------------------------------------


def _add_scene_base(scene: SceneMesh, mat: MaterialMap, rng: Random) -> None:
    base = _mat(mat, "display_base")
    earth = _mat(mat, "earth")
    paving = _mat(mat, "paving")
    water = _mat(mat, "water")
    water_edge = _mat(mat, "water_edge")
    stone = _mat(mat, "stone")
    moss = _mat(mat, "moss")

    # Đế sa bàn chính: giữ nguyên kích thước tổng thể của các bản trước.
    # FIX 8: xử lý hiện tượng "chớp chớp" bằng cách tách các mặt nước/đất ra
    # thành những vùng hình học KHÔNG chồng mặt phẳng lên nhau. Ở bản trước,
    # lớp nước có overlap nhẹ vào bờ để che khe, dễ gây z-fighting khi kéo/xoay model.
    scene_width = 15.80
    scene_depth = 9.80
    scene_center_z = 0.35
    x_min = -scene_width / 2.0
    x_max = scene_width / 2.0
    z_min = scene_center_z - scene_depth / 2.0
    z_max = scene_center_z + scene_depth / 2.0

    scene.add_box((0.0, -0.36, scene_center_z), (scene_width, 0.36, scene_depth), base)
    scene.add_box((0.0, -0.12, scene_center_z), (15.2, 0.12, 9.2), earth)

    # Vùng kênh và bờ: bờ đất/lát hai bên, kênh nước ở giữa.
    canal_width = 11.60
    canal_half = canal_width / 2.0
    canal_depth = 9.35
    canal_center_z = scene_center_z

    # Seam được giấu dưới kè đá: đất và nước không overlap nhau, nhưng nhìn vẫn kín.
    water_x_min = -canal_half + 0.080
    water_x_max = canal_half - 0.080
    left_bank_max = -canal_half + 0.020
    right_bank_min = canal_half - 0.020

    # Top hơi tràn ra ngoài mép sa bàn một chút để không lộ nền xám khi nhìn xiên.
    # Phần tràn này nằm theo hướng ngoài, không phải nước chồng lên đất.
    surface_outset = 0.035
    surface_z_min = z_min - surface_outset
    surface_z_max = z_max + surface_outset
    surface_depth = surface_z_max - surface_z_min
    surface_center_z = (surface_z_min + surface_z_max) / 2.0

    # Mặt nước là quad riêng, không dùng box nước dày chồng vào bờ.
    # Đây là điểm chính để hết nhấp nháy/z-fighting ở ranh đất-nước.
    water_y = 0.096
    water_uv_u = max(1.0, water_x_max - water_x_min)
    water_uv_v = max(1.0, surface_z_max - surface_z_min)
    scene.add_quad(
        (water_x_min, water_y, surface_z_min),
        (water_x_max, water_y, surface_z_min),
        (water_x_max, water_y, surface_z_max),
        (water_x_min, water_y, surface_z_max),
        water,
        normal=(0.0, 1.0, 0.0),
        uv=((0.0, 0.0), (water_uv_u, 0.0), (water_uv_u, water_uv_v), (0.0, water_uv_v)),
    )

    # Hai bờ đất/lát là các khối riêng, dừng trước vùng nước và được kè đá che seam.
    bank_top = 0.145
    bank_bottom = 0.018
    bank_y = (bank_top + bank_bottom) / 2.0
    bank_h = bank_top - bank_bottom
    left_bank_center_x = (x_min - surface_outset + left_bank_max) / 2.0
    left_bank_w = left_bank_max - (x_min - surface_outset)
    right_bank_center_x = (right_bank_min + x_max + surface_outset) / 2.0
    right_bank_w = (x_max + surface_outset) - right_bank_min
    scene.add_box((left_bank_center_x, bank_y, surface_center_z), (left_bank_w, bank_h, surface_depth), paving)
    scene.add_box((right_bank_center_x, bank_y, surface_center_z), (right_bank_w, bank_h, surface_depth), paving)

    # Lớp đất nâu dưới mặt lát cũng tách rời khỏi nước.
    earth_top = bank_bottom
    earth_bottom = -0.055
    earth_y = (earth_top + earth_bottom) / 2.0
    earth_h = earth_top - earth_bottom
    scene.add_box((left_bank_center_x, earth_y, surface_center_z), (left_bank_w, earth_h, surface_depth), earth)
    scene.add_box((right_bank_center_x, earth_y, surface_center_z), (right_bank_w, earth_h, surface_depth), earth)

    # Hai bờ kè đá chạy dọc sát mép kênh, che hoàn toàn khe nhỏ giữa đất và nước.
    for x_edge in (-canal_half, canal_half):
        scene.add_box((x_edge, 0.075, canal_center_z), (0.24, 0.18, canal_depth + 0.10), stone)
        scene.add_box((x_edge * 0.998, 0.18, -1.10), (0.07, 0.035, 3.05), moss)

    # Skin vật liệu cho thành dày và đáy: đặt lệch ra ngoài đủ xa để không co-planar
    # với mặt đế xám. Nhờ đó khi di chuyển camera sẽ không còn nhấp nháy giữa 2 material.
    edge_y_min = -0.575
    edge_y_max_land = bank_top
    edge_y_max_water = water_y
    edge_outset = 0.060
    bottom_y = edge_y_min - 0.010

    def _vertical_z_face(x0: float, x1: float, z_face: float, y_top: float, material: int, outward: float) -> None:
        if x1 <= x0:
            return
        width = max(1.0, abs(x1 - x0))
        height = max(1.0, y_top - edge_y_min)
        scene.add_quad(
            (x0, edge_y_min, z_face),
            (x1, edge_y_min, z_face),
            (x1, y_top, z_face),
            (x0, y_top, z_face),
            material,
            normal=(0.0, 0.0, outward),
            uv=((0.0, 0.0), (width, 0.0), (width, height), (0.0, height)),
        )

    def _vertical_x_face(x_face: float, z0: float, z1: float, material: int, outward: float) -> None:
        if z1 <= z0:
            return
        depth = max(1.0, abs(z1 - z0))
        height = max(1.0, edge_y_max_land - edge_y_min)
        scene.add_quad(
            (x_face, edge_y_min, z0),
            (x_face, edge_y_min, z1),
            (x_face, edge_y_max_land, z1),
            (x_face, edge_y_max_land, z0),
            material,
            normal=(outward, 0.0, 0.0),
            uv=((0.0, 0.0), (depth, 0.0), (depth, height), (0.0, height)),
        )

    front_z = z_min - edge_outset
    back_z = z_max + edge_outset
    for z_face, outward in ((front_z, -1.0), (back_z, 1.0)):
        # 4 góc là đất/lát, đoạn giữa dưới kênh là nước, các đoạn chỉ chạm mép nhau.
        # Hai dải cực nhỏ giữa đất và nước dùng vật liệu kè đá để lấp kín seam,
        # tránh vừa hở xám vừa không tạo mặt trùng nhau.
        _vertical_z_face(x_min - surface_outset, left_bank_max, z_face, edge_y_max_land, paving, outward)
        _vertical_z_face(left_bank_max, water_x_min, z_face, edge_y_max_land, stone, outward)
        _vertical_z_face(water_x_min, water_x_max, z_face, edge_y_max_water, water_edge, outward)
        _vertical_z_face(water_x_max, right_bank_min, z_face, edge_y_max_land, stone, outward)
        _vertical_z_face(right_bank_min, x_max + surface_outset, z_face, edge_y_max_land, paving, outward)

    # Mép trái/phải là bờ đất/liền full.
    _vertical_x_face(x_min - edge_outset, surface_z_min, surface_z_max, paving, -1.0)
    _vertical_x_face(x_max + edge_outset, surface_z_min, surface_z_max, paving, 1.0)

    # Mặt đáy đồng bộ vật liệu: bờ = đất/lát, lòng kênh = nước.
    scene.add_quad(
        (x_min - surface_outset, bottom_y, surface_z_min),
        (left_bank_max, bottom_y, surface_z_min),
        (left_bank_max, bottom_y, surface_z_max),
        (x_min - surface_outset, bottom_y, surface_z_max),
        paving,
        normal=(0.0, -1.0, 0.0),
        uv=((0.0, 0.0), (left_bank_w, 0.0), (left_bank_w, surface_depth), (0.0, surface_depth)),
    )
    scene.add_quad(
        (left_bank_max, bottom_y, surface_z_min),
        (water_x_min, bottom_y, surface_z_min),
        (water_x_min, bottom_y, surface_z_max),
        (left_bank_max, bottom_y, surface_z_max),
        stone,
        normal=(0.0, -1.0, 0.0),
        uv=((0.0, 0.0), (max(1.0, water_x_min - left_bank_max), 0.0), (max(1.0, water_x_min - left_bank_max), surface_depth), (0.0, surface_depth)),
    )
    scene.add_quad(
        (water_x_min, bottom_y, surface_z_min),
        (water_x_max, bottom_y, surface_z_min),
        (water_x_max, bottom_y, surface_z_max),
        (water_x_min, bottom_y, surface_z_max),
        water_edge,
        normal=(0.0, -1.0, 0.0),
        uv=((0.0, 0.0), (water_uv_u, 0.0), (water_uv_u, water_uv_v), (0.0, water_uv_v)),
    )
    scene.add_quad(
        (water_x_max, bottom_y, surface_z_min),
        (right_bank_min, bottom_y, surface_z_min),
        (right_bank_min, bottom_y, surface_z_max),
        (water_x_max, bottom_y, surface_z_max),
        stone,
        normal=(0.0, -1.0, 0.0),
        uv=((0.0, 0.0), (max(1.0, right_bank_min - water_x_max), 0.0), (max(1.0, right_bank_min - water_x_max), surface_depth), (0.0, surface_depth)),
    )
    scene.add_quad(
        (right_bank_min, bottom_y, surface_z_min),
        (x_max + surface_outset, bottom_y, surface_z_min),
        (x_max + surface_outset, bottom_y, surface_z_max),
        (right_bank_min, bottom_y, surface_z_max),
        paving,
        normal=(0.0, -1.0, 0.0),
        uv=((0.0, 0.0), (right_bank_w, 0.0), (right_bank_w, surface_depth), (0.0, surface_depth)),
    )

    # FIX 9: nâng hai bờ đất liền ở hai đầu cầu.
    # Ảnh thật có phần bờ/đường dẫn lên cầu cao hơn mặt nước khá nhiều; vì vậy
    # chỉ đắp thêm khối đất/lát ở hai bên ngoài kênh, còn mặt nước trung tâm giữ
    # nguyên cao độ và kích thước để không ảnh hưởng những lần fix trước.
    # FIX 10: hai bờ đất hai bên giữ cao nhưng làm MẶT PHẲNG, không còn dốc xuống.
    # Mặt nước trung tâm vẫn giữ nguyên cao độ như bản trước.
    raised_flat_y = 0.82
    raised_bottom_y = earth_bottom

    def _add_raised_bank_approach(x0: float, x1: float, y_top: float) -> None:
        if x1 <= x0:
            return
        top_depth = surface_depth
        top_width = x1 - x0
        # Mặt lát trên cùng là mặt phẳng ngang, không nghiêng trái/phải.
        scene.add_quad(
            (x0, y_top, surface_z_min),
            (x1, y_top, surface_z_min),
            (x1, y_top, surface_z_max),
            (x0, y_top, surface_z_max),
            paving,
            normal=(0.0, 1.0, 0.0),
            uv=((0.0, 0.0), (top_width, 0.0), (top_width, top_depth), (0.0, top_depth)),
        )
        # Mặt đứng trước/sau đồng bộ là đất/lát nâu với mép trên phẳng ngang.
        for z_face, outward in ((front_z - 0.006, -1.0), (back_z + 0.006, 1.0)):
            scene.add_quad(
                (x0, raised_bottom_y, z_face),
                (x1, raised_bottom_y, z_face),
                (x1, y_top, z_face),
                (x0, y_top, z_face),
                paving,
                normal=(0.0, 0.0, outward),
                uv=((0.0, 0.0), (top_width, 0.0), (top_width, max(1.0, y_top - raised_bottom_y)), (0.0, max(1.0, y_top - raised_bottom_y))),
            )
        # Mặt ngoài theo trục X và mặt giáp kênh: dùng paving để nhìn như tường/bờ kè lát.
        scene.add_quad(
            (x0, raised_bottom_y, surface_z_min),
            (x0, raised_bottom_y, surface_z_max),
            (x0, y_top, surface_z_max),
            (x0, y_top, surface_z_min),
            paving,
            normal=(-1.0 if x0 < 0.0 else 1.0, 0.0, 0.0),
            uv=((0.0, 0.0), (top_depth, 0.0), (top_depth, max(1.0, y_top - raised_bottom_y)), (0.0, max(1.0, y_top - raised_bottom_y))),
        )
        scene.add_quad(
            (x1, raised_bottom_y, surface_z_min),
            (x1, raised_bottom_y, surface_z_max),
            (x1, y_top, surface_z_max),
            (x1, y_top, surface_z_min),
            paving,
            normal=(1.0 if x1 > 0.0 else -1.0, 0.0, 0.0),
            uv=((0.0, 0.0), (top_depth, 0.0), (top_depth, max(1.0, y_top - raised_bottom_y)), (0.0, max(1.0, y_top - raised_bottom_y))),
        )
        # Gân lát mỏng trên mặt phẳng, nâng nhẹ để tránh z-fighting.
        for k in range(5):
            z_line = surface_z_min + (k + 1) * top_depth / 6.0
            scene.add_box_between(
                (x0 + 0.12, y_top + 0.018, z_line),
                (x1 - 0.12, y_top + 0.018, z_line),
                0.018,
                earth,
                width=0.030,
                up_hint=(0.0, 1.0, 0.0),
            )

    _add_raised_bank_approach(x_min - surface_outset, left_bank_max - 0.010, raised_flat_y)
    _add_raised_bank_approach(right_bank_min + 0.010, x_max + surface_outset, raised_flat_y)

    # Các mảng lát phụ trên bờ giữ lại để bề mặt không bị phẳng quá.
    for x, w in ((left_bank_center_x, left_bank_w), (right_bank_center_x, right_bank_w)):
        for z in (-4.25, -2.05, 0.15, 2.35, 4.45):
            scene.add_box((x, 0.172, z), (min(1.85, w * 0.84), 0.034, 0.34), paving)

    # Mảng rêu lác đác chỉ đặt sát bờ kè, tránh nổi giữa mặt nước.
    for _ in range(22):
        edge = rng.choice([-canal_half, canal_half])
        x = edge + _rand(rng, -0.035, 0.035)
        z = _rand(rng, -4.20, 3.45)
        scene.add_box((x, 0.11, z), (_rand(rng, 0.04, 0.08), 0.018, _rand(rng, 0.16, 0.34)), moss)


# -----------------------------------------------------------------------------
# Móng/trụ đá và các nhịp/vòm dưới cầu
# -----------------------------------------------------------------------------


def _add_bridge_foundation(scene: SceneMesh, mat: MaterialMap, rng: Random) -> None:
    stone = _mat(mat, "stone")
    stone_dark = _mat(mat, "stone_dark")
    stone_light = _mat(mat, "stone_light")
    moss = _mat(mat, "moss")
    water = _mat(mat, "water")

    length = 11.1
    width = 3.38
    y_base = 0.08
    # FIX 10: tăng nhẹ cao độ dầm/khung đá dưới thân cầu.
    y_top = 1.04

    # Hai dầm đá dài trước/sau; các nhịp tối nằm sau vòm để nhìn như khoảng rỗng.
    for z in (-width / 2.0, width / 2.0):
        scene.add_box((0.0, y_base + 0.05, z), (length + 0.30, 0.14, 0.22), stone)
        scene.add_box((0.0, y_top, z), (length + 0.44, 0.26, 0.30), stone)
        scene.add_box((-length / 2.0, 0.54, z), (0.38, 0.96, 0.32), stone)
        scene.add_box((length / 2.0, 0.54, z), (0.38, 0.96, 0.32), stone)

        # 5 nhịp: mở tối + vòm đá sáng; đây là chi tiết nhận diện dưới cầu.
        span_centers = [-4.32, -2.16, 0.0, 2.16, 4.32]
        for c in span_centers:
            opening_z = z + (0.018 if z < 0 else -0.018)
            # FIX 2: cả 5 nhịp đều nhìn xuống dòng nước, đúng như ảnh gốc
            # Chùa Cầu bắc qua kênh. Lớp tối phía trên chỉ là bóng sâu bên trong vòm,
            # không còn biến hai ô ngoài thành đất liền.
            scene.add_box((c, 0.40, opening_z), (1.46, 0.38, 0.036), water)
            scene.add_box((c, 0.70, opening_z), (1.46, 0.15, 0.030), stone_dark)
            _add_arch_trim(scene, center_x=c, z=z + (0.055 if z < 0 else -0.055), width=1.52, base_y=0.25, arch_y=0.94, material=stone_light, front=(z < 0))

        # Trụ đứng chia nhịp.
        for x in [-3.24, -1.08, 1.08, 3.24]:
            scene.add_box((x, 0.55, z), (0.34, 0.96, 0.33), stone)

    # Dầm ngang đá đầu cầu nối hai mặt trước-sau.
    for x in (-5.55, 5.55):
        scene.add_box((x, 0.56, 0.0), (0.36, 0.96, width + 0.18), stone)

    # FIX 9: phủ thêm mặt tiền đá cong/cao hơn để phần dưới cầu giống ảnh thật hơn.
    _add_crowned_foundation_overlay(scene, mat)

    # Rêu nhỏ quanh chân đá.
    for _ in range(28):
        x = _rand(rng, -5.0, 5.0)
        z = rng.choice([-1.83, 1.83]) + _rand(rng, -0.05, 0.05)
        y = _rand(rng, 0.17, 0.95)
        scene.add_box((x, y, z), (_rand(rng, 0.05, 0.17), _rand(rng, 0.025, 0.06), _rand(rng, 0.018, 0.05)), moss)



def _foundation_crown_y(x: float) -> float:
    """Cao độ vòm/crown của mặt đá dưới cầu ở mặt tiền.

    Hai đầu thấp, lên cao dần ở giữa rồi hạ xuống, gợi dáng cầu cong trong ảnh
    thật nhưng không di chuyển mái/thân gỗ để giữ những phần đã ổn định.
    """
    half = 5.72
    # FIX 10: nâng khung đá/vòm thêm một chút để phần chân cầu cao và gần ảnh thật hơn.
    edge_y = 1.08
    peak_y = 1.42
    t = min(1.0, abs(x) / half)
    return edge_y + (peak_y - edge_y) * (1.0 - t ** 1.75)


def _add_crowned_foundation_overlay(scene: SceneMesh, mat: MaterialMap) -> None:
    stone = _mat(mat, "stone")
    stone_light = _mat(mat, "stone_light")
    stone_dark = _mat(mat, "stone_dark")
    water = _mat(mat, "water")
    moss = _mat(mat, "moss")

    length = 11.38
    half = length / 2.0
    width = 3.38
    band_bottom = 0.70
    cap_depth = 0.27
    xsegs = 34
    span_centers = [-4.32, -2.16, 0.0, 2.16, 4.32]

    # Mặt tiền/mặt hậu có dải đá cong: thấp ở hai đầu, cao nhất ở khoảng giữa.
    for z_outer, outward in ((-width / 2.0 - 0.075, -1.0), (width / 2.0 + 0.075, 1.0)):
        z_inner = z_outer + (cap_depth if outward < 0.0 else -cap_depth)
        for ix in range(xsegs):
            x0 = -half + length * ix / xsegs
            x1 = -half + length * (ix + 1) / xsegs
            y0 = _foundation_crown_y(x0)
            y1 = _foundation_crown_y(x1)
            uvx0 = ix / 2.4
            uvx1 = (ix + 1) / 2.4
            # Dải đứng bằng đá che đường thẳng ngang cũ và tạo silhouette cầu cong.
            scene.add_quad(
                (x0, band_bottom, z_outer),
                (x1, band_bottom, z_outer),
                (x1, y1, z_outer),
                (x0, y0, z_outer),
                stone,
                normal=(0.0, 0.0, outward),
                uv=((uvx0, 0.0), (uvx1, 0.0), (uvx1, 1.15), (uvx0, 1.15)),
            )
            # Mặt top mỏng đi theo độ dốc, để khi nhìn từ trên thấy đường lên giữa rồi xuống.
            scene.add_quad(
                (x0, y0 + 0.010, z_outer),
                (x1, y1 + 0.010, z_outer),
                (x1, y1 + 0.010, z_inner),
                (x0, y0 + 0.010, z_inner),
                stone_light,
                normal=(0.0, 1.0, 0.0),
                uv=((uvx0, 0.0), (uvx1, 0.0), (uvx1, cap_depth), (uvx0, cap_depth)),
            )

        # Viền đá sáng chạy theo đường crown giúp đọc rõ độ dốc của cầu.
        pts = [(-half + length * i / xsegs, _foundation_crown_y(-half + length * i / xsegs) + 0.035, z_outer + 0.010 * outward) for i in range(xsegs + 1)]
        for p0, p1 in zip(pts, pts[1:]):
            scene.add_box_between(p0, p1, 0.042, stone_light, width=0.070, up_hint=(0.0, 0.0, outward))

        # Làm lại hàng vòm ở phía ngoài để không bị mặt cong che mất chi tiết cũ.
        # Trung tâm cao hơn nhẹ, hai bên thấp hơn, giống cảm giác nhịp cầu thật.
        trim_z = z_outer + 0.055 * outward
        for c in span_centers:
            # FIX 10: nâng đỉnh vòm/khung thêm một chút, nhưng vẫn nằm dưới dải đá cong.
            arch_top = 1.05 + 0.115 * (1.0 - min(1.0, abs(c) / 4.45))
            _add_arch_trim(scene, center_x=c, z=trim_z, width=1.48, base_y=0.24, arch_y=arch_top, material=stone_light, front=(outward < 0.0))
            # Mảng nước/tối phía sau từng vòm, lùi vào trong nên không z-fight với viền.
            scene.add_box((c, 0.41, z_outer - 0.020 * outward), (1.26, 0.36, 0.030), water)
            scene.add_box((c, arch_top - 0.10, z_outer - 0.024 * outward), (1.24, 0.12, 0.028), stone_dark)

        # Trụ đá nổi ở ranh các nhịp, cao lên theo đường crown.
        for x in [-5.55, -3.24, -1.08, 1.08, 3.24, 5.55]:
            top = _foundation_crown_y(x) - 0.055
            bottom = 0.17
            if top > bottom:
                scene.add_box((x, (top + bottom) / 2.0, z_outer + 0.028 * outward), (0.30, top - bottom, 0.105), stone)
                scene.add_box((x, top + 0.025, z_outer + 0.034 * outward), (0.38, 0.050, 0.120), stone_light)

        # Rêu mỏng trên mép trên và chân vòm, giữ cảm giác đá cũ ẩm nhưng không chồng vào nước.
        for x in [-4.95, -3.60, -2.25, -0.85, 0.85, 2.25, 3.60, 4.95]:
            y = _foundation_crown_y(x) - 0.045
            scene.add_box((x, y, z_outer + 0.072 * outward), (0.22, 0.026, 0.028), moss)


def _add_arch_trim(scene: SceneMesh, center_x: float, z: float, width: float, base_y: float, arch_y: float, material: int, *, front: bool) -> None:
    radius_x = width / 2.0
    radius_y = arch_y - base_y
    # Hai jamb đứng.
    scene.add_box((center_x - radius_x, (base_y + arch_y) / 2.0, z), (0.075, arch_y - base_y, 0.075), material)
    scene.add_box((center_x + radius_x, (base_y + arch_y) / 2.0, z), (0.075, arch_y - base_y, 0.075), material)
    # Bán nguyệt vòm ghép từ các thanh ngắn.
    pts: list[Vec3] = []
    for i in range(15):
        theta = math.pi * i / 14.0
        x = center_x + math.cos(theta) * radius_x
        y = base_y + math.sin(theta) * radius_y
        pts.append((x, y, z))
    for p0, p1 in zip(pts, pts[1:]):
        scene.add_box_between(p0, p1, 0.065, material, width=0.082, up_hint=(0.0, 0.0, 1.0 if front else -1.0))


# -----------------------------------------------------------------------------
# Thân cầu gỗ, lan can, cổng đỏ
# -----------------------------------------------------------------------------


def _add_bridge_deck_body_and_railings(scene: SceneMesh, mat: MaterialMap, rng: Random) -> None:
    wood_dark = _mat(mat, "wood_dark")
    wood = _mat(mat, "wood")
    wood_light = _mat(mat, "wood_light")
    red_dark = _mat(mat, "red_dark")
    shadow = _mat(mat, "interior_shadow")

    length = 10.95
    width = 3.08
    deck_y = 1.02

    scene.add_box((0.0, deck_y, 0.0), (length, 0.24, width), wood_dark)
    # Ván sàn theo từng tấm hẹp.
    for z in [-1.20, -0.80, -0.40, 0.0, 0.40, 0.80, 1.20]:
        scene.add_box((0.0, deck_y + 0.145, z), (length - 0.40, 0.035, 0.035), wood_light)

    # Mảng vách nửa kín hai bên kiểu cầu có mái: dưới đặc, trên lan can song gỗ.
    for z in (-1.47, 1.47):
        scene.add_box((0.0, 1.34, z), (10.45, 0.42, 0.14), red_dark)
        scene.add_box((0.0, 1.67, z), (10.45, 0.10, 0.18), wood)
        scene.add_box((0.0, 2.03, z), (10.45, 0.10, 0.18), wood_dark)
        # Thanh đứng lan can lặp đều.
        for i in range(23):
            x = -5.05 + i * (10.10 / 22.0)
            scene.add_box((x, 1.84, z), (0.055, 0.42, 0.08), wood)

    # Lòng cầu tối dưới mái.
    scene.add_box((0.0, 1.74, 0.0), (10.0, 1.25, 2.36), shadow)


def _add_end_gates_and_signage(scene: SceneMesh, mat: MaterialMap, rng: Random) -> None:
    red = _mat(mat, "red")
    red_dark = _mat(mat, "red_dark")
    black = _mat(mat, "black")
    gold = _mat(mat, "gold")
    wood_dark = _mat(mat, "wood_dark")

    # Hai cổng đầu cầu, khung đỏ sơn son với lối vào tối.
    for x, sign in [(-5.60, -1.0), (5.60, 1.0)]:
        scene.add_box((x, 1.77, -1.22), (0.34, 1.68, 0.28), red)
        scene.add_box((x, 1.77, 1.22), (0.34, 1.68, 0.28), red)
        scene.add_box((x, 2.58, 0.0), (0.36, 0.42, 2.72), red)
        scene.add_box((x, 1.55, 0.0), (0.38, 1.22, 1.38), black)
        scene.add_box((x - 0.02 * sign, 0.94, 0.0), (0.40, 0.15, 2.75), wood_dark)
        # Bảng phụ ở đầu cầu, cách điệu chữ vàng.
        scene.add_box((x - 0.20 * sign, 2.83, 0.0), (0.055, 0.30, 1.30), red_dark)
        for j in range(5):
            scene.add_box((x - 0.235 * sign, 2.77 + 0.045 * (j % 2), -0.48 + j * 0.24), (0.035, 0.035, 0.15), gold)

    # Biển chính đặt ở mặt trước z âm để người xem nhận ra "Lai Viễn Kiều".
    scene.add_box((0.0, 2.28, -1.72), (2.92, 0.46, 0.075), red_dark)
    scene.add_box((0.0, 2.28, -1.765), (2.74, 0.34, 0.065), red)
    # Mặt trước z âm bị lật trái/phải trong nhiều trình xem 3D, nên đảo X để
    # người xem đọc thuận chiều.  Lớp phụ phía sau giữ chiều X thường để khi xoay
    # model vẫn tránh cảm giác chữ bị ngược.
    _add_block_text_z(scene, "LAI VIỄN KIỀU", center=(0.0, 2.19, -1.82), char_height=0.23, material=gold, depth=0.045, mirror_x=True)
    _add_block_text_z(scene, "LAI VIỄN KIỀU", center=(0.0, 2.19, -1.635), char_height=0.23, material=gold, depth=0.040)

    # Hai mắt cửa tròn ở dưới bảng biển.
    for x in (-0.66, 0.66):
        scene.add_frustum_between((x, 1.88, -1.84), (x, 1.88, -1.75), 0.095, 0.095, red_dark, segments=24)
        scene.add_frustum_between((x, 1.88, -1.855), (x, 1.88, -1.795), 0.047, 0.047, gold, segments=18)


_LETTERS: dict[str, list[str]] = {
    "A": ["01110", "10001", "10001", "11111", "10001", "10001", "10001"],
    "E": ["11111", "10000", "10000", "11110", "10000", "10000", "11111"],
    "I": ["111", "010", "010", "010", "010", "010", "111"],
    "K": ["10001", "10010", "10100", "11000", "10100", "10010", "10001"],
    "L": ["10000", "10000", "10000", "10000", "10000", "10000", "11111"],
    "N": ["10001", "11001", "10101", "10011", "10001", "10001", "10001"],
    "U": ["10001", "10001", "10001", "10001", "10001", "10001", "01110"],
    "V": ["10001", "10001", "10001", "10001", "10001", "01010", "00100"],
    " ": ["0", "0", "0", "0", "0", "0", "0"],
}

# Các chữ Việt dùng trên biển “LAI VIỄN KIỀU”.  Glyph vẫn là khối pixel
# để GLB thuần Python không phụ thuộc font bên ngoài; dấu được ghép bằng thanh nhỏ.
_VIETNAMESE_LETTER_INFO: dict[str, tuple[str, tuple[str, ...]]] = {
    "Ê": ("E", ("circumflex",)),
    "Ề": ("E", ("circumflex", "grave")),
    "Ể": ("E", ("circumflex", "hook")),
    "Ễ": ("E", ("circumflex", "tilde")),
    "Ệ": ("E", ("circumflex", "dot_below")),
}


def _letter_info(ch: str) -> tuple[str, tuple[str, ...]]:
    upper = ch.upper()
    if upper in _VIETNAMESE_LETTER_INFO:
        return _VIETNAMESE_LETTER_INFO[upper]
    return (upper if upper in _LETTERS else " ", ())


def _add_accent_segment(scene: SceneMesh, p0: Vec3, p1: Vec3, material: int, *, depth: float, width: float) -> None:
    # up_hint theo Z để đoạn dấu nằm trên mặt bảng X-Y và có bề dày theo trục Z.
    scene.add_box_between(p0, p1, depth, material, width=width, up_hint=(0.0, 0.0, 1.0))


def _add_text_diacritics_z(
    scene: SceneMesh,
    *,
    base_char: str,
    accents: tuple[str, ...],
    char_x: float,
    char_y: float,
    char_width: float,
    char_height: float,
    center_z: float,
    scene_center_x: float,
    pix: float,
    material: int,
    depth: float,
    mirror_x: bool,
) -> None:
    if not accents:
        return

    def pt(x: float, y: float) -> Vec3:
        if mirror_x:
            x = scene_center_x - (x - scene_center_x)
        return (x, y, center_z)

    def add_segment(x0: float, y0: float, x1: float, y1: float, w: float = 0.42) -> None:
        _add_accent_segment(scene, pt(x0, y0), pt(x1, y1), material, depth=depth, width=pix * w)

    mid = char_x + char_width / 2.0
    top = char_y + char_height
    # Dấu mũ của Ê/Ề/Ễ, đặt đủ cao để nhìn rõ nhưng vẫn nằm trong khung biển.
    if "circumflex" in accents:
        y_low = top + pix * 0.18
        y_high = top + pix * 0.98
        add_segment(mid - pix * 1.18, y_low, mid, y_high, 0.46)
        add_segment(mid, y_high, mid + pix * 1.18, y_low, 0.46)

    # Dấu phụ phía trên dấu mũ.  Các dấu này được vẽ đơn giản bằng khối nhỏ,
    # ưu tiên dễ nhận ra trong GLB low-poly.
    upper_base = top + pix * 1.30
    if "grave" in accents:
        add_segment(mid + pix * 0.78, upper_base + pix * 0.82, mid - pix * 0.18, upper_base + pix * 0.18, 0.42)
    if "tilde" in accents:
        add_segment(mid - pix * 1.18, upper_base + pix * 0.22, mid - pix * 0.42, upper_base + pix * 0.55, 0.34)
        add_segment(mid - pix * 0.42, upper_base + pix * 0.55, mid + pix * 0.35, upper_base + pix * 0.20, 0.34)
        add_segment(mid + pix * 0.35, upper_base + pix * 0.20, mid + pix * 1.14, upper_base + pix * 0.52, 0.34)
    if "hook" in accents:
        add_segment(mid - pix * 0.25, upper_base + pix * 0.70, mid + pix * 0.45, upper_base + pix * 0.70, 0.34)
        add_segment(mid + pix * 0.45, upper_base + pix * 0.70, mid + pix * 0.12, upper_base + pix * 0.24, 0.34)
    if "dot_below" in accents:
        scene.add_box(pt(mid, char_y - pix * 0.52), (pix * 0.42, pix * 0.42, depth), material)


def _add_block_text_z(
    scene: SceneMesh,
    text: str,
    center: Vec3,
    char_height: float,
    material: int,
    *,
    depth: float,
    mirror_x: bool = False,
) -> None:
    """Chữ Latin/Vietnamese dạng khối trên mặt phẳng Z.

    mirror_x=True đảo hình học theo trục X; dùng cho mặt trước z âm để trong
    trình xem 3D dòng “LAI VIỄN KIỀU” đọc thuận chiều, không bị lật trái/phải.
    """
    rows = 7
    pix = char_height / rows
    spacing = pix * 1.25
    infos = [_letter_info(ch) for ch in text]
    widths = [len(_LETTERS[base][0]) * pix for base, _ in infos]
    total = sum(widths) + spacing * (len(text) - 1)
    x0 = center[0] - total / 2.0
    y0 = center[1] - char_height / 2.0
    x = x0

    def mirrored_x(value: float) -> float:
        return center[0] - (value - center[0]) if mirror_x else value

    for (base_char, accents), width in zip(infos, widths):
        pattern = _LETTERS[base_char]
        for r, row in enumerate(pattern):
            for c, value in enumerate(row):
                if value == "1":
                    cx = mirrored_x(x + c * pix + pix / 2.0)
                    cy = y0 + (rows - 1 - r) * pix + pix / 2.0
                    scene.add_box((cx, cy, center[2]), (pix * 0.72, pix * 0.72, depth), material)
        _add_text_diacritics_z(
            scene,
            base_char=base_char,
            accents=accents,
            char_x=x,
            char_y=y0,
            char_width=width,
            char_height=char_height,
            center_z=center[2],
            scene_center_x=center[0],
            pix=pix,
            material=material,
            depth=depth,
            mirror_x=mirror_x,
        )
        x += width + spacing


def _add_columns_and_frame(scene: SceneMesh, mat: MaterialMap, rng: Random) -> None:
    wood = _mat(mat, "wood")
    wood_dark = _mat(mat, "wood_dark")
    red = _mat(mat, "red")

    xs = [-5.15, -3.43, -1.72, 0.0, 1.72, 3.43, 5.15]
    for x in xs:
        for z in (-1.35, 1.35):
            scene.add_box((x, 1.74, z), (0.16, 1.64, 0.16), red if x in (-5.15, 5.15) else wood)
            scene.add_box((x, 2.57, z), (0.22, 0.12, 0.22), wood_dark)
        # Kèo ngang qua chiều rộng cầu.
        scene.add_box((x, 2.35, 0.0), (0.14, 0.12, 2.90), wood_dark)

    # Dầm dọc dưới mái.
    for z in (-1.37, 1.37):
        scene.add_box((0.0, 2.46, z), (10.55, 0.14, 0.16), wood_dark)
        scene.add_box((0.0, 2.18, z), (10.35, 0.10, 0.12), wood)

    # Một số thanh chéo trang trí/giằng gợi khung gỗ cổ.
    for x in [-4.25, -2.55, -0.85, 0.85, 2.55, 4.25]:
        for z in (-1.36, 1.36):
            scene.add_box_between((x - 0.35, 2.13, z), (x + 0.35, 2.43, z), 0.045, wood_dark, width=0.055)
            scene.add_box_between((x + 0.35, 2.13, z), (x - 0.35, 2.43, z), 0.045, wood_dark, width=0.055)


# -----------------------------------------------------------------------------
# Mái chính, mái miếu phụ và chi tiết nóc
# -----------------------------------------------------------------------------


def _roof_point_main(x: float, side: int, t: float, *, length: float, width: float, eave_y: float, ridge_y: float) -> Vec3:
    # t = 0 ở mép mái, t = 1 ở sống mái. Mép mái/nóc hơi vểnh ở hai đầu.
    half = length / 2.0
    end_lift = 0.12 * (abs(x) / half) ** 2
    z = side * (width / 2.0) * (1.0 - t)
    y = eave_y + (ridge_y - eave_y) * math.sin(t * math.pi / 2.0) + end_lift * (0.65 + 0.35 * (1.0 - t))
    return (x, y, z)


def _add_main_roof(scene: SceneMesh, mat: MaterialMap, rng: Random) -> None:
    roof_base = _mat(mat, "roof_base")
    roof_tiles = _mat_list(mat, "roof_tiles")
    red_dark = _mat(mat, "red_dark")
    wood_dark = _mat(mat, "wood_dark")

    length = 12.25
    width = 4.55
    eave_y = 2.45
    ridge_y = 4.06
    xsegs = 36
    tsegs = 8

    # Hai mặt mái cong nhẹ; silhouette này là yếu tố quan trọng nhất của Chùa Cầu.
    for side in (-1, 1):
        for ix in range(xsegs):
            x0 = -length / 2.0 + length * ix / xsegs
            x1 = -length / 2.0 + length * (ix + 1) / xsegs
            for it in range(tsegs):
                t0 = it / tsegs
                t1 = (it + 1) / tsegs
                p00 = _roof_point_main(x0, side, t0, length=length, width=width, eave_y=eave_y, ridge_y=ridge_y)
                p10 = _roof_point_main(x1, side, t0, length=length, width=width, eave_y=eave_y, ridge_y=ridge_y)
                p11 = _roof_point_main(x1, side, t1, length=length, width=width, eave_y=eave_y, ridge_y=ridge_y)
                p01 = _roof_point_main(x0, side, t1, length=length, width=width, eave_y=eave_y, ridge_y=ridge_y)
                scene.add_quad(p00, p10, p11, p01, roof_base, uv=((ix / 4, it / 2), ((ix + 1) / 4, it / 2), ((ix + 1) / 4, (it + 1) / 2), (ix / 4, (it + 1) / 2)))

    # Các sống ngói âm-dương chạy dọc theo mái, làm bằng ống nhỏ lặp lại.
    for side in (-1, 1):
        for it in range(1, tsegs + 1):
            t = it / (tsegs + 1)
            mat_tile = roof_tiles[(it + (0 if side < 0 else 2)) % len(roof_tiles)]
            p0 = _roof_point_main(-length / 2.0 + 0.28, side, t, length=length, width=width, eave_y=eave_y, ridge_y=ridge_y)
            p1 = _roof_point_main(length / 2.0 - 0.28, side, t, length=length, width=width, eave_y=eave_y, ridge_y=ridge_y)
            p0 = (p0[0], p0[1] + 0.045, p0[2])
            p1 = (p1[0], p1[1] + 0.045, p1[2])
            scene.add_frustum_between(p0, p1, 0.032, 0.032, mat_tile, segments=10)

    # Hàng ngói nhỏ riêng ở mép mái trước/sau.
    for side in (-1, 1):
        z = side * width / 2.0
        y = eave_y + 0.02
        for i in range(34):
            x = -length / 2.0 + 0.25 + i * ((length - 0.50) / 33.0)
            m = roof_tiles[i % len(roof_tiles)]
            scene.add_box((x, y, z + side * 0.035), (0.22, 0.055, 0.13), m)
        scene.add_box((0.0, y - 0.08, z + side * 0.03), (length, 0.12, 0.16), red_dark)

    # Sống mái, hai hồi tam giác và khung gỗ dưới mái.
    scene.add_frustum_between((-length / 2.0 + 0.08, ridge_y + 0.06, 0.0), (length / 2.0 - 0.08, ridge_y + 0.06, 0.0), 0.075, 0.075, roof_tiles[1], segments=12)
    for x in (-length / 2.0, length / 2.0):
        # Hồi tam giác đỏ sẫm, gợi mặt cắt mái có trang trí nhưng không mô phỏng chi tiết quá mức.
        scene.add_triangle((x, eave_y, -width / 2.0), (x, eave_y, width / 2.0), (x, ridge_y, 0.0), red_dark)
        scene.add_triangle((x, eave_y, width / 2.0), (x, eave_y, -width / 2.0), (x, ridge_y, 0.0), red_dark)
        scene.add_box_between((x, eave_y, -width / 2.0), (x, ridge_y, 0.0), 0.06, wood_dark, width=0.07)
        scene.add_box_between((x, eave_y, width / 2.0), (x, ridge_y, 0.0), 0.06, wood_dark, width=0.07)
        scene.add_box_between((x, eave_y, -width / 2.0), (x, eave_y, width / 2.0), 0.055, wood_dark, width=0.06)


def _add_shrine_wing(scene: SceneMesh, mat: MaterialMap, rng: Random) -> None:
    """Khối miếu nhỏ nhô về phía bắc, tạo mặt bằng chữ T/Đinh theo tư liệu.

    Chưa có bản vẽ chi tiết nên khối này dựng ước lượng: mái nhỏ, vách gỗ/cửa thượng song hạ bản,
    bàn thờ tối giản bên trong.
    """
    wood = _mat(mat, "wood")
    wood_dark = _mat(mat, "wood_dark")
    red = _mat(mat, "red")
    red_dark = _mat(mat, "red_dark")
    black = _mat(mat, "black")
    roof_tiles = _mat_list(mat, "roof_tiles")

    # Sàn phụ và vách miếu.
    scene.add_box((0.0, 1.00, 2.55), (3.25, 0.22, 1.85), wood_dark)
    scene.add_box((0.0, 1.70, 2.75), (3.00, 1.26, 0.22), red_dark)
    scene.add_box((-1.48, 1.70, 2.33), (0.22, 1.20, 1.20), red)
    scene.add_box((1.48, 1.70, 2.33), (0.22, 1.20, 1.20), red)
    scene.add_box((0.0, 2.32, 2.33), (3.00, 0.20, 1.20), red)
    # Cửa thượng song hạ bản: trên song gỗ, dưới mảng kín.
    scene.add_box((0.0, 1.42, 1.94), (1.38, 0.40, 0.08), wood_dark)
    for x in [-0.54, -0.27, 0.0, 0.27, 0.54]:
        scene.add_box((x, 1.92, 1.91), (0.055, 0.66, 0.07), wood)
    scene.add_box((0.0, 1.96, 2.04), (1.55, 0.82, 0.08), black)
    # Bàn thờ tối giản trong miếu; chỉ gợi không gian thờ, không dựng tượng khi thiếu dữ liệu.
    scene.add_box((0.0, 1.29, 2.68), (0.85, 0.16, 0.42), red_dark)
    scene.add_box((0.0, 1.50, 2.68), (0.50, 0.25, 0.12), _mat(mat, "gold"))

    # Mái nhỏ của miếu, sống mái theo trục Z.
    length_z = 2.42
    width_x = 3.65
    eave_y = 2.25
    ridge_y = 3.18
    center_z = 2.45
    xsegs = 6
    zsegs = 16
    for side in (-1, 1):
        for iz in range(zsegs):
            z0 = center_z - length_z / 2.0 + length_z * iz / zsegs
            z1 = center_z - length_z / 2.0 + length_z * (iz + 1) / zsegs
            for ix in range(xsegs):
                t0 = ix / xsegs
                t1 = (ix + 1) / xsegs
                p00 = _roof_point_shrine(z0, side, t0, width_x=width_x, eave_y=eave_y, ridge_y=ridge_y)
                p10 = _roof_point_shrine(z1, side, t0, width_x=width_x, eave_y=eave_y, ridge_y=ridge_y)
                p11 = _roof_point_shrine(z1, side, t1, width_x=width_x, eave_y=eave_y, ridge_y=ridge_y)
                p01 = _roof_point_shrine(z0, side, t1, width_x=width_x, eave_y=eave_y, ridge_y=ridge_y)
                scene.add_quad(p00, p10, p11, p01, _mat(mat, "roof_base"))
        # Ribs mái miếu.
        for t in [0.20, 0.38, 0.56, 0.74, 0.90]:
            p0 = _roof_point_shrine(center_z - length_z / 2 + 0.12, side, t, width_x=width_x, eave_y=eave_y, ridge_y=ridge_y)
            p1 = _roof_point_shrine(center_z + length_z / 2 - 0.12, side, t, width_x=width_x, eave_y=eave_y, ridge_y=ridge_y)
            scene.add_frustum_between((p0[0], p0[1] + 0.04, p0[2]), (p1[0], p1[1] + 0.04, p1[2]), 0.026, 0.026, roof_tiles[int(t * 10) % len(roof_tiles)], segments=8)
    scene.add_frustum_between((0.0, ridge_y + 0.04, center_z - length_z / 2.0), (0.0, ridge_y + 0.04, center_z + length_z / 2.0), 0.055, 0.055, roof_tiles[2], segments=10)


def _roof_point_shrine(z: float, side: int, t: float, *, width_x: float, eave_y: float, ridge_y: float) -> Vec3:
    x = side * (width_x / 2.0) * (1.0 - t)
    y = eave_y + (ridge_y - eave_y) * math.sin(t * math.pi / 2.0)
    return (x, y, z)


def _add_ceramics_dragons_and_roof_details(scene: SceneMesh, mat: MaterialMap, rng: Random) -> None:
    ceramic = _mat(mat, "ceramic")
    ceramic_blue = _mat(mat, "ceramic_blue")
    gold = _mat(mat, "gold")
    red_dark = _mat(mat, "red_dark")
    roof_tiles = _mat_list(mat, "roof_tiles")

    # Đĩa gốm men lam dọc bờ mái/nóc, một dấu hiệu được nhắc trong tư liệu.
    for x in [-5.0, -4.1, -3.2, -2.3, -1.4, -0.5, 0.5, 1.4, 2.3, 3.2, 4.1, 5.0]:
        scene.add_frustum_between((x, 3.98, -0.085), (x, 3.98, -0.010), 0.075, 0.075, ceramic, segments=24)
        scene.add_frustum_between((x, 3.985, 0.010), (x, 3.985, 0.080), 0.055, 0.055, ceramic_blue, segments=18)

    # Đĩa gốm nhỏ trên mặt trước mái.
    for x in [-4.8, -3.6, -2.4, -1.2, 0.0, 1.2, 2.4, 3.6, 4.8]:
        scene.add_frustum_between((x, 2.55, -2.34), (x, 2.55, -2.27), 0.060, 0.060, ceramic, segments=20)

    # Cặp rồng + châu ở giữa nóc, dựng low-poly bằng chuỗi ống cong và cầu nhỏ.
    _add_uv_sphere(scene, (0.0, 4.34, 0.0), (0.16, 0.16, 0.16), gold, segments=16, rings=8)
    for side in (-1, 1):
        points: list[Vec3] = []
        for i in range(8):
            t = i / 7.0
            x = side * (0.28 + 1.55 * t)
            y = 4.21 + 0.08 * math.sin(t * math.pi * 1.7)
            z = 0.055 * math.sin(t * math.pi * 2.0)
            points.append((x, y, z))
        for p0, p1 in zip(points, points[1:]):
            scene.add_frustum_between(p0, p1, 0.035, 0.030, gold, segments=8)
        # Đầu rồng cách điệu, quay về quả châu.
        _add_uv_sphere(scene, (side * 0.26, 4.25, 0.0), (0.11, 0.08, 0.08), gold, segments=12, rings=6)
        for p in points[2::2]:
            scene.add_box((p[0], p[1] + 0.05, p[2]), (0.055, 0.11, 0.030), red_dark)

    # Họa tiết mây/lửa cách điệu ở hai đầu mái.
    for x in (-5.95, 5.95):
        _add_uv_sphere(scene, (x, 4.12, 0.0), (0.14, 0.07, 0.07), roof_tiles[3], segments=12, rings=6)
        scene.add_frustum_between((x, 4.10, -0.10), (x, 4.10, 0.10), 0.035, 0.030, roof_tiles[0], segments=8)


# -----------------------------------------------------------------------------
# Tượng linh vật và các chi tiết nhỏ
# -----------------------------------------------------------------------------


def _add_guardian_animals(scene: SceneMesh, mat: MaterialMap, rng: Random) -> None:
    stone = _mat(mat, "stone_light")
    stone_dark = _mat(mat, "stone_dark")

    # Tượng chó ở một đầu, tượng khỉ ở đầu còn lại; dựng tượng nhỏ low-poly trên bệ.
    # Vị trí và tạo hình là ước lượng vì Prompt 2 không cung cấp bản vẽ chính xác từng tượng.
    for z in (-0.88, 0.88):
        _add_dog_statue(scene, center=(4.78, 1.30, z), material=stone, dark=stone_dark)
        _add_monkey_statue(scene, center=(-4.78, 1.30, z), material=stone, dark=stone_dark)


def _add_dog_statue(scene: SceneMesh, center: Vec3, material: int, dark: int) -> None:
    x, y, z = center
    scene.add_box((x, y - 0.07, z), (0.34, 0.12, 0.28), dark)
    _add_uv_sphere(scene, (x, y + 0.08, z), (0.19, 0.13, 0.11), material, segments=12, rings=6)
    _add_uv_sphere(scene, (x + 0.16, y + 0.15, z), (0.10, 0.09, 0.09), material, segments=12, rings=6)
    scene.add_frustum_between((x + 0.24, y + 0.14, z), (x + 0.34, y + 0.13, z), 0.040, 0.026, material, segments=8)
    for dz in (-0.06, 0.06):
        scene.add_box((x + 0.13, y - 0.07, z + dz), (0.045, 0.14, 0.035), material)
        scene.add_box((x - 0.12, y - 0.07, z + dz), (0.045, 0.14, 0.035), material)
    scene.add_frustum_between((x - 0.17, y + 0.10, z), (x - 0.28, y + 0.20, z), 0.022, 0.014, material, segments=6)


def _add_monkey_statue(scene: SceneMesh, center: Vec3, material: int, dark: int) -> None:
    x, y, z = center
    scene.add_box((x, y - 0.07, z), (0.34, 0.12, 0.28), dark)
    _add_uv_sphere(scene, (x, y + 0.08, z), (0.13, 0.18, 0.11), material, segments=12, rings=6)
    _add_uv_sphere(scene, (x, y + 0.27, z), (0.10, 0.10, 0.09), material, segments=12, rings=6)
    _add_uv_sphere(scene, (x, y + 0.27, z - 0.09), (0.035, 0.045, 0.020), material, segments=8, rings=4)
    _add_uv_sphere(scene, (x, y + 0.27, z + 0.09), (0.035, 0.045, 0.020), material, segments=8, rings=4)
    # Đuôi cong cách điệu.
    pts = [(x - 0.10, y + 0.10, z + 0.10), (x - 0.18, y + 0.18, z + 0.18), (x - 0.10, y + 0.30, z + 0.16)]
    for p0, p1 in zip(pts, pts[1:]):
        scene.add_frustum_between(p0, p1, 0.018, 0.014, material, segments=6)


# -----------------------------------------------------------------------------
# Bối cảnh Hội An: nhà vàng, đèn lồng, cây nhỏ
# -----------------------------------------------------------------------------


def _add_hoi_an_context(scene: SceneMesh, mat: MaterialMap, rng: Random) -> None:
    yellow = _mat(mat, "yellow_wall")
    wood_dark = _mat(mat, "wood_dark")
    red = _mat(mat, "red")
    roof_tiles = _mat_list(mat, "roof_tiles")
    leaf = _mat(mat, "leaf")
    paving = _mat(mat, "paving")

    # Nhà cổ Hội An phía sau, dựng thấp để không lấn át Chùa Cầu.
    _add_simple_old_town_house(scene, center=(-4.3, 0.0, 4.18), width=3.0, height=1.55, depth=1.0, yellow=yellow, roof=roof_tiles[2], wood=wood_dark)
    _add_simple_old_town_house(scene, center=(4.25, 0.0, 4.12), width=3.2, height=1.45, depth=1.1, yellow=yellow, roof=roof_tiles[3], wood=wood_dark)

    # Lối đá trước mặt cầu được tách thành hai bên bờ ngoài cùng.
    # FIX 2: vùng trước 5 ô vòm là nước liên tục, nên không đặt nền lát đè lên kênh.
    scene.add_box((-6.72, 0.045, -3.22), (1.55, 0.055, 1.35), paving)
    scene.add_box((6.72, 0.045, -3.22), (1.55, 0.055, 1.35), paving)

    # Dây đèn lồng nhỏ trước cầu.
    for x in [-4.8, -3.6, -2.4, -1.2, 1.2, 2.4, 3.6, 4.8]:
        material = _mat(mat, "lantern_red") if int(abs(x) * 10) % 2 == 0 else _mat(mat, "lantern_yellow")
        scene.add_box((x, 2.46, -1.82), (0.035, 0.42, 0.035), wood_dark)
        _add_lantern(scene, (x, 2.19, -1.82), material, _mat(mat, "lantern_glow"))

    # Cây xanh nhỏ ở hai góc, không che công trình.
    for center in [(-6.65, 0.84, -3.55), (6.65, 0.84, -3.50), (-6.8, 0.84, 3.45), (6.85, 0.84, 3.35)]:
        _add_simple_tree(scene, center, trunk=wood_dark, leaf=leaf, rng=rng)


def _add_simple_old_town_house(scene: SceneMesh, center: Vec3, *, width: float, height: float, depth: float, yellow: int, roof: int, wood: int) -> None:
    x, y, z = center
    scene.add_box((x, y + height / 2.0, z), (width, height, depth), yellow)
    scene.add_box((x, y + 0.55, z - depth / 2.0 - 0.035), (0.62, 0.92, 0.08), wood)
    for wx in (-width * 0.32, width * 0.32):
        scene.add_box((x + wx, y + 0.92, z - depth / 2.0 - 0.04), (0.45, 0.38, 0.07), wood)
    # Gable roof mini.
    roof_y = y + height + 0.04
    scene.add_box((x, roof_y + 0.18, z), (width + 0.32, 0.18, depth + 0.28), roof, y_axis=v_norm((0.0, 0.5, 0.0)))
    scene.add_box_between((x - width / 2.0 - 0.18, roof_y, z - depth / 2.0 - 0.18), (x, roof_y + 0.42, z - depth / 2.0 - 0.18), 0.05, roof, width=depth + 0.36)
    scene.add_box_between((x + width / 2.0 + 0.18, roof_y, z - depth / 2.0 - 0.18), (x, roof_y + 0.42, z - depth / 2.0 - 0.18), 0.05, roof, width=depth + 0.36)


def _add_lantern(scene: SceneMesh, center: Vec3, material: int, glow: int) -> None:
    x, y, z = center
    profile = [(0.02, -0.14), (0.10, -0.10), (0.13, 0.0), (0.10, 0.10), (0.02, 0.14)]
    scene.add_lathe((x, y, z), profile, material, segments=16, cap_bottom=True, cap_top=True)
    scene.add_frustum_between((x, y - 0.13, z), (x, y + 0.13, z), 0.012, 0.012, glow, segments=10)


def _add_simple_tree(scene: SceneMesh, center: Vec3, trunk: int, leaf: int, rng: Random) -> None:
    x, y, z = center
    height = _rand(rng, 1.0, 1.35)
    scene.add_frustum_between((x, y, z), (x + _rand(rng, -0.08, 0.08), y + height, z + _rand(rng, -0.08, 0.08)), 0.055, 0.035, trunk, segments=8)
    for dx, dy, dz, s in [
        (0.00, height + 0.10, 0.00, 1.0),
        (-0.22, height * 0.92, 0.05, 0.75),
        (0.24, height * 0.88, -0.04, 0.72),
        (0.05, height * 1.03, 0.22, 0.66),
    ]:
        _add_uv_sphere(scene, (x + dx, y + dy, z + dz), (0.38 * s, 0.28 * s, 0.34 * s), leaf, segments=12, rings=6)


# -----------------------------------------------------------------------------
# Mesh helper hữu cơ / cầu tròn
# -----------------------------------------------------------------------------


def _add_uv_sphere(scene: SceneMesh, center: Vec3, radii: Vec3, material: int, *, segments: int = 16, rings: int = 8) -> None:
    cx, cy, cz = center
    rx, ry, rz = radii
    vertices: list[list[int]] = []
    for r in range(rings + 1):
        phi = -math.pi / 2.0 + math.pi * r / rings
        row: list[int] = []
        for s in range(segments):
            theta = math.tau * s / segments
            x = cx + math.cos(phi) * math.cos(theta) * rx
            y = cy + math.sin(phi) * ry
            z = cz + math.cos(phi) * math.sin(theta) * rz
            normal = v_norm(((x - cx) / max(rx, 1e-5), (y - cy) / max(ry, 1e-5), (z - cz) / max(rz, 1e-5)))
            row.append(scene.push_vertex((x, y, z), normal, (s / segments, r / rings)))
        vertices.append(row)
    out = scene.indices_by_material[material]
    for r in range(rings):
        for s in range(segments):
            j = (s + 1) % segments
            a = vertices[r][s]
            b = vertices[r][j]
            c = vertices[r + 1][j]
            d = vertices[r + 1][s]
            if r == 0:
                out.extend([a, c, d])
            elif r == rings - 1:
                out.extend([a, b, d])
            else:
                out.extend([a, b, c, a, c, d])
