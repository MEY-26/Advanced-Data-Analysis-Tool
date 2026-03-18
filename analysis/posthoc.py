"""
Post-hoc testler: Tukey HSD, Levene.
"""

import pandas as pd
import numpy as np
from typing import Optional, Dict, Any

try:
    from scipy.stats import levene as scipy_levene
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False

try:
    from statsmodels.stats.multicomp import pairwise_tukeyhsd
    HAS_STATS = True
except ImportError:
    HAS_STATS = False


def tukey_hsd(
    df: pd.DataFrame,
    response: str,
    factor: str,
    alpha: float = 0.05,
) -> Dict[str, Any]:
    """
    Tukey HSD post-hoc testi.
    
    Args:
        df: DataFrame
        response: Bağımlı değişken kolonu
        factor: Grup değişkeni kolonu
        alpha: Anlamlılık düzeyi
        
    Returns:
        {"result": TukeyHSDResult, "summary": str, "reject": bool array, "groups": list}
    """
    if not HAS_STATS:
        return {"error": "statsmodels gerekli", "summary": ""}
    if response not in df.columns or factor not in df.columns:
        return {"error": "Kolon bulunamadı", "summary": ""}
    
    data = df[[response, factor]].dropna()
    if len(data) < 3:
        return {"error": "Yetersiz veri", "summary": ""}
    
    try:
        res = pairwise_tukeyhsd(
            data[response],
            data[factor],
            alpha=alpha,
        )
        return {
            "result": res,
            "summary": str(res.summary()) if hasattr(res, "summary") else str(res),
            "reject": getattr(res, "reject", None),
            "groups": data[factor].unique().tolist(),
        }
    except Exception as e:
        return {"error": str(e), "summary": str(e)}


def levene_test(
    df: pd.DataFrame,
    response: str,
    factor: str,
    alpha: float = 0.05,
) -> Dict[str, Any]:
    """
    Levene varyans homojenliği testi.
    
    Args:
        df: DataFrame
        response: Bağımlı değişken
        factor: Grup değişkeni
        alpha: Anlamlılık düzeyi (equal_var kararı için)
        
    Returns:
        {"statistic": float, "pvalue": float, "equal_var": bool, "bf_statistic": float, "bf_pvalue": float}
    """
    if not HAS_SCIPY:
        return {"error": "scipy gerekli", "statistic": None, "pvalue": None}
    if response not in df.columns or factor not in df.columns:
        return {"error": "Kolon bulunamadı", "statistic": None, "pvalue": None}
    
    data = df[[response, factor]].dropna()
    groups = [data[data[factor] == g][response].values for g in data[factor].unique()]
    if len(groups) < 2 or any(len(g) < 2 for g in groups):
        return {"error": "Yetersiz grup verisi", "statistic": None, "pvalue": None}
    
    try:
        stat_mean, pval_mean = scipy_levene(*groups, center="mean")
        stat_med, pval_med = scipy_levene(*groups, center="median")
        return {
            "statistic": float(stat_mean),
            "pvalue": float(pval_mean),
            "equal_var": pval_mean > alpha,
            "bf_statistic": float(stat_med),
            "bf_pvalue": float(pval_med),
        }
    except Exception as e:
        return {"error": str(e), "statistic": None, "pvalue": None}
