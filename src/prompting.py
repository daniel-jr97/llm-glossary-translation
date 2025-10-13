# src/prompting.py
# Build translation prompts and safely protect/restore tags/tokens.

from typing import List, Dict, Tuple
import re

# Protect simple HTML tags like <b>...</b> and "do not translate" tokens like {{SKU_123}}
PROTECT_PAT = re.compile(r"(<[^>]+>)|(\{\{[^}]+\}\})")

def protect_spans(text: str) -> Tuple[str, list]:
    """
    Replace protected spans with placeholders like [[PROT_0]].
    Return (protected_text, [(placeholder, original), ...]).
    """
    parts = []
    spans = []
    i = 0
    for m in PROTECT_PAT.finditer(text):
        parts.append(text[i:m.start()])
        placeholder = f"[[PROT_{len(spans)}]]"
        parts.append(placeholder)
        spans.append((placeholder, m.group(0)))
        i = m.end()
    parts.append(text[i:])
    return ''.join(parts), spans

def restore_spans(text: str, spans: list) -> str:
    """Put protected spans back into the text."""
    for ph, original in spans:
        text = text.replace(ph, original)
    return text

def build_constraint_table(constraints: List[Dict]) -> str:
    """
    Turn constraints into a bullet list for the prompt.
    Each item: 'src_term' → 'target_term' (definition)
    """
    if not constraints:
        return "None"
    rows = []
    for c in constraints:
        rows.append(f"- '{c['term_src']}' → '{c['target']}'  (def: {c.get('definition','')})")
    return "\n".join(rows)

BASE_TRANSLATION_PROMPT = """
You are a professional translator. Translate the SOURCE into the TARGET LANGUAGE.
Follow these rules strictly:
1) Honor protected tokens and HTML tags: do not translate, remove, or move them.
2) Apply the glossary constraints exactly (match case/spacing unless noted).
3) Keep tone neutral and natural.
4) If the glossary suggests keeping acronyms (e.g., GPU, ID), keep them.

GLOSSARY CONSTRAINTS:
{constraint_table}

EDGE-CASE GUIDANCE (few-shot hints):
- Gender/morphology: choose natural forms; if brand names, keep unchanged.
- Casing: preserve title casing for product/policy names unless target convention differs.
- Verb vs noun 'checkout': translate based on context.

TARGET LANGUAGE: {tgt_lang}

SOURCE:
{source}
"""

def make_prompt(source: str, tgt_lang: str, constraints: List[Dict]):
    """
    Return (prompt_text, protected_spans_list).
    - source is preprocessed to protect HTML/DNT.
    - tgt_lang should be a language name like 'French', 'Italian', 'Japanese'.
    """
    protected, spans = protect_spans(source)
    table = build_constraint_table(constraints)
    prompt = BASE_TRANSLATION_PROMPT.format(
        constraint_table=table,
        tgt_lang=tgt_lang,
        source=protected
    )
    return prompt, spans
