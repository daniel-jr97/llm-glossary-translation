# src/retrieval.py
# Utilities for building a text corpus from the glossary and retrieving top-k terms.

from typing import List, Dict
import pandas as pd
import numpy as np

def build_glossary_corpus(glossary_df: pd.DataFrame, target_lang: str) -> List[str]:
    """
    Turn each glossary row into a short text 'document' that includes
    the source term, definition, domain, and the preferred target form.
    """
    docs = []
    target_col = target_lang  # e.g., 'fr', 'it', or 'ja'
    for _, r in glossary_df.iterrows():
        tgt = r.get(target_col, "")
        piece = (
            f"term: {r.get('term','')}\n"
            f"pos: {r.get('part_of_speech','')}\n"
            f"domain: {r.get('domain','')}\n"
            f"definition: {r.get('definition','')}\n"
            f"target_{target_lang}: {tgt}\n"
        )
        docs.append(piece)
    return docs

def best_k_terms(query: str, docs: List[str], embeddings, k: int = 3) -> List[int]:
    """
    Given a source string and the glossary documents, return indices of the top-k
    most similar docs using cosine similarity over SentenceTransformer embeddings.
    """
    # Embed the query and all docs
    q_emb = embeddings.encode([query], convert_to_numpy=True)
    d_emb = embeddings.encode(docs, convert_to_numpy=True)

    # Cosine similarity
    q_norm = np.linalg.norm(q_emb)
    d_norms = np.linalg.norm(d_emb, axis=1)
    sims = (q_emb @ d_emb.T) / (q_norm * d_norms)

    # Return indices of top-k
    idx = np.argsort(-sims[0])[:k]
    return idx.tolist()

def select_constraints(glossary_df: pd.DataFrame, idxs: List[int], target_lang: str) -> List[Dict]:
    """
    Turn top-k rows into a list of constraint dicts:
    [{'term_src': ..., 'target': ..., 'definition': ..., 'notes': ...}, ...]
    """
    out = []
    for i in idxs:
        row = glossary_df.iloc[i].to_dict()
        out.append({
            "term_src": row.get("term", ""),
            "target": row.get(target_lang, ""),
            "definition": row.get("definition", ""),
            "notes": row.get("notes", ""),
        })
    return out
