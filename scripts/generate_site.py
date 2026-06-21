from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from glb_forge import generate_site, get_site


def ensure_textures() -> None:
    texture_dir = PROJECT_ROOT / "assets" / "textures" / "chua_cau_hoi_an"
    required = [
        texture_dir / "old_roof_tile_basecolor.png",
        texture_dir / "old_roof_tile_normal.png",
        texture_dir / "old_roof_tile_roughness.png",
        texture_dir / "damp_stain_basecolor.png",
        texture_dir / "aged_gold_leaf_basecolor.png",
        texture_dir / "lantern_silk_basecolor.png",
    ]
    if not all(path.exists() and path.stat().st_size > 0 for path in required):
        subprocess.run([sys.executable, str(PROJECT_ROOT / "scripts" / "generate_textures.py")], check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate one heritage site GLB by registry key.")
    parser.add_argument("site_key", help="Dạng key: 43-da-nang/chua-cau-hoi-an")
    args = parser.parse_args()

    ensure_textures()
    site = get_site(args.site_key)
    result = generate_site(site, PROJECT_ROOT / "output")

    print(f"Generated file: {result.path}")
    print(f"{site.registry_key} vertices: {result.vertex_count:,}")
    print(f"{site.registry_key} materials: {result.material_count:,}")


if __name__ == "__main__":
    main()
