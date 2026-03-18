"""
Grafik fonksiyonlari.
Tum fonksiyonlar matplotlib Figure dondurur (Qt canvas'a gomulecek).
"""

import numpy as np
import pandas as pd
from typing import Optional, Dict, List
import matplotlib
matplotlib.use("Agg")  # Headless for thread safety
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from scipy import stats


def plot_residuals_vs_fitted(model) -> Figure:
    """
    Residual vs Fitted deger grafigi.
    
    Args:
        model: statsmodels OLSResults
        
    Returns:
        matplotlib Figure
    """
    fig, ax = plt.subplots(figsize=(6, 4))
    fitted = model.fittedvalues
    residuals = model.resid
    ax.scatter(fitted, residuals, alpha=0.6, edgecolors="k", linewidth=0.5)
    ax.axhline(0, color="red", linestyle="--", linewidth=1)
    ax.set_xlabel("Fitted values")
    ax.set_ylabel("Residuals")
    ax.set_title("Residual vs Fitted")
    fig.tight_layout()
    return fig


def plot_qq(model) -> Figure:
    """
    Q-Q plot (normallik kontrolu).
    
    Args:
        model: statsmodels OLSResults
        
    Returns:
        matplotlib Figure
    """
    fig, ax = plt.subplots(figsize=(6, 4))
    stats.probplot(model.resid, dist="norm", plot=ax)
    ax.set_title("Normal Q-Q Plot")
    fig.tight_layout()
    return fig


def _get_prediction_grid(
    model,
    df: pd.DataFrame,
    factor1: str,
    factor2: str,
    fixed_vals: Dict[str, float],
) -> tuple:
    """Model prediction icin grid olusturur. Sadece numerik faktorler desteklenir."""
    numeric_factors = ["devir", "feed", "paso"]
    factors = [factor1, factor2]
    fixed_factors = [f for f in numeric_factors if f not in factors]
    
    x_min, x_max = float(df[factor1].min()), float(df[factor1].max())
    y_min, y_max = float(df[factor2].min()), float(df[factor2].max())
    x = np.linspace(x_min, x_max, 30)
    y = np.linspace(y_min, y_max, 30)
    X, Y = np.meshgrid(x, y)
    
    # Sabit degerler (kategorikler icin ilk seviyeyi kullan)
    base_row = df.iloc[0].to_dict()
    for f in fixed_factors:
        base_row[f] = fixed_vals.get(f, float(df[f].median()))
    
    Z = np.zeros_like(X)
    for i in range(X.shape[0]):
        for j in range(X.shape[1]):
            row = base_row.copy()
            row[factor1] = X[i, j]
            row[factor2] = Y[i, j]
            pred_df = pd.DataFrame([row])
            try:
                Z[i, j] = model.predict(pred_df)[0]
            except Exception:
                Z[i, j] = np.nan
    
    return X, Y, Z


def plot_3d_surface(
    model,
    df: pd.DataFrame,
    factor1: str,
    factor2: str,
    fixed_vals: Optional[Dict[str, float]] = None,
) -> Figure:
    """
    3D yuzey grafigi.
    
    Args:
        model: Fitted OLS model
        df: Veri (araliklar icin)
        factor1: X ekseni faktor
        factor2: Y ekseni faktor
        fixed_vals: 3. faktorun sabit degeri {faktor: deger}
        
    Returns:
        matplotlib Figure
    """
    if fixed_vals is None:
        fixed_vals = {}
    
    X, Y, Z = _get_prediction_grid(model, df, factor1, factor2, fixed_vals)
    
    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(111, projection="3d")
    ax.plot_surface(X, Y, Z, cmap="viridis", alpha=0.8)
    ax.set_xlabel(factor1)
    ax.set_ylabel(factor2)
    ax.set_zlabel("Response")
    ax.set_title(f"Response Surface: {factor1} vs {factor2}")
    fig.tight_layout()
    return fig


