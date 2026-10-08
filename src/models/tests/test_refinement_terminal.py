"""Synthetic checks of evaluation eligibility and paired resampling; no Olist fit."""
import unittest
import numpy as np
import pandas as pd
from src.models.refinement_terminal import terminal_cohorts, paired_intervals


class TerminalTests(unittest.TestCase):
    def frames(self):
        rows=pd.DataFrame({
            'order_id':['pre','good','missing','early','ineligible'],
            'prediction_timestamp':['2018-05-24','2018-05-26','2018-05-26','2018-05-26','2018-05-26'],
            'eligible_regression':[1,1,1,1,0], 'eligible_classification':[1,1,1,1,0],
            'regression_label_available_at':['2018-05-27','2018-05-28','2018-05-28','2018-05-25',None],
            'lead_days':[3,2,2,-1,np.nan], 'review_score_min':[4,2,1,2,np.nan],
            'is_detractor':[0,1,1,1,np.nan]})
        reviews=pd.DataFrame({'order_id':['good','missing','missing','early'],
                              'review_score':[2,1,5,2],
                              'review_answer_timestamp':['2018-05-29',None,'2018-05-30','2018-05-25']})
        return rows,reviews

    def test_chronology_and_all_review_timestamps(self):
        rows,reviews=self.frames()
        terminal,frames,eligibility=terminal_cohorts(rows,reviews,'2018-05-25')
        self.assertEqual(set(terminal.order_id),{'good','missing','early','ineligible'})
        self.assertEqual(set(frames['regression'].order_id),{'good','missing'})
        self.assertEqual(set(frames['classification'].order_id),{'good'})
        self.assertEqual(len(eligibility),8)

    def test_mismatched_target_rejected(self):
        rows,reviews=self.frames();rows.loc[rows.order_id=='good','is_detractor']=0
        with self.assertRaises(ValueError):terminal_cohorts(rows,reviews,'2018-05-25')

    def test_identical_models_zero_paired_difference(self):
        for task,y,score in [('regression',[1,2,3,4],[1.5,1.5,3.5,3.5]),
                             ('classification',[0,1,0,1],[.1,.8,.3,.9])]:
            result=paired_intervals(task,y,score,score,['a','a','b','b'],replicates=20)
            self.assertEqual(result['lower_95'],0)
            self.assertEqual(result['upper_95'],0)

    def test_bootstrap_seed_and_direction(self):
        args=('regression',[1,2,3,4],[1,2,3,4],[2,3,4,5],['a','a','b','b'])
        a=paired_intervals(*args,replicates=20);b=paired_intervals(*args,replicates=20)
        self.assertEqual(a,b)
        self.assertEqual(a['difference_selected_minus_reference'],-1)


if __name__=='__main__':unittest.main()
