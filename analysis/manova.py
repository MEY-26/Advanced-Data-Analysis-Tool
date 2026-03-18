"""
MANOVA (Multivariate Analysis of Variance) analizi.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional

try:
    from statsmodels.multivariate.manova import MANOVA
    HAS_STATS = True
except ImportError:
    HAS_STATS = False


def run_manova(
    df: pd.DataFrame,
    responses: List[str],
    factors: List[str],
) -> Dict[str, Any]:
    """
    MANOVA çalıştırır.
    
    Args:
        df: DataFrame
        responses: Bağımlı değişkenler (2+)
        factors: Bağımsız değişkenler
        
    Returns:
        {"result": MANOVA result, "summary": str}
    """
    if not HAS_STATS:
        raise ImportError("statsmodels gerekli.")
    
    missing = [c for c in responses + factors if c not in df.columns]
    if missing:
        raise ValueError(f"Kolonlar bulunamadı: {missing}")
    
    if len(responses) < 2:
        raise ValueError("MANOVA için en az 2 response gerekli.")
    
    data = df[responses + factors].dropna()
    if len(data) < len(responses) + len(factors) + 2:
        raise ValueError("Yetersiz veri.")
    
    formula = " + ".join(responses) + " ~ " + " + ".join([f"C({f})" for f in factors])
    manova = MANOVA.from_formula(formula, data=data)
    result = manova.mv_test()
    
    return {
        "result": result,
        "summary": str(result),
        "manova": manova,
    }
