"""Verified zero-fit scoring for the active matched two-cycle release."""
from pathlib import Path
import json,hashlib,argparse
import pandas as pd
from .data import ROOT
from .experiment4_pipeline import Experiment4Scorer

def load_active(task):
    config=json.loads((ROOT/'src/models/configs/active_pipeline.json').read_text())
    bundle=ROOT/config['tasks'][task]['bundle']
    manifest=json.loads((bundle/'manifest.json').read_text())['sha256']
    for name,digest in manifest.items():
        if hashlib.sha256((bundle/name).read_bytes()).hexdigest()!=digest:raise ValueError('Bundle checksum mismatch: '+name)
    scorer=Experiment4Scorer(bundle)
    if scorer.task!=task:raise ValueError('Wrong task in bundle')
    return scorer

def score(task,frame):
    if 'order_id' not in frame or frame.order_id.isna().any() or frame.order_id.duplicated().any():raise ValueError('Missing or repeated order identifiers')
    if frame.columns.duplicated().any():raise ValueError('Repeated feature columns')
    scorer=load_active(task);missing=set(scorer.schema['predictor_allowlist'])-set(frame.columns)
    if missing:raise ValueError('Missing features: '+str(sorted(missing)))
    return scorer.score(frame)
if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--task',choices=['regression','classification'],required=True);a.add_argument('--input',type=Path,required=True);a.add_argument('--output',type=Path,required=True);args=a.parse_args()
    if args.output.exists():raise FileExistsError('Preserve existing scoring output')
    score(args.task,pd.read_csv(args.input,dtype={'order_id':'string'})).to_csv(args.output,index=False)
