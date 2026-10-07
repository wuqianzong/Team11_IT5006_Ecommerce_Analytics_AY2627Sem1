"""Stage-specific executable identities without internal/future report dependencies."""
import hashlib
import json

from src.common.loaders import sha256_file
from .stage4_checkpoint import stage4_identity


def identity(root, phase="supplement"):
    if phase not in {"supplement", "final"}:
        raise ValueError("Unknown Stage 5 phase")
    result = stage4_identity(root)
    paths = [root / "src/models" / f"{name}.py" for name in
             ["tutorial8", "verify_tutorial8", "stage5_identity"]]
    paths += [root / "src/models/tests/test_tutorial8.py"]
    if phase == "final":
        paths += [root / "src/models" / f"{name}.py" for name in
                  ["finalize", "reproduction", "score", "verify_stage5", "stage5_checkpoint"]]
        paths += [root / "src/models/tests/test_stage5.py", root / "src/models/tests/test_reproduction.py",
                  root / "src/models/tests/test_stage5_checkpoint.py",
                  root / "src/models/configs/stage5_frozen_protocol.json"]
    hashes = {**result["implementation_and_document_hashes"],
              **{str(p.relative_to(root)): sha256_file(p) for p in paths}}
    result.update(scope=f"stage5_{phase}_executable_dependencies",
                  implementation_and_document_hashes=hashes,
                  code_identity_sha256=hashlib.sha256(json.dumps(hashes, sort_keys=True).encode()).hexdigest())
    return result
