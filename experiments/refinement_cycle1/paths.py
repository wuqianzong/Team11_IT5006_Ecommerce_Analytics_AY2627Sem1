"""Portable output binding; scientific parameters remain in frozen protocols."""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def run_root():
    value = Path(os.environ.get('IT5006_REFINEMENT_RUN_ROOT', 'artifacts/generated/refinement-cycle1'))
    value = (ROOT / value).resolve()
    if not value.is_relative_to(ROOT) or value == ROOT:
        raise ValueError('Run output must be a dedicated subdirectory of this checkout')
    return value


def binding(protocol):
    """Relocate evidence only; never change folds, features, models or rules."""
    protocol = dict(protocol)
    names = {'feature-selection-v3-screen': 'screen',
             'feature-selection-v3-combinations': 'combinations'}
    protocol['baseline_evidence'] = str((run_root() / 'initial_reference/results').relative_to(ROOT))
    protocol['baseline_membership'] = str((run_root() / 'core/chronological_fold_membership.csv').relative_to(ROOT))
    if 'screen_evidence' in protocol:
        protocol['screen_evidence'] = str((run_root() / names[Path(protocol['screen_evidence']).name]).relative_to(ROOT))
    if 'reuse' in protocol:
        protocol['reuse'] = [dict(r, source=str((run_root() / names[Path(r['source']).name]).relative_to(ROOT))) for r in protocol['reuse']]
    return protocol
