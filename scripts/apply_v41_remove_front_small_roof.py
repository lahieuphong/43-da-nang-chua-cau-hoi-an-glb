from __future__ import annotations

import json
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

import numpy as np

V40_PROJECT = Path('/mnt/data/work_v40/chua_cau_hoi_an_textured_fixed_v40_roof_drop_to_red_gable_fix_project')
V41_PROJECT = Path('/mnt/data/chua_cau_hoi_an_textured_fixed_v41_remove_front_small_roof_project')
OUT_GLB = Path('/mnt/data/chua_cau_hoi_an_chuan_barem_v41.glb')
OUT_ZIP = Path('/mnt/data/chua_cau_hoi_an_source_chuan_barem_v41.zip')

# The v40 procedural patch appends geometry in this exact order:
# base kept geometry -> dropped main roof -> front canopy (+z) -> back canopy (-z) -> back fill.
# The requested removal is precisely the single front small roof/canopy (visible from the front),
# corresponding to this contiguous appended vertex span.
FRONT_CANOPY_START = 217_352
FRONT_CANOPY_END = 250_825  # inclusive


def load_scene():
    sys.path.insert(0, str(V40_PROJECT / 'src'))
    from glb_forge.scenes.chua_cau_hoi_an import create_chua_cau_hoi_an  # type: ignore
    return create_chua_cau_hoi_an()


def compact_scene(scene) -> None:
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


def remove_front_canopy(scene) -> dict[str, object]:
    removed_by_material: dict[int, int] = {}
    total_removed = 0
    for material_index in range(len(scene.materials)):
        raw = scene.indices_by_material.get(material_index, [])
        if not raw:
            removed_by_material[material_index] = 0
            continue
        keep: list[int] = []
        removed = 0
        # SceneMesh primitives are stored as triangle index triples.
        for a, b, c in zip(raw[0::3], raw[1::3], raw[2::3]):
            if (FRONT_CANOPY_START <= a <= FRONT_CANOPY_END and
                FRONT_CANOPY_START <= b <= FRONT_CANOPY_END and
                FRONT_CANOPY_START <= c <= FRONT_CANOPY_END):
                removed += 1
            else:
                keep.extend([a, b, c])
        scene.indices_by_material[material_index] = keep
        removed_by_material[material_index] = removed
        total_removed += removed

    compact_scene(scene)
    return {
        'removed_front_canopy_vertex_span_in_v40': [FRONT_CANOPY_START, FRONT_CANOPY_END],
        'removed_front_canopy_triangles_total': total_removed,
        'removed_front_canopy_triangles_by_material': removed_by_material,
        'kept_back_small_roof': True,
        'kept_main_roof_and_remaining_model': True,
    }


def save_scene_npz(scene, geometry_path: Path) -> None:
    arrays: dict[str, np.ndarray] = {
        'positions': np.asarray(scene.positions, dtype=np.float32),
        'normals': np.asarray(scene.normals, dtype=np.float32),
        'texcoords': np.asarray(scene.texcoords, dtype=np.float32),
    }
    for material_index in range(len(scene.materials)):
        arrays[f'indices_{material_index:02d}'] = np.asarray(scene.indices_by_material.get(material_index, []), dtype=np.uint32)
    geometry_path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(geometry_path, **arrays)


