"""
Evrensel Kodlama Formulu (Duzensiz Araliklar Icin).
15.Madde: X_kodlu = (X_gercek - X_orta) / ((X_max - X_min) / 2)
X_orta = (X_max + X_min) / 2
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple, Union


def code_value(x_real: float, x_min: float, x_max: float) -> float:
    """
    Gercek degeri [-1, +1] kodlanmis degerine cevirir.
    
    Args:
        x_real: Gercek (olceklenmis) deger
        x_min: Faktor minimum degeri
        x_max: Faktor maximum degeri
        
    Returns:
        Kodlanmis deger (-1 ile +1 arasi)
    """
    x_mid = (x_max + x_min) / 2
    half_range = (x_max - x_min) / 2
    if half_range == 0:
        return 0.0
    return float((x_real - x_mid) / half_range)


def decode_value(x_coded: float, x_min: float, x_max: float) -> float:
    """
    Kodlanmis degeri gercek degerine cevirir.
    
    Args:
        x_coded: Kodlanmis deger (-1 ile +1 arasi)
        x_min: Faktor minimum degeri
        x_max: Faktor maximum degeri
        
    Returns:
        Gercek deger
    """
    x_mid = (x_max + x_min) / 2
    half_range = (x_max - x_min) / 2
    return float(x_coded * half_range + x_mid)


def code_dataframe(
    df: pd.DataFrame,
    factor_ranges: Dict[str, Tuple[float, float]],
) -> pd.DataFrame:
    """
    DataFrame'deki faktor kolonlarini kodlanmis degerlere cevirir.
    
    Args:
        df: Kaynak DataFrame
        factor_ranges: {faktor_adi: (min, max)} sozlugu
        
    Returns:
        Kodlanmis degerlerle yeni DataFrame (diger kolonlar aynen kopyalanir)
    """
    result = df.copy()
    for factor, (x_min, x_max) in factor_ranges.items():
        if factor in result.columns:
            result[factor] = result[factor].apply(
                lambda x, mn=x_min, mx=x_max: code_value(float(x), mn, mx) if pd.notna(x) else np.nan
            )
    return result


def decode_dataframe(
    df: pd.DataFrame,
    factor_ranges: Dict[str, Tuple[float, float]],
) -> pd.DataFrame:
    """
    DataFrame'deki kodlanmis faktor kolonlarini gercek degerlere cevirir.
    
    Args:
        df: Kodlanmis degerler iceren DataFrame
        factor_ranges: {faktor_adi: (min, max)} sozlugu
        
    Returns:
        Gercek degerlerle yeni DataFrame
    """
    result = df.copy()
    for factor, (x_min, x_max) in factor_ranges.items():
        if factor in result.columns:
            result[factor] = result[factor].apply(
                lambda x, mn=x_min, mx=x_max: decode_value(float(x), mn, mx) if pd.notna(x) else np.nan
            )
    return result


def get_factor_ranges_from_df(
    df: pd.DataFrame,
    factors: list,
) -> Dict[str, Tuple[float, float]]:
    """
    DataFrame'den her faktor icin min/max degerlerini alir.
    
    Args:
        df: Kaynak DataFrame
        factors: Faktor kolon adlari
        
    Returns:
        {faktor_adi: (min, max)} sozlugu
    """
    result = {}
    for f in factors:
        if f in df.columns:
            vals = pd.to_numeric(df[f], errors="coerce").dropna()
            if len(vals) > 0:
                result[f] = (float(vals.min()), float(vals.max()))
    return result
