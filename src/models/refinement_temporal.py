"""Independent chronological manifests and mature-label training; no terminal target API."""
from __future__ import annotations
import pandas as pd
import numpy as np
from .data import load_development, TARGETS

def chronological_data(root,protocol):
    dev,_,hashes=load_development(root)
    dev['prediction_timestamp']=pd.to_datetime(dev.prediction_timestamp)
    cutoff=pd.Timestamp(protocol['terminal_cutoff'])
    identity=dev.loc[dev.prediction_timestamp.ge(cutoff),['order_id','customer_unique_id','prediction_timestamp']].copy()
    terminal_groups=set(identity.customer_unique_id)
    pre=dev.loc[dev.prediction_timestamp.lt(cutoff)].copy()
    reserved=pre.customer_unique_id.isin(terminal_groups)
    purged=pre.loc[reserved,['order_id','customer_unique_id']].copy()
    pre=pre.loc[~reserved].copy();del dev
    reviews=pd.read_csv(root/'data/preprocessed/olist_order_reviews_dataset.csv',usecols=['order_id','review_score','review_answer_timestamp'],dtype={'order_id':'string'})
    reviews=reviews.loc[reviews.order_id.isin(pre.order_id)].copy()
    score=pd.to_numeric(reviews.review_score,errors='coerce')
    valid=score.notna()&np.isfinite(score)&score.mod(1).eq(0)&score.between(1,5)
    reviews=reviews.loc[valid].copy();reviews['_score']=score.loc[valid]
    reviews['_date']=pd.to_datetime(reviews.review_answer_timestamp,errors='coerce');reviews['_missing']=reviews._date.isna()
    agg=reviews.groupby('order_id').agg(min_answer=('_date','min'),max_answer=('_date','max'),missing_answers=('_missing','sum'),min_score=('_score','min'))
    pre=pre.merge(agg,on='order_id',how='left',validate='one_to_one')
    mask=pre.eligible_classification.eq(1)
    if not pre.loc[mask,'review_score_min'].eq(pre.loc[mask,'min_score']).all():raise ValueError('Review targets differ from source')
    pre['regression_label_available_at']=pd.to_datetime(pre.regression_label_available_at,errors='coerce')
    valid_time={
        'regression':pre.regression_label_available_at.notna()&pre.regression_label_available_at.gt(pre.prediction_timestamp),
        'classification':pre.min_answer.notna()&pre.max_answer.notna()&pre.missing_answers.eq(0)&pre.min_answer.ge(pre.prediction_timestamp)}
    available={'regression':pre.regression_label_available_at,'classification':pre.max_answer}
    folds={};members=[];excluded=[];final={};boundaries=list(map(pd.Timestamp,protocol['inner_calendar_boundaries']))
    for task in TARGETS:
        eligibility=pre['eligible_'+task].eq(1)
        if task == 'classification':
            eligibility = eligibility & pre.has_items.eq(1)
        final_mask=eligibility&valid_time[task]&available[task].lt(cutoff)
        final[task]=pre.loc[final_mask].copy()
        for _,r in pre.loc[pre['eligible_'+task].eq(1)&~final_mask,['order_id']].iterrows():
            i=r.name
            excluded.append({'order_id':r.order_id,'task':task,'fold':-1,'role':'terminal_training','reasons':'zero_items_cart_ineligible' if pre.loc[i,'has_items']==0 else ('label_timestamp_missing_or_inconsistent' if not valid_time[task].loc[i] else 'label_not_observable_by_cutoff')})
        for fold,(lo,hi) in enumerate(zip(boundaries[:-1],boundaries[1:])):
            window=pre.prediction_timestamp.ge(lo)&pre.prediction_timestamp.lt(hi)
            groups=set(pre.loc[window,'customer_unique_id'])
            tr_window=eligibility&pre.prediction_timestamp.lt(lo);va_window=eligibility&window
            same=pre.customer_unique_id.isin(groups)
            tr_mask=tr_window&~same&valid_time[task]&available[task].lt(lo)
            va_mask=va_window&valid_time[task]&available[task].lt(cutoff)
            tr,va=pre.loc[tr_mask].copy(),pre.loc[va_mask].copy()
            if tr.empty or va.empty or set(tr.customer_unique_id)&set(va.customer_unique_id):raise ValueError('Invalid chronological cohort')
            if task=='classification' and (set(tr.is_detractor)!={0,1} or set(va.is_detractor)!={0,1}):raise ValueError('Missing classification class')
            assert available[task].loc[tr_mask].lt(lo).all()
            folds[task,fold]=(tr,va)
            for role,frame in [('training',tr),('validation',va)]:
                members.extend({'order_id':oid,'task':task,'fold':fold,'role':role} for oid in frame.order_id)
            for role,base,when in [('training',tr_window,lo),('validation',va_window,cutoff)]:
                for i in pre.index[base]:
                    reasons=[]
                    if role=='training' and same.loc[i]:reasons.append('validation_customer_purge')
                    if not valid_time[task].loc[i]:reasons.append('label_timestamp_missing_or_inconsistent')
                    elif not available[task].loc[i]<when:reasons.append('label_not_observable_by_cutoff')
                    if reasons:excluded.append({'order_id':pre.loc[i,'order_id'],'task':task,'fold':fold,'role':role,'reasons':';'.join(reasons)})
    for task,rows in final.items():
        if rows.empty or set(rows.customer_unique_id)&terminal_groups:raise ValueError('Invalid terminal-fit training pool')
    return {'folds':folds,'final_training':final,'terminal_identities':identity,'terminal_group_purge':purged,
            'membership':pd.DataFrame(members),'exclusions':pd.DataFrame(excluded),'input_hashes':hashes}
