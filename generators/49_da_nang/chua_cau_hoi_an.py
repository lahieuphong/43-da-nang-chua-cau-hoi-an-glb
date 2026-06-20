from __future__ import annotations

import subprocess
import sys
from pathlib import Path

# Cho phép chạy file này trực tiếp mà không cần cài package.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from glb_forge import generate_site, get_site

SITE_KEY = "49-da-nang/chua-cau-hoi-an"
REQUIRED_TEXTURE = PROJECT_ROOT / "assets" / "textures" / "chua_cau_hoi_an" / "old_roof_tile_basecolor.png"


def ensure_textures() -> None:
    if REQUIRED_TEXTURE.exists():
        return
    script = PROJECT_ROOT / "scripts" / "generate_textures.py"
    print("Chưa thấy texture procedural, đang sinh texture...")
    subprocess.run([sys.executable, str(script)], check=True)


def main() -> None:
    ensure_textures()
    site = get_site(SITE_KEY)
    result = generate_site(site, PROJECT_ROOT / "output")
    print(f"Đã tạo: {result.path}")
    print(f"Site: {site.registry_key}")
    print(f"Vertices: {result.vertex_count:,}")
    print(f"Materials: {result.material_count:,}")


if __name__ == "__main__":
    main()
