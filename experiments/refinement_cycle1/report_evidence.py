"""Numerical contract for an externally supplied report; no private file required."""
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd
from src.common.loaders import sha256_file
from src.models.io import write_json
from .paths import ROOT

CONTRACT = ROOT/'artifacts/metrics/refinement-cycle1-evidence/report_evidence.json'


def claims(run):
    result = []
    def add(section, file, selector, field, value):
        result.append({'claim_id': f'C{len(result)+1:03d}', 'report_section':section,
                       'source':file,'selector':selector,'field':field,'value':float(value)})
    terminal = pd.read_csv(run/'terminal/metrics.csv')
    for row in terminal.itertuples():
        section='6' if row.task=='regression' else '7'
        for key in (['n','mae','rmse','r2','negative_predictions'] if row.task=='regression' else ['n','positives','prevalence','average_precision','roc_auc','brier']):
            add(section,'terminal/metrics.csv',{'task':row.task,'role':row.role},key,getattr(row,key))
    dev = pd.read_csv(run/'development_fold_metrics.csv')
    for task,key in [('regression','mae'),('classification','average_precision')]:
        for partition in ['training_resubstitution','validation']:
            x=dev[(dev.task==task)&(dev.partition==partition)][key]
            for statistic,value in [('mean',x.mean()),('sd',x.std(ddof=1))]:
                add('6','development_fold_metrics.csv',{'task':task,'partition':partition},key+'_'+statistic,value)
    policy=json.loads((run/'frozen_decision_policy.json').read_text())
    add('7','frozen_decision_policy.json',{},'threshold',policy['threshold'])
    add('7','frozen_decision_policy.json',{},'cost_ratio_fn_to_fp',policy['cost_ratio_fn_to_fp'])
    comparison=json.loads((run/'terminal/classification_policy_comparison.json').read_text())
    for kind in ['frozen_policy','fixed_05_diagnostic']:
        for key in ['alerts','precision_1','recall_1','f1_1','tp','fp','tn','fn','illustrative_cost_5_to_1','alert_fraction','fpr','fnr']:
            add('7','terminal/classification_policy_comparison.json',{'policy':kind},key,comparison[kind][key])
    add('7','terminal/classification_policy_comparison.json',{},'no_alert_cost',comparison['no_alert_cost'])
    subgroups=pd.read_csv(run/'terminal/subgroups.csv',dtype={'subgroup':'string'})
    for row in subgroups[(subgroups.task=='regression')&subgroups.dimension.isin(['observed_duration_days','customer_state'])].itertuples():
        if row.dimension=='customer_state' and row.subgroup not in {'SP','RJ'}:continue
        for field in ['n','mae']:
            add('Appendix B','terminal/subgroups.csv',{'task':row.task,'dimension':row.dimension,'subgroup':row.subgroup},field,getattr(row,field))
    coef=pd.read_csv(run/'development_diagnostics/logistic_coefficients.csv')
    for row in coef[coef.transformed_feature.isin(['numeric__n_items','numeric__n_products','numeric__n_sellers','numeric__total_freight'])].itertuples():
        for field in ['coefficient','odds_ratio']:
            add('Appendix C','development_diagnostics/logistic_coefficients.csv',{'transformed_feature':row.transformed_feature},field,getattr(row,field))
    perm=pd.read_csv(run/'development_diagnostics/permutation_summary.csv')
    for row in perm.itertuples():
        add('Appendix C','development_diagnostics/permutation_summary.csv',{'task':row.task,'feature':row.feature},'mean',row.mean)
    intervals=pd.read_csv(run/'terminal/paired_intervals.csv')
    for row in intervals.itertuples():
        for field in ['difference_selected_minus_reference','lower_95','upper_95','replicates_requested','replicates_valid','seed']:
            add('6-7','terminal/paired_intervals.csv',{'task':row.task,'reference':row.reference},field,getattr(row,field))
    classes=pd.read_csv(run/'terminal/classification_per_class.csv')
    for _,row in classes.iterrows():
        for field in ['support','predicted_n','precision','recall','f1']:
            add('Appendix B','terminal/classification_per_class.csv',{'class':int(row['class'])},field,row[field])
    importance=pd.read_csv(run/'development_diagnostics/tree_importance.csv')
    for row in importance[importance.impurity_importance.gt(0)].itertuples():
        add('Appendix C','development_diagnostics/tree_importance.csv',{'transformed_feature':row.transformed_feature},'impurity_importance',row.impurity_importance)
    membership=pd.read_csv(run/'chronological_fold_membership.csv')
    for (task,fold,role),group in membership.groupby(['task','fold','role']):
        add('Appendix D','chronological_fold_membership.csv',{'task':task,'fold':int(fold),'role':role},'n',len(group))
    base=pd.read_csv(ROOT/'data/business/ml/orders_ml_features.csv',dtype={'order_id':'string'}).set_index('order_id')
    for task,target in [('regression','lead_days'),('classification','is_detractor')]:
        ids=pd.read_csv(run/f'{task}_training_ids.csv',dtype={'order_id':'string'}).order_id
        add('6-7',f'{task}_training_ids.csv',{'target_from':'data/business/ml/orders_ml_features.csv'},'training_n',len(ids))
        add('6-7',f'{task}_training_ids.csv',{'target_from':'data/business/ml/orders_ml_features.csv'},'training_target_mean',base.loc[ids,target].mean())
    eligibility=pd.read_csv(run/'terminal/eligibility.csv')
    add('Appendix D','terminal/eligibility.csv',{},'reserved_unique_orders',eligibility.order_id.nunique())
    for (task,reason),group in eligibility.groupby(['task','reason']):
        add('Appendix D','terminal/eligibility.csv',{'task':task,'reason':reason},'n',len(group))
    return result


def verify(run, report=None):
    expected=json.loads(CONTRACT.read_text())
    actual=claims(run)
    assert len(actual)==len(expected['claims'])
    for a,b in zip(actual,expected['claims']):
        assert {k:v for k,v in a.items() if k!='value'}=={k:v for k,v in b.items() if k!='value'}
        assert np.isclose(a['value'],b['value'],rtol=1e-10,atol=1e-10), a
    if report is not None and sha256_file(report)!=expected['external_report_sha256']:
        raise ValueError('Different report version: review text/claims and issue a new contract, not a silent match')
    print(f'PASS {len(actual)} numerical report claims; prose still needs human review')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--run',type=Path,required=True)
    p.add_argument('--verify',action='store_true');p.add_argument('--create-contract',action='store_true')
    p.add_argument('--report',type=Path)
    a=p.parse_args()
    if a.create_contract:
        if CONTRACT.exists() or a.report is None: p.error('New contract requires an external report; never overwrite')
        write_json({'version':'refinement-selected-v3','external_report_sha256':sha256_file(a.report),
                    'claims':claims(a.run),
                    'trial_sections':{'4':'initial_reference/results and audit','5':'screen, combinations/incremental_comparisons and model_gate/model_comparisons'},
                    'verification_scope':'Calculations and version identity, not semantic validation of every sentence or Word layout.'},CONTRACT)
    elif a.verify:verify(a.run,a.report)
    else:p.error('Choose --verify or --create-contract')