def plot_contour(
    model,
    df: pd.DataFrame,
    factor1: str,
    factor2: str,
    fixed_vals: Optional[Dict[str, float]] = None,
) -> Figure:
    """
    Contour grafigi.
    
    Args:
        model: Fitted OLS model
        df: Veri
        factor1: X ekseni
        factor2: Y ekseni
        fixed_vals: 3. faktor sabit degeri
        
    Returns:
        matplotlib Figure
    """
    if fixed_vals is None:
        fixed_vals = {}
    
    X, Y, Z = _get_prediction_grid(model, df, factor1, factor2, fixed_vals)
    
    fig, ax = plt.subplots(figsize=(6, 5))
    cf = ax.contourf(X, Y, Z, levels=15, cmap="viridis")
    plt.colorbar(cf, ax=ax)
    ax.set_xlabel(factor1)
    ax.set_ylabel(factor2)
    ax.set_title(f"Contour: {factor1} vs {factor2}")
    fig.tight_layout()
    return fig


def plot_main_effects(
    df: pd.DataFrame,
    factors: List[str],
    response: str,
) -> Figure:
    """
    Main effects plot (faktor bazli ortalama response).
    
    Args:
        df: DataFrame
        factors: Faktor kolonlari
        response: Response kolonu
        
    Returns:
        matplotlib Figure
    """
    available = [f for f in factors if f in df.columns]
    if len(available) == 0 or response not in df.columns:
        return plt.figure(figsize=(6, 4))
    
    n = len(available)
    fig, axes = plt.subplots(1, n, figsize=(4 * n, 4))
    if n == 1:
        axes = [axes]
    
    for ax, f in zip(axes, available):
        means = df.groupby(f)[response].mean()
        stds = df.groupby(f)[response].std()
        x = range(len(means))
        ax.errorbar(x, means, yerr=stds, fmt="o-", capsize=5)
        ax.set_xticks(x)
        ax.set_xticklabels(means.index, rotation=45, ha="right")
        ax.set_xlabel(f)
        ax.set_ylabel(response)
        ax.set_title(f"Main Effect: {f}")
    
    fig.suptitle("Main Effects Plot", fontsize=12, y=1.02)
    fig.tight_layout()
    return fig


def plot_correlation_heatmap(corr_matrix: pd.DataFrame) -> Figure:
    """
    Korelasyon matrisi heatmap.
    
    Args:
        corr_matrix: Korelasyon DataFrame
        
    Returns:
        matplotlib Figure
    """
    if corr_matrix.empty:
        return plt.figure(figsize=(4, 4))
    
    fig, ax = plt.subplots(figsize=(6, 5))
    im = ax.imshow(corr_matrix, cmap="RdBu_r", vmin=-1, vmax=1)
    ax.set_xticks(range(len(corr_matrix.columns)))
    ax.set_yticks(range(len(corr_matrix.index)))
    ax.set_xticklabels(corr_matrix.columns)
    ax.set_yticklabels(corr_matrix.index)
    plt.colorbar(im, ax=ax)
    for i in range(len(corr_matrix)):
        for j in range(len(corr_matrix.columns)):
            val = corr_matrix.iloc[i, j]
            if not np.isnan(val):
                ax.text(j, i, f"{val:.2f}", ha="center", va="center", fontsize=10)
    ax.set_title("Korelasyon Matrisi (Devir, Feed, Paso)")
    fig.tight_layout()
    return fig


def plot_delta_distribution(
    df: pd.DataFrame,
    groupby: Optional[str] = None,
    kind: str = "hist",
) -> Figure:
    """
    Delta dagilim grafigi (histogram, box, violin).
    
    Args:
        df: Delta kolonu iceren DataFrame
        groupby: Gruplama kolonu (None ise tek dagilim)
        kind: "hist" | "box" | "violin"
        
    Returns:
        matplotlib Figure
    """
    if "Delta" not in df.columns:
        return plt.figure(figsize=(6, 4))
    
    df_valid = df.dropna(subset=["Delta"])
    if df_valid.empty:
        return plt.figure(figsize=(6, 4))
    
    fig, ax = plt.subplots(figsize=(6, 4))
    
    if groupby and groupby in df_valid.columns:
        if kind == "hist":
            for g in df_valid[groupby].unique():
                subset = df_valid[df_valid[groupby] == g]["Delta"]
                ax.hist(subset, alpha=0.5, label=str(g), bins=15)
            ax.legend()
        elif kind == "box":
            df_valid.boxplot(column="Delta", by=groupby, ax=ax)
        elif kind == "violin":
            parts = []
            for g in df_valid[groupby].unique():
                parts.append(df_valid[df_valid[groupby] == g]["Delta"])
            ax.violinplot(parts, positions=range(len(parts)), showmeans=True)
            ax.set_xticks(range(len(parts)))
            ax.set_xticklabels(df_valid[groupby].unique())
    else:
        if kind == "hist":
            ax.hist(df_valid["Delta"], bins=20, edgecolor="black", alpha=0.7)
        elif kind == "box":
            ax.boxplot(df_valid["Delta"])
        elif kind == "violin":
            ax.violinplot([df_valid["Delta"]], positions=[0], showmeans=True)
    
    ax.set_ylabel("Delta")
    ax.set_title("Delta Dagilimi")
    fig.tight_layout()
    return fig


