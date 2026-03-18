"""
One-Way ANOVA analizi.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List

try:
    from scipy.stats import f_oneway
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False

try:
    from statsmodels.formula.api import ols
    from statsmodels.stats.anova import anova_lm
    HAS_STATS = True
except ImportError:
    HAS_STATS = False


def run_one_way_anova(
    df: pd.DataFrame,
    response: str,
    factor: str,
) -> Dict[str, Any]:
    """
    One-Way ANOVA çalıştırır.
    
    Args:
        df: DataFrame
        response: Bağımlı değişken
        factor: Grup değişkeni (kategorik)
        
    Returns:
        {"anova_df": DataFrame, "group_means": DataFrame, "f_stat": float, "p_value": float}
    """
    if response not in df.columns or factor not in df.columns:
        raise ValueError(f"{response} veya {factor} kolonu bulunamadı.")
    
    data = df[[response, factor]].dropna()
    if len(data) < 3:
        raise ValueError("Yetersiz veri.")
    
    if HAS_STATS:
        model = ols(f"{response} ~ C({factor})", data=data).fit()
        anova_df = anova_lm(model, typ=2)
        group_means = data.groupby(factor)[response].agg(["mean", "std", "count"]).reset_index()
        non_resid = [i for i in anova_df.index if i != "Residual"]
        f_row = anova_df.loc[non_resid[0]] if non_resid else anova_df.iloc[0]
        f_stat = float(f_row["F"]) if "F" in f_row and pd.notna(f_row.get("F")) else np.nan
        p_val = float(f_row["PR(>F)"]) if "PR(>F)" in f_row and pd.notna(f_row.get("PR(>F)")) else np.nan
        ss_total = anova_df["sum_sq"].sum()
        ss_between = anova_df.loc[non_resid[0], "sum_sq"] if non_resid else 0.0
        eta_sq = float(ss_between / ss_total) if ss_total > 0 else np.nan
        return {
            "anova_df": anova_df,
            "group_means": group_means,
            "model": model,
            "f_stat": f_stat,
            "p_value": p_val,
            "eta_squared": eta_sq,
            "r_squared": eta_sq,
        }
    
    if HAS_SCIPY:
        groups = [data[data[factor] == g][response].values for g in data[factor].unique()]
        if any(len(g) < 2 for g in groups):
            raise ValueError("Her grupta en az 2 gozlem olmali.")
        f_stat, p_val = f_oneway(*groups)
        group_means = data.groupby(factor)[response].agg(["mean", "std", "count"]).reset_index()
        grand_mean = data[response].mean()
        ss_total = ((data[response] - grand_mean) ** 2).sum()
        ss_between = sum(len(g) * (np.mean(g) - grand_mean) ** 2 for g in groups)
        eta_sq = float(ss_between / ss_total) if ss_total > 0 else np.nan
        return {
            "anova_df": None,
            "group_means": group_means,
            "f_stat": float(f_stat),
            "p_value": float(p_val),
            "eta_squared": eta_sq,
            "r_squared": eta_sq,
        }
    
    raise ImportError("scipy veya statsmodels gerekli.")
