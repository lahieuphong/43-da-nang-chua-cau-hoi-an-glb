from __future__ import annotations

import json
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path
from typing import Callable

import numpy as np

BASE_PROJECT = next(Path('/mnt/data/v38src').glob('*_project'))
V39_PROJECT = Path('/mnt/data/v39_work/chua_cau_hoi_an_textured_fixed_v39_roof_square_fill_fix_project')
V40_PROJECT = Path('/mnt/data/chua_cau_hoi_an_textured_fixed_v40_roof_drop_to_red_gable_fix_project')
SRC_DIR = BASE_PROJECT / 'src'
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from glb_forge.scenes.chua_cau_hoi_an import create_chua_cau_hoi_an  # type: ignore
from glb_forge.scene import SceneMesh
from glb_forge.scene_writer import write_scene_glb

MAT_WOOD_DARK = 8
MAT_WOOD = 9
MAT_WOOD_LIGHT = 10
MAT_RED = 12
MAT_RED_DARK = 13
MAT_GOLD = 14
MAT_BLACK = 15
MAT_ROOF_BASE = 16
MAT_ROOF_TILES = (17, 18, 19, 20, 21)
MAT_CERAMIC = 22
MAT_CERAMIC_BLUE = 23


def clamp01(v: float) -> float:
    return max(0.0, min(1.0, v))


def drop_triangles(scene: SceneMesh, material_indices: set[int], predicate: Callable[[np.ndarray, np.ndarray], bool]) -> dict[int, int]:
    """Remove triangles selected by centroid/bounds predicate."""
    positions = np.asarray(scene.positions, dtype=np.float64)
    removed: dict[int, int] = {}
    for material_index in sorted(material_indices):
        raw = scene.indices_by_material.get(material_index, [])
        if not raw:
            removed[material_index] = 0
            continue
        tris = np.asarray(raw, dtype=np.int64).reshape(-1, 3)
        keep: list[int] = []
        rem = 0
        for tri in tris:
            pts = positions[tri]
            c = pts.mean(axis=0)
            b = np.concatenate([pts.min(axis=0), pts.max(axis=0)])
            if predicate(c, b):
                rem += 1
            else:
                keep.extend(map(int, tri))
        scene.indices_by_material[material_index] = keep
        removed[material_index] = rem
    return removed


def compact_scene(scene: SceneMesh) -> None:
    used: list[int] = []
    for material_index in range(len(scene.materials)):
        used.extend(scene.indices_by_material.get(material_index, []))
    unique = sorted(set(used))
    mapping = {old: new for new, old in enumerate(unique)}
    scene.positions = [scene.positions[i] for i in unique]
    scene.normals = [scene.normals[i] for i in unique]
    scene.texcoords = [scene.texcoords[i] for i in unique]
    for material_index in range(len(scene.materials)):
        scene.indices_by_material[material_index] = [mapping[i] for i in scene.indices_by_material.get(material_index, [])]


# ---------------------------------------------------------------------------
# v40 roof profile aligned to the existing dark-red triangular gable.
# Red gable reference from v38/v39 side panels:
#   base: z = -2.275 / +2.275 at y = 2.948
#   peak: z = 0.000 at y = 4.569371
# The large roof still keeps its v39 footprint/overhang, but its slope/ridge
# is dropped onto this red triangle profile so no visible gap remains.
# ---------------------------------------------------------------------------
MAIN_X_HALF = 5.72
MAIN_Z_MIN = -2.48
MAIN_Z_MAX = 2.84
MAIN_Z_RIDGE = 0.0

RED_GABLE_Z_CENTER = 0.0
RED_GABLE_Z_HALF = 2.275
RED_GABLE_EAVE_Y = 2.948
RED_GABLE_RIDGE_Y = 4.569371
RED_GABLE_RISE = RED_GABLE_RIDGE_Y - RED_GABLE_EAVE_Y

# Keep small-roof/canopy layout exactly from v39 so the rest of the model stays unchanged.
V39_MAIN_Z_CENTER = 0.18
V39_MAIN_Z_HALF = 2.66
CANOPY_X_HALF = 1.78
CANOPY_EXTRA = 1.38
CANOPY_EAVE_Y = 2.91
CANOPY_RISE = 0.68


