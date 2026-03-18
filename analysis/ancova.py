"""
ANCOVA (Analysis of Covariance) analizi.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional

try:
    from statsmodels.formula.api import ols
    from statsmodels.stats.anova import anova_lm
    HAS_STATS = True
except ImportError:
    HAS_STATS = False


def run_ancova(
    df: pd.DataFrame,
    response: str,
    factors: List[str],
    covariates: List[str],
    anova_type: str = "3",
) -> Dict[str, Any]:
    """
    ANCOVA çalıştırır.
    
    Args:
        df: DataFrame
        response: Bağımlı değişken
        factors: Kategorik faktörler
        covariates: Kovaryatlar (sürekli)
        anova_type: "2" veya "3"
        
    Returns:
        {"anova_df": DataFrame, "model": OLSResults}
    """
    if not HAS_STATS:
        raise ImportError("statsmodels gerekli.")
    
    all_cols = [response] + factors + covariates
    missing = [c for c in all_cols if c not in df.columns]
    if missing:
        raise ValueError(f"Kolonlar bulunamadı: {missing}")
    
    data = df[all_cols].dropna()
    if len(data) < 4:
        raise ValueError("Yetersiz veri.")
    
    formula_parts = [f"C({f})" for f in factors] + covariates
    formula = f"{response} ~ " + " + ".join(formula_parts)
    
    model = ols(formula, data=data).fit()
    typ = 2 if anova_type.upper() == "2" else 3
    anova_df = anova_lm(model, typ=typ)
    
    return {
        "anova_df": anova_df,
        "model": model,
        "formula": formula,
    }
