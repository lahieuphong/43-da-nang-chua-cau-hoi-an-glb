from __future__ import annotations

"""v48: Xoá thanh nâu mat13 phía trước (Z_center < Z_FRONT_THRESH).

Lấy v47 làm base. Xoá các triangle của mat13 (dark oxidized red lacquer)
ở mặt TRƯỚC cầu (Z_center < -1.5), tức là phần "dải ngang" / thanh cong
lên-ngang-xuống hiển thị bên dưới mái ngói khi nhìn từ phía trước.
Compact geometry sau khi xoá.
"""

import json
import subprocess
from pathlib import Path

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / 'src'

V47_GEOM     = 'chua_cau_hoi_an_v47_roof_curve_geometry.npz'
V47_MANIFEST = 'chua_cau_hoi_an_v47_roof_curve_manifest.json'
V48_GEOM     = 'chua_cau_hoi_an_v48_remove_front_mat13_geometry.npz'
V48_MANIFEST = 'chua_cau_hoi_an_v48_remove_front_mat13_manifest.json'
V48_OUTPUT   = 'chua_cau_hoi_an_textured_fixed_v48_remove_front_mat13.glb'

# Xoá mat13 ở mặt trước (Z_center < ngưỡng này)
Z_FRONT_THRESH = -1.5
MAT_TO_REMOVE = 13


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

        if mat_idx != MAT_TO_REMOVE:
            new_indices_raw[mat_idx] = orig
            removed_by_mat[mat_idx] = 0
            continue

        a_i, b_i, c_i = orig[0::3], orig[1::3], orig[2::3]
        a, b, c = positions[a_i], positions[b_i], positions[c_i]
        zc = (a[:, 2] + b[:, 2] + c[:, 2]) / 3.0

        # Xoá các triangle ở mặt trước (Z_center < Z_FRONT_THRESH)
        remove_mask = zc < Z_FRONT_THRESH
        removed_by_mat[mat_idx] = int(remove_mask.sum())

        keep = ~remove_mask
        kept = np.empty(keep.sum() * 3, dtype=np.uint32)
        kept[0::3] = a_i[keep]
        kept[1::3] = b_i[keep]
        kept[2::3] = c_i[keep]
        new_indices_raw[mat_idx] = kept

    total_removed = sum(removed_by_mat.values())
    print(f'Removed front mat13 triangles: {total_removed}')
    for m, n in removed_by_mat.items():
        if n:
            print(f'  mat{m:02d}: -{n}')

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
    print(f'Vertices: {len(positions):,} -> {len(new_positions):,} (removed {len(positions)-len(new_positions):,})')

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
        'n_orig': int(len(positions)),
        'n_new':  int(len(new_positions)),
        'removed_triangles': removed_by_mat,
        'new_index_counts': new_index_counts,
        'new_component_types': new_component_types,
    }
    return arrays, stats


def update_manifest(src_path: Path, arrays: dict, stats: dict) -> dict:
    manifest = json.loads(src_path.read_text(encoding='utf-8'))
    positions = arrays['positions']
    manifest.update({
        'version': 'v48_remove_front_mat13',
        'geometry_npz': V48_GEOM,
        'vertex_count': stats['n_new'],
        'primitive_count': sum(1 for v in stats['new_index_counts'].values() if v > 0),
        'primitive_index_count': stats['new_index_counts'],
        'primitive_component_types': stats['new_component_types'],
        'position_bounds_source': {
            'min': [float(v) for v in positions.min(axis=0)],
            'max': [float(v) for v in positions.max(axis=0)],
        },
        'patch_summary': (
            f'v48: base là v47; xoá mat13 (thanh nâu cong) ở mặt trước '
            f'(Z_center < {Z_FRONT_THRESH}). Giữ mat13 phần còn lại (mặt sau, cột giữa).'
        ),
        'v48_changes': {
            'requested_by_user': 'Bỏ phần dải ngang (thanh nâu mat13) hiển thị phía đằng trước.',
            'base_version': 'v47',
            'mat_removed': MAT_TO_REMOVE,
            'z_front_thresh': Z_FRONT_THRESH,
            'removed_triangles_by_material': stats['removed_triangles'],
        },
    })
    return manifest


