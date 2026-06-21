from __future__ import annotations

"""v47: Áp dụng đường cong lên-ngang-xuống cho mái ngói (mat16-23).

Lấy v46 làm base. Dịch chuyển Y của các vertex mái theo hàm parabol đối xứng
theo X, giống profile thanh nâu (mat13): giữa phẳng cao, hai đầu thấp xuống.
Không xoá tam giác nào — chỉ sửa tọa độ Y của vertex mái.
"""

import json
import subprocess
import sys
from pathlib import Path

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / 'src'

V46_GEOM     = 'chua_cau_hoi_an_v46_remove_back_vien_nau_geometry.npz'
V46_MANIFEST = 'chua_cau_hoi_an_v46_remove_back_vien_nau_manifest.json'
V47_GEOM     = 'chua_cau_hoi_an_v47_roof_curve_geometry.npz'
V47_MANIFEST = 'chua_cau_hoi_an_v47_roof_curve_manifest.json'
V47_OUTPUT   = 'chua_cau_hoi_an_textured_fixed_v47_roof_curve.glb'

# Vật liệu được áp đường cong (mái ngói + gốm viền mái)
ARCH_MATS = {16, 17, 18, 19, 20, 21, 22, 23}

# Tham số đường cong: parabol Y_offset(X) = -MAX_DROP * (X/DESCENT_HALF)^2
# Giữa (X=0): không đổi; hai đầu (|X|=DESCENT_HALF): thấp xuống MAX_DROP
MAX_DROP     = 0.25   # (m) độ dốc tối đa ở hai đầu cầu
DESCENT_HALF = 5.5    # (m) vị trí X tham chiếu, ≈ mép mái


def arch_y_offset(x: np.ndarray) -> np.ndarray:
    """Parabol đối xứng: center=0, edge=-MAX_DROP."""
    t = np.clip(np.abs(x) / DESCENT_HALF, 0.0, 1.0)
    return (-MAX_DROP * t ** 2).astype(np.float32)


def apply_arch_to_geometry(data: np.lib.npyio.NpzFile, n_mat: int):
    positions = data['positions'].astype(np.float32, copy=True)
    normals   = data['normals'].astype(np.float32, copy=True)
    texcoords = data['texcoords'].astype(np.float32, copy=True)

    # Thu thập vertex indices của vật liệu mái
    arch_verts: set[int] = set()
    for m in ARCH_MATS:
        key = f'indices_{m:02d}'
        if key in data and len(data[key]) > 0:
            arch_verts.update(data[key].astype(np.int64).tolist())

    arch_arr = np.array(sorted(arch_verts), dtype=np.int64)
    print(f'Arch verts: {len(arch_arr):,}')

    # Áp Y offset theo X
    x_vals   = positions[arch_arr, 0]
    y_deltas = arch_y_offset(x_vals)
    positions[arch_arr, 1] += y_deltas

    print(f'X range of arch verts: {x_vals.min():.3f} to {x_vals.max():.3f}')
    print(f'Y offset range: {y_deltas.min():.4f} to {y_deltas.max():.4f}')

    # Giữ nguyên tất cả index arrays (không xoá tam giác nào)
    arrays: dict[str, np.ndarray] = {
        'positions': positions,
        'normals':   normals,
        'texcoords': texcoords,
    }
    new_index_counts: dict[str, int] = {}
    new_component_types: dict[str, int] = {}

    for mat_idx in range(n_mat):
        key = f'indices_{mat_idx:02d}'
        orig = data[key].astype(np.uint32) if key in data else np.array([], dtype=np.uint32)
        arrays[key] = orig
        new_index_counts[str(mat_idx)] = int(len(orig))
        if len(orig) > 0:
            new_component_types[str(mat_idx)] = 5125 if int(orig.max()) > 65535 else 5123
        else:
            new_component_types[str(mat_idx)] = 5123

    stats = {
        'n_orig': int(len(data['positions'])),
        'n_new':  int(len(positions)),
        'arch_verts_modified': int(len(arch_arr)),
        'y_offset_min': float(y_deltas.min()),
        'y_offset_max': float(y_deltas.max()),
        'new_index_counts': new_index_counts,
        'new_component_types': new_component_types,
    }
    return arrays, stats


def update_manifest(src_path: Path, arrays: dict, stats: dict) -> dict:
    manifest = json.loads(src_path.read_text(encoding='utf-8'))
    positions = arrays['positions']
    manifest.update({
        'version': 'v47_roof_curve',
        'geometry_npz': V47_GEOM,
        'vertex_count': stats['n_new'],
        'primitive_count': sum(1 for v in stats['new_index_counts'].values() if v > 0),
        'primitive_index_count': stats['new_index_counts'],
        'primitive_component_types': stats['new_component_types'],
        'position_bounds_source': {
            'min': [float(v) for v in positions.min(axis=0)],
            'max': [float(v) for v in positions.max(axis=0)],
        },
        'patch_summary': (
            'v47: base là v46; áp đường cong lên-ngang-xuống (parabol) '
            f'cho mái ngói (mat16-23): MAX_DROP={MAX_DROP}m tại |X|={DESCENT_HALF}m.'
        ),
        'v47_changes': {
            'requested_by_user': 'Mái ngói vẽ lại theo đường cong lên-ngang-xuống như thanh nâu (mat13).',
            'base_version': 'v46',
            'arch_mats': sorted(ARCH_MATS),
            'arch_function': 'parabolic: Y_offset = -MAX_DROP * (abs(X)/DESCENT_HALF)^2',
            'max_drop_m': MAX_DROP,
            'descent_half_m': DESCENT_HALF,
            'arch_verts_modified': stats['arch_verts_modified'],
            'y_offset_range_m': [stats['y_offset_min'], stats['y_offset_max']],
        },
    })
    return manifest


