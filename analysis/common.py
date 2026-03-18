"""
Ortak istatistik yardımcıları: MS, SE, anlamlılık, uyarılar.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple, Union

try:
    from statsmodels.regression.linear_model import OLSResults
    HAS_STATS = True
except ImportError:
    HAS_STATS = False

try:
    from scipy.stats import jarque_bera
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False


def compute_ms_values(anova_df: pd.DataFrame) -> Dict[str, float]:
    """
    ANOVA tablosundan MS (Mean Square) değerlerini çıkarır.
    
    Args:
        anova_df: statsmodels anova_lm çıktısı (sum_sq, df, F, PR(>F) kolonları)
        
    Returns:
        {"MS_model", "MS_error", "MS_effect": ...} veya mevcut MS kolonu varsa onu kullanır
    """
    result = {}
    if anova_df is None or anova_df.empty:
        return result
    
    # statsmodels anova_lm genelde sum_sq ve df verir, MS = sum_sq / df
    if "sum_sq" in anova_df.columns and "df" in anova_df.columns:
        for idx in anova_df.index:
            ss = anova_df.loc[idx, "sum_sq"]
            df_val = anova_df.loc[idx, "df"]
            if df_val is not None and df_val > 0:
                result[f"MS_{idx}"] = float(ss / df_val)
    
    if "Residual" in anova_df.index:
        result["MS_error"] = result.get("MS_Residual", np.nan)
    if "Model" in anova_df.index or "Regression" in anova_df.index:
        key = "Model" if "Model" in anova_df.index else "Regression"
        result["MS_model"] = result.get(f"MS_{key}", np.nan)
    
    return result


def compute_standard_error(model: Any) -> Optional[pd.Series]:
    """
    Model katsayılarının standart hatalarını döndürür.
    
    Args:
        model: OLSResults veya bse attribute'u olan model
        
    Returns:
        Standart hatalar Series veya None
    """
    if not HAS_STATS:
        return None
    if hasattr(model, "bse"):
        return model.bse
    return None


def format_significance(p_value: float) -> str:
    """
    p-değerini anlamlılık seviyesi metni olarak formatlar.
    
    Args:
        p_value: p-değeri
        
    Returns:
        "p<0.001 ***", "p<0.01 **", "p<0.05 *", "p>=0.05" gibi
    """
    if pd.isna(p_value):
        return ""
    p = float(p_value)
    if p < 0.001:
        return "p<0.001 ***"
    if p < 0.01:
        return "p<0.01 **"
    if p < 0.05:
        return "p<0.05 *"
    return "p>=0.05"


def generate_warnings(
    model: Any = None,
    anova_df: pd.DataFrame = None,
    vif_df: pd.DataFrame = None,
    n_obs: int = None,
) -> List[Tuple[str, str]]:
    """
    Model, ANOVA ve VIF bilgilerine göre uyarı metinleri oluşturur.
    
    Args:
        model: OLS model (df_resid, nobs vb.)
        anova_df: ANOVA tablosu
        vif_df: VIF tablosu
        n_obs: Gözlem sayısı (model yoksa)
        
    Returns:
        Uyarı listesi: [(severity, message), ...] severity: "KRITIK" veya "UYARI"
    """
    warnings: List[Tuple[str, str]] = []
    
    n = n_obs
    df_resid = None
    if model is not None and hasattr(model, "nobs"):
        n = int(model.nobs)
    if model is not None and hasattr(model, "df_resid"):
        df_resid = int(model.df_resid)
    
    if n is not None and n < 30:
        warnings.append(("UYARI", f"Düşük gözlem sayısı (n={n}). Sonuçlar güvenilir olmayabilir."))
    
    if df_resid is not None and df_resid < 5:
        warnings.append(("UYARI", f"Düşük serbestlik derecesi (df_resid={df_resid}). Model aşırı uyum gösterebilir."))
    
    if vif_df is not None and not vif_df.empty and "VIF" in vif_df.columns:
        high_vif = vif_df[vif_df["VIF"] > 10]
        inf_vif = vif_df[(vif_df["VIF"] == np.inf) | (vif_df["VIF"] > 1e10)]
        if len(high_vif) > 0:
            warnings.append(("UYARI", f"Yüksek VIF (>10) olan {len(high_vif)} değişken var. Çoklu doğrusal bağımlılık kontrol edin."))
        if len(inf_vif) > 0:
            warnings.append(("KRITIK", f"VIF=∞ olan {len(inf_vif)} değişken var (tam çoklu doğrusal bağımlılık)."))
    
    if anova_df is not None and not anova_df.empty and "df" in anova_df.columns:
        zero_df = anova_df[anova_df["df"] == 0]
        if len(zero_df) > 0:
            warnings.append(("KRITIK", "Serbestlik derecesi 0 olan kaynaklar var. Model spesifikasyonunu kontrol edin."))
    
    # Non-normal residuals (Jarque-Bera)
    if HAS_SCIPY and model is not None and hasattr(model, "resid"):
        try:
            jb_stat, jb_p = jarque_bera(model.resid)
            if jb_p < 0.05:
                warnings.append(("KRITIK", f"Hatalar normal dağılmıyor (Jarque-Bera p={jb_p:.4f}). Model sonuçları güvenilir olmayabilir."))
        except Exception:
            pass
    
    # Condition number (multicollinearity)
    if model is not None and hasattr(model, "condition_number"):
        try:
            cond = model.condition_number
            if cond > 1000:
                warnings.append(("KRITIK", f"Çoklu doğrusal bağlantılılık (Cond.No={cond:.0f}). Katsayılar güvenilmez olabilir."))
        except Exception:
            pass
    
    # R-sq
    if model is not None and hasattr(model, "rsquared_adj"):
        try:
            if model.rsquared_adj < 0:
                warnings.append(("KRITIK", "Adj. R-sq negatif. Model hiçbir şey açıklamıyor."))
            elif hasattr(model, "rsquared") and model.rsquared < 0.4:
                warnings.append(("UYARI", f"Düşük R-sq ({model.rsquared:.3f}). Model açıklama gücü zayıf."))
        except Exception:
            pass
    
    return warnings


def warnings_to_text(warnings_list: List[Tuple[str, str]]) -> str:
    """Uyari listesini metin olarak dondurur (geriye uyumluluk)."""
    return "\n".join(msg for _, msg in warnings_list) if warnings_list else ""
