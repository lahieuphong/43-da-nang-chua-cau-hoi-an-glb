from __future__ import annotations

from glb_forge.scenes.chua_cau_hoi_an import create_chua_cau_hoi_an
from glb_forge.sites.models import HeritageSite, Province

DA_NANG = Province(code="43", slug="da-nang", name="Đà Nẵng / Hội An", output_name="da_nang")

DA_NANG_SITES = [
    HeritageSite(
        site_id="chua-cau-hoi-an",
        name="Chùa Cầu Hội An / Cầu Nhật Bản / Lai Viễn Kiều",
        province=DA_NANG,
        output_name="chua_cau_hoi_an",
        create_scene=create_chua_cau_hoi_an,
    )
]
