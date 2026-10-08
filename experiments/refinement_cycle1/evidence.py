"""Check losslessly compressed accepted evidence and compare a complete new run."""
import argparse
import csv
import io
import json
from pathlib import Path
import tarfile
import tempfile
import numpy as np
import pandas as pd
from src.common.loaders import sha256_file
from src.models.io import write_json
from .paths import ROOT

PACKAGE = ROOT/'artifacts/metrics/refinement-cycle1-evidence'


def unpack(destination):
    if destination.exists():
        raise FileExistsError('Use a new evidence directory')
    manifest = json.loads((PACKAGE/'manifest.json').read_text())
    for rel, expected in manifest['input_hashes'].items():
        if sha256_file(ROOT/rel) != expected:
            raise ValueError('Committed input changed: '+rel)
    destination.mkdir(parents=True)
    for archive in manifest['archives']:
        path = PACKAGE/archive['file']
        assert sha256_file(path) == archive['sha256'], path
        folder = destination/archive['phase'];folder.mkdir()
        with tarfile.open(path, 'r:gz') as tar:
            tar.extractall(folder, filter='data')
        compact=folder/'.compact/predictions.json'
        if compact.exists():
            for record in json.loads(compact.read_text()):
                parts=[]
                for key in ['base','scores']:
                    with (folder/record[key]).open(newline='') as f:
                        reader=csv.DictReader(f);parts.append(list(reader))
                assert len(parts[0])==len(parts[1])
                dest=folder/record['output'];dest.parent.mkdir(parents=True,exist_ok=True)
                with dest.open('w',newline='') as f:
                    writer=csv.DictWriter(f,fieldnames=record['header'],lineterminator='\n')
                    writer.writeheader();writer.writerows([{**a,**b} for a,b in zip(*parts)])
        for rel, digest in archive['members'].items():
            assert sha256_file(folder/rel) == digest, rel
    return manifest


def compare_csv(new, old):
    a,b = pd.read_csv(new),pd.read_csv(old)
    # Timing is execution evidence, not a deterministic model output.
    ignored = {'fit_seconds'}
    cols = [c for c in b.columns if c not in ignored]
    if set(a.columns)-ignored != set(cols) or len(a) != len(b):
        raise AssertionError('Different rows/schema: '+str(new))
    for c in cols:
        if pd.api.types.is_numeric_dtype(b[c]) and pd.api.types.is_numeric_dtype(a[c]):
            np.testing.assert_allclose(a[c], b[c], rtol=1e-10, atol=1e-10, equal_nan=True, err_msg=str(new)+':'+c)
        else:
            pd.testing.assert_series_equal(a[c].astype('string'), b[c].astype('string'), check_names=False)


def compare(run):
    with tempfile.TemporaryDirectory(prefix='it5006-evidence-') as temporary:
        expected = Path(temporary)/'accepted'
        manifest = unpack(expected)
        counts={}
        # Per-job predictions include ALL rejected/retained candidates, not just
        # rounded summary winners. All fold metrics, counts and IDs also match.
        for archive in manifest['archives']:
            phase = archive['phase']; checked=0
            for rel in archive['comparison_csvs']:
                compare_csv(run/phase/rel, expected/phase/rel)
                checked+=1
            counts[phase]=checked
        write_json({'status':'passed','compared_csvs_by_phase':counts,
                    'all_candidate_validation_predictions_compared':True,
                    'tolerance':{'rtol':1e-10,'atol':1e-10},
                    'excluded_nondeterministic_fields':['fit_seconds','timestamps','absolute output paths','pickle bytes'],
                    'accepted_evidence_manifest_sha256':sha256_file(PACKAGE/'manifest.json')},run/'accepted_evidence_comparison.json')
    print('PASS accepted evidence comparisons',counts)


if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='command',required=True)
    u=sub.add_parser('unpack');u.add_argument('--output',type=Path,required=True)
    c=sub.add_parser('compare');c.add_argument('--run',type=Path,required=True)
    a=p.parse_args()
    if a.command=='unpack':
        unpack(a.output.resolve());print('PASS archive and input checksums; no fits')
    else:compare(a.run.resolve())
