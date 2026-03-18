"""
Lack of Fit (LOF) testi.
Model hatasini Pure Error ve LOF Error olarak ayirir.
Replika gozlemler (ayni faktor kombinasyonunda birden fazla olcum) gerekir.
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, List
from scipy.stats import f as f_dist

try:
    from statsmodels.regression.linear_model import OLSResults
    HAS_STATS = True
except ImportError:
    HAS_STATS = False


def compute_lack_of_fit(
    model: "OLSResults",
    df: pd.DataFrame,
    factors: List[str],
    response: str | None = None,
) -> Dict[str, Any]:
    """
    Lack of Fit testi hesaplar.
    
    SS_Residual = SS_PureError + SS_LOF
    F_LOF = (MS_LOF) / (MS_PureError)
    
    Args:
        model: OLS fitted model (statsmodels)
        df: Model fit edilirken kullanilan DataFrame (model ile ayni satirlar)
        factors: Gruplama icin faktor kolonlari (design points = unique factor combinations)
        response: Response kolonu (yoksa model.formula veya model.model.endog_names'dan alinir)
        
    Returns:
        {"has_replicates": True, "ss_pure_error", "ss_lof", "df_pure_error", "df_lof",
         "ms_pure_error", "ms_lof", "f_lof", "p_value", "warning": None}
        veya replika yoksa: {"has_replicates": False, "warning": "..."}
    """
    if not HAS_STATS or model is None:
        return {"has_replicates": False, "warning": "Model veya statsmodels yok."}
    
    # df ile model satirlarini hizalayalim
    # Model genelde df.dropna() ile fit edilir; model.model.data.frame kullanilabilir
    try:
        model_df = model.model.data.frame
    except Exception:
        model_df = df.dropna()
    
    # Response kolonu
    if response is None:
        try:
            response = model.model.endog_names
        except Exception:
            response = df.select_dtypes(include=["number"]).columns[0] if not df.empty else None
    
    if not factors or response is None:
        return {"has_replicates": False, "warning": "Faktor veya response belirtilmedi."}
    
    missing = [c for c in factors + [response] if c not in model_df.columns]
    if missing:
        return {"has_replicates": False, "warning": f"Eksik kolonlar: {missing}"}
    
    work = model_df[factors + [response]].copy()
    work["_fitted"] = model.fittedvalues.values
    
    # Design points: unique factor combinations
    grouped = work.groupby(factors, dropna=False)
    n_design_points = len(grouped)
    n_total = len(work)
    
    # Replika var mi? En az bir grupta 2+ gozlem olmali
    group_sizes = grouped.size()
    has_replicates = (group_sizes > 1).any()
    
    if not has_replicates:
        return {
            "has_replicates": False,
            "warning": "Lack of Fit hesaplanamaz: replika gozlem yok (ayni faktor kombinasyonunda birden fazla olcum gerekli).",
        }
    
    # SS_PureError = sum over groups of sum over j of (y_ij - y_bar_i)^2
    ss_pure = 0.0
    for name, grp in grouped:
        y_vals = grp[response].values
        y_mean = np.mean(y_vals)
        ss_pure += np.sum((y_vals - y_mean) ** 2)
    
    # df_PureError = N - n (n = unique design points)
    df_pure = n_total - n_design_points
    if df_pure <= 0:
        return {"has_replicates": False, "warning": "Pure Error serbestlik derecesi <= 0."}
    
    # SS_Residual (model'den)
    ss_residual = float(model.ssr)
    
    # SS_LOF = SS_Residual - SS_PureError
    ss_lof = ss_residual - ss_pure
    if ss_lof < 0:
        ss_lof = 0.0  # numerik hata
    
    # df_Residual = n - p (model'den)
    df_resid = int(model.df_resid)
    df_lof = df_resid - df_pure
    if df_lof <= 0:
        return {
            "has_replicates": True,
            "ss_pure_error": ss_pure,
            "ss_lof": ss_lof,
            "df_pure_error": df_pure,
            "df_lof": df_lof,
            "warning": "LOF serbestlik derecesi <= 0. F testi hesaplanamadi.",
        }
    
    ms_pure = ss_pure / df_pure
    ms_lof = ss_lof / df_lof
    f_lof = ms_lof / ms_pure if ms_pure > 0 else np.nan
    p_value = float(1 - f_dist.cdf(f_lof, df_lof, df_pure)) if not np.isnan(f_lof) else np.nan
    
    return {
        "has_replicates": True,
        "ss_pure_error": ss_pure,
        "ss_lof": ss_lof,
        "df_pure_error": df_pure,
        "df_lof": df_lof,
        "ms_pure_error": ms_pure,
        "ms_lof": ms_lof,
        "f_lof": f_lof,
        "p_value": p_value,
        "warning": None,
    }
