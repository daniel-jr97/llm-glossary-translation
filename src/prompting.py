# src/prompting.py
# Build translation prompts and safely protect/restore tags/tokens.

from typing import List, Dict, Tuple, Optional
import re

# HTML/XML tag (incl. self-closing, attributes), HTML comments, CDATA
TAG_RE = r"""
    (?: <!--.*?--> )                                   # HTML comments
  | (?: <\!\[CDATA\[(?:.|\n)*?\]\]> )                  # CDATA
  | (?: </?[A-Za-z][\w:\-]*(?:\s+[\w:\-]+(?:\s*=\s*(?:"[^"]*"|'[^']*'|[^\s"'=<>`]+))?)*\s*/?> )
"""

# Double-curly placeholders like {{SKU_123}} or {{ name | upper }}
DBL_CURLY_RE = r"(?:\{\{[^{}]+\}\})"

# Single-curly placeholders like {name}, {count}, {price:,.2f} – avoid grabbing math/braces in prose
SINGLE_CURLY_RE = r"(?:\{[A-Za-z_][A-Za-z0-9_:. ,|-]*\})"

# Inline code `...` and fenced code ```...```
CODE_RE = r"(?:`{3}[\s\S]*?`{3}|`[^`]*`)"

# HTML entities (&nbsp;, &#160;, &#xA0;)
ENTITY_RE = r"(?:&[A-Za-z0-9#x]+;)"

# Base protection: tags, placeholders, code, entities
PROTECT_PAT = re.compile(
    rf"(?:{TAG_RE}|{DBL_CURLY_RE}|{SINGLE_CURLY_RE}|{CODE_RE}|{ENTITY_RE})",
    re.VERBOSE | re.DOTALL,
)

# Currency (symbol or code) + number; percentages; plain numbers; ISO-ish dates/times
CURRENCY_SYM = r"[$€¥₹£]"
CURRENCY_CODE = r"(?:USD|CAD|EUR|GBP|JPY|INR|AUD|NZD|SGD|CNY|RMB)"
NUM_CORE = r"(?:-?\d{1,3}(?:,\d{3})*(?:\.\d+)?|-?\d+(?:\.\d+)?)"

CURRENCY_TOKEN_RE = rf"(?:{CURRENCY_SYM}\s?{NUM_CORE}|{CURRENCY_CODE}\s?{NUM_CORE}|{NUM_CORE}\s?(?:{CURRENCY_SYM}|{CURRENCY_CODE}))"
PERCENT_TOKEN_RE = rf"(?:{NUM_CORE}\s?%)"
PLAIN_NUM_RE      = rf"(?:{NUM_CORE})"  # used conservatively after currencies/percents
DATE_TOKEN_RE     = r"(?:\b\d{4}-\d{2}-\d{2}\b|\b\d{2}/\d{2}/\d{4}\b|\b\d{1,2}:\d{2}(?::\d{2})?\b)"

NUMERIC_PAT = re.compile(
    rf"(?:{CURRENCY_TOKEN_RE}|{PERCENT_TOKEN_RE}|{DATE_TOKEN_RE})",
    re.VERBOSE,
)

# If you really want to freeze *all* numbers (including plain counts), set PROTECT_PLAIN_NUMBERS=True.
PLAIN_NUM_PAT = re.compile(PLAIN_NUM_RE)

