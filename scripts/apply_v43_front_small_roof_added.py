from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / 'src'

V42_GEOM = 'chua_cau_hoi_an_v42_back_small_roof_on_red_geometry.npz'
V42_MANIFEST = 'chua_cau_hoi_an_v42_back_small_roof_on_red_manifest.json'
V43_GEOM = 'chua_cau_hoi_an_v43_front_small_roof_added_geometry.npz'
V43_MANIFEST = 'chua_cau_hoi_an_v43_front_small_roof_added_manifest.json'
V43_OUTPUT = 'chua_cau_hoi_an_textured_fixed_v43_front_small_roof_added.glb'

# In v42, the back small roof occupies this vertex span (same as v41 after compaction).
BACK_SMALL_ROOF_START = 217_352
BACK_SMALL_ROOF_END = 250_855  # inclusive


def build_v43_geometry(data: np.lib.npyio.NpzFile) -> tuple[dict[str, np.ndarray], dict]:
    positions = data['positions'].astype(np.float32, copy=True)
    normals = data['normals'].astype(np.float32, copy=True)
    texcoords = data['texcoords'].astype(np.float32, copy=True)

    n_orig = len(positions)

    # Extract back small roof vertices
    roof_pos = positions[BACK_SMALL_ROOF_START:BACK_SMALL_ROOF_END + 1].copy()
    roof_nrm = normals[BACK_SMALL_ROOF_START:BACK_SMALL_ROOF_END + 1].copy()
    roof_uv = texcoords[BACK_SMALL_ROOF_START:BACK_SMALL_ROOF_END + 1].copy()

    print(f'Back small roof vertices: {len(roof_pos)}')
    print(f'  Z: {roof_pos[:, 2].min():.3f} to {roof_pos[:, 2].max():.3f}')
    print(f'  Y: {roof_pos[:, 1].min():.3f} to {roof_pos[:, 1].max():.3f}')

    # Mirror around z=0: negate Z in positions and normals
    mirror_pos = roof_pos.copy()
    mirror_pos[:, 2] *= -1.0

    mirror_nrm = roof_nrm.copy()
    mirror_nrm[:, 2] *= -1.0  # flip Z component of surface normals

    print(f'Mirrored (front) roof:')
    print(f'  Z: {mirror_pos[:, 2].min():.3f} to {mirror_pos[:, 2].max():.3f}')
    print(f'  Y: {mirror_pos[:, 1].min():.3f} to {mirror_pos[:, 1].max():.3f}')

    new_positions = np.concatenate([positions, mirror_pos])
    new_normals = np.concatenate([normals, mirror_nrm])
    new_texcoords = np.concatenate([texcoords, roof_uv])

    n_new = len(new_positions)
    mirror_start = n_orig

    arrays: dict[str, np.ndarray] = {
        'positions': new_positions,
        'normals': new_normals,
        'texcoords': new_texcoords,
    }

    new_index_counts: dict[str, int] = {}
    new_component_types: dict[str, int] = {}

    for mat_idx in range(30):
        key = f'indices_{mat_idx:02d}'
        orig = data[key].astype(np.uint32) if key in data else np.array([], dtype=np.uint32)

        if len(orig) == 0:
            arrays[key] = orig
            new_index_counts[str(mat_idx)] = 0
            new_component_types[str(mat_idx)] = 5123
            continue

        a, b, c = orig[0::3], orig[1::3], orig[2::3]
        in_roof = (
            (a >= BACK_SMALL_ROOF_START) & (a <= BACK_SMALL_ROOF_END) &
            (b >= BACK_SMALL_ROOF_START) & (b <= BACK_SMALL_ROOF_END) &
            (c >= BACK_SMALL_ROOF_START) & (c <= BACK_SMALL_ROOF_END)
        )

        if np.any(in_roof):
            # Remap to new mirror vertex indices; reverse winding so normals face correctly
            ma = a[in_roof] - BACK_SMALL_ROOF_START + mirror_start
            mb = b[in_roof] - BACK_SMALL_ROOF_START + mirror_start
            mc = c[in_roof] - BACK_SMALL_ROOF_START + mirror_start

            new_tris = np.empty(len(ma) * 3, dtype=np.uint32)
            new_tris[0::3] = ma
            new_tris[1::3] = mc  # reversed b↔c for mirrored winding
            new_tris[2::3] = mb

            combined = np.concatenate([orig, new_tris]).astype(np.uint32)
            print(f'  mat {mat_idx}: {len(orig) // 3} + {len(ma)} mirror = {len(combined) // 3} tris')
        else:
            combined = orig

        arrays[key] = combined
        new_index_counts[str(mat_idx)] = int(len(combined))
        new_component_types[str(mat_idx)] = 5125 if int(combined.max()) > 65535 else 5123

    stats = {
        'n_orig': n_orig,
        'n_new': n_new,
        'mirror_vertex_span': [mirror_start, n_new - 1],
        'new_index_counts': new_index_counts,
    }
    return arrays, stats


