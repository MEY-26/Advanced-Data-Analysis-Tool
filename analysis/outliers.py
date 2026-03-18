"""
Aykırı değer (outlier) tespiti: IQR ve Z-score yöntemleri.
"""

import numpy as np
import pandas as pd
from typing import Tuple, Dict, List, Optional


def detect_outliers_iqr(
    series: pd.Series,
    factor: float = 1.5,
) -> Tuple[pd.Series, Optional[float], Optional[float]]:
    """
    IQR yöntemi ile aykırı değerleri tespit eder.
    
    Args:
        series: Veri serisi
        factor: IQR çarpanı (1.5 = standart, 3.0 = daha az hassas)
        
    Returns:
        (outlier_mask boolean Series, lower_bound, upper_bound)
    """
    q1 = series.quantile(0.25)
    q3 = series.quantile(0.75)
    iqr = q3 - q1
    if iqr == 0:
        return pd.Series(False, index=series.index), float(q1), float(q3)
    lower = q1 - factor * iqr
    upper = q3 + factor * iqr
    mask = (series < lower) | (series > upper)
    return mask, float(lower), float(upper)


def detect_outliers_zscore(
    series: pd.Series,
    threshold: float = 3.0,
) -> Tuple[pd.Series, Optional[float], Optional[float]]:
    """
    Z-score yöntemi ile aykırı değerleri tespit eder.
    
    Args:
        series: Veri serisi (sayısal)
        threshold: Z-score eşiği (|z| > threshold = outlier)
        
    Returns:
        (outlier_mask, mean, std)
    """
    clean = series.dropna()
    if len(clean) < 2:
        return pd.Series(False, index=series.index), None, None
    mean = clean.mean()
    std = clean.std()
    if std == 0:
        return pd.Series(False, index=series.index), float(mean), 0.0
    z = np.abs((series - mean) / std)
    mask = z > threshold
    return mask, float(mean), float(std)


def get_outlier_summary(
    df: pd.DataFrame,
    columns: List[str],
    method: str = "iqr",
    **kwargs,
) -> Dict[str, Dict]:
    """
    Birden fazla kolon için outlier özeti.
    
    Args:
        df: DataFrame
        columns: İncelenecek kolonlar
        method: "iqr" veya "zscore"
        **kwargs: detect_outliers_* fonksiyonlarına geçilecek argümanlar
        
    Returns:
        {column: {"n_outliers": int, "pct": float, "bounds": (lower, upper), "mask": Series}}
    """
    result = {}
    for col in columns:
        if col not in df.columns:
            continue
        series = pd.to_numeric(df[col], errors="coerce").dropna()
        if len(series) < 2:
            result[col] = {"n_outliers": 0, "pct": 0.0, "bounds": (None, None), "mask": pd.Series()}
            continue
        if method == "zscore":
            mask, mean, std = detect_outliers_zscore(series, **kwargs)
            bounds = (mean - kwargs.get("threshold", 3) * std if std else None,
                      mean + kwargs.get("threshold", 3) * std if std else None)
        else:
            mask, lower, upper = detect_outliers_iqr(series, **kwargs)
            bounds = (lower, upper)
        n = int(mask.sum())
        pct = 100.0 * n / len(series) if len(series) > 0 else 0
        result[col] = {"n_outliers": n, "pct": pct, "bounds": bounds, "mask": mask}
    return result
