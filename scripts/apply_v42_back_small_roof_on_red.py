from __future__ import annotations

import json
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

import numpy as np

V41_PROJECT = Path('/mnt/data/chua_cau_hoi_an_textured_fixed_v41_remove_front_small_roof_project')
V42_PROJECT = Path('/mnt/data/chua_cau_hoi_an_textured_fixed_v42_back_small_roof_on_red_project')
OUT_GLB = Path('/mnt/data/chua_cau_hoi_an_chuan_barem_v42.glb')
OUT_ZIP = Path('/mnt/data/chua_cau_hoi_an_source_chuan_barem_v42.zip')

OLD_GEOM = 'chua_cau_hoi_an_v41_remove_front_small_roof_geometry.npz'
OLD_MANIFEST = 'chua_cau_hoi_an_v41_remove_front_small_roof_manifest.json'
NEW_GEOM = 'chua_cau_hoi_an_v42_back_small_roof_on_red_geometry.npz'
NEW_MANIFEST = 'chua_cau_hoi_an_v42_back_small_roof_on_red_manifest.json'
OLD_OUTPUT = 'chua_cau_hoi_an_textured_fixed_v41_remove_front_small_roof.glb'
NEW_OUTPUT = 'chua_cau_hoi_an_textured_fixed_v42_back_small_roof_on_red.glb'

# In v41, the remaining rear/back small roof is the compacted appended span that
# came after the removed front canopy. Move only this contiguous roof assembly.
BACK_SMALL_ROOF_START = 217_352
BACK_SMALL_ROOF_END = 250_855  # inclusive, last vertex in v41 geometry
Z_OFFSET_TO_RED_BLOCK = 0.77


def save_npz_like(src_npz: Path, dst_npz: Path, positions: np.ndarray) -> None:
    src = np.load(src_npz)
    arrays: dict[str, np.ndarray] = {
        'positions': positions.astype(np.float32, copy=False),
        'normals': src['normals'].astype(np.float32, copy=False),
        'texcoords': src['texcoords'].astype(np.float32, copy=False),
    }
    for key in src.files:
        if key.startswith('indices_'):
            arrays[key] = src[key].astype(np.uint32, copy=False)
    dst_npz.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(dst_npz, **arrays)


def make_manifest(project: Path, positions: np.ndarray, old_manifest_path: Path) -> dict:
    manifest = json.loads(old_manifest_path.read_text(encoding='utf-8'))
    manifest.update({
        'version': 'v42_back_small_roof_on_red',
        'source_glb_file': OLD_OUTPUT,
        'geometry_npz': NEW_GEOM,
        'vertex_count': int(len(positions)),
        'position_bounds_source': {
            'min': [float(v) for v in positions.min(axis=0)],
            'max': [float(v) for v in positions.max(axis=0)],
        },
        'patch_summary': 'v42: giữ nguyên v41, chỉ di chuyển mái nhỏ phía sau theo trục Z lên đúng vùng/khối màu đỏ để khớp vị trí người dùng chỉ định.',
        'v42_changes': {
            'requested_by_user': 'Di chuyển phần mái nhỏ phía sau lên chỗ màu đỏ trong góc nhìn từ trên xuống; các phần còn lại giữ nguyên.',
            'moved_vertex_span_v41': [BACK_SMALL_ROOF_START, BACK_SMALL_ROOF_END],
            'translation': {'x': 0.0, 'y': 0.0, 'z': Z_OFFSET_TO_RED_BLOCK},
            'materials_preserved': True,
            'other_geometry_preserved': True,
        },
    })

    # Keep material metadata in sync with existing manifest; no material/texture changes.
    return manifest