def update_manifest(src_path: Path, arrays: dict, stats: dict) -> dict:
    manifest = json.loads(src_path.read_text(encoding='utf-8'))
    positions = arrays['positions']
    manifest.update({
        'version': 'v43_front_small_roof_added',
        'geometry_npz': V43_GEOM,
        'vertex_count': stats['n_new'],
        'primitive_index_count': stats['new_index_counts'],
        'position_bounds_source': {
            'min': [float(v) for v in positions.min(axis=0)],
            'max': [float(v) for v in positions.max(axis=0)],
        },
        'patch_summary': (
            'v43: giữ nguyên v42, thêm mái nhỏ đối xứng ở đầu phía trước (+Z) '
            'bằng cách lật gương mái nhỏ phía sau quanh z=0.'
        ),
        'v43_changes': {
            'requested_by_user': (
                'Thêm mái nhỏ (hình 2) lên vùng màu đỏ ở đầu còn lại (hình 3); '
                'các phần còn lại giữ nguyên.'
            ),
            'geometry_action': (
                'Mirror back small roof vertices (217352..250855) around z=0: '
                'negate Z in positions and normals, reverse triangle winding.'
            ),
            'source_vertex_span': [BACK_SMALL_ROOF_START, BACK_SMALL_ROOF_END],
            'new_vertex_span': stats['mirror_vertex_span'],
        },
    })
    # Sync primitive_component_types
    for k, v in stats['new_index_counts'].items():
        if v > 0:
            mat_indices = arrays[f'indices_{int(k):02d}']
            manifest['primitive_component_types'][k] = 5125 if int(mat_indices.max()) > 65535 else 5123
        else:
            manifest['primitive_component_types'][k] = 5123
    return manifest


