"""
Excel veri okuma, temizlik ve dogrulama modulu.
Dinamik sütun eşleme destekler - roller kullanıcı tarafından atanır.
"""

import pandas as pd
from pathlib import Path
from typing import Tuple, List, Optional, Dict, Any

# Rol anahtarları (column_dialog ile uyumlu)
ROLE_RESPONSE = "response"
ROLE_NUMERIC_FACTORS = "numeric_factors"
ROLE_CATEGORICAL_FACTORS = "categorical_factors"
ROLE_COVARIATES = "covariates"
ROLE_BLOCK = "block"

# Eski sabit format için varsayılan eşleme (geriye dönük uyumluluk)
DEFAULT_COLUMN_ROLES = {
    ROLE_RESPONSE: ["oncesi", "sonrasi"],
    ROLE_NUMERIC_FACTORS: ["devir", "feed", "paso"],
    ROLE_CATEGORICAL_FACTORS: ["delik", "olcum"],
    ROLE_COVARIATES: [],
    ROLE_BLOCK: ["numune"],
}


def get_excel_sheets(path: str) -> List[str]:
    """
    Excel dosyasindaki sayfa isimlerini dondurur.
    Dosya okunduktan sonra kapatilir (baskalari dosyayi duzenleyebilir).
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Dosya bulunamadi: {path}")
    try:
        with pd.ExcelFile(path, engine="openpyxl") as xl:
            return xl.sheet_names.copy()
    except Exception as e:
        raise ValueError(f"Excel dosyasi okunamadi: {e}") from e


def _normalize_col_name(name: str) -> str:
    """Kolon adini normalize eder (kucuk harf, bosluk ve ozel karakter temizleme)."""
    if not isinstance(name, str):
        name = str(name)
    name = name.strip().lower().replace(" ", "")
    for ch in ['/', '\\', '-', '(', ')', '[', ']', '{', '}', '?', '*', ':', '<', '>', '|', '"', "'", '#', '%', '&', '+', '=', '!', '@', '^', '~', '`']:
        name = name.replace(ch, '_')
    while '__' in name:
        name = name.replace('__', '_')
    name = name.strip('_')
    return name if name else "unnamed"


def load_excel_raw(path: str, sheet_name: Optional[str] = None) -> pd.DataFrame:
    """
    Excel dosyasindan ham veri okur. Sütun eşlemesi yapmaz.
    Dosya okunduktan sonra kapatilir (baskalari dosyayi duzenleyebilir).
    
    Args:
        path: Excel dosya yolu
        sheet_name: Sayfa adi. None ise ilk sayfa okunur.
        
    Returns:
        Ham DataFrame (orijinal sütun adlarıyla)
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Dosya bulunamadi: {path}")
    
    try:
        with pd.ExcelFile(path, engine="openpyxl") as xl:
            sheets = xl.sheet_names
            if not sheets:
                raise ValueError("Excel dosyasinda sayfa bulunamadi.")
            if sheet_name is None:
                sheet_name = sheets[0]
            elif sheet_name not in sheets:
                raise ValueError(f"Sayfa bulunamadi: {sheet_name}. Mevcut: {sheets}")
            df = pd.read_excel(xl, sheet_name=sheet_name)
    except ValueError:
        raise
    except Exception as e:
        raise ValueError(f"Excel dosyasi okunamadi: {e}") from e
    
    if df.empty:
        raise ValueError(f"Sayfa bos: {sheet_name}")
    
    return df


def load_excel(
    path: str,
    sheet_name: Optional[str] = None,
    column_roles: Optional[Dict[str, List[str]]] = None,
) -> pd.DataFrame:
    """
    Excel dosyasindan veri okur.
    
    column_roles verilirse: Ham veri okunur, sütunlar olduğu gibi kalır.
    column_roles verilmezse: Eski davranış - otomatik eşleme denenir (geriye dönük uyumluluk).
    
    Args:
        path: Excel dosya yolu
        sheet_name: Sayfa adi
        column_roles: Sütun rolleri (ColumnDialog'dan). None ise varsayılan eşleme denenir.
        
    Returns:
        DataFrame
    """
    df = load_excel_raw(path, sheet_name)
    
    if column_roles is None:
        # Eski otomatik eşleme (FormTester formatı)
        df, _ = _auto_map_columns(df)
        missing = [c for c in ["numune", "delik", "devir", "feed", "paso", "olcum", "oncesi", "sonrasi"] 
                   if c not in df.columns]
        if missing:
            raise ValueError(f"Eksik kolonlar: {missing}. Mevcut: {list(df.columns)}")
        return df
    
    # column_roles ile: Sütun adları zaten Excel'deki gibi. Roller sadece hangi sütunun ne olduğunu belirtir.
    return df


