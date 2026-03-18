"""
Discriminant Function Analysis (DFA).
sklearn LinearDiscriminantAnalysis ile siniflandirma.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional

try:
    from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
    from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False

try:
    from statsmodels.multivariate.manova import MANOVA
    HAS_STATS = True
except ImportError:
    HAS_STATS = False


def run_dfa(
    df: pd.DataFrame,
    group_col: str,
    feature_cols: List[str],
) -> Dict[str, Any]:
    """
    Discriminant Function Analysis calistirir.
    
    Args:
        df: DataFrame
        group_col: Grup (kategorik) kolonu
        feature_cols: Ozellik (numerik) kolonlari
        
    Returns:
        {"lda", "accuracy", "classification_report", "confusion_matrix",
         "discriminant_scores", "coefficients", "eigenvalues", "wilks_lambda"}
    """
    if not HAS_SKLEARN:
        raise ImportError("scikit-learn gerekli. Kurulum: pip install scikit-learn")
    
    missing = [c for c in [group_col] + feature_cols if c not in df.columns]
    if missing:
        raise ValueError(f"Kolonlar bulunamadi: {missing}")
    
    # Grup kolonunu ozelliklerden cikar (duplicate kolon ve y 2D hatasini onler)
    feature_cols_clean = [f for f in feature_cols if f != group_col]
    if not feature_cols_clean:
        raise ValueError("Grup degiskeni ozellik olarak secilemez. En az 1 farkli ozellik secin.")
    
    cols = [group_col] + feature_cols_clean
    data = df[cols].dropna()
    if len(data) < 4:
        raise ValueError("Yetersiz veri.")
    
    X = data[feature_cols_clean].values
    y = np.asarray(data[group_col]).astype(str).ravel()
    
    n_classes = len(np.unique(y))
    n_samples = len(X)
    if n_classes < 2:
        raise ValueError("En az 2 grup gerekli.")
    
    if n_samples <= n_classes:
        raise ValueError(
            f"Gözlem sayısı ({n_samples}) sınıf sayısından ({n_classes}) fazla olmalıdır. "
            f"Grup değişkeni ('{group_col}') çok fazla benzersiz değer içeriyor. "
            f"Az sayıda kategoriye sahip bir değişken (örn. delik, numune) seçin."
        )
    
    if len(feature_cols_clean) < 1:
        raise ValueError("En az 1 ozellik gerekli.")
    
    lda = LinearDiscriminantAnalysis()
    lda.fit(X, y)
    
    y_pred = lda.predict(X)
    accuracy = float(accuracy_score(y, y_pred))
    
    report_str = classification_report(y, y_pred, zero_division=0)
    cm = confusion_matrix(y, y_pred)
    cm_df = pd.DataFrame(
        cm,
        index=lda.classes_,
        columns=[f"Pred_{c}" for c in lda.classes_],
    )
    
    scores = lda.transform(X)
    n_components = scores.shape[1]
    ld_cols = [f"LD{i+1}" for i in range(n_components)]
    scores_df = pd.DataFrame(scores, columns=ld_cols, index=data.index)
    group_vals = np.asarray(data[group_col]).astype(str).ravel()
    scores_df.insert(0, group_col, group_vals)
    
    # coef_ shape: (n_classes-1, n_features) - 2 sinifta (1, n_features), 3+ sinifta (n_classes, n_features)
    n_coef_rows = lda.coef_.shape[0]
    if n_coef_rows == len(lda.classes_):
        coef_index = lda.classes_
    else:
        coef_index = [f"LD{i+1}" for i in range(n_coef_rows)]
    coef_df = pd.DataFrame(
        lda.coef_,
        index=coef_index,
        columns=feature_cols_clean,
    )
    coef_df["intercept"] = np.atleast_1d(lda.intercept_)[:n_coef_rows]
    
    ev_ratio = np.atleast_1d(lda.explained_variance_ratio_)
    if len(ev_ratio) != len(ld_cols):
        ld_cols = [f"LD{i+1}" for i in range(len(ev_ratio))]
    eigenvalues = pd.Series(ev_ratio, index=ld_cols)
    
    wilks_lambda = max(0.0, min(1.0, 1.0 - np.sum(ev_ratio)))
    
    return {
        "lda": lda,
        "accuracy": accuracy,
        "classification_report": report_str,
        "confusion_matrix": cm_df,
        "discriminant_scores": scores_df,
        "coefficients": coef_df,
        "eigenvalues": eigenvalues,
        "wilks_lambda": float(wilks_lambda),
        "classes": lda.classes_.tolist(),
    }
