# Unified Evaluation Summary (BLEU + LLM Rubric)

**Generated:** 20251014_134316

### Per-Model Metrics

| model       |   llm_acc_with |   llm_grammar_with |   llm_meaning_with |   llm_natural_with |   confidence_with |   llm_acc_without |   llm_grammar_without |   llm_meaning_without |   llm_natural_without |   confidence_without |   llm_acc_delta |   llm_grammar_delta |   llm_meaning_delta |   llm_natural_delta |   bleu_with |   bleu_without |   bleu_delta |   chrf3_with |   chrf3_without |   chrf3_delta |
|:------------|---------------:|-------------------:|-------------------:|-------------------:|------------------:|------------------:|----------------------:|----------------------:|----------------------:|---------------------:|----------------:|--------------------:|--------------------:|--------------------:|------------:|---------------:|-------------:|-------------:|----------------:|--------------:|
| gpt-4o-mini |          0.959 |              0.989 |              0.972 |              0.933 |             0.779 |             0.981 |                 0.998 |                 0.988 |                 0.949 |                0.8   |          -0.022 |              -0.009 |              -0.016 |              -0.016 |       0.511 |          0.539 |       -0.028 |        0.802 |           0.821 |        -0.019 |
| llama3-70b  |          0.938 |              0.986 |              0.952 |              0.922 |             0.769 |             0.964 |                 0.994 |                 0.978 |                 0.938 |                0.766 |          -0.026 |              -0.008 |              -0.026 |              -0.016 |       0.525 |          0.512 |        0.013 |        0.772 |           0.751 |         0.021 |
| llama3-8b   |          0.952 |              0.985 |              0.96  |              0.913 |             0.589 |             0.966 |                 0.985 |                 0.98  |                 0.92  |                0.617 |          -0.014 |               0     |              -0.02  |              -0.007 |       0.212 |          0.238 |       -0.026 |        0.482 |           0.535 |        -0.053 |

### Notes
- Δ = With Retrieval − Without Retrieval
- BLEU / chrF3: automatic MT metrics (higher = better)
- LLM metrics: rubric-based scores on Accuracy / Naturalness

![Change with Retrieval](mt_eval_unified_summary_20251014_134316.png)
