from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / 'src'

# Start from v44 (front is v44-intact), only remove BACK viền nâu
V44_GEOM     = 'chua_cau_hoi_an_v44_remove_front_small_roof_geometry.npz'
V44_MANIFEST = 'chua_cau_hoi_an_v44_remove_front_small_roof_manifest.json'
V46_GEOM     = 'chua_cau_hoi_an_v46_remove_back_vien_nau_geometry.npz'
V46_MANIFEST = 'chua_cau_hoi_an_v46_remove_back_vien_nau_manifest.json'
V46_OUTPUT   = 'chua_cau_hoi_an_textured_fixed_v46_remove_back_vien_nau.glb'

# BACK only: mat08 + mat10 with Z_center > threshold, excluding mirror-small-roof face panels
Z_BACK_THRESH     = 2.0
Z_BACK_ROOF_GUARD = 2.8   # tris where ALL 3 verts Z > this → mirror small roof → KEEP
MATS_TO_FILTER    = {8, 10}


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

        zc = (a[:, 2] + b[:, 2] + c[:, 2]) / 3.0

        # BACK only: Z_center > Z_BACK_THRESH AND NOT all-3-verts above Z_BACK_ROOF_GUARD
        is_back_zone = zc > Z_BACK_THRESH
        all_above_guard = (
            (a[:, 2] > Z_BACK_ROOF_GUARD) &
            (b[:, 2] > Z_BACK_ROOF_GUARD) &
            (c[:, 2] > Z_BACK_ROOF_GUARD)
        )
        remove_mask = is_back_zone & ~all_above_guard
        removed_by_mat[mat_idx] = int(remove_mask.sum())

        keep = ~remove_mask
        kept = np.empty(keep.sum() * 3, dtype=np.uint32)
        kept[0::3] = a_i[keep]
        kept[1::3] = b_i[keep]
        kept[2::3] = c_i[keep]
        new_indices_raw[mat_idx] = kept

    total_removed = sum(removed_by_mat.values())
    print(f'Removed back viền nâu triangles: {total_removed}')
    for m, n in removed_by_mat.items():
        if n:
            print(f'  mat {m:02d}: -{n}')

    # Compact
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
        'version': 'v46_remove_back_vien_nau',
        'geometry_npz': V46_GEOM,
        'vertex_count': stats['n_new'],
        'primitive_count': sum(1 for v in stats['new_index_counts'].values() if v > 0),
        'primitive_index_count': stats['new_index_counts'],
        'primitive_component_types': stats['new_component_types'],
        'position_bounds_source': {
            'min': [float(v) for v in positions.min(axis=0)],
            'max': [float(v) for v in positions.max(axis=0)],
        },
        'patch_summary': (
            'v46: base là v44 (mặt trước giữ nguyên như v44); '
            'chỉ xoá viền nâu mat08/mat10 ở đầu SAU (+Z), giữ mái gương nhỏ đằng sau.'
        ),
        'v46_changes': {
            'requested_by_user': 'Trả lại mặt trước như v44, chỉ xoá viền nâu đầu sau.',
            'base_version': 'v44',
            'mats_filtered': list(MATS_TO_FILTER),
            'back_z_thresh': Z_BACK_THRESH,
            'back_roof_guard': Z_BACK_ROOF_GUARD,
            'removed_triangles_by_material': stats['removed_triangles'],
        },
    })
    return manifest