def make_manifest(scene, source_manifest_path: Path, geometry_filename: str, stats: dict[str, object]) -> dict:
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
        'version': 'v41_remove_front_small_roof',
        'scene_name': 'Chua_Cau_Hoi_An_Lai_Vien_Kieu',
        'source_glb_file': 'chua_cau_hoi_an_textured_fixed_v40_roof_drop_to_red_gable_fix.glb',
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
        'patch_summary': 'v41: giữ nguyên bản v40, chỉ bỏ đúng một mái nhỏ/canopy ở mặt trước theo yêu cầu; mái chính, mái sau và các phần còn lại giữ nguyên.',
        'v41_changes': {
            'requested_by_user': 'Bỏ đi đúng một cái mái nhỏ ở đằng trước, phần còn lại giữ nguyên.',
            'geometry_actions': stats,
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
    text = text.replace('bản v40 roof drop to red gable fix', 'bản v41 remove front small roof')
    text = text.replace('v40 roof drop to red gable fix', 'v41 remove front small roof')
    text = text.replace('chua_cau_hoi_an_v40_roof_drop_to_red_gable_fix_geometry.npz', geom_name)
    text = text.replace('chua_cau_hoi_an_v40_roof_drop_to_red_gable_fix_manifest.json', manifest_name)
    text = text.replace('Không tìm thấy manifest v40', 'Không tìm thấy manifest v41')
    text = text.replace('Không tìm thấy geometry v40', 'Không tìm thấy geometry v41')
    text = text.replace('Geometry v40 không hợp lệ', 'Geometry v41 không hợp lệ')
    text = text.replace('Sai số material so với manifest v40', 'Sai số material so với manifest v41')
    text = text.replace('GLB nâng cấp v40: giữ bố cục/chất liệu v39 và hạ mái chính trùng với tam giác đỏ.',
                        'GLB nâng cấp v41: giữ nguyên v40, chỉ bỏ đúng một mái nhỏ ở mặt trước.')
    scene_file.write_text(text, encoding='utf-8')

    main_file = project / 'main.py'
    main_text = main_file.read_text(encoding='utf-8')
    main_text = main_text.replace('bản v40 roof drop to red gable fix', 'bản v41 remove front small roof')
    main_text = main_text.replace('Bản này giữ bố cục/chất liệu v39 và hạ mái chính xuống trùng với hình tam giác đỏ.',
                                  'Bản này giữ nguyên v40 và chỉ bỏ đúng một mái nhỏ ở đằng trước theo yêu cầu.')
    main_text = main_text.replace('chua_cau_hoi_an_textured_fixed_v40_roof_drop_to_red_gable_fix.glb',
                                  'chua_cau_hoi_an_textured_fixed_v41_remove_front_small_roof.glb')
    main_file.write_text(main_text, encoding='utf-8')

    registry = project / 'src' / 'glb_forge' / 'sites' / 'provinces' / 'da_nang.py'
    if registry.exists():
        rt = registry.read_text(encoding='utf-8')
        rt = rt.replace('chua_cau_hoi_an_textured_fixed_v40_roof_drop_to_red_gable_fix',
                        'chua_cau_hoi_an_textured_fixed_v41_remove_front_small_roof')
        registry.write_text(rt, encoding='utf-8')

    readme = project / 'README.md'
    readme.write_text(
        '# Chùa Cầu Hội An - source chuẩn barem v41\n\n'
        'Bản v41 giữ nguyên bản v40, chỉ bỏ đúng một mái nhỏ/canopy ở mặt trước như hình người dùng khoanh/zoom.\n\n'
        'Chạy `python main.py` để xuất lại GLB trong thư mục `output/`.\n',
        encoding='utf-8',
    )

    docs = project / 'docs'
    docs.mkdir(exist_ok=True)
    (docs / 'v41_remove_front_small_roof_note.md').write_text(
        '# v41 remove front small roof\n\n'
        '- Giữ nguyên mô hình v40.\n'
        '- Bỏ đúng một mái nhỏ ở mặt trước: canopy trung tâm hướng +Z, vertex span v40 217352..250825.\n'
        '- Không tác động mái chính, mái sau, tam giác đỏ, chất liệu và các phần kiến trúc còn lại.\n',
        encoding='utf-8',
    )

    script_dst = project / 'scripts' / 'apply_v41_remove_front_small_roof.py'
    script_dst.write_text(Path(__file__).read_text(encoding='utf-8'), encoding='utf-8')


def main() -> None:
    if not V40_PROJECT.exists():
        raise FileNotFoundError(f'Không tìm thấy source v40: {V40_PROJECT}')

    scene = load_scene()
    before_vertices = len(scene.positions)
    stats = remove_front_canopy(scene)
    after_vertices = len(scene.positions)
    print('vertices before/after', before_vertices, after_vertices)
    print(json.dumps(stats, ensure_ascii=False, indent=2))

    if V41_PROJECT.exists():
        shutil.rmtree(V41_PROJECT)
    shutil.copytree(V40_PROJECT, V41_PROJECT)

    geom_name = 'chua_cau_hoi_an_v41_remove_front_small_roof_geometry.npz'
    manifest_name = 'chua_cau_hoi_an_v41_remove_front_small_roof_manifest.json'
    geom_path = V41_PROJECT / 'assets' / 'geometry' / geom_name
    manifest_path = V41_PROJECT / 'assets' / 'geometry' / manifest_name
    source_manifest = V40_PROJECT / 'assets' / 'geometry' / 'chua_cau_hoi_an_v40_roof_drop_to_red_gable_fix_manifest.json'
    save_scene_npz(scene, geom_path)
    manifest = make_manifest(scene, source_manifest, geom_name, stats)
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    patch_project_files(V41_PROJECT, geom_name, manifest_name)

    # Export directly once, then verify the packaged source can regenerate the same target name.
    sys.path.insert(0, str(V41_PROJECT / 'src'))
    from glb_forge.scene_writer import write_scene_glb  # type: ignore
    direct = write_scene_glb(scene, OUT_GLB)
    print('direct glb:', direct, direct.stat().st_size)

    subprocess.run([sys.executable, str(V41_PROJECT / 'main.py')], cwd=str(V41_PROJECT), check=True)
    packaged_output = V41_PROJECT / 'output' / 'chua_cau_hoi_an_textured_fixed_v41_remove_front_small_roof.glb'
    if not packaged_output.exists():
        raise FileNotFoundError(packaged_output)
    shutil.copy2(packaged_output, OUT_GLB)

    if OUT_ZIP.exists():
        OUT_ZIP.unlink()
    with zipfile.ZipFile(OUT_ZIP, 'w', zipfile.ZIP_DEFLATED) as zf:
        root = V41_PROJECT.parent
        for path in sorted(V41_PROJECT.rglob('*')):
            zf.write(path, path.relative_to(root))

    print('final glb:', OUT_GLB, OUT_GLB.stat().st_size)
    print('source zip:', OUT_ZIP, OUT_ZIP.stat().st_size)


if __name__ == '__main__':
    main()
