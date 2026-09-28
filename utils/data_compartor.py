from typing import Dict, List, Tuple
import pandas as pd



class DataComparator:

    @staticmethod
    def compare_dataframes(df_expected: pd.DataFrame,df_actual: pd.DataFrame,Key_column:str) -> Tuple[bool,List[str]]:

        discrepancies = []

        if len(df_expected) != len(df_actual):
            discrepancies.append(f"Row count Mismatch: Expected {len(df_expected)}, Actual {len(df_actual)}")


        exp_indexed = df_expected.set_index(Key_column)

        act_indexed = df_expected.set_index(Key_column)


        missing_in_act = set(exp_indexed.index) - set(act_indexed.index)

        if missing_in_act:
            discrepancies.append(f"Keys of missing in target:{list(missing_in_act)[:5]} ")


        unexpected_in_act = set(act_indexed.index) - set(exp_indexed.index)

        if unexpected_in_act:
            discrepancies.append(f"Unexpected Keys in target:{list(unexpected_in_act)[:5]} ")


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
                            discrepancies.append(f"Key [{key}] col [{col}] expected '{val_e}' but we got '{val_a}'")
                            if len(discrepancies) >= 10:
                                return False, discrepancies

        return len(discrepancies) == 0, discrepancies