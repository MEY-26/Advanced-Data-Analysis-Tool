"""
DOE (Deney Tasarimi) - Full Factorial, Fractional, CCD, Box-Behnken, D/I-Optimal.
Madde 3 + 4. pyDOE2 yerine numpy/scipy kullanir (Python 3.13 uyumlu).
"""

import itertools
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional

from analysis.coding import decode_dataframe


def _ff2n(n: int) -> np.ndarray:
    """2 seviyeli tam faktoriyel (-1, +1)."""
    rows = list(itertools.product([-1.0, 1.0], repeat=n))
    return np.array(rows)


def _parse_fracfact_gen(gen: str) -> Tuple[int, List[Tuple[int, ...]]]:
    """
    Generator string parse: 'a b ab' -> 3 kolon, 3. kolon = col0*col1
    Donus: (n_base, [(base_indices), ...]) - her derived icin carpilacak kolonlar
    """
    terms = gen.lower().replace("-", "").split()
    letter_to_col = {}
    derived = []
    for t in terms:
        if not t:
            continue
        if len(t) == 1:
            letter_to_col[t] = len(letter_to_col)
        else:
            indices = tuple(sorted(set(letter_to_col[c] for c in t if c in letter_to_col)))
            if indices:
                derived.append(indices)
    n_base = len(letter_to_col)
    return n_base, derived


def _fracfact_from_gen(gen: str, n_cols: int) -> np.ndarray:
    """Generator string ile kesirli faktoriyel matris."""
    n_base, derived = _parse_fracfact_gen(gen)
    if n_base == 0:
        return _ff2n(n_cols)
    base_mat = _ff2n(n_base)
    out_cols = [base_mat[:, i].copy() for i in range(n_base)]
    for indices in derived:
        if len(out_cols) >= n_cols:
            break
        col = np.ones(len(base_mat))
        for j in indices:
            if j < len(out_cols):
                col *= out_cols[j]
        out_cols.append(col)
    mat = np.column_stack(out_cols[:n_cols])
    return mat


# Varsayilan fractional factorial generator (Resolution III)
_DEFAULT_FRAC_GEN = {
    3: "a b ab",
    4: "a b ab c",
    5: "a b ab c ac",
    6: "a b ab c ac bc",
    7: "a b ab c ac bc abc",
    8: "a b ab c ac bc abc d",
}


def generate_full_factorial(levels: Dict[str, List[float]]) -> pd.DataFrame:
    """
    Tum kombinasyonlarla tam faktoriyel tasarim.
    levels: {faktor_adi: [deger1, deger2, ...]} - gercek veya kodlanmis seviyeler
    """
    if not levels:
        return pd.DataFrame()
    names = list(levels.keys())
    vals = [levels[n] for n in names]
    rows = list(itertools.product(*vals))
    return pd.DataFrame(rows, columns=names)


def generate_fractional_factorial(
    n_factors: int,
    gen: Optional[str] = None,
    factor_names: Optional[List[str]] = None,
) -> pd.DataFrame:
    """
    Kesirli faktoriyel tasarim (2 seviyeli, kodlanmis -1/+1).
    """
    gen_str = gen if gen else _DEFAULT_FRAC_GEN.get(n_factors)
    if gen_str is None:
        mat = _ff2n(n_factors)
    else:
        try:
            mat = _fracfact_from_gen(gen_str, n_factors)
        except Exception:
            mat = _ff2n(n_factors)
    n_cols = mat.shape[1]
    cols = factor_names[:n_cols] if factor_names and len(factor_names) >= n_cols else [f"F{i+1}" for i in range(n_cols)]
    return pd.DataFrame(mat, columns=cols)


def generate_ccd(
    n_factors: int,
    center: Tuple[int, int] = (4, 4),
    alpha: str = "orthogonal",
    face: str = "circumscribed",
    factor_names: Optional[List[str]] = None,
) -> pd.DataFrame:
    """
    Central Composite Design (kodlanmis -1/+1).
    """
    n_center_f, n_center_s = center
    fact_mat = _ff2n(n_factors)
    n_fact = len(fact_mat)
    if alpha.lower() in ("rotatable", "r"):
        alpha_val = (n_fact) ** 0.25
    else:
        alpha_val = (n_fact) ** 0.5
    if face.lower() in ("inscribed", "cci"):
        alpha_val = 1.0
    elif face.lower() in ("faced", "ccf"):
        alpha_val = 1.0
    star_rows = []
    for i in range(n_factors):
        for sgn in [-1, 1]:
            row = np.zeros(n_factors)
            row[i] = sgn * alpha_val
            star_rows.append(row)
    star_mat = np.array(star_rows)
    blocks = [fact_mat]
    if n_center_f > 0:
        blocks.append(np.zeros((n_center_f, n_factors)))
    blocks.append(star_mat)
    if n_center_s > 0:
        blocks.append(np.zeros((n_center_s, n_factors)))
    mat = np.vstack(blocks)
    cols = factor_names[:n_factors] if factor_names and len(factor_names) >= n_factors else [f"F{i+1}" for i in range(n_factors)]
    return pd.DataFrame(mat, columns=cols)


def generate_box_behnken(
    n_factors: int,
    center: int = 3,
    factor_names: Optional[List[str]] = None,
) -> pd.DataFrame:
    """
    Box-Behnken tasarimi (kodlanmis -1/0/+1). En az 3 faktor gerekir.
    """
    if n_factors < 3:
        n_factors = 3
    rows = []
    for i in range(n_factors):
        for j in range(i + 1, n_factors):
            for a, b in itertools.product([-1, 1], repeat=2):
                row = np.zeros(n_factors)
                row[i] = a
                row[j] = b
                rows.append(row)
    mat = np.array(rows)
    for _ in range(center):
        mat = np.vstack([mat, np.zeros(n_factors)])
    cols = factor_names[:n_factors] if factor_names and len(factor_names) >= n_factors else [f"F{i+1}" for i in range(n_factors)]
    return pd.DataFrame(mat, columns=cols)


