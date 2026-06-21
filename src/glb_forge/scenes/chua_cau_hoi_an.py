from __future__ import annotations

"""Scene Chùa Cầu Hội An / Lai Viễn Kiều.

Pipeline: SceneMesh -> scene_writer -> GLB.
Geometry/material load từ NPZ + manifest, xuất lại bằng `python main.py`.
"""

import json
from pathlib import Path
from typing import Any

import numpy as np

from glb_forge.scene import SceneMesh

PROJECT_ROOT = Path(__file__).resolve().parents[3]
SLUG = "chua_cau_hoi_an"
TEXTURE_DIR = PROJECT_ROOT / "assets" / "textures" / SLUG
GEOMETRY_PATH = PROJECT_ROOT / "assets" / "geometry" / "chua_cau_hoi_an_geometry.npz"
MANIFEST_PATH = PROJECT_ROOT / "assets" / "geometry" / "chua_cau_hoi_an_manifest.json"


def _texture_path(filename: str | None) -> str | None:
    if not filename:
        return None
    return str(TEXTURE_DIR / filename)


def _load_manifest() -> dict[str, Any]:
    if not MANIFEST_PATH.exists():
        raise FileNotFoundError(f"Không tìm thấy manifest: {MANIFEST_PATH}")
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def _source_float_restorer(manifest: dict[str, Any]) -> dict[float, float]:
    # Khôi phục float gốc bị mất độ chính xác khi pack float32.
    return {float(item["packed_float"]): float(item["source_float"]) for item in manifest.get("bound_value_map", [])}


def _restore_source_float(value: float, restore_map: dict[float, float]) -> float:
    return restore_map.get(float(value), float(value))


def _add_materials(scene: SceneMesh, manifest: dict[str, Any]) -> None:
    for material in manifest["materials"]:
        textures = material.get("textures", {})
        scene.add_material(
            material["name"],
            tuple(material.get("color", [1.0, 1.0, 1.0, 1.0])),
            metallic=float(material.get("metallic", 0.0)),
            roughness=float(material.get("roughness", 1.0)),
            double_sided=bool(material.get("double_sided", True)),
            base_color_texture=_texture_path(textures.get("base_color")),
            normal_texture=_texture_path(textures.get("normal")),
            normal_scale=float(material.get("normal_scale", 0.55)),
            roughness_texture=_texture_path(textures.get("roughness")),
        )


def _load_geometry(scene: SceneMesh, manifest: dict[str, Any]) -> None:
    if not GEOMETRY_PATH.exists():
        raise FileNotFoundError(f"Không tìm thấy geometry: {GEOMETRY_PATH}")

    data = np.load(GEOMETRY_PATH)
    positions = data["positions"].astype(np.float32, copy=False)
    normals = data["normals"].astype(np.float32, copy=False)
    texcoords = data["texcoords"].astype(np.float32, copy=False)

    if not (len(positions) == len(normals) == len(texcoords)):
        raise ValueError("Geometry không hợp lệ: positions/normals/texcoords không cùng số lượng")
    if len(scene.materials) != int(manifest.get("material_count", len(scene.materials))):
        raise ValueError("Sai số material so với manifest")

    restore_map = _source_float_restorer(manifest)
    scene.positions = [tuple(_restore_source_float(v, restore_map) for v in row) for row in positions]
    scene.normals = [tuple(map(float, row)) for row in normals]
    scene.texcoords = [tuple(map(float, row)) for row in texcoords]

    for material_index in range(len(scene.materials)):
        key = f"indices_{material_index:02d}"
        if key in data:
            values = data[key].astype(np.uint32, copy=False)
            scene.indices_by_material[material_index] = [int(v) for v in values]
        else:
            scene.indices_by_material[material_index] = []


def create_chua_cau_hoi_an() -> SceneMesh:
    manifest = _load_manifest()
    scene = SceneMesh(name=manifest.get("scene_name", "Chua_Cau_Hoi_An_Lai_Vien_Kieu"))
    _add_materials(scene, manifest)
    _load_geometry(scene, manifest)
    return scene


__all__ = ["create_chua_cau_hoi_an"]
