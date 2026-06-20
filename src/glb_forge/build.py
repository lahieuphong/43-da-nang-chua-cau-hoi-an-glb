from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from glb_forge.scene_writer import write_scene_glb
from glb_forge.sites import HeritageSite


@dataclass(frozen=True)
class BuildResult:
    site: HeritageSite
    path: Path
    vertex_count: int
    material_count: int


def generate_site(site: HeritageSite, output_root: str | Path) -> BuildResult:
    scene = site.create_scene()
    path = write_scene_glb(scene, site.output_path(output_root))
    return BuildResult(site=site, path=path, vertex_count=len(scene.positions), material_count=len(scene.materials))


__all__ = ["BuildResult", "generate_site"]