# -----------------------------------
# Protect / Restore implementation
# -----------------------------------
def protect_spans(text: str) -> Tuple[str, list]:
    """
    Replace protected spans with placeholders like [[PROT_0]].
    Returns (protected_text, [(placeholder, original), ...]).
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

def protect_numeric_tokens(text: str, protect_plain_numbers: bool = False) -> Tuple[str, list]:
    """
    Optionally protect numeric tokens (currency, %, dates/times, and (optionally) plain numbers).
    Returns (text, spans) just like protect_spans; call this AFTER protect_spans to avoid nesting conflicts.
    """
    spans = []
    # First pass: currency/%/date
    def _replace_numeric(pattern: re.Pattern, txt: str, label: str) -> Tuple[str, list]:
        out_parts, local_spans, j = [], [], 0
        for m in pattern.finditer(txt):
            out_parts.append(txt[j:m.start()])
            ph = f"[[{label}_{len(spans)+len(local_spans)}]]"
            out_parts.append(ph)
            local_spans.append((ph, m.group(0)))
            j = m.end()
        out_parts.append(txt[j:])
        return ''.join(out_parts), local_spans

    text, s1 = _replace_numeric(NUMERIC_PAT, text, "NUM")
    spans.extend(s1)

    if protect_plain_numbers:
        
        def safe_plain_repl(match):
            token = match.group(0)
            # Don’t replace if inside a protected span or next to % or currency symbol/code
            return token if match.re is None else f"[[PNUM_{len(spans)}]]"

        out_parts, j = [], 0
        for m in PLAIN_NUM_PAT.finditer(text):
            # Don’t replace inside placeholders
            before = text[max(0, m.start()-2):m.start()]
            after = text[m.end():m.end()+2]
            if "[[" in before or "]]" in after or after.startswith('%'):
                continue
            out_parts.append(text[j:m.start()])
            ph = f"[[PNUM_{len(spans)}]]"
            out_parts.append(ph)
            spans.append((ph, m.group(0)))
            j = m.end()
        out_parts.append(text[j:])
        text = ''.join(out_parts)

    return text, spans

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


BASE_SYSTEM_PROMPT = """You are a professional localization specialist. Translate while preserving the author’s intent, formatting, and any markup.

Non-negotiable rules:
1) Do NOT change meaning or tone. No additions, no omissions.
2) Preserve ALL markup and special syntax exactly:
   • Angle-bracket tags: <tag>...</tag>, self-closing tags, attributes. Do not add/remove/rename/reorder.
   • Curly placeholders: {{like_this}} and {like_this}. Do not translate inside braces or alter structure.
   • HTML entities: &nbsp;, &#160;, &#xA0; must remain.
   • Code spans: `inline` and ```blocks``` must remain verbatim.
3) Numeric integrity:
   • Keep digits and precision. Do not alter values.
   • Preserve percentages (e.g., 12.5%) and currency values/symbols/codes (e.g., $15.99, €12,50, CAD 12.00).
   • Preserve units (kg, cm), ISO dates/times (YYYY-MM-DD, HH:MM). Do not localize formats unless asked.
4) Do NOT translate: URLs, emails, file paths, JSON keys, variable names, hashtags, @mentions.
5) Keep line breaks, list markers, and paragraph boundaries unchanged.
6) Apply glossary exactly if provided (no paraphrasing).
7) If a segment is ambiguous or untranslatable (e.g., codes), copy it verbatim.
8) Return ONLY the translation, nothing else.

Before returning, self-check silently:
- Tags/braces intact? Placeholders unchanged? Numbers/%/currency/dates preserved? Meaning consistent?
Return only the final translated text."""

BASE_USER_PROMPT = """
Task: Translate the SOURCE into the TARGET language.

Constraints recap:
- Keep all angle-bracket tags <...> unchanged.
- Keep all braces {{...}} and {...} unchanged (do NOT translate their contents).
- Preserve numbers, percentages, currency symbols/codes and values, units, ISO dates/times, URLs, emails, hashtags, @mentions.
- No added or removed sentences. Output must be ONLY the translated text.

Glossary:
{constraint_table}

TARGET LANGUAGE: {tgt_lang}

