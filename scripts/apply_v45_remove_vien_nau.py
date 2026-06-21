from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / 'src'

V44_GEOM = 'chua_cau_hoi_an_v44_remove_front_small_roof_geometry.npz'
V44_MANIFEST = 'chua_cau_hoi_an_v44_remove_front_small_roof_manifest.json'
V45_GEOM = 'chua_cau_hoi_an_v45_remove_vien_nau_geometry.npz'
V45_MANIFEST = 'chua_cau_hoi_an_v45_remove_vien_nau_manifest.json'
V45_OUTPUT = 'chua_cau_hoi_an_textured_fixed_v45_remove_vien_nau.glb'

# Remove the brown border structure (viền nâu mái dư) at both front and back ends.
#
# FRONT (-Z end): mat08 and mat10 tris with Z_center < Z_FRONT_THRESH
# BACK  (+Z end): mat08 and mat10 tris with Z_center > Z_BACK_THRESH
#                 excluding the mirror small roof's face panels (all Z > Z_BACK_ROOF_GUARD)
Z_FRONT_THRESH = -1.9
Z_BACK_THRESH  =  2.0
Z_BACK_ROOF_GUARD = 2.8  # tris where ALL 3 vertices exceed this are mirror-small-roof parts → KEEP

MATS_TO_FILTER = {8, 10}  # mat 08 (dark bridge wood) + mat 10 (golden brown wood edge)


def _tri_z_center(a: np.ndarray, b: np.ndarray, c: np.ndarray) -> np.ndarray:
    return (a[:, 2] + b[:, 2] + c[:, 2]) / 3.0


def _tri_y_center(a: np.ndarray, b: np.ndarray, c: np.ndarray) -> np.ndarray:
    return (a[:, 1] + b[:, 1] + c[:, 1]) / 3.0


def remove_and_compact(data: np.lib.npyio.NpzFile, n_mat: int):
    positions = data['positions'].astype(np.float32, copy=True)
    normals   = data['normals'].astype(np.float32, copy=True)
    texcoords = data['texcoords'].astype(np.float32, copy=True)

    new_indices_raw: dict[int, np.ndarray] = {}
    removed_by_mat: dict[int, int] = {}

    for mat_idx in range(n_mat):
        key = f'indices_{mat_idx:02d}'
        orig = data[key].astype(np.uint32) if key in data else np.array([], dtype=np.uint32)
        if len(orig) == 0:
            new_indices_raw[mat_idx] = orig
            removed_by_mat[mat_idx] = 0
            continue

        a_i, b_i, c_i = orig[0::3], orig[1::3], orig[2::3]
        a, b, c = positions[a_i], positions[b_i], positions[c_i]

        if mat_idx not in MATS_TO_FILTER:
            new_indices_raw[mat_idx] = orig
            removed_by_mat[mat_idx] = 0
            continue

        zc = _tri_z_center(a, b, c)

        # Front: remove tris with Z_center < Z_FRONT_THRESH
        is_front_vien = zc < Z_FRONT_THRESH

        # Back: Z_center > Z_BACK_THRESH AND NOT all-3-verts above Z_BACK_ROOF_GUARD
        is_back_zone = zc > Z_BACK_THRESH
        all_above_guard = (
            (a[:, 2] > Z_BACK_ROOF_GUARD) &
            (b[:, 2] > Z_BACK_ROOF_GUARD) &
            (c[:, 2] > Z_BACK_ROOF_GUARD)
        )
        is_back_vien = is_back_zone & ~all_above_guard

        remove_mask = is_front_vien | is_back_vien
        removed_by_mat[mat_idx] = int(remove_mask.sum())

        keep = ~remove_mask
        kept = np.empty(keep.sum() * 3, dtype=np.uint32)
        kept[0::3] = a_i[keep]
        kept[1::3] = b_i[keep]
        kept[2::3] = c_i[keep]
        new_indices_raw[mat_idx] = kept

    total_removed = sum(removed_by_mat.values())
    print(f'Removed viền nâu triangles: {total_removed}')
    for m, n in removed_by_mat.items():
        if n:
            print(f'  mat {m:02d}: -{n}')

    # Compact unused vertices
    used: list[int] = []
    for idx_arr in new_indices_raw.values():
        used.extend(idx_arr.tolist())
    unique = sorted(set(used))
    mapping = np.full(len(positions), -1, dtype=np.int64)
    for new_i, old_i in enumerate(unique):
        mapping[old_i] = new_i

    new_positions = np.asarray([positions[i] for i in unique], dtype=np.float32)
    new_normals   = np.asarray([normals[i]   for i in unique], dtype=np.float32)
    new_texcoords = np.asarray([texcoords[i] for i in unique], dtype=np.float32)
    print(f'Vertices: {len(positions)} -> {len(new_positions)} (removed {len(positions) - len(new_positions)})')

    arrays: dict[str, np.ndarray] = {
        'positions': new_positions,
        'normals':   new_normals,
        'texcoords': new_texcoords,
    }
    new_index_counts: dict[str, int] = {}
    new_component_types: dict[str, int] = {}

    for mat_idx in range(n_mat):
        orig = new_indices_raw[mat_idx]
        if len(orig) == 0:
            arrays[f'indices_{mat_idx:02d}'] = orig.astype(np.uint32)
            new_index_counts[str(mat_idx)] = 0
            new_component_types[str(mat_idx)] = 5123
            continue
        remapped = mapping[orig].astype(np.int64)
        assert (remapped >= 0).all(), f'mat {mat_idx}: unmapped index'
        remapped = remapped.astype(np.uint32)
        arrays[f'indices_{mat_idx:02d}'] = remapped
        new_index_counts[str(mat_idx)] = int(len(remapped))
        new_component_types[str(mat_idx)] = 5125 if int(remapped.max()) > 65535 else 5123

    stats = {
        'n_orig': len(positions),
        'n_new': len(new_positions),
        'removed_triangles': removed_by_mat,
        'new_index_counts': new_index_counts,
        'new_component_types': new_component_types,
    }
    return arrays, stats