def patch_project_files(project: Path) -> None:
    scene_file = project / 'src' / 'glb_forge' / 'scenes' / 'chua_cau_hoi_an.py'
    text = scene_file.read_text(encoding='utf-8')
    text = text.replace('bản v41 remove front small roof', 'bản v42 back small roof on red')
    text = text.replace('v41 remove front small roof', 'v42 back small roof on red')
    text = text.replace(OLD_GEOM, NEW_GEOM)
    text = text.replace(OLD_MANIFEST, NEW_MANIFEST)
    text = text.replace('Không tìm thấy manifest v41', 'Không tìm thấy manifest v42')
    text = text.replace('Không tìm thấy geometry v41', 'Không tìm thấy geometry v42')
    text = text.replace('Geometry v41 không hợp lệ', 'Geometry v42 không hợp lệ')
    text = text.replace('Sai số material so với manifest v41', 'Sai số material so với manifest v42')
    text = text.replace('GLB nâng cấp v41: giữ nguyên v40, chỉ bỏ đúng một mái nhỏ ở mặt trước.',
                        'GLB nâng cấp v42: giữ nguyên v41, chỉ di chuyển mái nhỏ phía sau lên vùng màu đỏ.')
    scene_file.write_text(text, encoding='utf-8')

    main_file = project / 'main.py'
    main_text = main_file.read_text(encoding='utf-8')
    main_text = main_text.replace('bản v41 remove front small roof', 'bản v42 back small roof on red')
    main_text = main_text.replace('Bản này giữ nguyên v40 và chỉ bỏ đúng một mái nhỏ ở đằng trước theo yêu cầu.',
                                  'Bản này giữ nguyên v41 và chỉ di chuyển mái nhỏ phía sau lên vùng màu đỏ theo yêu cầu.')
    main_text = main_text.replace(OLD_OUTPUT, NEW_OUTPUT)
    main_file.write_text(main_text, encoding='utf-8')

    registry = project / 'src' / 'glb_forge' / 'sites' / 'provinces' / 'da_nang.py'
    if registry.exists():
        rt = registry.read_text(encoding='utf-8')
        rt = rt.replace('chua_cau_hoi_an_textured_fixed_v41_remove_front_small_roof',
                        'chua_cau_hoi_an_textured_fixed_v42_back_small_roof_on_red')
        registry.write_text(rt, encoding='utf-8')

    readme = project / 'README.md'
    readme.write_text(
        '# Chùa Cầu Hội An - source chuẩn barem v42\n\n'
        'Bản v42 giữ nguyên v41 và chỉ di chuyển phần mái nhỏ phía sau lên đúng vùng/khối màu đỏ theo hình người dùng chỉ định.\n\n'
        'Chạy `python main.py` để xuất lại GLB trong thư mục `output/`.\n',
        encoding='utf-8',
    )

    docs = project / 'docs'
    docs.mkdir(exist_ok=True)
    (docs / 'v42_back_small_roof_on_red_note.md').write_text(
        '# v42 back small roof on red\n\n'
        '- Giữ nguyên toàn bộ bản v41.\n'
        f'- Chỉ di chuyển mái nhỏ phía sau: vertex span v41 {BACK_SMALL_ROOF_START}..{BACK_SMALL_ROOF_END}.\n'
        f'- Tịnh tiến theo trục Z: +{Z_OFFSET_TO_RED_BLOCK}.\n'
        '- Không đổi chất liệu, mái chính, mái trước đã bỏ, tường đỏ hay các chi tiết còn lại.\n',
        encoding='utf-8',
    )

    script_dst = project / 'scripts' / 'apply_v42_back_small_roof_on_red.py'
    script_dst.write_text(Path(__file__).read_text(encoding='utf-8'), encoding='utf-8')


def main() -> None:
    if not V41_PROJECT.exists():
        raise FileNotFoundError(f'Không tìm thấy source v41: {V41_PROJECT}')

    if V42_PROJECT.exists():
        subprocess.run(['rm', '-rf', str(V42_PROJECT)], check=True)
    subprocess.run(['cp', '-a', str(V41_PROJECT), str(V42_PROJECT)], check=True)

    # Remove old generated output so packaged source contains a clean v42 build output.
    outdir = V42_PROJECT / 'output'
    if outdir.exists():
        shutil.rmtree(outdir)

    src_npz = V41_PROJECT / 'assets' / 'geometry' / OLD_GEOM
    old_manifest = V41_PROJECT / 'assets' / 'geometry' / OLD_MANIFEST
    data = np.load(src_npz)
    positions = data['positions'].astype(np.float32, copy=True)
    before_bounds = positions[BACK_SMALL_ROOF_START:BACK_SMALL_ROOF_END + 1].copy()
    positions[BACK_SMALL_ROOF_START:BACK_SMALL_ROOF_END + 1, 2] += Z_OFFSET_TO_RED_BLOCK
    after_bounds = positions[BACK_SMALL_ROOF_START:BACK_SMALL_ROOF_END + 1]
    print('back small roof before:', before_bounds.min(axis=0), before_bounds.max(axis=0))
    print('back small roof after:', after_bounds.min(axis=0), after_bounds.max(axis=0))

    geom_path = V42_PROJECT / 'assets' / 'geometry' / NEW_GEOM
    save_npz_like(src_npz, geom_path, positions)

    manifest = make_manifest(V42_PROJECT, positions, old_manifest)
    manifest_path = V42_PROJECT / 'assets' / 'geometry' / NEW_MANIFEST
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')

    patch_project_files(V42_PROJECT)

    # Regenerate via packaged source to verify the ZIP source can rebuild the GLB.
    subprocess.run([sys.executable, str(V42_PROJECT / 'main.py')], cwd=str(V42_PROJECT), check=True)
    packaged_output = V42_PROJECT / 'output' / NEW_OUTPUT
    if not packaged_output.exists():
        raise FileNotFoundError(packaged_output)
    shutil.copy2(packaged_output, OUT_GLB)

    if OUT_ZIP.exists():
        OUT_ZIP.unlink()
    with zipfile.ZipFile(OUT_ZIP, 'w', zipfile.ZIP_DEFLATED) as zf:
        root = V42_PROJECT.parent
        for path in sorted(V42_PROJECT.rglob('*')):
            zf.write(path, path.relative_to(root))

    print('final glb:', OUT_GLB, OUT_GLB.stat().st_size)
    print('source zip:', OUT_ZIP, OUT_ZIP.stat().st_size)


if __name__ == '__main__':
    main()
