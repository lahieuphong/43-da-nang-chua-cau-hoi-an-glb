from __future__ import annotations

"""Entry point chính cho bản v42 back small roof on red.

Chạy file này để dựng lại mô hình Chùa Cầu Hội An từ source theo barem ZIP mẫu,
rồi xuất GLB textured tại thư mục output/. Bản này giữ nguyên v41 và chỉ di chuyển mái nhỏ phía sau lên vùng màu đỏ theo yêu cầu.
"""

import shutil
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from glb_forge.scene_writer import write_scene_glb
from glb_forge.scenes.chua_cau_hoi_an import create_chua_cau_hoi_an

SLUG = "chua_cau_hoi_an"
OUTPUT_NAME = "chua_cau_hoi_an_textured_fixed_v42_back_small_roof_on_red.glb"
COMPAT_OUTPUT_NAME = f"{SLUG}_textured.glb"
TEXTURE_DIR = PROJECT_ROOT / "assets" / "textures" / SLUG
ROOT_OUTPUT = PROJECT_ROOT / "output" / OUTPUT_NAME
ROOT_COMPAT_OUTPUT = PROJECT_ROOT / "output" / COMPAT_OUTPUT_NAME
REGISTRY_OUTPUT = PROJECT_ROOT / "output" / "49_da_nang" / OUTPUT_NAME
REGISTRY_COMPAT_OUTPUT = PROJECT_ROOT / "output" / "49_da_nang" / COMPAT_OUTPUT_NAME

REQUIRED_TEXTURES = [
    "old_wood_basecolor.png", "old_wood_normal.png", "old_wood_roughness.png",
    "weathered_stone_basecolor.png", "weathered_stone_normal.png", "weathered_stone_roughness.png",
    "old_roof_tile_basecolor.png", "old_roof_tile_normal.png", "old_roof_tile_roughness.png",
    "aged_red_lacquer_basecolor.png", "aged_red_lacquer_normal.png", "aged_red_lacquer_roughness.png",
    "hoi_an_yellow_wall_basecolor.png", "hoi_an_yellow_wall_normal.png", "hoi_an_yellow_wall_roughness.png",
    "warm_paving_brick_basecolor.png", "warm_paving_brick_normal.png", "warm_paving_brick_roughness.png",
    "blue_white_ceramic_basecolor.png", "blue_white_ceramic_normal.png", "blue_white_ceramic_roughness.png",
    "soft_moss_basecolor.png", "soft_moss_normal.png", "soft_moss_roughness.png",
    "canal_water_basecolor.png", "canal_water_normal.png", "canal_water_roughness.png",
    "village_leaf_basecolor.png", "village_leaf_normal.png", "village_leaf_roughness.png",
    "aged_gold_leaf_basecolor.png", "aged_gold_leaf_normal.png", "aged_gold_leaf_roughness.png",
    "damp_stain_basecolor.png", "damp_stain_normal.png", "damp_stain_roughness.png",
    "lantern_silk_basecolor.png", "lantern_silk_normal.png", "lantern_silk_roughness.png",
]


def ensure_textures() -> None:
    """Kiểm tra texture procedural nhúng vào GLB; sinh lại nếu thiếu."""
    TEXTURE_DIR.mkdir(parents=True, exist_ok=True)
    missing = [TEXTURE_DIR / name for name in REQUIRED_TEXTURES if not (TEXTURE_DIR / name).exists()]
    if missing:
        subprocess.run([sys.executable, str(PROJECT_ROOT / "scripts" / "generate_textures.py")], check=True)
    missing_after = [name for name in REQUIRED_TEXTURES if not (TEXTURE_DIR / name).exists()]
    if missing_after:
        raise FileNotFoundError("Missing textures after generation: " + ", ".join(missing_after))


def main() -> None:
    ensure_textures()
    scene = create_chua_cau_hoi_an()
    output_path = write_scene_glb(scene, ROOT_OUTPUT)

    ROOT_COMPAT_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(output_path, ROOT_COMPAT_OUTPUT)

    REGISTRY_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(output_path, REGISTRY_OUTPUT)
    shutil.copy2(output_path, REGISTRY_COMPAT_OUTPUT)

    texture_count = len(list(TEXTURE_DIR.glob("*.png")))
    print(f"Generated GLB: {output_path}")
    print(f"Compatibility copy: {ROOT_COMPAT_OUTPUT}")
    print(f"Registry copy: {REGISTRY_OUTPUT}")
    print(f"Registry compatibility copy: {REGISTRY_COMPAT_OUTPUT}")
    print(f"Vertices: {len(scene.positions):,}")
    print(f"Materials: {len(scene.materials):,}")
    print(f"Textures: {texture_count} PNG files available and referenced")


if __name__ == "__main__":
    main()
