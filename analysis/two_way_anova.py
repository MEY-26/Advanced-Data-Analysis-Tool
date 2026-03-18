"""
Two-Way ANOVA analizi.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List

try:
    from statsmodels.formula.api import ols
    from statsmodels.stats.anova import anova_lm
    HAS_STATS = True
except ImportError:
    HAS_STATS = False


def run_two_way_anova(
    df: pd.DataFrame,
    response: str,
    factor1: str,
    factor2: str,
    interaction: bool = True,
    anova_type: str = "3",
) -> Dict[str, Any]:
    """
    Two-Way ANOVA çalıştırır.
    
    Args:
        df: DataFrame
        response: Bağımlı değişken
        factor1: Birinci faktör
        factor2: İkinci faktör
        interaction: Etkileşim terimi dahil mi
        anova_type: "2" veya "3"
        
    Returns:
        {"anova_df": DataFrame, "model": OLSResults}
    """
    if not HAS_STATS:
        raise ImportError("statsmodels gerekli.")
    
    if response not in df.columns or factor1 not in df.columns or factor2 not in df.columns:
        raise ValueError("Gerekli kolonlar bulunamadı.")
    
    data = df[[response, factor1, factor2]].dropna()
    if len(data) < 4:
        raise ValueError("Yetersiz veri.")
    
    if interaction:
        formula = f"{response} ~ C({factor1}) + C({factor2}) + C({factor1}):C({factor2})"
    else:
        formula = f"{response} ~ C({factor1}) + C({factor2})"
    
    model = ols(formula, data=data).fit()
    typ = 2 if anova_type.upper() == "2" else 3
    anova_df = anova_lm(model, typ=typ)
    ss_total = anova_df["sum_sq"].sum()
    r_sq = float(model.rsquared) if hasattr(model, "rsquared") else np.nan
    partial_eta = {}
    for idx in anova_df.index:
        if idx != "Residual" and "sum_sq" in anova_df.columns:
            ss_effect = anova_df.loc[idx, "sum_sq"]
            ss_error = anova_df.loc["Residual", "sum_sq"] if "Residual" in anova_df.index else ss_total
            partial_eta[idx] = float(ss_effect / (ss_effect + ss_error)) if (ss_effect + ss_error) > 0 else np.nan
    return {
        "anova_df": anova_df,
        "model": model,
        "formula": formula,
        "r_squared": r_sq,
        "partial_eta_squared": partial_eta,
    }