def patch_source_files() -> None:
    scene_file = SRC_DIR / 'glb_forge' / 'scenes' / 'chua_cau_hoi_an.py'
    text = scene_file.read_text(encoding='utf-8')
    text = text.replace(V47_GEOM, V48_GEOM)
    text = text.replace(V47_MANIFEST, V48_MANIFEST)
    text = text.replace('v47_roof_curve', 'v48_remove_front_mat13')
    text = text.replace('v47 roof curve', 'v48 remove front mat13')
    text = text.replace('Không tìm thấy geometry v47', 'Không tìm thấy geometry v48')
    text = text.replace('Không tìm thấy manifest v47', 'Không tìm thấy manifest v48')
    text = text.replace('Geometry v47 không hợp lệ', 'Geometry v48 không hợp lệ')
    text = text.replace('Sai số material so với manifest v47', 'Sai số material so với manifest v48')
    text = text.replace(
        'GLB nâng cấp v47: base=v46, áp đường cong lên-ngang-xuống cho mái ngói.',
        'GLB nâng cấp v48: base=v47, xoá mat13 thanh nâu cong mặt trước.',
    )
    scene_file.write_text(text, encoding='utf-8')
    print('Updated: src/glb_forge/scenes/chua_cau_hoi_an.py')

    main_file = PROJECT_ROOT / 'main.py'
    t = main_file.read_text(encoding='utf-8')
    t = t.replace('v47 roof curve', 'v48 remove front mat13')
    t = t.replace(
        'Bản này base=v47, áp đường cong lên-ngang-xuống cho mái ngói (mat16-23).',
        'Bản này base=v47, xoá mat13 (thanh nâu cong) hiển thị ở mặt trước cầu.',
    )
    t = t.replace(
        'chua_cau_hoi_an_textured_fixed_v47_roof_curve.glb',
        V48_OUTPUT,
    )
    main_file.write_text(t, encoding='utf-8')
    print('Updated: main.py')

    registry = SRC_DIR / 'glb_forge' / 'sites' / 'provinces' / 'da_nang.py'
    if registry.exists():
        rt = registry.read_text(encoding='utf-8')
        rt = rt.replace(
            'chua_cau_hoi_an_textured_fixed_v47_roof_curve',
            'chua_cau_hoi_an_textured_fixed_v48_remove_front_mat13',
        )
        registry.write_text(rt, encoding='utf-8')
        print('Updated: src/glb_forge/sites/provinces/da_nang.py')

    doc = PROJECT_ROOT / 'docs' / 'v48_remove_front_mat13_note.md'
    doc.write_text(
        '# v48 remove front mat13\n\n'
        '- Base là v47 (v46 + mái ngói cong lên-ngang-xuống).\n'
        f'- Xoá mat13 (dark oxidized red lacquer / thanh nâu cong) ở mặt TRƯỚC '
        f'(Z_center < {Z_FRONT_THRESH}).\n'
        '- Giữ nguyên mat13 ở mặt sau và các cột giữa bên trong.\n'
        '- Compact geometry.\n',
        encoding='utf-8',
    )
    print('Created: docs/v48_remove_front_mat13_note.md')


def main() -> None:
    geom_dir = PROJECT_ROOT / 'assets' / 'geometry'
    src_npz      = geom_dir / V47_GEOM
    src_manifest = geom_dir / V47_MANIFEST

    if not src_npz.exists():
        raise FileNotFoundError(f'Không tìm thấy geometry v47: {src_npz}')

    manifest_src = json.loads(src_manifest.read_text(encoding='utf-8'))
    n_mat = int(manifest_src.get('material_count', 30))

    print('=== Building v48 geometry (base: v47, remove front mat13) ===')
    data = np.load(src_npz)
    arrays, stats = remove_and_compact(data, n_mat)

    dst_npz = geom_dir / V48_GEOM
    np.savez_compressed(dst_npz, **arrays)
    print(f'Saved NPZ: {dst_npz.name}  ({dst_npz.stat().st_size:,} bytes)')

    manifest = update_manifest(src_manifest, arrays, stats)
    dst_manifest = geom_dir / V48_MANIFEST
    dst_manifest.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'Saved manifest: {dst_manifest.name}')

    print()
    print('=== Patching source files ===')
    patch_source_files()

    print()
    print('=== Regenerating GLB ===')
    result = subprocess.run(
        ['python3.12', str(PROJECT_ROOT / 'main.py')],
        cwd=str(PROJECT_ROOT), capture_output=True, text=True,
    )
    if result.returncode != 0:
        print('STDERR:', result.stderr[-2000:])
        raise RuntimeError('main.py failed')
    print(result.stdout)
    print('Done.')


if __name__ == '__main__':
    main()