def patch_source_files() -> None:
    scene_file = SRC_DIR / 'glb_forge' / 'scenes' / 'chua_cau_hoi_an.py'
    text = scene_file.read_text(encoding='utf-8')
    text = text.replace(V46_GEOM, V47_GEOM)
    text = text.replace(V46_MANIFEST, V47_MANIFEST)
    text = text.replace('v46_remove_back_vien_nau', 'v47_roof_curve')
    text = text.replace('v46 remove back viền nâu', 'v47 roof curve')
    text = text.replace('Không tìm thấy geometry v46', 'Không tìm thấy geometry v47')
    text = text.replace('Không tìm thấy manifest v46', 'Không tìm thấy manifest v47')
    text = text.replace('Geometry v46 không hợp lệ', 'Geometry v47 không hợp lệ')
    text = text.replace('Sai số material so với manifest v46', 'Sai số material so với manifest v47')
    text = text.replace(
        'GLB nâng cấp v46: mặt trước như v44, xoá viền nâu đầu sau.',
        'GLB nâng cấp v47: base=v46, áp đường cong lên-ngang-xuống cho mái ngói.',
    )
    scene_file.write_text(text, encoding='utf-8')
    print('Updated: src/glb_forge/scenes/chua_cau_hoi_an.py')

    main_file = PROJECT_ROOT / 'main.py'
    t = main_file.read_text(encoding='utf-8')
    t = t.replace('v46 remove back viền nâu', 'v47 roof curve')
    t = t.replace(
        'Bản này giữ mặt trước như v44, chỉ xoá viền nâu đầu sau; giữ mái gương nhỏ đằng sau.',
        'Bản này base=v46, áp đường cong lên-ngang-xuống cho mái ngói (mat16-23).',
    )
    t = t.replace(
        'chua_cau_hoi_an_textured_fixed_v46_remove_back_vien_nau.glb',
        V47_OUTPUT,
    )
    main_file.write_text(t, encoding='utf-8')
    print('Updated: main.py')

    registry = SRC_DIR / 'glb_forge' / 'sites' / 'provinces' / 'da_nang.py'
    if registry.exists():
        rt = registry.read_text(encoding='utf-8')
        rt = rt.replace(
            'chua_cau_hoi_an_textured_fixed_v46_remove_back_vien_nau',
            'chua_cau_hoi_an_textured_fixed_v47_roof_curve',
        )
        registry.write_text(rt, encoding='utf-8')
        print('Updated: src/glb_forge/sites/provinces/da_nang.py')

    doc = PROJECT_ROOT / 'docs' / 'v47_roof_curve_note.md'
    doc.write_text(
        '# v47 roof curve\n\n'
        '- Base là v46 (mặt trước v44, xoá viền nâu đầu sau).\n'
        f'- Áp đường cong parabol lên-ngang-xuống cho mái ngói (mat {sorted(ARCH_MATS)}).\n'
        f'- Y_offset(X) = -{MAX_DROP} * (|X|/{DESCENT_HALF})²\n'
        f'  - Giữa (X=0): offset=0 (không đổi)\n'
        f'  - Hai đầu (|X|={DESCENT_HALF}): offset=-{MAX_DROP}m\n'
        '- Không xoá tam giác nào, giữ nguyên index arrays.\n'
        '- Cùng profile đường cong với thanh gỗ nâu (mat13).\n',
        encoding='utf-8',
    )
    print('Created: docs/v47_roof_curve_note.md')


def main() -> None:
    geom_dir = PROJECT_ROOT / 'assets' / 'geometry'
    src_npz      = geom_dir / V46_GEOM
    src_manifest = geom_dir / V46_MANIFEST

    if not src_npz.exists():
        raise FileNotFoundError(f'Không tìm thấy geometry v46: {src_npz}')

    manifest_src = json.loads(src_manifest.read_text(encoding='utf-8'))
    n_mat = int(manifest_src.get('material_count', 30))

    print('=== Building v47 geometry (base: v46, apply roof curve) ===')
    data = np.load(src_npz)
    arrays, stats = apply_arch_to_geometry(data, n_mat)

    dst_npz = geom_dir / V47_GEOM
    np.savez_compressed(dst_npz, **arrays)
    print(f'Saved NPZ: {dst_npz.name}  ({dst_npz.stat().st_size:,} bytes)')

    manifest = update_manifest(src_manifest, arrays, stats)
    dst_manifest = geom_dir / V47_MANIFEST
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