def plot_histogram_with_distribution(
    series: pd.Series,
    title: str = "Dağılım",
    bins: int = 20,
) -> Figure:
    """
    Histogram + KDE + normal eğri.
    """
    clean = pd.to_numeric(series, errors="coerce").dropna()
    if len(clean) < 2:
        return plt.figure(figsize=(6, 4))
    
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.hist(clean, bins=bins, density=True, alpha=0.6, color="steelblue", edgecolor="black")
    try:
        from scipy.stats import gaussian_kde
        kde = gaussian_kde(clean)
        x = np.linspace(clean.min(), clean.max(), 100)
        ax.plot(x, kde(x), "b-", linewidth=2, label="KDE")
    except Exception:
        pass
    try:
        x = np.linspace(clean.min(), clean.max(), 100)
        ax.plot(x, stats.norm.pdf(x, clean.mean(), clean.std()), "r--", linewidth=1.5, label="Normal")
    except Exception:
        pass
    ax.set_xlabel(series.name or "Değer")
    ax.set_ylabel("Yoğunluk")
    ax.set_title(title)
    ax.legend()
    fig.tight_layout()
    return fig


def plot_boxplot_outliers(
    df: pd.DataFrame,
    column: str,
    outlier_mask: Optional[pd.Series] = None,
) -> Figure:
    """
    Outlier'ları vurgulayan boxplot.
    """
    if column not in df.columns:
        return plt.figure(figsize=(6, 4))
    
    series = pd.to_numeric(df[column], errors="coerce").dropna()
    if len(series) < 1:
        return plt.figure(figsize=(6, 4))
    
    fig, ax = plt.subplots(figsize=(6, 4))
    bp = ax.boxplot([series], labels=[column], patch_artist=True)
    for patch in bp["boxes"]:
        patch.set_facecolor("lightblue")
    
    if outlier_mask is not None and outlier_mask.any():
        outliers = series[outlier_mask.reindex(series.index).fillna(False)]
        if len(outliers) > 0:
            ax.scatter([1] * len(outliers), outliers, color="red", marker="o", s=30, zorder=5, label="Outlier")
            ax.legend()
    
    ax.set_ylabel(column)
    ax.set_title(f"Boxplot: {column}")
    fig.tight_layout()
    return fig


def plot_distribution_panel(series: pd.Series, title: str = "Dağılım") -> Figure:
    """
    Histogram + boxplot + Q-Q birleşik panel.
    """
    clean = pd.to_numeric(series, errors="coerce").dropna()
    if len(clean) < 2:
        return plt.figure(figsize=(10, 4))
    
    fig, axes = plt.subplots(1, 3, figsize=(12, 4))
    
    axes[0].hist(clean, bins=20, edgecolor="black", alpha=0.7)
    axes[0].set_xlabel(series.name or "Değer")
    axes[0].set_ylabel("Frekans")
    axes[0].set_title("Histogram")
    
    axes[1].boxplot(clean, labels=[series.name or "Değer"])
    axes[1].set_ylabel(series.name or "Değer")
    axes[1].set_title("Boxplot")
    
    stats.probplot(clean, dist="norm", plot=axes[2])
    axes[2].set_title("Q-Q Plot")
    
    fig.suptitle(title, fontsize=12, y=1.02)
    fig.tight_layout()
    return fig