def patch_source_files() -> None:
    scene_file = SRC_DIR / 'glb_forge' / 'scenes' / 'chua_cau_hoi_an.py'
    text = scene_file.read_text(encoding='utf-8')
    # Update geometry/manifest paths (may currently point to v44 or v45)
    for old_geom in [
        'chua_cau_hoi_an_v45_remove_vien_nau_geometry.npz',
        'chua_cau_hoi_an_v44_remove_front_small_roof_geometry.npz',
    ]:
        text = text.replace(old_geom, V46_GEOM)
    for old_man in [
        'chua_cau_hoi_an_v45_remove_vien_nau_manifest.json',
        'chua_cau_hoi_an_v44_remove_front_small_roof_manifest.json',
    ]:
        text = text.replace(old_man, V46_MANIFEST)
    for old_ver, new_ver in [
        ('v45_remove_vien_nau', 'v46_remove_back_vien_nau'),
        ('v44_remove_front_small_roof', 'v46_remove_back_vien_nau'),
        ('v45 remove viền nâu', 'v46 remove back viền nâu'),
        ('v44 remove front small roof', 'v46 remove back viền nâu'),
        ('Không tìm thấy geometry v45', 'Không tìm thấy geometry v46'),
        ('Không tìm thấy geometry v44', 'Không tìm thấy geometry v46'),
        ('Không tìm thấy manifest v45', 'Không tìm thấy manifest v46'),
        ('Không tìm thấy manifest v44', 'Không tìm thấy manifest v46'),
        ('Geometry v45 không hợp lệ', 'Geometry v46 không hợp lệ'),
        ('Geometry v44 không hợp lệ', 'Geometry v46 không hợp lệ'),
        ('Sai số material so với manifest v45', 'Sai số material so với manifest v46'),
        ('Sai số material so với manifest v44', 'Sai số material so với manifest v46'),
    ]:
        text = text.replace(old_ver, new_ver)
    # Update comment line
    for old_c in [
        'GLB nâng cấp v45: xoá viền nâu (mat08/mat10) đầu trước và sau, giữ mái gương nhỏ.',
        'GLB nâng cấp v44: giữ nguyên v43, xoá mái nhỏ đằng trước, chỉ giữ mái nhỏ đằng sau.',
    ]:
        text = text.replace(old_c, 'GLB nâng cấp v46: mặt trước như v44, xoá viền nâu đầu sau.')
    scene_file.write_text(text, encoding='utf-8')
    print('Updated: src/glb_forge/scenes/chua_cau_hoi_an.py')

    main_file = PROJECT_ROOT / 'main.py'
    t = main_file.read_text(encoding='utf-8')
    for old_o, new_o in [
        ('chua_cau_hoi_an_textured_fixed_v45_remove_vien_nau.glb', V46_OUTPUT),
        ('chua_cau_hoi_an_textured_fixed_v44_remove_front_small_roof.glb', V46_OUTPUT),
    ]:
        t = t.replace(old_o, new_o)
    for old_d, new_d in [
        ('v45 remove viền nâu', 'v46 remove back viền nâu'),
        ('v44 remove front small roof', 'v46 remove back viền nâu'),
        ('Bản này xoá viền nâu (mat08/mat10) ở đầu trước và sau; giữ mái gương nhỏ đằng sau.',
         'Bản này giữ mặt trước như v44, chỉ xoá viền nâu đầu sau; giữ mái gương nhỏ đằng sau.'),
        ('Bản này giữ nguyên v43 và xoá mái nhỏ đằng trước, chỉ giữ mái nhỏ đằng sau theo yêu cầu.',
         'Bản này giữ mặt trước như v44, chỉ xoá viền nâu đầu sau; giữ mái gương nhỏ đằng sau.'),
    ]:
        t = t.replace(old_d, new_d)
    main_file.write_text(t, encoding='utf-8')
    print('Updated: main.py')

    registry = SRC_DIR / 'glb_forge' / 'sites' / 'provinces' / 'da_nang.py'
    if registry.exists():
        rt = registry.read_text(encoding='utf-8')
        for old_r, new_r in [
            ('chua_cau_hoi_an_textured_fixed_v45_remove_vien_nau',
             'chua_cau_hoi_an_textured_fixed_v46_remove_back_vien_nau'),
            ('chua_cau_hoi_an_textured_fixed_v44_remove_front_small_roof',
             'chua_cau_hoi_an_textured_fixed_v46_remove_back_vien_nau'),
        ]:
            rt = rt.replace(old_r, new_r)
        registry.write_text(rt, encoding='utf-8')
        print('Updated: src/glb_forge/sites/provinces/da_nang.py')

    doc = PROJECT_ROOT / 'docs' / 'v46_remove_back_vien_nau_note.md'
    doc.write_text(
        '# v46 remove back viền nâu\n\n'
        '- Base là v44 (mặt trước giữ nguyên như v44).\n'
        f'- Xoá mat08 và mat10 ở đầu SAU (Z_center > {Z_BACK_THRESH}), '
        f'trừ phần mái gương nhỏ (all Z > {Z_BACK_ROOF_GUARD}).\n'
        '- Compact geometry.\n'
        '- Mặt trước và mái gương nhỏ đằng sau được giữ nguyên.\n',
        encoding='utf-8',
    )
    print('Created: docs/v46_remove_back_vien_nau_note.md')


def main() -> None:
    geom_dir = PROJECT_ROOT / 'assets' / 'geometry'
    src_npz      = geom_dir / V44_GEOM
    src_manifest = geom_dir / V44_MANIFEST

    if not src_npz.exists():
        raise FileNotFoundError(f'Không tìm thấy geometry v44: {src_npz}')

    manifest_src = json.loads(src_manifest.read_text(encoding='utf-8'))
    n_mat = int(manifest_src.get('material_count', 30))

    print('=== Building v46 geometry (base: v44) ===')
    data = np.load(src_npz)
    arrays, stats = remove_and_compact(data, n_mat)

    dst_npz = geom_dir / V46_GEOM
    np.savez_compressed(dst_npz, **arrays)
    print(f'Saved NPZ: {dst_npz.name}  ({dst_npz.stat().st_size:,} bytes)')

    manifest = update_manifest(src_manifest, arrays, stats)
    dst_manifest = geom_dir / V46_MANIFEST
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
