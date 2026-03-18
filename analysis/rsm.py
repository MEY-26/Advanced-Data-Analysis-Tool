"""
RSM (Response Surface Methodology) ve ANOVA analiz motoru.
statsmodels ile OLS model, ANOVA, VIF ve korelasyon hesaplari.
"""

import numpy as np
import pandas as pd
from typing import List, Optional, Dict, Any
from statsmodels.formula.api import ols
from statsmodels.regression.linear_model import OLSResults
from statsmodels.stats.anova import anova_lm
from statsmodels.stats.outliers_influence import variance_inflation_factor
import warnings

# Varsayılan numerik faktörler (geriye dönük uyumluluk)
NUMERIC_FACTORS = ["devir", "feed", "paso"]


def build_formula(
    response: str,
    factors: List[str],
    include_interactions: bool = True,
    include_quadratic: bool = True,
    categoricals: Optional[List[str]] = None,
) -> str:
    """
    statsmodels patsy formulu olusturur.
    
    Args:
        response: Bagimli degisken (ornegin "oncesi" veya "delta")
        factors: Numerik faktorler (devir, feed, paso veya dinamik)
        include_interactions: Ikili etkilesimler dahil mi
        include_quadratic: Karesel terimler dahil mi
        categoricals: Kategorik bloklar (delik, olcum, numune)
        
    Returns:
        Patsy formulu string
    """
    parts = []
    
    # Ana etkiler - tum verilen faktorler
    main_terms = [f for f in factors if f]
    parts.extend(main_terms)
    
    # Ikili etkilesimler
    if include_interactions and len(main_terms) >= 2:
        for i, a in enumerate(main_terms):
            for b in main_terms[i + 1 :]:
                parts.append(f"{a}:{b}")
    
    # Karesel terimler
    if include_quadratic:
        for f in main_terms:
            parts.append(f"I({f}**2)")
    
    # Kategorikler
    if categoricals:
        for cat in categoricals:
            if cat:
                parts.append(f"C({cat})")
    
    formula = f"{response} ~ " + " + ".join(parts)
    return formula


def fit_rsm_model(
    df: pd.DataFrame,
    formula: str,
) -> OLSResults:
    """
    RSM OLS modelini kurar ve fit eder.
    """
    df_clean = df.dropna()
    if len(df_clean) < 2:
        raise ValueError("Model icin yeterli veri yok (en az 2 satir gerekli).")
    
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        try:
            model = ols(formula, data=df_clean).fit()
        except Exception as e:
            raise ValueError(f"Model kurulamadi: {e}") from e
        
        for warning in w:
            if "singular" in str(warning.message).lower() or "multicollinearity" in str(warning.message).lower():
                warnings.warn(str(warning.message), UserWarning)
    
    return model


def _anova_minimal_fallback(model: OLSResults) -> pd.DataFrame:
    """anova_lm basarisiz oldugunda model ozetinden minimal ANOVA tablosu olusturur."""
    df_model = int(model.df_model)
    df_resid = int(model.df_resid)
    ess = float(model.ess)
    ssr = float(model.ssr)
    ms_model = ess / df_model if df_model > 0 else np.nan
    ms_resid = ssr / df_resid if df_resid > 0 else np.nan
    f_val = ms_model / ms_resid if ms_resid and ms_resid > 0 else np.nan
    from scipy import stats
    p_val = 1 - stats.f.cdf(f_val, df_model, df_resid) if not np.isnan(f_val) else np.nan
    return pd.DataFrame(
        {
            "sum_sq": [ess, ssr],
            "df": [df_model, df_resid],
            "mean_sq": [ms_model, ms_resid],
            "F": [f_val, np.nan],
            "PR(>F)": [p_val, np.nan],
        },
        index=["Model", "Residual"],
    )


def run_anova(model: OLSResults, anova_type: str = "3") -> pd.DataFrame:
    """ANOVA tablosu hesaplar. Basarisiz olursa minimal tablo (Model/Residual) dondurur."""
    typ = 2 if anova_type.upper() == "2" else 3
    for attempt_typ in [typ, 1]:
        try:
            return anova_lm(model, typ=attempt_typ)
        except Exception:
            pass
    return _anova_minimal_fallback(model)


def compute_vif_from_model(model: OLSResults) -> pd.DataFrame:
    """Fitted modelin tasarim matrisi uzerinden VIF hesaplar."""
    exog = model.model.exog
    exog_names = list(model.model.exog_names)
    if "Intercept" in exog_names:
        idx = exog_names.index("Intercept")
        exog_names.pop(idx)
        exog = np.delete(exog, idx, axis=1)
    
    if exog.shape[1] == 0:
        return pd.DataFrame(columns=["factor", "VIF"])
    
    vif_data = []
    for i in range(exog.shape[1]):
        try:
            vif = variance_inflation_factor(exog, i)
            vif_data.append({"factor": exog_names[i], "VIF": vif})
        except Exception:
            vif_data.append({"factor": exog_names[i], "VIF": np.nan})
    
    return pd.DataFrame(vif_data)


def compute_vif(df: pd.DataFrame, factors: List[str]) -> pd.DataFrame:
    """Basit VIF hesaplar (sadece numerik faktorler)."""
    available = [f for f in factors if f in df.columns]
    if len(available) < 2:
        return pd.DataFrame(columns=["factor", "VIF"])
    
    X = df[available].dropna()
    if len(X) < 2:
        return pd.DataFrame(columns=["factor", "VIF"])

    X_with_const = np.column_stack([np.ones(len(X)), X.values])
    vif_data = []
    for i, col in enumerate(available):
        try:
            vif = variance_inflation_factor(X_with_const, i + 1)
            vif_data.append({"factor": col, "VIF": vif})
        except Exception:
            vif_data.append({"factor": col, "VIF": np.nan})
    
    return pd.DataFrame(vif_data)


def correlation_matrix(df: pd.DataFrame, factors: Optional[List[str]] = None, response: Optional[str] = None) -> pd.DataFrame:
    """Faktorler arasi Pearson korelasyon matrisi. Response dahil edilebilir."""
    if factors is None:
        factors = [f for f in NUMERIC_FACTORS if f in df.columns]
    else:
        factors = [f for f in factors if f in df.columns]
    
    cols = list(factors)
    if response and response in df.columns and response not in cols:
        cols.insert(0, response)
    
    if len(cols) < 2:
        return pd.DataFrame()
    
    return df[cols].corr()


def get_model_summary(model: OLSResults) -> Dict[str, Any]:
    """Model ozet bilgilerini sozluk olarak dondurur."""
    summary = model.summary()
    return {
        "r_squared": model.rsquared,
        "adj_r_squared": model.rsquared_adj,
        "aic": model.aic,
        "bic": model.bic,
        "n_obs": int(model.nobs),
        "df_resid": int(model.df_resid),
        "summary_text": str(summary),
        "params": model.params,
        "pvalues": model.pvalues,
        "conf_int": model.conf_int(),
    }
