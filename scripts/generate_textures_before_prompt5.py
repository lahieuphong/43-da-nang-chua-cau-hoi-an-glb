from __future__ import annotations

import math
import random
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

PROJECT_ROOT = Path(__file__).resolve().parents[1]
TEXTURE_DIR = PROJECT_ROOT / "assets" / "textures" / "chua_cau_hoi_an"
DOCS_DIR = PROJECT_ROOT / "docs"
SIZE = 512


def clamp_array(a: np.ndarray) -> np.ndarray:
    return np.clip(a, 0, 255).astype(np.uint8)


def save(img: Image.Image, name: str) -> None:
    TEXTURE_DIR.mkdir(parents=True, exist_ok=True)
    img.save(TEXTURE_DIR / name)


def noise_base(base: tuple[int, int, int], jitter: int, seed: int) -> Image.Image:
    rng = np.random.default_rng(seed)
    y, x = np.mgrid[0:SIZE, 0:SIZE]
    wave = np.sin(x * 0.031 + y * 0.017) * jitter * 0.32 + np.sin((x + y) * 0.013) * jitter * 0.23
    noise = rng.integers(-jitter, jitter + 1, size=(SIZE, SIZE)) + wave
    arr = np.zeros((SIZE, SIZE, 3), dtype=np.float32)
    for c, b in enumerate(base):
        arr[:, :, c] = b + noise
    return Image.fromarray(clamp_array(arr), "RGB")


def normal_from_height(height: Image.Image, strength: float = 2.5) -> Image.Image:
    h = np.asarray(height.convert("L"), dtype=np.float32) / 255.0
    dy, dx = np.gradient(h)
    nx = -dx * strength
    ny = -dy * strength
    nz = np.ones_like(h)
    length = np.sqrt(nx * nx + ny * ny + nz * nz)
    normal = np.dstack(((nx / length * 0.5 + 0.5) * 255, (ny / length * 0.5 + 0.5) * 255, (nz / length * 0.5 + 0.5) * 255))
    return Image.fromarray(clamp_array(normal), "RGB")


def roughness_map(value: int, jitter: int, seed: int, metallic: int = 0) -> Image.Image:
    # glTF metallicRoughnessTexture: G = roughness, B = metallic.
    rng = np.random.default_rng(seed)
    y, x = np.mgrid[0:SIZE, 0:SIZE]
    wave = np.sin(x * 0.021 + y * 0.029) * jitter * 0.25
    rough = value + rng.integers(-jitter, jitter + 1, size=(SIZE, SIZE)) + wave
    arr = np.zeros((SIZE, SIZE, 3), dtype=np.uint8)
    arr[:, :, 1] = clamp_array(rough)
    arr[:, :, 2] = metallic
    return Image.fromarray(arr, "RGB").filter(ImageFilter.GaussianBlur(0.35))


def texture_old_wood() -> None:
    rng = random.Random(101)
    img = noise_base((82, 47, 26), 18, 102)
    draw = ImageDraw.Draw(img, "RGBA")
    height = Image.new("L", (SIZE, SIZE), 126)
    hd = ImageDraw.Draw(height)
    for x in range(-30, SIZE + 30, 11):
        draw.line([(x, 0), (x + rng.randint(-30, 30), SIZE)], fill=(42, 25, 15, rng.randint(70, 130)), width=rng.randint(1, 4))
        hd.line([(x, 0), (x + rng.randint(-18, 18), SIZE)], fill=105 + rng.randint(-30, 26), width=rng.randint(1, 3))
    for _ in range(80):
        x, y = rng.randrange(SIZE), rng.randrange(SIZE)
        draw.arc([x - 35, y - 9, x + 35, y + 9], 0, 360, fill=(128, 75, 43, rng.randint(35, 80)), width=1)
    save(img.filter(ImageFilter.GaussianBlur(0.2)), "old_wood_basecolor.png")
    save(normal_from_height(height.filter(ImageFilter.GaussianBlur(0.8)), 3.1), "old_wood_normal.png")
    save(roughness_map(218, 22, 103), "old_wood_roughness.png")


