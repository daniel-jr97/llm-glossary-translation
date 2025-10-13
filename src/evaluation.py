# src/evaluation.py
# Simple metrics for the translation pipeline.

from typing import List, Dict
import pandas as pd

def term_adherence(hypothesis: str, constraints: List[Dict]) -> float:
    """
    Returns a score in [0,1]: proportion of retrieved terms whose target form
    actually appears in the hypothesis (case-insensitive).
    If there are no constraints, returns 1.0 by convention.
    """
    if not constraints:
        return 1.0
    hyp_lower = (hypothesis or "").lower()
    total = 0
    hits = 0
    for c in constraints:
        tgt = (c.get("target") or "").strip()
        if not tgt:
            continue
        total += 1
        if tgt.lower() in hyp_lower:
            hits += 1
    return hits / total if total else 1.0

def basic_metrics(df: pd.DataFrame) -> Dict:
    """
    Expects columns:
      - term_acc_with, term_acc_without
    Returns a small dict of averages and count.
    """
    out = {"n": len(df)}
    if "term_acc_with" in df:
        out["avg_term_adherence_with"] = float(df["term_acc_with"].mean())
    if "term_acc_without" in df:
        out["avg_term_adherence_without"] = float(df["term_acc_without"].mean())
    return out
