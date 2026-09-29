"""Paired, fixed-prediction evaluation for the dated scientific correction.

The released label-permutation comparison is retained in the historical
artifacts. It is not a test of equality of two correlated AUROCs.
"""

from __future__ import annotations

import math

import numpy as np
from scipy.stats import norm
from scipy.optimize import minimize
from scipy.special import expit
from sklearn.metrics import average_precision_score, brier_score_loss, roc_auc_score


def _validated(y, *scores):
    y = np.asarray(y)
    if y.ndim != 1 or len(y) < 3 or not np.isin(y, [0, 1]).all():
        raise ValueError("y must be a one-dimensional binary donor label vector")
    if len(np.unique(y)) != 2:
        raise ValueError("both outcome classes are required")
    out = []
    for score in scores:
        score = np.asarray(score, dtype=float)
        if score.shape != y.shape or not np.isfinite(score).all():
            raise ValueError("each score must be finite and aligned to y")
        out.append(score)
    return y.astype(int), out


def paired_delong(y, score_a, score_b):
    """Two-sided paired DeLong comparison using case/control placements.

    Returns the empirical AUROCs, their difference, estimated standard error,
    and asymptotic p value. A zero estimated variance with unequal AUROCs is
    reported as undefined rather than as an artificial p value of zero.
    """
    y, (a, b) = _validated(y, score_a, score_b)
    positive = y == 1
    n_case, n_control = int(positive.sum()), int((~positive).sum())
    if min(n_case, n_control) < 2:
        raise ValueError("DeLong covariance needs at least two donors per class")

    placements = []
    for score in (a, b):
        delta = score[positive, None] - score[None, ~positive]
        comparison = (delta > 0).astype(float) + 0.5 * (delta == 0)
        placements.append((comparison.mean(axis=1), comparison.mean(axis=0)))
    case_placements = np.stack([item[0] for item in placements])
    control_placements = np.stack([item[1] for item in placements])
    aucs = case_placements.mean(axis=1)
    covariance = (np.cov(case_placements) / n_case +
                  np.cov(control_placements) / n_control)
    contrast = np.array([1.0, -1.0])
    difference = float(aucs[0] - aucs[1])
    variance = float(contrast @ covariance @ contrast)
    if variance < -1e-12:
        raise ArithmeticError("negative DeLong contrast variance")
    standard_error = math.sqrt(max(0.0, variance))
    p_value = (float(2 * norm.sf(abs(difference) / standard_error))
               if standard_error > 0 else (1.0 if difference == 0 else None))
    return {
        "auroc_a": float(aucs[0]), "auroc_b": float(aucs[1]),
        "difference": difference, "standard_error": standard_error,
        "p_two_sided": p_value, "n_case": n_case, "n_control": n_control,
        "delong_method": "paired DeLong, asymptotic two-sided",
    }


def paired_bootstrap_ci(y, score_a, score_b, *, n_bootstrap=5000, seed=20260721):
    y, (a, b) = _validated(y, score_a, score_b)
    rng = np.random.RandomState(seed)
    differences = []
    skipped = 0
    for _ in range(n_bootstrap):
        idx = rng.randint(0, len(y), len(y))
        if np.unique(y[idx]).size < 2:
            skipped += 1
            continue
        differences.append(roc_auc_score(y[idx], a[idx]) - roc_auc_score(y[idx], b[idx]))
    if not differences:
        raise ValueError("all bootstrap draws were degenerate")
    return {
        "ci95": [float(v) for v in np.percentile(differences, [2.5, 97.5])],
        "valid_draws": len(differences), "degenerate_draws": skipped,
        "bootstrap_method": "paired donor bootstrap, percentile, fixed predictions",
    }


def holm_adjust(p_values):
    """Holm adjusted two-sided p values for the supplied comparison family."""
    if any(p is None or not 0 <= p <= 1 for p in p_values.values()):
        raise ValueError("all p values must be defined and in [0, 1]")
    ordered = sorted(p_values, key=p_values.get)
    adjusted = {}
    running = 0.0
    n = len(ordered)
    for rank, name in enumerate(ordered):
        running = max(running, min(1.0, (n - rank) * p_values[name]))
        adjusted[name] = running
    return adjusted


def probability_metrics(y, probability, *, development_prevalence):
    y, (p,) = _validated(y, probability)
    if not np.logical_and(p >= 0, p <= 1).all():
        raise ValueError("probabilities must lie in [0, 1]")
    return {
        "auroc": float(roc_auc_score(y, p)),
        "average_precision": float(average_precision_score(y, p)),
        "brier_score": float(brier_score_loss(y, p)),
        "external_prevalence": float(y.mean()),
        "development_prevalence": float(development_prevalence),
        "development_prevalence_constant_brier": float(
            brier_score_loss(y, np.full(len(y), development_prevalence))
        ),
        "calibration": calibration_fit(y, p),
    }


def calibration_fit(y, probability):
    """Logistic recalibration slope/intercept with Wald uncertainty.

    Fits a diagnostic curve to the evaluation labels. The fitted parameters
    are never used to change the evaluated probabilities.
    """
    y, (p,) = _validated(y, probability)
    clipped = np.clip(p, 1e-6, 1 - 1e-6)
    logit = np.log(clipped / (1 - clipped))
    design = np.column_stack([np.ones(len(y)), logit])

    def score(beta):
        return design.T @ (expit(design @ beta) - y)

    def objective(beta):
        eta = design @ beta
        return float(np.logaddexp(0, eta).sum() - y @ eta)

    def information(beta):
        fitted = expit(design @ beta)
        return design.T @ ((fitted * (1 - fitted))[:, None] * design)

    fit = minimize(objective, np.array([0.0, 1.0]), jac=score,
                   hess=information, method="Newton-CG")
    if not np.isfinite(fit.x).all() or np.linalg.norm(score(fit.x)) > 1e-6:
        return {"status": "undefined", "reason": "calibration score equations did not converge"}
    fisher_information = information(fit.x)
    if np.linalg.cond(fisher_information) > 1e12:
        return {"status": "undefined", "reason": "singular information matrix"}
    standard_errors = np.sqrt(np.diag(np.linalg.inv(fisher_information)))
    return {
        "status": "estimated", "intercept": float(fit.x[0]),
        "slope": float(fit.x[1]),
        "intercept_ci95_wald": [float(fit.x[0] - 1.96 * standard_errors[0]),
                                float(fit.x[0] + 1.96 * standard_errors[0])],
        "slope_ci95_wald": [float(fit.x[1] - 1.96 * standard_errors[1]),
                            float(fit.x[1] + 1.96 * standard_errors[1])],
        "method": "diagnostic logistic recalibration, unpenalized Wald CI; fixed predictions",
    }
