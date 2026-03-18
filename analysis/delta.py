"""
Degisim analizi modulu.
Oncesi-Sonrasi fark metrikleri, grup ozetleri ve RSM modelleme.
"""

import pandas as pd
import numpy as np
from typing import List, Optional
from analysis.rsm import (
    build_formula,
    fit_rsm_model,
    run_anova,
    compute_vif_from_model,
    correlation_matrix,
    get_model_summary,
    NUMERIC_FACTORS,
)


def compute_delta(
    df: pd.DataFrame,
    before_col: str = "oncesi",
    after_col: str = "sonrasi",
    metric: str = "absolute",
    direction: str = "smaller_better",
    zero_handling: str = "nan",
) -> pd.DataFrame:
    """
    Degisim metriklerini hesaplar ve Delta kolonu ekler.
    
    Args:
        df: DataFrame
        before_col: Öncesi kolonu
        after_col: Sonrası kolonu
        metric: "absolute" | "percent" | "improvement"
        direction: "smaller_better" | "larger_better"
        zero_handling: Oncesi=0 icin "nan" veya "0"
        
    Returns:
        Delta kolonu eklenmis DataFrame
    """
    df = df.copy()
    
    if before_col not in df.columns or after_col not in df.columns:
        raise ValueError(f"{before_col} ve {after_col} kolonlari gerekli.")
    
    if metric == "absolute":
        df["Delta"] = df[after_col] - df[before_col]
    
    elif metric == "percent":
        mask_zero = df[before_col] == 0
        pct = pd.Series(np.nan, index=df.index)
        safe = ~mask_zero
        pct[safe] = (df.loc[safe, after_col] - df.loc[safe, before_col]) / df.loc[safe, before_col] * 100
        if zero_handling != "nan":
            pct[mask_zero] = 0.0
        df["Delta"] = pct
    
    elif metric == "improvement":
        if direction == "smaller_better":
            df["Delta"] = df[before_col] - df[after_col]
        else:
            df["Delta"] = df[after_col] - df[before_col]
    
    else:
        raise ValueError(f"Bilinmeyen metrik: {metric}")
    
    return df


def group_summary(
    df: pd.DataFrame,
    groupby_cols: Optional[List[str]] = None,
) -> pd.DataFrame:
    """
    Grup bazli Delta ozeti: ortalama, std, n, min, max.
    """
    if "Delta" not in df.columns:
        raise ValueError("Delta kolonu gerekli.")
    
    if groupby_cols is None:
        groupby_cols = ["devir", "feed", "paso", "delik", "olcum"]
    
    available = [c for c in groupby_cols if c in df.columns]
    if not available:
        return pd.DataFrame()
    
    df_valid = df.dropna(subset=["Delta"])
    if df_valid.empty:
        return pd.DataFrame()
    
    agg = df_valid.groupby(available, dropna=False).agg(
        Delta_mean=("Delta", "mean"),
        Delta_std=("Delta", "std"),
        n=("Delta", "count"),
        Delta_min=("Delta", "min"),
        Delta_max=("Delta", "max"),
    ).reset_index()
    
    agg = agg.sort_values("Delta_mean", ascending=False).reset_index(drop=True)
    return agg


def run_delta_rsm(
    df: pd.DataFrame,
    factors: Optional[List[str]] = None,
    include_interactions: bool = True,
    include_quadratic: bool = True,
    categoricals: Optional[List[str]] = None,
    anova_type: str = "2",
) -> dict:
    """
    Delta'yi response olarak RSM modeli kurar.
    """
    if "Delta" not in df.columns:
        raise ValueError("Delta kolonu gerekli.")
    
    if factors is None:
        factors = [f for f in NUMERIC_FACTORS if f in df.columns]
    else:
        factors = [f for f in factors if f in df.columns]
    
    formula = build_formula(
        response="Delta",
        factors=factors,
        include_interactions=include_interactions,
        include_quadratic=include_quadratic,
        categoricals=categoricals,
    )
    
    model = fit_rsm_model(df, formula)
    anova_df = run_anova(model, anova_type)
    vif_df = compute_vif_from_model(model)
    corr_df = correlation_matrix(df, factors)
    
    return {
        "model": model,
        "formula": formula,
        "summary": get_model_summary(model),
        "anova": anova_df,
        "vif": vif_df,
        "correlation": corr_df,
    }
