"""Development-only group-sampling fixtures, independent of final evaluation."""
import unittest
import pandas as pd
from src.models.tutorial8 import group_subset


class Tutorial8Tests(unittest.TestCase):
    def test_nested_group_selection_and_reorder(self):
        rows = pd.DataFrame({"customer_unique_id": ["x", "x", "y", "z", "w"], "order_id": list("abcde")})
        small = rows.iloc[group_subset(rows, .25)]
        medium = rows.iloc[group_subset(rows, .5)]
        self.assertLessEqual(set(small.order_id), set(medium.order_id))
        reversed_rows = rows.iloc[::-1]
        self.assertEqual(set(small.order_id), set(reversed_rows.iloc[group_subset(reversed_rows, .25)].order_id))
        self.assertEqual(set(rows.iloc[group_subset(rows, 1)].order_id), set(rows.order_id))

    def test_invalid_group_sampling(self):
        with self.assertRaises(ValueError):
            group_subset(pd.DataFrame({"customer_unique_id": [None]}), .5)
        with self.assertRaises(ValueError):
            group_subset(pd.DataFrame({"customer_unique_id": ["x"]}), 0)
