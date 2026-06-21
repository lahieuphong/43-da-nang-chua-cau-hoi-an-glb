from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / 'src'

V43_GEOM = 'chua_cau_hoi_an_v43_front_small_roof_added_geometry.npz'
V43_MANIFEST = 'chua_cau_hoi_an_v43_front_small_roof_added_manifest.json'
V44_GEOM = 'chua_cau_hoi_an_v44_remove_front_small_roof_geometry.npz'
V44_MANIFEST = 'chua_cau_hoi_an_v44_remove_front_small_roof_manifest.json'
V44_OUTPUT = 'chua_cau_hoi_an_textured_fixed_v44_remove_front_small_roof.glb'

# In v43: original back-small-roof (now at -Z / "front face") occupies this span.
FRONT_ROOF_START = 217_352
FRONT_ROOF_END = 250_855  # inclusive — these get removed


def remove_and_compact(data: np.lib.npyio.NpzFile, n_mat: int) -> tuple[dict, dict]:
    positions = data['positions'].astype(np.float32, copy=True)
    normals   = data['normals'].astype(np.float32, copy=True)
    texcoords = data['texcoords'].astype(np.float32, copy=True)

    # Step 1 – drop all triangles whose 3 vertices all fall in the front-roof span.
    new_indices_raw: dict[int, np.ndarray] = {}
    removed_by_mat: dict[int, int] = {}

    for mat_idx in range(n_mat):
        key = f'indices_{mat_idx:02d}'
        orig = data[key].astype(np.uint32) if key in data else np.array([], dtype=np.uint32)
        if len(orig) == 0:
            new_indices_raw[mat_idx] = orig
            removed_by_mat[mat_idx] = 0
            continue

        a, b, c = orig[0::3], orig[1::3], orig[2::3]
        in_front = (
            (a >= FRONT_ROOF_START) & (a <= FRONT_ROOF_END) &
            (b >= FRONT_ROOF_START) & (b <= FRONT_ROOF_END) &
            (c >= FRONT_ROOF_START) & (c <= FRONT_ROOF_END)
        )
        removed_by_mat[mat_idx] = int(in_front.sum())
        keep = ~in_front
        kept = np.empty(keep.sum() * 3, dtype=np.uint32)
        kept[0::3] = a[keep]; kept[1::3] = b[keep]; kept[2::3] = c[keep]
        new_indices_raw[mat_idx] = kept

    total_removed = sum(removed_by_mat.values())
    print(f'Removed front-roof triangles: {total_removed}')
    for m, n in removed_by_mat.items():
        if n:
            print(f'  mat {m}: -{n}')

    # Step 2 – compact: collect used vertex indices and remap.
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

    print(f'Vertices: {len(positions)} -> {len(new_positions)} (removed {len(positions)-len(new_positions)})')

    # Step 3 – remap index arrays.
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
        assert (remapped >= 0).all(), f'mat {mat_idx}: unmapped index found'
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
        'version': 'v44_remove_front_small_roof',
        'geometry_npz': V44_GEOM,
        'vertex_count': stats['n_new'],
        'primitive_count': sum(1 for v in stats['new_index_counts'].values() if v > 0),
        'primitive_index_count': stats['new_index_counts'],
        'primitive_component_types': stats['new_component_types'],
        'position_bounds_source': {
            'min': [float(v) for v in positions.min(axis=0)],
            'max': [float(v) for v in positions.max(axis=0)],
        },
        'patch_summary': (
            'v44: giữ nguyên v43, xoá mái nhỏ đằng trước (-Z span 217352..250855); '
            'chỉ giữ mái nhỏ đằng sau (+Z mirror) và toàn bộ phần còn lại.'
        ),
        'v44_changes': {
            'requested_by_user': 'Xoá mái nhỏ đằng trước, giữ mái nhỏ đằng sau và phần còn lại.',
            'removed_vertex_span_v43': [FRONT_ROOF_START, FRONT_ROOF_END],
            'removed_triangles_by_material': stats['removed_triangles'],
        },
    })
    return manifest