def update_manifest(src_path: Path, arrays: dict, stats: dict) -> dict:
    manifest = json.loads(src_path.read_text(encoding='utf-8'))
    positions = arrays['positions']
    manifest.update({
        'version': 'v45_remove_vien_nau',
        'geometry_npz': V45_GEOM,
        'vertex_count': stats['n_new'],
        'primitive_count': sum(1 for v in stats['new_index_counts'].values() if v > 0),
        'primitive_index_count': stats['new_index_counts'],
        'primitive_component_types': stats['new_component_types'],
        'position_bounds_source': {
            'min': [float(v) for v in positions.min(axis=0)],
            'max': [float(v) for v in positions.max(axis=0)],
        },
        'patch_summary': (
            'v45: xoá viền nâu (cấu trúc gỗ nâu tối mat08 + mat10) ở đầu trước và sau cầu; '
            'giữ nguyên mái gương nhỏ đằng sau và toàn bộ phần còn lại.'
        ),
        'v45_changes': {
            'requested_by_user': 'Xoá viền nâu mái dư ở phía trước và phía sau.',
            'mats_filtered': list(MATS_TO_FILTER),
            'front_z_thresh': Z_FRONT_THRESH,
            'back_z_thresh': Z_BACK_THRESH,
            'back_roof_guard': Z_BACK_ROOF_GUARD,
            'removed_triangles_by_material': stats['removed_triangles'],
        },
    })
    return manifest


