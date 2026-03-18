"""
Dağılım istatistikleri ve histogram verileri.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional

try:
    from scipy.stats import skew, kurtosis, shapiro
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False


def compute_distribution_stats(series: pd.Series) -> Dict[str, float]:
    """
    Dağılım istatistikleri: mean, median, std, skewness, kurtosis, Shapiro-Wilk p.
    
    Args:
        series: Sayısal seri
        
    Returns:
        İstatistik sözlüğü
    """
    clean = pd.to_numeric(series, errors="coerce").dropna()
    if len(clean) < 2:
        return {}
    
    result = {
        "mean": float(clean.mean()),
        "median": float(clean.median()),
        "std": float(clean.std()) if clean.std() > 0 else 0,
        "min": float(clean.min()),
        "max": float(clean.max()),
        "n": int(len(clean)),
    }
    if HAS_SCIPY:
        result["skewness"] = float(skew(clean, bias=False))
        result["kurtosis"] = float(kurtosis(clean, bias=False))
        if 3 <= len(clean) <= 5000:
            try:
                _, p = shapiro(clean)
                result["shapiro_p"] = float(p)
            except Exception:
                result["shapiro_p"] = np.nan
        else:
            result["shapiro_p"] = np.nan
    return result


def compute_histogram_data(
    series: pd.Series,
    bins: int = 20,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Histogram için bin kenarları ve sayıları.
    
    Args:
        series: Sayısal seri
        bins: Bin sayısı
        
    Returns:
        (bin_edges, counts)
    """
    clean = pd.to_numeric(series, errors="coerce").dropna()
    if len(clean) < 1:
        return np.array([]), np.array([])
    counts, bin_edges = np.histogram(clean, bins=bins)
    return bin_edges, counts