def patch_source_files() -> None:
    scene_file = SRC_DIR / 'glb_forge' / 'scenes' / 'chua_cau_hoi_an.py'
    text = scene_file.read_text(encoding='utf-8')
    text = text.replace('bản v43 front small roof added', 'bản v44 remove front small roof')
    text = text.replace('v43 front small roof added', 'v44 remove front small roof')
    text = text.replace(V43_GEOM, V44_GEOM)
    text = text.replace(V43_MANIFEST, V44_MANIFEST)
    for old, new in [('v43', 'v44'), ('Geometry v43', 'Geometry v44'),
                     ('manifest v43', 'manifest v44'), ('manifest v43', 'manifest v44')]:
        text = text.replace(f'Không tìm thấy {old}', f'Không tìm thấy {new}') if old.startswith('m') else text
    text = text.replace('Không tìm thấy manifest v43', 'Không tìm thấy manifest v44')
    text = text.replace('Không tìm thấy geometry v43', 'Không tìm thấy geometry v44')
    text = text.replace('Geometry v43 không hợp lệ', 'Geometry v44 không hợp lệ')
    text = text.replace('Sai số material so với manifest v43', 'Sai số material so với manifest v44')
    text = text.replace(
        'GLB nâng cấp v43: giữ nguyên v42, thêm mái nhỏ đối xứng ở đầu phía trước.',
        'GLB nâng cấp v44: giữ nguyên v43, xoá mái nhỏ đằng trước, chỉ giữ mái nhỏ đằng sau.',
    )
    scene_file.write_text(text, encoding='utf-8')
    print(f'Updated: src/glb_forge/scenes/chua_cau_hoi_an.py')

    main_file = PROJECT_ROOT / 'main.py'
    t = main_file.read_text(encoding='utf-8')
    t = t.replace('bản v43 front small roof added', 'bản v44 remove front small roof')
    t = t.replace(
        'Bản này giữ nguyên v42 và thêm mái nhỏ đối xứng ở đầu phía trước (hình 3) theo yêu cầu.',
        'Bản này giữ nguyên v43 và xoá mái nhỏ đằng trước, chỉ giữ mái nhỏ đằng sau theo yêu cầu.',
    )
    t = t.replace('chua_cau_hoi_an_textured_fixed_v43_front_small_roof_added.glb', V44_OUTPUT)
    main_file.write_text(t, encoding='utf-8')
    print('Updated: main.py')

    registry = SRC_DIR / 'glb_forge' / 'sites' / 'provinces' / 'da_nang.py'
    if registry.exists():
        rt = registry.read_text(encoding='utf-8')
        rt = rt.replace(
            'chua_cau_hoi_an_textured_fixed_v43_front_small_roof_added',
            'chua_cau_hoi_an_textured_fixed_v44_remove_front_small_roof',
        )
        registry.write_text(rt, encoding='utf-8')
        print(f'Updated: src/glb_forge/sites/provinces/da_nang.py')

    doc = PROJECT_ROOT / 'docs' / 'v44_remove_front_small_roof_note.md'
    doc.write_text(
        '# v44 remove front small roof\n\n'
        '- Giữ nguyên toàn bộ bản v43.\n'
        f'- Xoá mái nhỏ đằng trước (-Z): vertex span v43 {FRONT_ROOF_START}..{FRONT_ROOF_END}.\n'
        '- Compact lại geometry (loại bỏ vertices không dùng).\n'
        '- Chỉ giữ mái nhỏ đằng sau (+Z mirror) và toàn bộ phần còn lại.\n',
        encoding='utf-8',
    )
    print('Created: docs/v44_remove_front_small_roof_note.md')


def main() -> None:
    geom_dir = PROJECT_ROOT / 'assets' / 'geometry'
    src_npz = geom_dir / V43_GEOM
    src_manifest = geom_dir / V43_MANIFEST

    if not src_npz.exists():
        raise FileNotFoundError(f'Không tìm thấy geometry v43: {src_npz}')

    manifest_src = json.loads(src_manifest.read_text(encoding='utf-8'))
    n_mat = int(manifest_src.get('material_count', 30))

    print('=== Building v44 geometry ===')
    data = np.load(src_npz)
    arrays, stats = remove_and_compact(data, n_mat)

    dst_npz = geom_dir / V44_GEOM
    np.savez_compressed(dst_npz, **arrays)
    print(f'Saved NPZ: {dst_npz.name}  ({dst_npz.stat().st_size:,} bytes)')

    manifest = update_manifest(src_manifest, arrays, stats)
    dst_manifest = geom_dir / V44_MANIFEST
    dst_manifest.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'Saved manifest: {dst_manifest.name}')

    print()
    print('=== Patching source files ===')
    patch_source_files()

    print()
    print('=== Regenerating GLB ===')
    import subprocess
    subprocess.run([sys.executable, str(PROJECT_ROOT / 'main.py')],
                  cwd=str(PROJECT_ROOT), check=True)
    print('Done.')


if __name__ == '__main__':
    main()
