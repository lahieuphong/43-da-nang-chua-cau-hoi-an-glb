"""Generate the v31 inner-brown-deck up-flat-down textured GLB model for Chua Cau Hoi An."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from glb_forge.scene_writer import write_scene_glb
from glb_forge.scenes.chua_cau_hoi_an import create_chua_cau_hoi_an

from generator.texture_generator import generate_textures

OUTPUT_GLB = PROJECT_ROOT / "output" / "chua_cau_hoi_an_textured_fixed_v31_inner_brown_floor_profile_final_fix.glb"


def build_model(output_path: Path = OUTPUT_GLB) -> Path:
    """Build and write the final GLB with embedded procedural textures."""
    generate_textures(force=False)
    scene = create_chua_cau_hoi_an()
    return write_scene_glb(scene, output_path)


if __name__ == "__main__":
    result = build_model()
    print(f"Generated: {result}")
