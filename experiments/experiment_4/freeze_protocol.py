from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[2]
core=['n_items','n_products','total_price','total_freight','freight_ratio','customer_state','purchase_month','purchase_dayofweek','purchase_hour']
old=json.loads((ROOT/'src/models/configs/refinement_selected_v4.json').read_text())
catalog={}
for task in ['regression','classification']:
    expanded=old['predictors_by_task'][task]
    rows=[]
    def add(id,cycle,family,features,**kw):rows.append(dict(id=id,cycle=cycle,family=family,features=features,**kw))
    for family in ['dummy','plain','tree','forest']:add('core_'+family,1,family,core)
    for family in ['plain','tree','forest']:add('expanded_raw_'+family,2,family,expanded)
    add('expanded_inputlog_plain',2,'plain',expanded,input_log=True)
    if task=='regression':
        add('expanded_inputlog_forest',2,'forest',expanded,input_log=True)
        for family in ['plain','regularized','tree','forest']:add('expanded_log_'+family,2,family,expanded,input_log=True,target_log=True)
        add('expanded_log_forest_leaf50',2,'forest',expanded,input_log=True,target_log=True,leaf=50)
        add('expanded_log_forest_clip60',2,'forest',expanded,input_log=True,target_log=True,clip=60)
    else:
        for family in ['regularized','tree','forest']:add('expanded_inputlog_'+family,2,family,expanded,input_log=True)
    catalog[task]=rows
protocol=dict(version='experiment-4-v1',terminal_cutoff=old['terminal_cutoff'],inner_calendar_boundaries=old['inner_calendar_boundaries'],candidates=catalog,seed=42,selection={'regression':'minimum arithmetic mean fold MAE','classification':'maximum arithmetic mean fold average_precision','tie_tolerance':1e-10,'tie_break':'earliest candidate in catalog','terminal_used_for_selection':False},policy={'cost_fp':1,'cost_fn':5,'selection':'minimum integer loss on selected chronological OOF, highest threshold on ties'},evaluation_status='Development is reused/adaptive; terminal cohort previously inspected. No independent generalization guarantee.',fits=sum(len(v)*5 for v in catalog.values()))
p=ROOT/'experiments/experiment_4/protocol.json';assert not p.exists();p.write_text(json.dumps(protocol,indent=2));print('Frozen fold-fit count',protocol['fits'])