def _auto_map_columns(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, str]]:
    """Eski otomatik sütun eşlemesi (FormTester formatı için)."""
    expected = ["numune", "delik", "devir", "feed", "paso", "olcum", "oncesi", "sonrasi"]
    mapping = {}
    normalized_to_original = {_normalize_col_name(c): c for c in df.columns}
    
    for exp in expected:
        if exp in normalized_to_original:
            orig = normalized_to_original[exp]
            if orig != exp:
                mapping[orig] = exp
    
    if mapping:
        df = df.rename(columns=mapping)
    col_map = {c: _normalize_col_name(c) for c in df.columns}
    df = df.rename(columns=col_map)
    return df, mapping


def clean_data(
    df: pd.DataFrame,
    column_roles: Optional[Dict[str, List[str]]] = None,
) -> Tuple[pd.DataFrame, pd.DataFrame, Dict[str, List[str]]]:
    """
    Veriyi temizler: sayisal donusum, kategori normalize, eksik deger raporu.
    Sütun adları normalize edilir (küçük harf, boşluksuz).
    
    Args:
        df: Ham DataFrame
        column_roles: Sütun rolleri. None ise varsayılan roller kullanılır.
        
    Returns:
        (cleaned_df, issues_df, normalized_column_roles)
    """
    df = df.copy()
    issues = []
    
    if column_roles is None:
        column_roles = DEFAULT_COLUMN_ROLES
    
    # Sütun adlarını normalize et (küçük harf, boşluksuz)
    rename_map = {c: _normalize_col_name(c) for c in df.columns if _normalize_col_name(c) != c}
    if rename_map:
        df = df.rename(columns=rename_map)
    # column_roles'taki sütun adlarını da normalize et
    normalized_roles = {}
    for role, cols in column_roles.items():
        normalized_roles[role] = [_normalize_col_name(c) for c in cols]
    column_roles = normalized_roles
    
    numeric_cols = (
        column_roles.get(ROLE_RESPONSE, [])
        + column_roles.get(ROLE_NUMERIC_FACTORS, [])
        + column_roles.get(ROLE_COVARIATES, [])
        + column_roles.get(ROLE_BLOCK, [])
    )
    numeric_cols = [c for c in numeric_cols if c in df.columns]
    
    categorical_cols = column_roles.get(ROLE_CATEGORICAL_FACTORS, [])
    categorical_cols = [c for c in categorical_cols if c in df.columns]
    
    for col in numeric_cols:
        df[col] = df[col].replace({'-': pd.NA, '/': pd.NA, '': pd.NA})
        for idx, val in df[col].items():
            if pd.isna(val):
                continue
            try:
                df.at[idx, col] = float(val)
            except (ValueError, TypeError):
                issues.append({
                    "row": idx,
                    "column": col,
                    "original_value": str(val),
                    "error": "float donusumu basarisiz"
                })
                df.at[idx, col] = float("nan")
    
    for col in categorical_cols:
        mask = df[col].notna()
        df.loc[mask, col] = df.loc[mask, col].astype(str).str.strip().str.lower()
    
    issues_df = pd.DataFrame(issues) if issues else pd.DataFrame(
        columns=["row", "column", "original_value", "error"]
    )
    
    return df, issues_df, column_roles


def validate_data(
    df: pd.DataFrame,
    column_roles: Optional[Dict[str, List[str]]] = None,
) -> List[str]:
    """
    Veri dogrulama: uyarilar listesi dondurur.
    """
    warnings = []
    
    if column_roles is None:
        column_roles = DEFAULT_COLUMN_ROLES
    
    # Duplikat kontrolu: key kolonlar
    key_cols = (
        column_roles.get(ROLE_NUMERIC_FACTORS, [])
        + column_roles.get(ROLE_CATEGORICAL_FACTORS, [])
        + column_roles.get(ROLE_BLOCK, [])
    )
    key_cols = [c for c in key_cols if c in df.columns]
    if len(key_cols) >= 2:
        dup = df.duplicated(subset=key_cols, keep=False)
        if dup.any():
            n_dup = dup.sum()
            warnings.append(
                f"Ayni ({', '.join(key_cols[:5])}{'...' if len(key_cols) > 5 else ''}) "
                f"kombinasyonundan {n_dup} satir var."
            )
    
    # Response=0 kontrolu (yuzdesel degisim icin)
    responses = column_roles.get(ROLE_RESPONSE, [])
    for resp in responses:
        if resp in df.columns:
            zero_count = (pd.to_numeric(df[resp], errors="coerce") == 0).sum()
            if zero_count > 0:
                warnings.append(
                    f"{resp}=0 olan {zero_count} satir var. "
                    f"Yuzdesel degisim hesaplamasinda NaN veya 0 kullanilacak."
                )
    
    # Eksik deger ozeti
    missing = df.isnull().sum()
    if missing.any():
        msg_parts = [f"{c}: {int(missing[c])}" for c in missing[missing > 0].index]
        warnings.append(f"Eksik degerler: {', '.join(msg_parts)}")
    
    return warnings


def apply_column_mapping(df: pd.DataFrame, mapping: Dict[str, str]) -> pd.DataFrame:
    """Kullanici tarafindan belirlenen kolon eslemesini uygular."""
    return df.rename(columns=mapping)
