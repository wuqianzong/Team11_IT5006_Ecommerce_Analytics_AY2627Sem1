"""Strict JSON, input/code identities, and new-run-only publication helpers."""
from __future__ import annotations

import hashlib
import json
import math
import subprocess
from pathlib import Path

import numpy as np

from src.common.loaders import sha256_file
from src.features.serialization import write_csv_lf, write_text_lf


def clean_json(value):
    if isinstance(value, dict):
        return {str(k): clean_json(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, np.ndarray)):
        return [clean_json(v) for v in value]
    if isinstance(value, np.generic):
        return clean_json(value.item())
    if isinstance(value, float) and not math.isfinite(value):
        return None
    return value


def write_json(value, path):
    write_text_lf(json.dumps(clean_json(value), indent=2, sort_keys=True, allow_nan=False) + "\n", path)


def identity(root):
    # Only executable baseline dependencies belong to this checkpoint identity.
    # Later-stage or internal reporting files may exist locally but are not inputs.
    module_names = ["__init__", "audit", "data", "evaluate", "io", "pipelines",
                    "predict", "train", "verify", "verify_checkpoint"]
    paths = [root / "src/models" / f"{name}.py" for name in module_names]
    paths += list((root / "src/features").glob("*.py"))
    paths += [root / "src/common" / f"{name}.py"
              for name in ["__init__", "core_schemas", "loaders", "schemas"]]
    paths += [root / "src/models/configs/stage3_baseline.json",
              root / "src/models/tests/__init__.py",
              root / "src/models/tests/test_baselines.py",
              root / "src/models/tests/test_checkpoint.py"]
    paths += [root / "requirements.txt", root / "src/models/requirements-stage3.txt"]
    hashes = {str(p.relative_to(root)): sha256_file(p) for p in sorted(paths)}
    revision = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
    diff = subprocess.check_output(["git", "diff", "--binary", "HEAD"], cwd=root)
    return {"git_revision": revision, "tracked_diff_sha256": hashlib.sha256(diff).hexdigest(),
            "scope": "stage3_baseline_executable_dependencies",
            # Retain the historical schema key; new identities cover executable inputs only.
            "implementation_and_document_hashes": hashes,
            "code_identity_sha256": hashlib.sha256(json.dumps(hashes, sort_keys=True).encode()).hexdigest()}


def ids_digest(ids):
    return hashlib.sha256(("\n".join(sorted(map(str, ids))) + "\n").encode()).hexdigest()


__all__ = ["write_csv_lf", "write_json", "identity", "ids_digest"]
