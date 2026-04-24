from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class CorrectionRule:
    raw: str
    repair: str
    note: str = ""


@dataclass(frozen=True)
class AssetBundle:
    directory: Path
    policy: str
    system_prompt: str
    glossary: str
    correction_rules: tuple[CorrectionRule, ...]
    examples: str


REQUIRED_ASSET_FILES = (
    "policy.md",
    "system-prompt.md",
    "glossary.md",
    "correction-rules.yaml",
    "examples.md",
)


def default_assets_dir() -> Path:
    """Return the source-tree default assets directory for editable installs."""
    return Path(__file__).resolve().parents[2] / "assets" / "default"


def load_asset_bundle(directory: str | Path | None = None) -> AssetBundle:
    asset_dir = Path(directory) if directory is not None else default_assets_dir()
    asset_dir = asset_dir.expanduser().resolve()

    missing = [name for name in REQUIRED_ASSET_FILES if not (asset_dir / name).exists()]
    if missing:
        missing_list = ", ".join(missing)
        raise FileNotFoundError(f"missing repair asset(s) in {asset_dir}: {missing_list}")

    rules_data = _load_yaml(asset_dir / "correction-rules.yaml")
    rules = tuple(_parse_rule(item) for item in rules_data.get("rules", []))

    return AssetBundle(
        directory=asset_dir,
        policy=(asset_dir / "policy.md").read_text(encoding="utf-8"),
        system_prompt=(asset_dir / "system-prompt.md").read_text(encoding="utf-8"),
        glossary=(asset_dir / "glossary.md").read_text(encoding="utf-8"),
        correction_rules=rules,
        examples=(asset_dir / "examples.md").read_text(encoding="utf-8"),
    )


def _load_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if data is None:
        return {}
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a YAML mapping")
    return data


def _parse_rule(item: Any) -> CorrectionRule:
    if not isinstance(item, dict):
        raise ValueError("each correction rule must be a mapping")
    raw = str(item.get("raw", "")).strip()
    repair = str(item.get("repair", "")).strip()
    note = str(item.get("note", "")).strip()
    if not raw or not repair:
        raise ValueError("each correction rule requires non-empty raw and repair fields")
    return CorrectionRule(raw=raw, repair=repair, note=note)