def main_roof_y(z: float, lift: float = 0.0) -> float:
    d = abs(z - RED_GABLE_Z_CENTER)
    if d <= RED_GABLE_Z_HALF:
        y = RED_GABLE_EAVE_Y + RED_GABLE_RISE * (1.0 - d / RED_GABLE_Z_HALF)
    else:
        # The existing roof overhang remains outside the red gable, kept nearly flat at the gable eave.
        max_overhang = max(abs(MAIN_Z_MIN - RED_GABLE_Z_CENTER), abs(MAIN_Z_MAX - RED_GABLE_Z_CENTER)) - RED_GABLE_Z_HALF
        y = RED_GABLE_EAVE_Y - 0.020 * clamp01((d - RED_GABLE_Z_HALF) / max_overhang)
    return y + lift


def main_roof_point(x: float, z: float, lift: float = 0.0) -> tuple[float, float, float]:
    # Tiny end fall only at the far overhanging X tips, preserving v39 visual edge without lifting off the red gable.
    end_drop = 0.010 * clamp01((abs(x) - 5.25) / 0.47)
    return (x, main_roof_y(z, lift) - end_drop, z)


def add_main_roof_dropped_to_red_gable(scene: SceneMesh) -> None:
    """Large roof: same v39 square/tile material, lowered to match the red triangular gable."""
    x_steps = 64
    z_steps_left = 26
    z_steps_right = 30
    xs = [-MAIN_X_HALF + 2.0 * MAIN_X_HALF * i / x_steps for i in range(x_steps + 1)]
    left_zs = [MAIN_Z_MIN + (MAIN_Z_RIDGE - MAIN_Z_MIN) * j / z_steps_left for j in range(z_steps_left + 1)]
    right_zs = [MAIN_Z_RIDGE + (MAIN_Z_MAX - MAIN_Z_RIDGE) * j / z_steps_right for j in range(z_steps_right + 1)]

    def add_surface(zs: list[float], side_offset: int) -> None:
        for i in range(x_steps):
            for j in range(len(zs) - 1):
                z0, z1 = zs[j], zs[j + 1]
                x0, x1 = xs[i], xs[i + 1]
                material = MAT_ROOF_BASE if (j % 4) else MAT_ROOF_TILES[(i // 5 + j + side_offset) % len(MAT_ROOF_TILES)]
                scene.add_quad(
                    main_roof_point(x0, z0),
                    main_roof_point(x0, z1),
                    main_roof_point(x1, z1),
                    main_roof_point(x1, z0),
                    material,
                    uv=(
                        ((x0 + MAIN_X_HALF) * 0.48, (z0 - MAIN_Z_MIN) * 1.25),
                        ((x0 + MAIN_X_HALF) * 0.48, (z1 - MAIN_Z_MIN) * 1.25),
                        ((x1 + MAIN_X_HALF) * 0.48, (z1 - MAIN_Z_MIN) * 1.25),
                        ((x1 + MAIN_X_HALF) * 0.48, (z0 - MAIN_Z_MIN) * 1.25),
                    ),
                )

    add_surface(left_zs, 0)
    add_surface(right_zs, 2)

    x_line = [-MAIN_X_HALF + 0.10 + k * (2 * (MAIN_X_HALF - 0.10)) / 44 for k in range(45)]

    # Long horizontal tile courses across the roof length, lowered with the roof skin.
    course_zs = [MAIN_Z_MIN + k * (MAIN_Z_MAX - MAIN_Z_MIN) / 34 for k in range(35)]
    for ci, z in enumerate(course_zs):
        material = MAT_ROOF_TILES[(ci + 1) % len(MAT_ROOF_TILES)]
        radius = 0.010 if abs(z - MAIN_Z_RIDGE) > 0.09 else 0.018
        for x0, x1 in zip(x_line, x_line[1:]):
            scene.add_frustum_between(
                main_roof_point(x0, z, lift=0.030),
                main_roof_point(x1, z, lift=0.030),
                radius,
                radius,
                material,
                segments=5,
                cap_ends=True,
            )

    # Down-slope tile ribs, using the same old roof tile texture family.
    rib_xs = [-MAIN_X_HALF + 0.20 + k * (2 * (MAIN_X_HALF - 0.20)) / 46 for k in range(47)]
    for ri, x in enumerate(rib_xs):
        material = MAT_ROOF_TILES[(ri + 2) % len(MAT_ROOF_TILES)]
        for z0, z1 in zip(left_zs[:-1:2], left_zs[2::2]):
            scene.add_frustum_between(main_roof_point(x, z0, 0.045), main_roof_point(x, z1, 0.045), 0.0075, 0.0075, material, segments=5, cap_ends=True)
        for z0, z1 in zip(right_zs[:-1:2], right_zs[2::2]):
            scene.add_frustum_between(main_roof_point(x, z0, 0.045), main_roof_point(x, z1, 0.045), 0.0075, 0.0075, material, segments=5, cap_ends=True)

    # Ridge placed on the red triangle peak line (z=0.0 / y=4.569371).
    for x0, x1 in zip(x_line, x_line[1:]):
        scene.add_frustum_between(main_roof_point(x0, MAIN_Z_RIDGE, 0.070), main_roof_point(x1, MAIN_Z_RIDGE, 0.070), 0.028, 0.028, MAT_ROOF_TILES[1], segments=8, cap_ends=True)

    # Straight eave rows at the old v39 footprint; low and aligned to the dropped roof.
    for z, mat_shift in ((MAIN_Z_MIN, 0), (MAIN_Z_MAX, 2)):
        for x0, x1 in zip(x_line, x_line[1:]):
            scene.add_box_between(main_roof_point(x0, z, 0.025), main_roof_point(x1, z, 0.025), 0.040, MAT_ROOF_TILES[(mat_shift + 3) % len(MAT_ROOF_TILES)], width=0.045)
        for i in range(32):
            x = -MAIN_X_HALF + 0.25 + i * (2 * (MAIN_X_HALF - 0.25)) / 31
            p = (x, main_roof_y(z, -0.045), z + (0.010 if z > 0 else -0.010))
            scene.add_frustum(p, 0.024, 0.022, 0.032, MAT_CERAMIC, segments=8, cap_bottom=True, cap_top=True)

    # Side/gable slope caps: make the visible roof edge sit directly on the red triangle sides.
    for x in (-MAIN_X_HALF, MAIN_X_HALF):
        scene.add_box_between(main_roof_point(x, -RED_GABLE_Z_HALF, 0.035), main_roof_point(x, MAIN_Z_RIDGE, 0.035), 0.040, MAT_WOOD_DARK, width=0.045)
        scene.add_box_between(main_roof_point(x, MAIN_Z_RIDGE, 0.035), main_roof_point(x, RED_GABLE_Z_HALF, 0.035), 0.040, MAT_WOOD_DARK, width=0.045)

    # Rear/front fascia lowered with the new roof profile; no arched/open gap.
    z_fill = MAIN_Z_MAX + 0.045
    y_top = main_roof_y(MAIN_Z_MAX, -0.020)
    scene.add_quad(
        (-MAIN_X_HALF, y_top, z_fill),
        (MAIN_X_HALF, y_top, z_fill),
        (MAIN_X_HALF, y_top - 0.32, z_fill),
        (-MAIN_X_HALF, y_top - 0.32, z_fill),
        MAT_ROOF_BASE,
        normal=(0.0, 0.0, 1.0),
        uv=((0, 0), (6, 0), (6, 0.5), (0, 0.5)),
    )
    scene.add_box((0.0, y_top - 0.34, z_fill - 0.015), (2 * MAIN_X_HALF, 0.060, 0.060), MAT_WOOD_DARK)
    scene.add_box((0.0, main_roof_y(MAIN_Z_MIN, -0.080), MAIN_Z_MIN - 0.015), (2 * MAIN_X_HALF, 0.060, 0.055), MAT_WOOD_DARK)


def canopy_point(sign: float, u: float, v: float, lift: float = 0.0) -> tuple[float, float, float]:
    """v39 small roof geometry kept intact: same footprint/material, not moved with the main roof."""
    x = CANOPY_X_HALF * u
    seam_z = V39_MAIN_Z_CENTER + sign * (V39_MAIN_Z_HALF - 0.14)
    z = seam_z + sign * CANOPY_EXTRA * v
    pitch = 1.0 - min(abs(u), 1.0)
    seam_lift = 0.10 * (1.0 - v)
    front_drop = 0.03 * v
    y = CANOPY_EAVE_Y + seam_lift - front_drop + CANOPY_RISE * pitch * (1.0 - 0.10 * v) + lift
    return (x, y, z)


def add_canopy_square_roof(scene: SceneMesh, sign: float) -> None:
    u_steps = 18
    v_steps = 18
    us = [-1.0 + 2.0 * i / u_steps for i in range(u_steps + 1)]
    vs = [i / v_steps for i in range(v_steps + 1)]

    for i in range(u_steps):
        for j in range(v_steps):
            p00 = canopy_point(sign, us[i], vs[j])
            p01 = canopy_point(sign, us[i], vs[j + 1])
            p11 = canopy_point(sign, us[i + 1], vs[j + 1])
            p10 = canopy_point(sign, us[i + 1], vs[j])
            material = MAT_ROOF_BASE if ((i + j) % 3) else MAT_ROOF_TILES[(i + 2 * j) % len(MAT_ROOF_TILES)]
            if sign > 0:
                scene.add_quad(p00, p01, p11, p10, material, uv=((us[i], vs[j]), (us[i], vs[j + 1]), (us[i + 1], vs[j + 1]), (us[i + 1], vs[j])))
            else:
                scene.add_quad(p10, p11, p01, p00, material, uv=((us[i + 1], vs[j]), (us[i + 1], vs[j + 1]), (us[i], vs[j + 1]), (us[i], vs[j])))

    for ri, u in enumerate([-0.92 + k * (1.84 / 16) for k in range(17)]):
        material = MAT_ROOF_TILES[ri % len(MAT_ROOF_TILES)]
        pts = [canopy_point(sign, u, k / 24, lift=0.045) for k in range(25)]
        for p0, p1 in zip(pts, pts[1:]):
            scene.add_frustum_between(p0, p1, 0.010, 0.010, material, segments=5, cap_ends=True)

    for cj, v in enumerate([0.08 + k * (0.86 / 10) for k in range(11)]):
        material = MAT_ROOF_TILES[(cj + 2) % len(MAT_ROOF_TILES)]
        us_line = [-0.95 + k * (1.90 / 18) for k in range(19)]
        for u0, u1 in zip(us_line, us_line[1:]):
            scene.add_frustum_between(canopy_point(sign, u0, v, lift=0.054), canopy_point(sign, u1, v, lift=0.054), 0.011, 0.011, material, segments=5, cap_ends=True)

    for v in (0.0, 1.0):
        us_edge = [-0.98 + k * (1.96 / 20) for k in range(21)]
        for u0, u1 in zip(us_edge, us_edge[1:]):
            scene.add_box_between(canopy_point(sign, u0, v, lift=0.064), canopy_point(sign, u1, v, lift=0.064), 0.040, MAT_CERAMIC, width=0.050)

    for u in (-1.0, 1.0):
        vs_edge = [k / 18 for k in range(19)]
        for v0, v1 in zip(vs_edge, vs_edge[1:]):
            scene.add_box_between(canopy_point(sign, u, v0, lift=0.045), canopy_point(sign, u, v1, lift=0.045), 0.034, MAT_CERAMIC, width=0.045)

    left = canopy_point(sign, -1.0, 1.0, lift=-0.005)
    right = canopy_point(sign, 1.0, 1.0, lift=-0.005)
    peak = canopy_point(sign, 0.0, 1.0, lift=-0.005)
    if sign > 0:
        scene.add_triangle(left, right, peak, MAT_ROOF_BASE, normal=(0.0, 0.0, sign))
        scene.add_triangle(left, peak, right, MAT_ROOF_BASE, normal=(0.0, 0.0, sign))
    else:
        scene.add_triangle(right, left, peak, MAT_ROOF_BASE, normal=(0.0, 0.0, sign))
        scene.add_triangle(right, peak, left, MAT_ROOF_BASE, normal=(0.0, 0.0, sign))

    seam_z = V39_MAIN_Z_CENTER + sign * (V39_MAIN_Z_HALF - 0.16)
    outer_z = seam_z + sign * (CANOPY_EXTRA + 0.02)
    scene.add_box((0.0, CANOPY_EAVE_Y - 0.055, seam_z), (3.56, 0.080, 0.055), MAT_WOOD_DARK)
    scene.add_box((0.0, CANOPY_EAVE_Y - 0.075, outer_z), (3.56, 0.070, 0.060), MAT_WOOD_DARK)


def add_back_roof_fill(scene: SceneMesh) -> None:
    sign = -1.0
    z = V39_MAIN_Z_CENTER + sign * (V39_MAIN_Z_HALF + CANOPY_EXTRA + 0.025)
    p_left = (-CANOPY_X_HALF, CANOPY_EAVE_Y - 0.10, z)
    p_right = (CANOPY_X_HALF, CANOPY_EAVE_Y - 0.10, z)
    p_peak = (0.0, CANOPY_EAVE_Y + CANOPY_RISE - 0.08, z)
    scene.add_triangle(p_right, p_left, p_peak, MAT_ROOF_TILES[2], normal=(0.0, 0.0, -1.0))
    scene.add_triangle(p_right, p_peak, p_left, MAT_ROOF_TILES[2], normal=(0.0, 0.0, -1.0))
    scene.add_box_between(p_left, p_right, 0.045, MAT_ROOF_TILES[3], width=0.055)


def apply_v40_roof_fix(scene: SceneMesh) -> dict[str, object]:
    def central_roof_tile(c: np.ndarray, b: np.ndarray) -> bool:
        return (abs(float(c[0])) <= 5.88 and -2.78 <= float(c[2]) <= 4.24 and float(c[1]) >= 2.72)

    def central_trim(c: np.ndarray, b: np.ndarray) -> bool:
        return (abs(float(c[0])) <= 5.98 and -2.85 <= float(c[2]) <= 4.30 and float(c[1]) >= 2.62)

    def upper_wood_lattice(c: np.ndarray, b: np.ndarray) -> bool:
        x, y, z = map(float, c)
        return (abs(x) <= 5.95 and -2.55 <= z <= 2.55 and 2.45 <= y <= 3.68)

    def old_high_ornament(c: np.ndarray, b: np.ndarray) -> bool:
        x, y, z = map(float, c)
        return (abs(x) <= 2.05 and -0.42 <= z <= 0.48 and y >= 4.90)

    removed_roof = drop_triangles(scene, {MAT_ROOF_BASE, *MAT_ROOF_TILES}, central_roof_tile)
    removed_trim = drop_triangles(scene, {MAT_CERAMIC, MAT_CERAMIC_BLUE}, central_trim)
    removed_wood_lattice = drop_triangles(scene, {MAT_WOOD_DARK, MAT_WOOD, MAT_WOOD_LIGHT}, upper_wood_lattice)
    removed_high_ornament = drop_triangles(scene, {MAT_RED, MAT_RED_DARK, MAT_GOLD, MAT_BLACK}, old_high_ornament)

    add_main_roof_dropped_to_red_gable(scene)
    add_canopy_square_roof(scene, +1.0)
    add_canopy_square_roof(scene, -1.0)
    add_back_roof_fill(scene)

    compact_scene(scene)
    return {
        'removed_roof_tris': removed_roof,
        'removed_trim_tris': removed_trim,
        'removed_upper_wood_lattice_tris': removed_wood_lattice,
        'removed_old_high_ornament_tris': removed_high_ornament,
        'new_main_roof_profile': 'v40: roof dropped to red triangular gable, ridge at z=0/y=4.569371, eaves at z=±2.275/y=2.948',
        'small_roofs': 'kept in the v39 layout/material/fill; rest unchanged',
    }


def save_scene_npz(scene: SceneMesh, geometry_path: Path) -> None:
    arrays: dict[str, np.ndarray] = {
        'positions': np.asarray(scene.positions, dtype=np.float32),
        'normals': np.asarray(scene.normals, dtype=np.float32),
        'texcoords': np.asarray(scene.texcoords, dtype=np.float32),
    }
    for material_index in range(len(scene.materials)):
        arrays[f'indices_{material_index:02d}'] = np.asarray(scene.indices_by_material.get(material_index, []), dtype=np.uint32)
    geometry_path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(geometry_path, **arrays)


def make_manifest(scene: SceneMesh, source_manifest_path: Path, geometry_filename: str, stats: dict[str, object]) -> dict:
    manifest = json.loads(source_manifest_path.read_text(encoding='utf-8'))
    positions = np.asarray(scene.positions, dtype=np.float32)
    primitive_index_count: dict[str, int] = {}
    primitive_component_types: dict[str, int] = {}
    used_material_indices: list[int] = []
    for i in range(len(scene.materials)):
        idx = scene.indices_by_material.get(i, [])
        primitive_index_count[str(i)] = len(idx)
        if idx:
            used_material_indices.append(i)
            primitive_component_types[str(i)] = 5125 if max(idx) > 65535 else 5123
        else:
            primitive_component_types[str(i)] = 5123
    manifest.update({
        'version': 'v40_roof_drop_to_red_gable_fix',
        'scene_name': 'Chua_Cau_Hoi_An_Lai_Vien_Kieu',
        'source_glb_file': 'chua_cau_hoi_an_textured_fixed_v38_roof_architecture_image2_layout_fix.glb',
        'geometry_npz': geometry_filename,
        'vertex_count': int(len(scene.positions)),
        'material_count': int(len(scene.materials)),
        'primitive_count': int(sum(1 for i in range(len(scene.materials)) if scene.indices_by_material.get(i))),
        'used_material_indices': used_material_indices,
        'primitive_index_count': primitive_index_count,
        'primitive_component_types': primitive_component_types,
        'position_bounds_source': {
            'min': [float(v) for v in positions.min(axis=0)],
            'max': [float(v) for v in positions.max(axis=0)],
        },
        'patch_summary': 'v40: kept the v39 roof layout/material fixes, then lowered the large roof so its gable profile coincides with the existing dark-red triangular wall: peak z=0/y=4.569371 and eaves z=±2.275/y=2.948. Other parts were kept unchanged.',
        'v40_changes': {
            'requested_by_user': 'Drop the roof down so it is level/aligned with the red triangular gable; keep the remaining model unchanged.',
            'geometry_actions': stats,
            'red_gable_reference': {
                'eave_y': RED_GABLE_EAVE_Y,
                'ridge_y': RED_GABLE_RIDGE_Y,
                'z_half': RED_GABLE_Z_HALF,
                'ridge_z': RED_GABLE_Z_CENTER,
            },
        },
    })
    for i, material in enumerate(scene.materials):
        manifest['materials'][i]['name'] = material.name
        manifest['materials'][i]['color'] = list(material.color)
        manifest['materials'][i]['metallic'] = material.metallic
        manifest['materials'][i]['roughness'] = material.roughness
        manifest['materials'][i]['double_sided'] = material.double_sided
        manifest['materials'][i]['normal_scale'] = material.normal_scale
    return manifest


def patch_project_files(project: Path, geom_name: str, manifest_name: str) -> None:
    scene_file = project / 'src' / 'glb_forge' / 'scenes' / 'chua_cau_hoi_an.py'
    text = scene_file.read_text(encoding='utf-8')
    text = text.replace('bản v39 roof square fill fix', 'bản v40 roof drop to red gable fix')
    text = text.replace('v39 roof square fill fix', 'v40 roof drop to red gable fix')
    text = text.replace('chua_cau_hoi_an_v39_roof_square_fill_fix_geometry.npz', geom_name)
    text = text.replace('chua_cau_hoi_an_v39_roof_square_fill_fix_manifest.json', manifest_name)
    text = text.replace('Không tìm thấy manifest v39', 'Không tìm thấy manifest v40')
    text = text.replace('Không tìm thấy geometry v39', 'Không tìm thấy geometry v40')
    text = text.replace('Geometry v39 không hợp lệ', 'Geometry v40 không hợp lệ')
    text = text.replace('Sai số material so với manifest v39', 'Sai số material so với manifest v40')
    text = text.replace('GLB nâng cấp v39: bỏ phần trên rối, vuông hóa mái ngói nhỏ/sau, fill phần sau và giữ chất liệu ngói v37.', 'GLB nâng cấp v40: giữ bố cục/chất liệu v39 và hạ mái chính trùng với tam giác đỏ.')
    scene_file.write_text(text, encoding='utf-8')

    main_file = project / 'main.py'
    main_text = main_file.read_text(encoding='utf-8')
    main_text = main_text.replace('bản v39 roof square fill fix', 'bản v40 roof drop to red gable fix')
    main_text = main_text.replace('Bản này bỏ phần mái trên bị chồng, vuông hóa mái trước/sau và giữ chất liệu ngói v37.', 'Bản này giữ bố cục/chất liệu v39 và hạ mái chính xuống trùng với hình tam giác đỏ.')
    main_text = main_text.replace('chua_cau_hoi_an_textured_fixed_v39_roof_square_fill_fix.glb', 'chua_cau_hoi_an_textured_fixed_v40_roof_drop_to_red_gable_fix.glb')
    main_file.write_text(main_text, encoding='utf-8')

    registry = project / 'src' / 'glb_forge' / 'sites' / 'provinces' / 'da_nang.py'
    if registry.exists():
        rt = registry.read_text(encoding='utf-8')
        rt = rt.replace('chua_cau_hoi_an_textured_fixed_v39_roof_square_fill_fix', 'chua_cau_hoi_an_textured_fixed_v40_roof_drop_to_red_gable_fix')
        registry.write_text(rt, encoding='utf-8')

    readme = project / 'README.md'
    if readme.exists():
        readme.write_text(
            '# Chùa Cầu Hội An - source chuẩn barem v40\n\n'
            'Bản v40 giữ nguyên phần còn lại từ v39, chỉ hạ/khớp mái chính xuống đúng theo hình tam giác đỏ: đỉnh mái trùng z=0/y=4.569371 và hai chân mái trùng z=±2.275/y=2.948.\n\n'
            'Chạy `python main.py` để xuất lại GLB trong thư mục `output/`.\n',
            encoding='utf-8',
        )

    docs = project / 'docs'
    docs.mkdir(exist_ok=True)
    (docs / 'v40_roof_drop_to_red_gable_fix_note.md').write_text(
        '# v40 roof drop to red gable fix\n\n'
        '- Giữ lại bố cục/chất liệu/fill mái từ v39.\n'
        '- Hạ mái ngói chính xuống theo đúng mặt tam giác đỏ hiện có.\n'
        '- Đường sống mái đặt tại z=0, y=4.569371.\n'
        '- Hai chân tam giác mái đặt tại z=±2.275, y=2.948.\n'
        '- Các phần mái nhỏ và phần còn lại của mô hình được giữ theo bố cục v39.\n',
        encoding='utf-8',
    )

    # Keep a reproducible patch script in the source package.
    script_dst = project / 'scripts' / 'apply_v40_roof_drop_to_red_gable_fix.py'
    script_dst.write_text(Path(__file__).read_text(encoding='utf-8'), encoding='utf-8')


def main() -> None:
    scene = create_chua_cau_hoi_an()
    before = len(scene.positions)
    stats = apply_v40_roof_fix(scene)
    after = len(scene.positions)
    print('vertices before/after', before, after)
    print(json.dumps(stats, ensure_ascii=False, indent=2))

    if V40_PROJECT.exists():
        shutil.rmtree(V40_PROJECT)
    # Copy v39 source package as baseline so all previous fixes/docs/assets stay available.
    shutil.copytree(V39_PROJECT, V40_PROJECT)

    geom_name = 'chua_cau_hoi_an_v40_roof_drop_to_red_gable_fix_geometry.npz'
    manifest_name = 'chua_cau_hoi_an_v40_roof_drop_to_red_gable_fix_manifest.json'
    geom_path = V40_PROJECT / 'assets' / 'geometry' / geom_name
    manifest_path = V40_PROJECT / 'assets' / 'geometry' / manifest_name
    source_manifest = BASE_PROJECT / 'assets' / 'geometry' / 'chua_cau_hoi_an_v38_roof_architecture_image2_layout_fix_manifest.json'
    save_scene_npz(scene, geom_path)
    manifest = make_manifest(scene, source_manifest, geom_name, stats)
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    patch_project_files(V40_PROJECT, geom_name, manifest_name)

    # Direct GLB export.
    direct_output = Path('/mnt/data/chua_cau_hoi_an_chuan_barem_v40.glb')
    write_scene_glb(scene, direct_output)

    # Verify source package exports the same model by running main.py.
    subprocess.run([sys.executable, str(V40_PROJECT / 'main.py')], cwd=str(V40_PROJECT), check=True)
    source_output = V40_PROJECT / 'output' / 'chua_cau_hoi_an_textured_fixed_v40_roof_drop_to_red_gable_fix.glb'
    if source_output.exists():
        shutil.copy2(source_output, direct_output)

    zip_path = Path('/mnt/data/chua_cau_hoi_an_source_chuan_barem_v40.zip')
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        root = V40_PROJECT.parent
        for path in V40_PROJECT.rglob('*'):
            zf.write(path, path.relative_to(root))

    print('direct output:', direct_output, direct_output.stat().st_size)
    print('zip output:', zip_path, zip_path.stat().st_size)


if __name__ == '__main__':
    main()
