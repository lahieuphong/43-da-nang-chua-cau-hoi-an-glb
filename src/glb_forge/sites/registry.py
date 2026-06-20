from __future__ import annotations

from pathlib import Path

from glb_forge.sites.models import HeritageSite
from glb_forge.sites.provinces import DA_NANG_SITES

HERITAGE_SITES = [*DA_NANG_SITES]


def validate_registry(sites: list[HeritageSite] = HERITAGE_SITES) -> None:
    seen_keys: dict[str, HeritageSite] = {}
    seen_outputs: dict[Path, HeritageSite] = {}
    for site in sites:
        if site.registry_key in seen_keys:
            other = seen_keys[site.registry_key]
            raise ValueError(f"Trùng registry key: {site.registry_key!r} ({other.name} / {site.name})")
        seen_keys[site.registry_key] = site
        output_path = site.output_path("output")
        if output_path in seen_outputs:
            other = seen_outputs[output_path]
            raise ValueError(f"Trùng output path: {output_path} ({other.name} / {site.name})")
        seen_outputs[output_path] = site


def iter_sites() -> tuple[HeritageSite, ...]:
    validate_registry()
    return tuple(HERITAGE_SITES)


def get_site(registry_key: str) -> HeritageSite:
    validate_registry()
    for site in HERITAGE_SITES:
        if site.registry_key == registry_key:
            return site
    available = ", ".join(site.registry_key for site in HERITAGE_SITES)
    raise KeyError(f"Không tìm thấy di tích {registry_key!r}. Các key hiện có: {available}")


__all__ = ["HERITAGE_SITES", "get_site", "iter_sites", "validate_registry"]
