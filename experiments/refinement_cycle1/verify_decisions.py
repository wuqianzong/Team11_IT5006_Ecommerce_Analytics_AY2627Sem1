"""Recheck the recorded preterminal decision evidence; never optimise on terminal."""
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd
from src.models.io import write_json
from .paths import ROOT


def verify(run):
    summary = pd.read_csv(run/'model_gate/model_comparisons/model_summary.csv').set_index('id')
    paired = pd.read_csv(run/'model_gate/model_comparisons/paired_summary.csv').set_index(['candidate','comparator'])
    assert summary.loc['r19_tree','validation_mean'] < summary.loc['r13_tree','validation_mean']
    assert not bool(paired.loc[('r19_tree','r13_tree'),'practical_flag'])
    for subset in ['r13','r19']:
        assert paired.loc[(subset+'_forest',subset+'_tree'),'gain_mean'] < 0
    assert bool(paired.loc[('c14_regularized_logistic','c14_plain_logistic'),'practical_flag'])
    assert summary.loc['c14_regularized_logistic','validation_mean'] > summary.loc['c14_forest','validation_mean']
    decision = json.loads((ROOT/'experiments/feature_selection_v3/model_decision.json').read_text())
    np.testing.assert_allclose(summary.loc['r13_tree','validation_mean'], decision['regression']['mean_validation_mae'], rtol=1e-10, atol=1e-10)
    np.testing.assert_allclose(summary.loc['c14_regularized_logistic','validation_mean'], decision['classification']['mean_validation_average_precision'], rtol=1e-10, atol=1e-10)
    write_json({'status':'passed','regression_selected':'r13_tree','classification_selected':'c14_regularized_logistic',
                'numerical_regression_winner_preserved':'r19_tree','terminal_read':False,'new_fits':0},run/'decision_verification.json')


if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--run',type=Path,required=True)
    verify(p.parse_args().run.resolve())
