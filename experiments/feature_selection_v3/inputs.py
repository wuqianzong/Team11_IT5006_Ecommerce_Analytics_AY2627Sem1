"""Stable import identity for new trial bundles and explicit legacy loader."""
import sys
from contextlib import contextmanager
import joblib
from .runner import SubsetInputContract as LegacySubsetInputContract


class SubsetInputContract(LegacySubsetInputContract):
    """Same validated semantics, with a persistent module-qualified identity."""


@contextmanager
def legacy_contract_identity():
    """Offline compatibility for old -m bundles; restore __main__ afterwards."""
    module = sys.modules['__main__']
    existed = hasattr(module, 'SubsetInputContract')
    previous = getattr(module, 'SubsetInputContract', None)
    module.SubsetInputContract = LegacySubsetInputContract
    try:
        yield
    finally:
        if existed:
            module.SubsetInputContract = previous
        else:
            del module.SubsetInputContract


def load_trial(path):
    # Local trusted study artifacts only: pickle must never load untrusted files.
    with legacy_contract_identity():
        return joblib.load(path)
