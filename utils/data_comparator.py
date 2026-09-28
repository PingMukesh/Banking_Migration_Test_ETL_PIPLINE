"""
Data Comparator Utility
-----------------------
Provides deep comparison between source and target datasets,
row-by-row reconciliation, and mismatch reporting.
"""

from typing import Dict, List, Tuple
import pandas as pd


class DataComparator:
    @staticmethod
    def compare_dataframes(
        df_expected: pd.DataFrame, 
        df_actual: pd.DataFrame, 
        key_column: str
    ) -> Tuple[bool, List[str]]:
        """
        Compare two DataFrames by a key column.
        Returns (is_equal, list_of_discrepancy_messages).
        """
        discrepancies = []

        if len(df_expected) != len(df_actual):
            discrepancies.append(
                f"Row count mismatch: Expected {len(df_expected)}, Actual {len(df_actual)}"
            )

        # Index by key
        exp_indexed = df_expected.set_index(key_column)
        act_indexed = df_actual.set_index(key_column)

        # Check missing keys
        missing_in_act = set(exp_indexed.index) - set(act_indexed.index)
        if missing_in_act:
            discrepancies.append(f"Keys missing in target: {list(missing_in_act)[:5]}")

        unexpected_in_act = set(act_indexed.index) - set(exp_indexed.index)
        if unexpected_in_act:
            discrepancies.append(f"Unexpected keys in target: {list(unexpected_in_act)[:5]}")

        common_keys = set(exp_indexed.index).intersection(set(act_indexed.index))
        for key in list(common_keys)[:100]:
            row_exp = exp_indexed.loc[key]
            row_act = act_indexed.loc[key]
            for col in exp_indexed.columns:
                if col in act_indexed.columns:
                    val_e = row_exp[col]
                    val_a = row_act[col]
                    if pd.notna(val_e) or pd.notna(val_a):
                        if str(val_e).strip() != str(val_a).strip():
                            discrepancies.append(
                                f"Key [{key}] Col [{col}] expected '{val_e}' but got '{val_a}'"
                            )
                            if len(discrepancies) >= 15:
                                return False, discrepancies

        return len(discrepancies) == 0, discrepancies
