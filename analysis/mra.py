"""
Multiple Regression Analysis (MRA).
statsmodels OLS ile dogrusal regresyon.
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional
import warnings

try:
    from statsmodels.formula.api import ols
    from statsmodels.regression.linear_model import OLSResults
    from statsmodels.stats.anova import anova_lm
    from statsmodels.stats.outliers_influence import variance_inflation_factor
    HAS_STATS = True
except ImportError:
    HAS_STATS = False


def _build_mra_formula(response: str, predictors: List[str], include_interactions: bool) -> str:
    """MRA formulu olusturur (dogrusal + istege bagli etkilesimler)."""
    parts = list(predictors)
    if include_interactions and len(predictors) >= 2:
        for i, a in enumerate(predictors):
            for b in predictors[i + 1:]:
                parts.append(f"{a}:{b}")
    return f"{response} ~ " + " + ".join(parts)


def run_mra(
    df: pd.DataFrame,
    response: str,
    predictors: List[str],
    include_interactions: bool = False,
) -> Dict[str, Any]:
    """
    Coklu Regresyon Analizi calistirir.
    
    Args:
        df: DataFrame
        response: Bagimli degisken
        predictors: Bagimsiz degiskenler
        include_interactions: Ikili etkilesimler dahil mi
        
    Returns:
        {"model", "summary_text", "anova_df", "coefficients", "vif", "r_squared", "adj_r_squared"}
    """
    if not HAS_STATS:
        raise ImportError("statsmodels gerekli.")
    
    missing = [c for c in [response] + predictors if c not in df.columns]
    if missing:
        raise ValueError(f"Kolonlar bulunamadi: {missing}")
    
    if len(predictors) < 1:
        raise ValueError("En az 1 predictor gerekli.")
    
    data = df[[response] + predictors].dropna()
    if len(data) < len(predictors) + 2:
        raise ValueError("Yetersiz veri.")
    
    formula = _build_mra_formula(response, predictors, include_interactions)
    
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        try:
            model = ols(formula, data=data).fit()
        except Exception as e:
            raise ValueError(f"Model kurulamadi: {e}") from e
    
    anova_df = anova_lm(model, typ=3)
    
    coef_df = pd.DataFrame({
        "coef": model.params,
        "std err": model.bse,
        "t": model.tvalues,
        "P>|t|": model.pvalues,
        "[0.025": model.conf_int().iloc[:, 0],
        "0.975]": model.conf_int().iloc[:, 1],
    })
    
    exog = model.model.exog
    exog_names = list(model.model.exog_names)
    if "Intercept" in exog_names:
        idx = exog_names.index("Intercept")
        exog_names.pop(idx)
        exog = np.delete(exog, idx, axis=1)
    vif_data = []
    if exog.shape[1] > 0:
        for i in range(exog.shape[1]):
            try:
                vif = variance_inflation_factor(exog, i)
                vif_data.append({"factor": exog_names[i], "VIF": vif})
            except Exception:
                vif_data.append({"factor": exog_names[i], "VIF": np.nan})
    vif_df = pd.DataFrame(vif_data)
    
    return {
        "model": model,
        "formula": formula,
        "summary_text": str(model.summary()),
        "anova_df": anova_df,
        "coefficients": coef_df,
        "vif": vif_df,
        "r_squared": float(model.rsquared),
        "adj_r_squared": float(model.rsquared_adj),
    }