SOURCE:
<<<SOURCE_START>>>
{source}
<<<SOURCE_END>>>
"""


BASE_TRANSLATION_PROMPT = """
You are a professional translator. Translate the SOURCE into the TARGET LANGUAGE.
Follow these rules strictly:
1) Honor protected tokens, code spans, and HTML tags: do not translate, remove, or move them.
2) Apply the glossary constraints exactly (match case/spacing unless noted).
3) Keep tone neutral and natural.
4) Keep numbers, percentages, currency values/symbols, units, ISO dates/times unchanged.
5) Do not add or delete content. Return only the translation.

GLOSSARY CONSTRAINTS:
{constraint_table}

TARGET LANGUAGE: {tgt_lang}

SOURCE:
{source}
"""

def make_prompt(
    source: str,
    tgt_lang: str,
    constraints: List[Dict],
    *,
    protect_numbers: bool = True,
    protect_plain_numbers: bool = False,
) -> Tuple[str, list]:
    """
    Return (prompt_text, protected_spans_list).
    - Protects HTML/tags/placeholders/code/entities by default.
    - Optionally protects numeric tokens (currency/%/dates; and optionally plain numbers).
    - tgt_lang: e.g., 'French', 'Italian', 'Japanese'.
    """
    protected, spans = protect_spans(source)
    if protect_numbers:
        protected, num_spans = protect_numeric_tokens(protected, protect_plain_numbers=protect_plain_numbers)
        spans.extend(num_spans)
    table = build_constraint_table(constraints)
    prompt = BASE_TRANSLATION_PROMPT.format(
        constraint_table=table,
        tgt_lang=tgt_lang,
        source=protected
    )
    return prompt, spans


def build_chat_messages(
    source: str,
    tgt_lang: str,
    constraints: List[Dict],
    *,
    protect_numbers: bool = True,
    protect_plain_numbers: bool = False,
    domain: Optional[str] = None,
    style: Optional[str] = None,
) -> Tuple[list, list]:
    """
    Build messages=[{'role':'system','content':...},{'role':'user','content':...}] and spans.
    Use this if you call a chat-completions API. Preserves backward-compatible restore flow.
    """
    protected, spans = protect_spans(source)
    if protect_numbers:
        protected, num_spans = protect_numeric_tokens(protected, protect_plain_numbers=protect_plain_numbers)
        spans.extend(num_spans)

    # Augment user prompt with optional domain/style hints (non-destructive).
    domain_line = f"- Domain/context: {domain}" if domain else ""
    style_line = f"- Style/tone: {style}" if style else ""

    user_prompt = BASE_USER_PROMPT.format(
        constraint_table=build_constraint_table(constraints),
        tgt_lang=tgt_lang,
        source=protected
    )
    if domain_line or style_line:
        user_prompt = user_prompt.rstrip() + f"\n{domain_line}\n{style_line}\n"

    messages = [
        {"role": "system", "content": BASE_SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]
    return messages, spans


QC_USER_PROMPT = """
Quality Control Task:
- Compare SOURCE vs TRANSLATION for fidelity, numeric/token integrity, and tag/placeholder preservation.
- If (and only if) you detect a violation (meaning drift, changed number/%/currency, broken/moved tag, modified {{...}} or {...}), return a corrected translation.
- Otherwise, return the provided translation exactly as-is.

SOURCE:
<<<SOURCE_START>>>
{source}
<<<SOURCE_END>>>

TRANSLATION:
<<<TRANSLATION_START>>>
{translation}
<<<TRANSLATION_END>>>

Glossary:
{constraint_table}
"""

def build_qc_messages(
    source: str,
    translation: str,
    constraints: List[Dict],
) -> list:
    """Chat-style QC pass ensuring token and meaning fidelity."""
    sys = BASE_SYSTEM_PROMPT + "\nFor QC, prioritize token integrity and markup preservation. If faithful, return the translation unchanged."
    user = QC_USER_PROMPT.format(
        source=source,
        translation=translation,
        constraint_table=build_constraint_table(constraints)
    )
    return [
        {"role": "system", "content": sys},
        {"role": "user", "content": user},
    ]