def texture_weathered_stone() -> None:
    rng = random.Random(201)
    img = noise_base((137, 134, 124), 23, 202)
    draw = ImageDraw.Draw(img, "RGBA")
    height = img.convert("L")
    hd = ImageDraw.Draw(height)
    for _ in range(90):
        x0, y0 = rng.randrange(SIZE), rng.randrange(SIZE)
        pts = [(x0, y0)]
        for _ in range(rng.randint(2, 6)):
            x0 += rng.randint(-44, 44); y0 += rng.randint(8, 55); pts.append((x0, y0))
        draw.line(pts, fill=(55, 53, 48, rng.randint(35, 85)), width=rng.randint(1, 2))
        hd.line(pts, fill=65, width=1)
    for _ in range(120):
        x, y = rng.randrange(SIZE), rng.randrange(SIZE); r = rng.randint(3, 22)
        draw.ellipse([x-r, y-r, x+r, y+r], outline=(180, 174, 154, rng.randint(18, 55)), width=1)
    save(img, "weathered_stone_basecolor.png")
    save(normal_from_height(height.filter(ImageFilter.GaussianBlur(1.05)), 2.7), "weathered_stone_normal.png")
    save(roughness_map(232, 18, 203), "weathered_stone_roughness.png")


def texture_moss() -> None:
    rng = random.Random(301)
    img = noise_base((73, 102, 50), 30, 302)
    draw = ImageDraw.Draw(img, "RGBA")
    for _ in range(260):
        x, y = rng.randrange(SIZE), rng.randrange(SIZE); r = rng.randint(2, 9)
        draw.ellipse([x-r, y-r, x+r, y+r], fill=(80+rng.randint(-25,45), 128+rng.randint(-35,38), 58+rng.randint(-20,35), rng.randint(45,110)))
    save(img.filter(ImageFilter.GaussianBlur(0.35)), "soft_moss_basecolor.png")
    save(normal_from_height(img.convert("L"), 2.2), "soft_moss_normal.png")
    save(roughness_map(246, 7, 303), "soft_moss_roughness.png")


def texture_red_lacquer() -> None:
    rng = random.Random(401)
    img = noise_base((138, 31, 24), 18, 402)
    draw = ImageDraw.Draw(img, "RGBA")
    for _ in range(80):
        x, y = rng.randrange(SIZE), rng.randrange(SIZE)
        draw.line([(x, y), (x + rng.randint(-150, 150), y + rng.randint(-16, 16))], fill=(55, 13, 10, rng.randint(35, 105)), width=rng.randint(1, 3))
    for _ in range(42):
        x, y = rng.randrange(SIZE), rng.randrange(SIZE)
        draw.rectangle([x, y, x + rng.randint(8, 35), y + rng.randint(1, 5)], fill=(230, 103, 65, rng.randint(16, 42)))
    save(img, "aged_red_lacquer_basecolor.png")
    save(normal_from_height(img.convert("L").filter(ImageFilter.GaussianBlur(1.0)), 1.6), "aged_red_lacquer_normal.png")
    save(roughness_map(184, 34, 403), "aged_red_lacquer_roughness.png")


def texture_roof_tile() -> None:
    rng = random.Random(501)
    img = noise_base((128, 65, 43), 20, 502)
    draw = ImageDraw.Draw(img, "RGBA")
    height = Image.new("L", (SIZE, SIZE), 122)
    hd = ImageDraw.Draw(height)
    for y in range(0, SIZE, 27):
        draw.rectangle([0, y, SIZE, y+13], fill=(151, 79, 49, 110))
        draw.line([(0, y+15), (SIZE, y+15)], fill=(55, 33, 27, 150), width=2)
        hd.line([(0, y+15), (SIZE, y+15)], fill=78, width=2)
        for x in range(-20, SIZE, 42):
            draw.arc([x, y - 4, x + 46, y + 25], 0, 180, fill=(190, 106, 72, 100), width=2)
            hd.arc([x, y - 4, x + 46, y + 25], 0, 180, fill=170, width=2)
    for _ in range(110):
        x, y = rng.randrange(SIZE), rng.randrange(SIZE); r = rng.randint(1, 4)
        draw.ellipse([x-r, y-r, x+r, y+r], fill=(58, 45, 34, rng.randint(40, 90)))
    save(img, "old_roof_tile_basecolor.png")
    save(normal_from_height(height.filter(ImageFilter.GaussianBlur(0.55)), 4.0), "old_roof_tile_normal.png")
    save(roughness_map(230, 18, 503), "old_roof_tile_roughness.png")