def patch_source_files() -> None:
    scene_file = SRC_DIR / 'glb_forge' / 'scenes' / 'chua_cau_hoi_an.py'
    text = scene_file.read_text(encoding='utf-8')
    text = text.replace('bản v42 back small roof on red', 'bản v43 front small roof added')
    text = text.replace('v42 back small roof on red', 'v43 front small roof added')
    text = text.replace(V42_GEOM, V43_GEOM)
    text = text.replace(V42_MANIFEST, V43_MANIFEST)
    text = text.replace('Không tìm thấy manifest v42', 'Không tìm thấy manifest v43')
    text = text.replace('Không tìm thấy geometry v42', 'Không tìm thấy geometry v43')
    text = text.replace('Geometry v42 không hợp lệ', 'Geometry v43 không hợp lệ')
    text = text.replace('Sai số material so với manifest v42', 'Sai số material so với manifest v43')
    text = text.replace(
        'GLB nâng cấp v42: giữ nguyên v41, chỉ di chuyển mái nhỏ phía sau lên vùng màu đỏ.',
        'GLB nâng cấp v43: giữ nguyên v42, thêm mái nhỏ đối xứng ở đầu phía trước.',
    )
    scene_file.write_text(text, encoding='utf-8')
    print(f'Updated: {scene_file.relative_to(PROJECT_ROOT)}')

    main_file = PROJECT_ROOT / 'main.py'
    main_text = main_file.read_text(encoding='utf-8')
    main_text = main_text.replace('bản v42 back small roof on red', 'bản v43 front small roof added')
    main_text = main_text.replace(
        'Bản này giữ nguyên v41 và chỉ di chuyển mái nhỏ phía sau lên vùng màu đỏ theo yêu cầu.',
        'Bản này giữ nguyên v42 và thêm mái nhỏ đối xứng ở đầu phía trước (hình 3) theo yêu cầu.',
    )
    main_text = main_text.replace(
        'chua_cau_hoi_an_textured_fixed_v42_back_small_roof_on_red.glb', V43_OUTPUT
    )
    main_file.write_text(main_text, encoding='utf-8')
    print(f'Updated: main.py')

    registry = SRC_DIR / 'glb_forge' / 'sites' / 'provinces' / 'da_nang.py'
    if registry.exists():
        rt = registry.read_text(encoding='utf-8')
        rt = rt.replace(
            'chua_cau_hoi_an_textured_fixed_v42_back_small_roof_on_red',
            'chua_cau_hoi_an_textured_fixed_v43_front_small_roof_added',
        )
        registry.write_text(rt, encoding='utf-8')
        print(f'Updated: {registry.relative_to(PROJECT_ROOT)}')

    doc_path = PROJECT_ROOT / 'docs' / 'v43_front_small_roof_added_note.md'
    doc_path.write_text(
        '# v43 front small roof added\n\n'
        '- Giữ nguyên toàn bộ bản v42.\n'
        f'- Lấy mái nhỏ phía sau (vertex span v42 {BACK_SMALL_ROOF_START}..{BACK_SMALL_ROOF_END}).\n'
        '- Lật gương quanh z=0 (negate Z trong positions và normals, đảo winding).\n'
        '- Thêm mái nhỏ đối xứng ở đầu phía trước (+Z), ngay trên vùng màu đỏ (hình 3).\n',
        encoding='utf-8',
    )
    print(f'Created: docs/v43_front_small_roof_added_note.md')


def main() -> None:
    geom_dir = PROJECT_ROOT / 'assets' / 'geometry'
    src_npz = geom_dir / V42_GEOM
    src_manifest = geom_dir / V42_MANIFEST

    if not src_npz.exists():
        raise FileNotFoundError(f'Không tìm thấy geometry v42: {src_npz}')
    if not src_manifest.exists():
        raise FileNotFoundError(f'Không tìm thấy manifest v42: {src_manifest}')

    print('=== Building v43 geometry ===')
    data = np.load(src_npz)
    arrays, stats = build_v43_geometry(data)

    dst_npz = geom_dir / V43_GEOM
    np.savez_compressed(dst_npz, **arrays)
    print(f'Saved NPZ: {dst_npz.name}  ({dst_npz.stat().st_size:,} bytes)')

    manifest = update_manifest(src_manifest, arrays, stats)
    dst_manifest = geom_dir / V43_MANIFEST
    dst_manifest.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'Saved manifest: {dst_manifest.name}')

    print()
    print('=== Patching source files ===')
    patch_source_files()

    # Delete old v42 output GLB (user request)
    old_glb = PROJECT_ROOT / 'output' / 'chua_cau_hoi_an_textured_fixed_v42_back_small_roof_on_red.glb'
    if old_glb.exists():
        old_glb.unlink()
        print(f'Deleted: output/{old_glb.name}')

    old_glb_49 = PROJECT_ROOT / 'output' / '49_da_nang' / 'chua_cau_hoi_an_textured_fixed_v42_back_small_roof_on_red.glb'
    if old_glb_49.exists():
        old_glb_49.unlink()
        print(f'Deleted: output/49_da_nang/{old_glb_49.name}')

    print()
    print('=== Regenerating GLB via main.py ===')
    import subprocess
    subprocess.run([sys.executable, str(PROJECT_ROOT / 'main.py')], cwd=str(PROJECT_ROOT), check=True)
    print('Done.')


if __name__ == '__main__':
    main()
