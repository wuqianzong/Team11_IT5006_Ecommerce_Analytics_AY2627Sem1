"""Build fresh pre-terminal core bundles/references; no terminal scoring in this command."""
from __future__ import annotations
import argparse
import copy
import json
import warnings
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from sklearn.exceptions import ConvergenceWarning
from src.common.loaders import sha256_file
from .data import ROOT,TARGETS
from .io import write_json,ids_digest
from .pipelines import positive_probability
from .policy import select_cost_threshold,threshold_curve
from .refinement_core import CORE_FEATURES,CORE_SCHEMA_VERSION,make_core_pipeline
from .refinement_temporal import chronological_data

CONFIG=Path(__file__).parent/'configs/refinement_core_v2.json'

def build(root,output,evidence,config_path=CONFIG):
    if output.exists():raise FileExistsError('Versioned output exists; never overwrite')
    config=json.loads(config_path.read_text())
    if config['terminal_evaluation_allowed'] or config['predictors']!=CORE_FEATURES:raise ValueError('Invalid frozen boundary')
    selected=json.loads((evidence/'results/development_selection.json').read_text())['core_finalist_candidates']
    if selected!=config['selected']:raise ValueError('Settings differ from verified development selection')
    verify=json.loads((evidence/'audit/verification.json').read_text())
    if not all(verify['checks'].values()):raise ValueError('Diagnostic checks failed')
    protocol=json.loads((evidence/'results/identity.json').read_text())
    data=chronological_data(root,config)
    output.mkdir(parents=True)
    data['membership'].to_csv(output/'chronological_fold_membership.csv',index=False)
    data['exclusions'].to_csv(output/'chronological_exclusions.csv',index=False)
    data['terminal_identities'].to_csv(output/'terminal_identity_manifest.csv',index=False)
    data['terminal_group_purge'].to_csv(output/'terminal_group_training_purge.csv',index=False)
    # Compare independent production reconstruction with diagnostic memberships.
    old=pd.read_csv(evidence/'results/chronological_fold_membership.csv',dtype={'order_id':'string'})
    keys=['task','fold','role','order_id']
    if not data['membership'].astype({'order_id':'string'}).sort_values(keys).reset_index(drop=True).equals(old.sort_values(keys).reset_index(drop=True)):
        raise ValueError('Reconstructed memberships differ from diagnostics')
    chosen=config['selected']['classification']['id']
    oof=pd.concat([pd.read_csv(evidence/'results/jobs'/f'E01-classification-{chosen}-fold{f}'/'validation_predictions.csv') for f in range(5)],ignore_index=True)
    if oof.order_id.duplicated().any():raise ValueError('Repeated OOF policy observation')
    threshold,report=select_cost_threshold(oof.target,oof.prediction,config['policy_cost_ratio'])
    policy={'kind':'fixed_threshold','positive_class':1,'comparison':'>=','threshold':threshold,
            'cost_ratio_fn_to_fp':5,'cost_assumption':'illustrative, not measured business cost',
            'selection_population':'preterminal chronological OOF after model selection; not independent',
            'tie_break':'highest threshold among equal integer costs','OOF_report':report}
    write_json(policy,output/'frozen_decision_policy.json')
    threshold_curve(oof.target,oof.prediction).to_csv(output/'policy_threshold_curve.csv',index=False)
    scenarios=[]
    for ratio in [1,2,5,10]:
        value,scenario=select_cost_threshold(oof.target,oof.prediction,ratio)
        scenarios.append({'ratio':ratio,'threshold':value,**scenario})
    pd.DataFrame(scenarios).to_csv(output/'policy_scenarios.csv',index=False)
    attempts=[]
    for task in TARGETS:
        training=data['final_training'][task];X=training[CORE_FEATURES];y=training[TARGETS[task]]
        training[['order_id','customer_unique_id','prediction_timestamp']].to_csv(output/f'{task}_preterminal_training_ids.csv',index=False)
        candidates=[('selected',config['selected'][task])]+[(model,{'id':'baseline_'+model,'family':model,'baseline_model':model}) for model in ['dummy','linear','tree']]
        for role,candidate in candidates:
            folder=output/task/role;folder.mkdir(parents=True)
            pipe=make_core_pipeline(task,candidate,config['baseline_config'])
            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter('always');pipe.fit(X,y)
            notices=[{'category':w.category.__name__,'message':str(w.message)} for w in caught]
            if any(issubclass(w.category,ConvergenceWarning) for w in caught):raise RuntimeError('Unconverged final fit; stopped')
            joblib.dump(pipe,folder/'pipeline.joblib',compress=3)
            write_json({'predictor_allowlist':CORE_FEATURES,'version':CORE_SCHEMA_VERSION,'input_units':'original units',
                        'null_cells':'fold-fitted imputation; missing columns rejected','state_tokens':'malformed/unknown -> Unknown'},folder/'feature_schema.json')
            write_json({'task':task,'model_version':config['version'],'role':role,'candidate':candidate['id'],
                        'terminal_cutoff':config['terminal_cutoff'],'training_n':len(training),
                        'training_ids_sha256':ids_digest(training.order_id),'status':'prefitted_pending_terminal_evaluation',
                        'limitations':config['limitations']},folder/'metadata.json')
            write_json({'candidate':candidate,'baseline_config':config['baseline_config']},folder/'configuration.json')
            stats={c:{'missing_n':int(X[c].isna().sum()),'dtype':str(X[c].dtype)} for c in CORE_FEATURES}
            for c in CORE_FEATURES:
                if c=='customer_state':stats[c]['counts']=X[c].fillna('Unknown').value_counts().to_dict()
                else:
                    numeric=pd.to_numeric(X[c],errors='coerce')
                    stats[c].update(min=numeric.min(),max=numeric.max(),mean=numeric.mean(),std=numeric.std(),median=numeric.median())
            write_json(stats,folder/'feature_stats.json')
            write_json(notices,folder/'fit_warnings.json')
            if task=='classification':write_json(policy if role=='selected' else {'kind':'fixed_threshold','positive_class':1,'comparison':'>=','threshold':.5,'selection_population':'baseline diagnostic default; not optimized'},folder/'decision_policy.json')
            sample=X.iloc[:64];loaded=joblib.load(folder/'pipeline.joblib')
            before=pipe.predict(sample) if task=='regression' else positive_probability(pipe,sample)
            after=loaded.predict(sample) if task=='regression' else positive_probability(loaded,sample)
            if not np.allclose(before,after,rtol=1e-12,atol=1e-12):raise ValueError('Reload prediction mismatch')
            write_json({'output_hashes':{p.name:sha256_file(p) for p in folder.iterdir() if p.is_file()}},folder/'bundle_manifest.json')
            attempts.append({'task':task,'role':role,'candidate':candidate['id'],'training_n':len(training),'reload_matches':True,'warnings':notices})
            print('Prefit',task,role,len(training),flush=True)
    write_json({'status':'preterminal_bundles_verified_terminal_not_evaluated','new_predictive_fits':len(attempts),
                'total_cycle_predictive_fits':255+len(attempts),'attempts':attempts,'input_hashes':data['input_hashes'],
                'config_sha256':sha256_file(config_path),'diagnostic_identity':protocol,'terminal_evaluated':False},output/'implementation_verification.json')

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);p.add_argument('--evidence',type=Path,required=True)
    a=p.parse_args();build(ROOT,a.output,a.evidence)
