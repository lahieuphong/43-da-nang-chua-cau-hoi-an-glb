from __future__ import annotations

from pathlib import Path

TEXTURE_SLUG = "chua_cau_hoi_an"
TEXTURE_DIR = Path(__file__).resolve().parents[1] / "assets" / "textures" / TEXTURE_SLUG

MATERIAL_TEXTURES: dict[str, dict[str, str]] = {
    "weathered grey stone piers": {"basecolor": "weathered_stone_basecolor.png", "normal": "weathered_stone_normal.png", "roughness": "weathered_stone_roughness.png"},
    "old dark bridge wood": {"basecolor": "old_wood_basecolor.png", "normal": "old_wood_normal.png", "roughness": "old_wood_roughness.png"},
    "aged red lacquer gate and panels": {"basecolor": "aged_red_lacquer_basecolor.png", "normal": "aged_red_lacquer_normal.png", "roughness": "aged_red_lacquer_roughness.png"},
    "old yin-yang roof tile base": {"basecolor": "old_roof_tile_basecolor.png", "normal": "old_roof_tile_normal.png", "roughness": "old_roof_tile_roughness.png"},
    "blue white ceramic roof plates": {"basecolor": "blue_white_ceramic_basecolor.png", "normal": "blue_white_ceramic_normal.png", "roughness": "blue_white_ceramic_roughness.png"},
    "soft moss on old stone": {"basecolor": "soft_moss_basecolor.png", "normal": "soft_moss_normal.png", "roughness": "soft_moss_roughness.png"},
    "shallow green canal water": {"basecolor": "canal_water_basecolor.png", "normal": "canal_water_normal.png", "roughness": "canal_water_roughness.png"},
    "Hoi An yellow plaster wall": {"basecolor": "hoi_an_yellow_wall_basecolor.png", "normal": "hoi_an_yellow_wall_normal.png", "roughness": "hoi_an_yellow_wall_roughness.png"},
    "warm Hoi An street paving": {"basecolor": "warm_paving_brick_basecolor.png", "normal": "warm_paving_brick_normal.png", "roughness": "warm_paving_brick_roughness.png"},
    "old town green foliage": {"basecolor": "village_leaf_basecolor.png", "normal": "village_leaf_normal.png", "roughness": "village_leaf_roughness.png"},
    "muted gold leaf lettering": {"basecolor": "aged_gold_leaf_basecolor.png", "normal": "aged_gold_leaf_normal.png", "roughness": "aged_gold_leaf_roughness.png"},
    "dark damp age stains": {"basecolor": "damp_stain_basecolor.png", "normal": "damp_stain_normal.png", "roughness": "damp_stain_roughness.png"},
    "warm red silk lantern": {"basecolor": "lantern_silk_basecolor.png", "normal": "lantern_silk_normal.png", "roughness": "lantern_silk_roughness.png"},
}


def validate_texture_files() -> list[Path]:
    missing: list[Path] = []
    for maps in MATERIAL_TEXTURES.values():
        for filename in maps.values():
            path = TEXTURE_DIR / filename
            if not path.exists():
                missing.append(path)
    return missing


def material_texture_map() -> dict[str, dict[str, str]]:
    return MATERIAL_TEXTURES