def patch_source_files() -> None:
    scene_file = SRC_DIR / 'glb_forge' / 'scenes' / 'chua_cau_hoi_an.py'
    text = scene_file.read_text(encoding='utf-8')
    text = text.replace(V44_GEOM, V45_GEOM)
    text = text.replace(V44_MANIFEST, V45_MANIFEST)
    text = text.replace('v44_remove_front_small_roof', 'v45_remove_vien_nau')
    text = text.replace('v44 remove front small roof', 'v45 remove viền nâu')
    text = text.replace('Không tìm thấy geometry v44', 'Không tìm thấy geometry v45')
    text = text.replace('Không tìm thấy manifest v44', 'Không tìm thấy manifest v45')
    text = text.replace('Geometry v44 không hợp lệ', 'Geometry v45 không hợp lệ')
    text = text.replace('Sai số material so với manifest v44', 'Sai số material so với manifest v45')
    text = text.replace(
        'GLB nâng cấp v44: giữ nguyên v43, xoá mái nhỏ đằng trước, chỉ giữ mái nhỏ đằng sau.',
        'GLB nâng cấp v45: xoá viền nâu (mat08/mat10) đầu trước và sau, giữ mái gương nhỏ.',
    )
    scene_file.write_text(text, encoding='utf-8')
    print('Updated: src/glb_forge/scenes/chua_cau_hoi_an.py')

    main_file = PROJECT_ROOT / 'main.py'
    t = main_file.read_text(encoding='utf-8')
    t = t.replace('v44 remove front small roof', 'v45 remove viền nâu')
    t = t.replace(
        'Bản này giữ nguyên v43 và xoá mái nhỏ đằng trước, chỉ giữ mái nhỏ đằng sau theo yêu cầu.',
        'Bản này xoá viền nâu (mat08/mat10) ở đầu trước và sau; giữ mái gương nhỏ đằng sau.',
    )
    t = t.replace(
        'chua_cau_hoi_an_textured_fixed_v44_remove_front_small_roof.glb',
        V45_OUTPUT,
    )
    main_file.write_text(t, encoding='utf-8')
    print('Updated: main.py')

    registry = SRC_DIR / 'glb_forge' / 'sites' / 'provinces' / 'da_nang.py'
    if registry.exists():
        rt = registry.read_text(encoding='utf-8')
        rt = rt.replace(
            'chua_cau_hoi_an_textured_fixed_v44_remove_front_small_roof',
            'chua_cau_hoi_an_textured_fixed_v45_remove_vien_nau',
        )
        registry.write_text(rt, encoding='utf-8')
        print('Updated: src/glb_forge/sites/provinces/da_nang.py')

    doc = PROJECT_ROOT / 'docs' / 'v45_remove_vien_nau_note.md'
    doc.write_text(
        '# v45 remove viền nâu\n\n'
        '- Giữ nguyên toàn bộ bản v44.\n'
        f'- Xoá mat08 và mat10 ở đầu trước (Z_center < {Z_FRONT_THRESH}) '
        f'và đầu sau (Z_center > {Z_BACK_THRESH}, trừ phần mái gương).\n'
        '- Compact geometry.\n'
        '- Giữ mái gương nhỏ đằng sau và toàn bộ phần còn lại.\n',
        encoding='utf-8',
    )
    print('Created: docs/v45_remove_vien_nau_note.md')


def main() -> None:
    geom_dir = PROJECT_ROOT / 'assets' / 'geometry'
    src_npz = geom_dir / V44_GEOM
    src_manifest = geom_dir / V44_MANIFEST

    if not src_npz.exists():
        raise FileNotFoundError(f'Không tìm thấy geometry v44: {src_npz}')

    manifest_src = json.loads(src_manifest.read_text(encoding='utf-8'))
    n_mat = int(manifest_src.get('material_count', 30))

    print('=== Building v45 geometry ===')
    data = np.load(src_npz)
    arrays, stats = remove_and_compact(data, n_mat)

    dst_npz = geom_dir / V45_GEOM
    np.savez_compressed(dst_npz, **arrays)
    print(f'Saved NPZ: {dst_npz.name}  ({dst_npz.stat().st_size:,} bytes)')

    manifest = update_manifest(src_manifest, arrays, stats)
    dst_manifest = geom_dir / V45_MANIFEST
    dst_manifest.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'Saved manifest: {dst_manifest.name}')

    print()
    print('=== Patching source files ===')
    patch_source_files()

    print()
    print('=== Regenerating GLB ===')
    import subprocess
    result = subprocess.run(
        ['python3.12', str(PROJECT_ROOT / 'main.py')],
        cwd=str(PROJECT_ROOT), capture_output=True, text=True
    )
    if result.returncode != 0:
        print('STDERR:', result.stderr[-1000:])
        raise RuntimeError('main.py failed')
    print(result.stdout)
    print('Done.')


if __name__ == '__main__':
    main()