def _lhs(n: int, d: int, criterion: str = "center") -> np.ndarray:
    """Latin Hypercube Sampling - scipy veya basit numpy."""
    try:
        from scipy.stats import qmc
        sampler = qmc.LatinHypercube(d=d, seed=np.random.default_rng())
        samp = sampler.random(n=n)
        return samp
    except ImportError:
        pass
    samp = np.zeros((n, d))
    for j in range(d):
        perm = np.random.permutation(n)
        if criterion == "center":
            samp[:, j] = (perm + 0.5) / n
        else:
            samp[:, j] = perm / (n - 1) if n > 1 else 0.5
    return samp


def _build_model_matrix(df: pd.DataFrame, order: int) -> np.ndarray:
    """Kodlanmis tasarimdan model matrisi."""
    n = len(df)
    x = df.values
    rows = []
    for i in range(n):
        row = [1.0]
        for j in range(x.shape[1]):
            row.append(x[i, j])
        if order >= 2:
            for j in range(x.shape[1]):
                row.append(x[i, j] ** 2)
            for j in range(x.shape[1]):
                for k in range(j + 1, x.shape[1]):
                    row.append(x[i, j] * x[i, k])
        rows.append(row)
    return np.array(rows)


def generate_d_optimal(
    n_factors: int,
    n_runs: int,
    model_order: int = 2,
    factor_names: Optional[List[str]] = None,
) -> pd.DataFrame:
    """
    D-Optimal tasarim: det(X'X) maksimize edilir.
    """
    n_candidates = min(500, max(100, n_runs * 10))
    cand = _lhs(n_candidates, n_factors)
    cand = 2 * cand - 1
    n_params = 1 + n_factors
    if model_order >= 2:
        n_params += n_factors + n_factors * (n_factors - 1) // 2
    if n_runs < n_params:
        n_runs = n_params
    cand_df = pd.DataFrame(cand, columns=[f"F{i+1}" for i in range(n_factors)])
    X_cand = _build_model_matrix(cand_df, model_order)
    idx = np.random.choice(len(cand), size=n_runs, replace=False)
    X = X_cand[idx]
    best_det = np.linalg.det(X.T @ X)
    if best_det <= 0:
        cols = factor_names[:n_factors] if factor_names else [f"F{i+1}" for i in range(n_factors)]
        return generate_full_factorial({c: [-1.0, 1.0] for c in cols}).head(n_runs)
    for _ in range(50):
        improved = False
        for i in range(n_runs):
            for j in range(len(cand)):
                if j in idx:
                    continue
                idx_new = idx.copy()
                idx_new[i] = j
                X_new = X_cand[idx_new]
                det_new = np.linalg.det(X_new.T @ X_new)
                if det_new > best_det:
                    best_det = det_new
                    idx = idx_new
                    X = X_new
                    improved = True
        if not improved:
            break
    out = cand_df.iloc[idx].reset_index(drop=True)
    if factor_names and len(factor_names) >= n_factors:
        out.columns = factor_names[:n_factors]
    return out


def generate_i_optimal(
    n_factors: int,
    n_runs: int,
    model_order: int = 2,
    factor_names: Optional[List[str]] = None,
) -> pd.DataFrame:
    """
    I-Optimal tasarim: Tahminin ortalama varyansini minimize eder.
    """
    n_candidates = min(500, max(100, n_runs * 10))
    cand = _lhs(n_candidates, n_factors)
    cand = 2 * cand - 1
    n_params = 1 + n_factors
    if model_order >= 2:
        n_params += n_factors + n_factors * (n_factors - 1) // 2
    if n_runs < n_params:
        n_runs = n_params
    cand_df = pd.DataFrame(cand, columns=[f"F{i+1}" for i in range(n_factors)])
    X_cand = _build_model_matrix(cand_df, model_order)
    idx = np.random.choice(len(cand), size=n_runs, replace=False)
    X = X_cand[idx]
    try:
        inv = np.linalg.inv(X.T @ X)
        best_trace = np.trace(inv)
    except np.linalg.LinAlgError:
        cols = factor_names[:n_factors] if factor_names else [f"F{i+1}" for i in range(n_factors)]
        return generate_full_factorial({c: [-1.0, 1.0] for c in cols}).head(n_runs)
    for _ in range(50):
        improved = False
        for i in range(n_runs):
            for j in range(len(cand)):
                if j in idx:
                    continue
                idx_new = idx.copy()
                idx_new[i] = j
                X_new = X_cand[idx_new]
                try:
                    inv_new = np.linalg.inv(X_new.T @ X_new)
                    trace_new = np.trace(inv_new)
                    if trace_new < best_trace:
                        best_trace = trace_new
                        idx = idx_new
                        X = X_new
                        improved = True
                except np.linalg.LinAlgError:
                    pass
        if not improved:
            break
    out = cand_df.iloc[idx].reset_index(drop=True)
    if factor_names and len(factor_names) >= n_factors:
        out.columns = factor_names[:n_factors]
    return out


def decode_design(
    coded_df: pd.DataFrame,
    factor_ranges: Dict[str, Tuple[float, float]],
) -> pd.DataFrame:
    """Kodlanmis tasarimi gercek degerlere cevirir."""
    return decode_dataframe(coded_df, factor_ranges)