def plot_delta_boxplot_by_group(
    df: pd.DataFrame,
    group_col: str,
) -> Figure:
    """
    Grup bazli Delta boxplot.
    
    Args:
        df: Delta kolonu iceren DataFrame
        group_col: Gruplama kolonu (delik, olcum vb.)
        
    Returns:
        matplotlib Figure
    """
    if "Delta" not in df.columns or group_col not in df.columns:
        return plt.figure(figsize=(6, 4))
    
    df_valid = df.dropna(subset=["Delta", group_col])
    if df_valid.empty:
        return plt.figure(figsize=(6, 4))
    
    fig, ax = plt.subplots(figsize=(6, 4))
    groups = df_valid[group_col].unique()
    data = [df_valid[df_valid[group_col] == g]["Delta"].values for g in groups]
    bp = ax.boxplot(data, labels=[str(g) for g in groups], patch_artist=True)
    for patch in bp["boxes"]:
        patch.set_facecolor("lightblue")
    ax.set_xlabel(group_col)
    ax.set_ylabel("Delta")
    ax.set_title(f"Delta by {group_col}")
    fig.tight_layout()
    return fig


def plot_gra_ranking(grades: pd.Series, title: str = "GRA Dereceleri") -> Figure:
    """
    GRA dereceleri yatay bar grafigi (buyukten kucuge sirali).
    
    Args:
        grades: Seri adi -> Gray Relational Grade
        title: Grafik basligi
        
    Returns:
        matplotlib Figure
    """
    if grades is None or grades.empty:
        return plt.figure(figsize=(6, 4))
    sorted_grades = grades.sort_values(ascending=True)
    fig, ax = plt.subplots(figsize=(8, max(4, len(sorted_grades) * 0.4)))
    y_pos = np.arange(len(sorted_grades))
    bars = ax.barh(y_pos, sorted_grades.values, color="steelblue", alpha=0.8)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(sorted_grades.index)
    ax.set_xlabel("Gray Relational Grade")
    ax.set_title(title)
    ax.set_xlim(0, 1.05)
    fig.tight_layout()
    return fig


def plot_dfa_scatter(
    scores_df: pd.DataFrame,
    group_col: str,
    ld1: str = "LD1",
    ld2: str = "LD2",
    title: str = "DFA Skor Grafiği",
) -> Figure:
    """
    DFA diskriminant skorlari scatter plot (LD1 vs LD2, gruplara gore renkli).
    
    Args:
        scores_df: LD1, LD2, ... ve grup kolonu iceren DataFrame
        group_col: Grup kolonu adi
        ld1: Birinci diskriminant kolonu
        ld2: Ikinci diskriminant kolonu
        title: Grafik basligi
        
    Returns:
        matplotlib Figure
    """
    if scores_df is None or scores_df.empty or ld1 not in scores_df.columns:
        return plt.figure(figsize=(6, 4))
    if ld2 not in scores_df.columns and len(scores_df.columns) > 2:
        ld2 = [c for c in scores_df.columns if c.startswith("LD") and c != ld1]
        ld2 = ld2[0] if ld2 else ld1
    elif ld2 not in scores_df.columns:
        ld2 = ld1
    if group_col not in scores_df.columns:
        return plt.figure(figsize=(6, 4))
    df = scores_df[[ld1, ld2, group_col]].dropna()
    if df.empty:
        return plt.figure(figsize=(6, 4))
    fig, ax = plt.subplots(figsize=(7, 5))
    groups = df[group_col].unique()
    colors = plt.cm.tab10(np.linspace(0, 1, len(groups)))
    for i, g in enumerate(groups):
        mask = df[group_col] == g
        ax.scatter(df.loc[mask, ld1], df.loc[mask, ld2], label=str(g), alpha=0.7, c=[colors[i]])
    ax.set_xlabel(ld1)
    ax.set_ylabel(ld2)
    ax.set_title(title)
    ax.legend()
    ax.axhline(0, color="gray", linestyle="--", linewidth=0.5)
    ax.axvline(0, color="gray", linestyle="--", linewidth=0.5)
    fig.tight_layout()
    return fig
