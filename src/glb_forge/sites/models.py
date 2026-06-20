from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from glb_forge.scene import SceneMesh

SceneFactory = Callable[[], SceneMesh]


@dataclass(frozen=True)
class Province:
    code: str
    slug: str
    name: str
    output_name: str

    @property
    def output_dir(self) -> str:
        return f"{self.code}_{self.output_name}"


@dataclass(frozen=True)
class HeritageSite:
    site_id: str
    name: str
    province: Province
    output_name: str
    create_scene: SceneFactory

    @property
    def file_name(self) -> str:
        return f"{self.output_name}.glb"

    @property
    def registry_key(self) -> str:
        return f"{self.province.code}-{self.province.slug}/{self.site_id}"

    def output_path(self, output_root: str | Path) -> Path:
        return Path(output_root) / self.province.output_dir / self.file_name


__all__ = ["HeritageSite", "Province", "SceneFactory"]
