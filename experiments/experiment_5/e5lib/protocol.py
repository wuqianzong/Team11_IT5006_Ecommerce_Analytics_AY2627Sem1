"""Read spec/protocol.yaml; let owning stages write their data-dependent sections.

protocol.yaml is created in s01 (pre-registered layer). Data-dependent sections are written
only by the stage that owns them (README section 5.2) and are never overwritten silently.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import hashlib
import json

import yaml

from .paths import assert_inside_e5, spec_path

DATA_DEPENDENT_OWNERS = {
    "test_cutoffs": "s02_data",
    "core_set": "s04_features",
    "selected_set": "s04_features",
    "fold_boundaries": "s05_partition",
    "class_support": "s05_partition",
    "min_training_rows": "s05_partition",
}


_USED_SECTIONS: set[str] = set()  # data-dependent sections read or written in this process


def used_sections() -> list[str]:
    return sorted(_USED_SECTIONS)


def layer_hashes(data: dict[str, Any] | None = None) -> dict[str, str]:
    """sha256 of the pre-registered layer and of each data-dependent section.

    Manifests compare these instead of the whole file, so a later stage writing its own
    data-dependent section does not make earlier stages stale.
    """
    if data is None:
        data = load() if _path().exists() else {}
    def h(obj) -> str:
        return hashlib.sha256(json.dumps(obj, sort_keys=True, default=str).encode()).hexdigest()
    pre = {k: v for k, v in data.items() if k != "data_dependent"}
    out = {"pre_registered": h(pre)}
    for section, block in (data.get("data_dependent") or {}).items():
        out[f"data_dependent.{section}"] = h(block.get("values"))
    return out


class ProtocolError(RuntimeError):
    """protocol.yaml is missing, malformed, or a write broke the ownership rules."""


def _path():
    return spec_path("protocol.yaml")


def load() -> dict[str, Any]:
    path = _path()
    if not path.exists():
        raise ProtocolError(f"{path} not found: it is created by s01_problem (README section 5.2)")
    data = yaml.safe_load(path.read_text()) or {}
    if not isinstance(data, dict):
        raise ProtocolError("protocol.yaml must be a mapping at the top level")
    return data


def get(key: str, default: Any = ...) -> Any:
    """Dotted lookup, e.g. get("decision_rule.name"). Raises if missing and no default."""
    node: Any = load()
    parts = key.split(".")
    if parts[0] == "data_dependent" and len(parts) > 1:
        _USED_SECTIONS.add(parts[1])
    for part in parts:
        if isinstance(node, dict) and part in node:
            node = node[part]
        elif default is not ...:
            return default
        else:
            raise ProtocolError(f"protocol.yaml has no key {key!r}")
    return node


def set_data_dependent(section: str, values: Any, stage: str, *, replace: bool = False) -> None:
    """Write data_dependent.<section>; only its owning stage may do so.

    An existing value is kept unless replace=True, which must follow a CHANGELOG entry
    (README section 9.2).
    """
    owner = DATA_DEPENDENT_OWNERS.get(section)
    if owner is None:
        raise ProtocolError(f"unknown data-dependent section {section!r}")
    if stage != owner:
        raise ProtocolError(f"{section!r} is owned by {owner}, not {stage}")
    _USED_SECTIONS.add(section)
    data = load()
    block = data.setdefault("data_dependent", {})
    if section in block and not replace:
        if block[section].get("values") == values:
            return
        raise ProtocolError(
            f"data_dependent.{section} is already set by {block[section].get('set_by')}; "
            "changing it needs a CHANGELOG entry and replace=True"
        )
    block[section] = {
        "values": values,
        "set_by": stage,
        "set_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    path = assert_inside_e5(_path())
    path.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True))
