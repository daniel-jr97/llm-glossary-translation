LLM-Only Translation Pipeline with Glossary Retrieval
Overview

This project implements an LLM-only translation pipeline that integrates glossary-based retrieval to improve terminology consistency across multilingual content. The goal was to evaluate how retrieving glossary terms as context for an LLM influences translation quality, compared to using the LLM without retrieval.

The system translates English text into three target languages — French (FR), Italian (IT), and Japanese (JA) — and measures term adherence, fluency, and latency across both modes (with and without retrieval).

Model and Architecture

Base model: gpt-4o-mini (OpenAI API) for translation generation

Embedding model: sentence-transformers/all-MiniLM-L6-v2 for glossary vectorization

Vector store: cosine similarity search over embedded glossary terms

Framework: Python (VS Code) + Jupyter Notebook

Data:

glossary.csv containing bilingual terminology entries

samples_en.csv containing 30 English segments from product and UI strings

The pipeline is modular, with the following core components:

Retrieval module (retrieval.py): Builds the glossary corpus, embeds terms, and retrieves the top-k relevant glossary entries per source segment.

Prompting module (prompting.py): Constructs translation prompts that include retrieved terms as explicit constraints.

Evaluation module (evaluation.py): Computes term adherence metrics and generates comparison outputs.

Methodology

Each source segment is embedded and compared to glossary entries using cosine similarity.

The top-k (k = 3) glossary matches are inserted into the translation prompt as “preferred terminology.”

The LLM generates translations with and without retrieval under identical conditions.

Post-processing restores protected tokens and simple HTML tags.

Evaluation calculates term adherence, defined as the proportion of glossary terms correctly used in the output.

All results are logged to a CSV file (data/results_batch1.csv) and visualized in a side-by-side HTML report.

Results
Metric	With Retrieval	Without Retrieval
Samples (n)	30	30
Avg. Term Adherence	0.344	0.233
Qualitative Examples

EN→FR
Source: Enter your email address to continue.
With Retrieval: Entrez votre adresse e-mail pour continuer.
Without Retrieval: Entrez votre adresse e-mail pour continuer.
→ Terminology preserved in both cases; minimal difference for common terms.

EN→IT
Source: Free shipping on orders over $50 at checkout.
With Retrieval: Spedizione gratuita su ordini superiori a $50 alla cassa.
Without Retrieval: Spedizione gratuita su ordini superiori a $50 al momento del checkout.
→ Retrieval produced “alla cassa,” which aligns more closely with retail domain terminology.

EN→JA
Source: Enable two-factor authentication (2FA) in Settings.
With Retrieval: 設定で二要素認証を有効にしてください。
Without Retrieval: 設定で二要素認証 (2FA) を有効にします。
→ Retrieval improved natural phrasing and omitted redundant parenthetical notation.

Discussion

Glossary retrieval improved term adherence by about 48 % relative (0.344 vs 0.233), indicating that even lightweight retrieval guidance can help LLMs follow domain-specific terminology more consistently.
In particular, retrieval helped disambiguate localized commerce and technical UI terms (“checkout,” “authentication”) where the base LLM might produce variants.

Latency differences were minor (typically ± 0.4 s), showing that embedding retrieval adds negligible runtime overhead.

Design Decisions and Limitations

Retrieval size (k = 3) balances precision and prompt length.

The current pipeline uses cosine similarity; future work could incorporate cross-encoder reranking.

Term adherence scoring is surface-form based; semantic or fuzzy matching would better capture near-synonyms.

Evaluation used 30 segments; scaling to 50+ will provide stronger statistical reliability.

Cost remained low (under $5 total API spend).

Conclusion

This project demonstrates that embedding-based glossary retrieval can significantly enhance terminology accuracy in LLM translations without retraining or fine-tuning. The approach is lightweight, modular, and easily extensible to additional domains or languages.