def texture_water() -> None:
    img = noise_base((37, 88, 84), 9, 602)
    draw = ImageDraw.Draw(img, "RGBA")
    height = Image.new("L", (SIZE, SIZE), 128)
    hd = ImageDraw.Draw(height)
    rng = random.Random(601)
    for y in range(0, SIZE, 24):
        off = rng.randint(-4, 4)
        draw.line([(0, y+off), (SIZE, y+rng.randint(-4, 4))], fill=(112, 180, 170, rng.randint(22, 55)), width=1)
        hd.line([(0, y+off), (SIZE, y+off)], fill=158, width=1)
    save(img, "canal_water_basecolor.png")
    save(normal_from_height(height.filter(ImageFilter.GaussianBlur(1.5)), 1.3), "canal_water_normal.png")
    save(roughness_map(92, 24, 603), "canal_water_roughness.png")


def texture_paving() -> None:
    img = noise_base((153, 108, 79), 16, 702)
    draw = ImageDraw.Draw(img, "RGBA")
    height = Image.new("L", (SIZE, SIZE), 135)
    hd = ImageDraw.Draw(height)
    brick_w, brick_h = 64, 32
    for y in range(0, SIZE, brick_h):
        offset = 0 if (y // brick_h) % 2 == 0 else brick_w // 2
        draw.line([(0, y), (SIZE, y)], fill=(83, 60, 46, 150), width=2); hd.line([(0, y), (SIZE, y)], fill=70, width=2)
        for x in range(-offset, SIZE, brick_w):
            draw.line([(x, y), (x, y + brick_h)], fill=(83, 60, 46, 135), width=2); hd.line([(x, y), (x, y+brick_h)], fill=72, width=2)
    save(img, "warm_paving_brick_basecolor.png")
    save(normal_from_height(height, 3.0), "warm_paving_brick_normal.png")
    save(roughness_map(224, 16, 703), "warm_paving_brick_roughness.png")


def texture_yellow_wall() -> None:
    rng = random.Random(801)
    img = noise_base((211, 162, 81), 20, 802)
    draw = ImageDraw.Draw(img, "RGBA")
    for _ in range(55):
        x, y = rng.randrange(SIZE), rng.randrange(SIZE)
        draw.line([(x, y), (x+rng.randint(-65,65), y+rng.randint(-20,20))], fill=(112,75,40,rng.randint(24,78)), width=1)
    for _ in range(45):
        x, y = rng.randrange(SIZE), rng.randrange(SIZE); r = rng.randint(4, 28)
        draw.ellipse([x-r, y-r, x+r, y+r], fill=(178, 126, 61, rng.randint(12,42)))
    save(img, "hoi_an_yellow_wall_basecolor.png")
    save(normal_from_height(img.convert("L").filter(ImageFilter.GaussianBlur(1.2)), 1.5), "hoi_an_yellow_wall_normal.png")
    save(roughness_map(226, 20, 803), "hoi_an_yellow_wall_roughness.png")


def texture_ceramic() -> None:
    rng = random.Random(901)
    img = noise_base((228, 226, 211), 8, 902)
    draw = ImageDraw.Draw(img, "RGBA")
    for _ in range(38):
        x, y = rng.randrange(SIZE), rng.randrange(SIZE); r = rng.randint(15, 50)
        draw.arc([x-r, y-r, x+r, y+r], rng.randint(0, 270), rng.randint(70, 360), fill=(20,83,152,rng.randint(90,180)), width=rng.randint(2,5))
    save(img.filter(ImageFilter.GaussianBlur(0.15)), "blue_white_ceramic_basecolor.png")
    save(normal_from_height(img.convert("L"), 1.3), "blue_white_ceramic_normal.png")
    save(roughness_map(108, 28, 903), "blue_white_ceramic_roughness.png")


def texture_leaf() -> None:
    rng = random.Random(1001)
    img = noise_base((73, 127, 55), 28, 1002)
    draw = ImageDraw.Draw(img, "RGBA")
    for _ in range(165):
        x, y = rng.randrange(SIZE), rng.randrange(SIZE); r = rng.randint(5, 18)
        draw.ellipse([x-r, y-r, x+r, y+r], fill=(88+rng.randint(-25,30), 150+rng.randint(-35,30), 70+rng.randint(-18,25), rng.randint(40, 100)))
    save(img, "village_leaf_basecolor.png")
    save(normal_from_height(img.convert("L"), 1.8), "village_leaf_normal.png")
    save(roughness_map(210, 24, 1003), "village_leaf_roughness.png")


def texture_gold() -> None:
    rng = random.Random(1101)
    img = noise_base((214, 154, 48), 18, 1102)
    draw = ImageDraw.Draw(img, "RGBA")
    for _ in range(90):
        x, y = rng.randrange(SIZE), rng.randrange(SIZE)
        draw.line([(x, y), (x+rng.randint(-90,90), y+rng.randint(-10,10))], fill=(255,226,118,rng.randint(18,65)), width=1)
    save(img, "aged_gold_leaf_basecolor.png")
    save(normal_from_height(img.convert("L"), 0.9), "aged_gold_leaf_normal.png")
    save(roughness_map(118, 35, 1103, metallic=90), "aged_gold_leaf_roughness.png")


def texture_damp_stain() -> None:
    rng = random.Random(1201)
    img = noise_base((42, 54, 38), 12, 1202)
    draw = ImageDraw.Draw(img, "RGBA")
    for _ in range(80):
        x, y = rng.randrange(SIZE), rng.randrange(SIZE); r = rng.randint(8, 45)
        draw.ellipse([x-r, y-r, x+r, y+r], fill=(28, 40, 28, rng.randint(25,75)))
    save(img.filter(ImageFilter.GaussianBlur(0.6)), "damp_stain_basecolor.png")
    save(normal_from_height(img.convert("L").filter(ImageFilter.GaussianBlur(1.2)), 0.8), "damp_stain_normal.png")
    save(roughness_map(240, 10, 1203), "damp_stain_roughness.png")


def texture_lantern_silk() -> None:
    rng = random.Random(1301)
    img = noise_base((215, 74, 45), 20, 1302)
    draw = ImageDraw.Draw(img, "RGBA")
    for x in range(0, SIZE, 28):
        draw.line([(x, 0), (x+rng.randint(-10,10), SIZE)], fill=(255, 182, 92, rng.randint(20, 70)), width=1)
    for _ in range(36):
        x, y = rng.randrange(SIZE), rng.randrange(SIZE)
        draw.line([(x, y), (x+rng.randint(-70,70), y+rng.randint(-5,5))], fill=(130, 23, 18, rng.randint(18,55)), width=1)
    save(img, "lantern_silk_basecolor.png")
    save(normal_from_height(img.convert("L"), 0.9), "lantern_silk_normal.png")
    save(roughness_map(150, 20, 1303), "lantern_silk_roughness.png")


def make_contact_sheet() -> None:
    files = sorted(TEXTURE_DIR.glob("*_basecolor.png"))
    if not files:
        return
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    thumb, pad, cols = 118, 18, 4
    rows = math.ceil(len(files) / cols)
    sheet = Image.new("RGB", (cols * (thumb + pad) + pad, rows * (thumb + 38) + pad), (242, 238, 230))
    draw = ImageDraw.Draw(sheet)
    for i, path in enumerate(files):
        img = Image.open(path).convert("RGB").resize((thumb, thumb))
        x = pad + (i % cols) * (thumb + pad)
        y = pad + (i // cols) * (thumb + 38)
        sheet.paste(img, (x, y))
        draw.text((x, y + thumb + 5), path.name.replace("_basecolor.png", ""), fill=(35, 30, 24))
    sheet.save(DOCS_DIR / "texture_preview_contact_sheet.png")


def main() -> None:
    TEXTURE_DIR.mkdir(parents=True, exist_ok=True)
    for func in [
        texture_old_wood, texture_weathered_stone, texture_moss, texture_red_lacquer,
        texture_roof_tile, texture_water, texture_paving, texture_yellow_wall,
        texture_ceramic, texture_leaf, texture_gold, texture_damp_stain, texture_lantern_silk,
    ]:
        func()
    make_contact_sheet()
    print(f"Generated procedural textures: {TEXTURE_DIR}")


if __name__ == "__main__":
    main()
