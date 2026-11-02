"""DS.6 pooled confusion: b08's 'all' rows are used once, whatever dtype pandas gives the fold column (B-CR-48)."""
import io
import sys
from pathlib import Path

import pandas as pd

B_ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(B_ROOT.parent), str(B_ROOT)]

from e5b.doc_support import pooled_confusion  # noqa: E402

CSV = """model,fold,tp,fp,fn,tn
A,1,1,2,3,4
A,2,10,20,30,40
A,all,11,22,33,44
B,1,5,6,7,8
B,all,5,6,7,8
"""


def test_pooled_confusion_uses_the_all_rows_once():
    cc = pd.read_csv(io.StringIO(CSV))   # pandas 3 reads the mixed fold column as str, pandas 2 as object
    p = pooled_confusion(cc).set_index("model")
    assert p.loc["A", ["tp", "fp", "fn", "tn"]].tolist() == [11, 22, 33, 44]
    assert p.loc["B", ["tp", "fp", "fn", "tn"]].tolist() == [5, 6, 7, 8]


def test_pooled_confusion_sums_folds_without_all_rows():
    cc = pd.read_csv(io.StringIO("\n".join(CSV.splitlines()[:3] + CSV.splitlines()[4:5]) + "\n"))
    p = pooled_confusion(cc).set_index("model")
    assert p.loc["A", "tp"] == 11 and p.loc["B", "tn"] == 8


def test_pooled_confusion_matches_b08_totals():
    cc = pd.read_csv(B_ROOT / "stages" / "b08" / "classification" / "outputs" / "confusion_comparison.csv")
    p = pooled_confusion(cc)
    assert len(p) == 2
    assert int(p.tn.sum() + p.fp.sum() + p.fn.sum() + p.tp.sum()) == 2 * 50215   # two models, B's validation rows
