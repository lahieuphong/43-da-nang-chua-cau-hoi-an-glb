"""Wrapper to generate procedural textures for Chua Cau Hoi An.

Textures are generated with Pillow, not copied from news/web images.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
TEXTURE_DIR = PROJECT_ROOT / "assets" / "textures" / "chua_cau_hoi_an"
TEXTURE_BASENAMES = [
    "old_wood",
    "weathered_stone",
    "old_roof_tile",
    "aged_red_lacquer",
    "hoi_an_yellow_wall",
    "warm_paving_brick",
    "blue_white_ceramic",
    "soft_moss",
    "canal_water",
    "village_leaf",
    "aged_gold_leaf",
    "damp_stain",
    "lantern_silk",
]
REQUIRED_TEXTURES = [
    f"{name}_{kind}.png"
    for name in TEXTURE_BASENAMES
    for kind in ("basecolor", "normal", "roughness")
]


def textures_ready() -> bool:
    return all((TEXTURE_DIR / name).exists() for name in REQUIRED_TEXTURES)


def generate_textures(force: bool = False) -> Path:
    if force or not textures_ready():
        script = PROJECT_ROOT / "scripts" / "generate_textures.py"
        subprocess.run([sys.executable, str(script)], cwd=str(PROJECT_ROOT), check=True)
    return TEXTURE_DIR


if __name__ == "__main__":
    print(generate_textures(force=True))
