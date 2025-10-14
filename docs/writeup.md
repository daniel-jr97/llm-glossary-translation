# **LLM-Only Translation Pipeline with Glossary Retrieval**

## **Overview**

This project implements a glossary-aware, LLM-only translation pipeline designed to improve terminology consistency across multilingual content. The system compares **three models** — **GPT-4o-mini (OpenAI)**, **Llama-3.1-8B (Groq)**, and **Llama-3.3-70B (Groq)** — to assess how glossary retrieval enhances translation accuracy and fluency across **English → French, Italian, and Japanese**.

Glossary retrieval provides each model with relevant term definitions before translation, guiding it to use preferred terminology in context. The pipeline evaluates and compares translations **with vs. without retrieval**, measuring **term adherence**, **latency**, and qualitative accuracy.

---

## **Model and Architecture**

- **Translation Models:** GPT-4o-mini (OpenAI), Llama-3.1-8B (Groq), Llama-3.3-70B (Groq)  
- **Embedding Model:** `sentence-transformers/all-MiniLM-L6-v2` for glossary vectorization  
- **Vector Store:** Cosine similarity over embedded glossary entries  
- **Framework:** Python (VS Code) + Jupyter Notebook  
- **Data:**  
  - `glossary.csv` — bilingual glossary with preferred terminology  
  - `samples_en.csv` — 50 English UI and product-related text segments  

### **Core Components**

- **Retrieval Module (`retrieval.py`)** — Builds the glossary corpus, embeds terms, and retrieves top-k matches (k = 3).  
- **Prompting Module (`prompting.py`)** — Inserts retrieved glossary terms into prompts as explicit constraints.  
- **Evaluation Module (`evaluation.py`)** — Computes term adherence and generates CSV and HTML comparison reports.

---

## **Methodology**

1. Each English source segment is embedded and compared with glossary entries via cosine similarity.  
2. The **top-k (= 3)** glossary matches are retrieved and inserted into the translation prompt as “preferred terms.”  
3. Translations are generated for all three models, both **with** and **without retrieval**.  
4. Post-processing restores any protected tokens or HTML tags.  
5. Evaluation calculates:  
   - **Term Adherence:** proportion of glossary terms correctly used.  
   - **Latency:** average time to generate each translation.  

All outputs — including per-model CSVs and HTML side-by-side reports — are saved under the `/data` directory.

---

## **Results Summary (50 Segments)**

| **Model**     | **Term Accuracy (With Retrieval)** | **Term Accuracy (Without Retrieval)** | **Avg Latency (With Retrieval)** | **Avg Latency (Without Retrieval)** |
|----------------|------------------------------------|---------------------------------------|----------------------------------|-----------------------------------|
| GPT-4o-mini    | 0.91                               | 0.18                                  | 1.42 s                           | 1.19 s                            |
| Llama-3.3-70B  | 0.82                               | 0.09                                  | 1.97 s                           | 1.89 s                            |
| Llama-3.1-8B   | 1.00                               | 0.18                                  | 1.58 s                           | 2.03 s                            |

### **Key Insights**
- Glossary retrieval improves term accuracy by **70–80 percentage points** across all models.  
- **Llama-3.1-8B** achieved perfect adherence (1.00) while maintaining low latency.  
- **GPT-4o-mini** continues to lead in efficiency and balanced performance across languages.  
- Latency differences remain minimal, proving retrieval adds negligible computational overhead.

### Visual Comparisons

![Term Accuracy by Model and Language](../data/figures/term_accuracy_by_model_language_latest.png)

![Average Latency by Model and Language](../data/figures/latency_by_model_language_latest.png)

---

## **Qualitative Examples**

### **EN → FR**
**Source:** Enter your email address to continue.  
**With Retrieval:** Entrez votre adresse e-mail pour continuer.  
**Without Retrieval:** Entrez votre adresse e-mail pour continuer.  
→ Both preserve terminology; no degradation from retrieval.

### **EN → IT**
**Source:** Free shipping on orders over $50 at checkout.  
**With Retrieval:** Spedizione gratuita su ordini superiori a $50 alla cassa.  
**Without Retrieval:** Spedizione gratuita su ordini superiori a $50 al momento del checkout.  
→ Retrieval aligns better with retail-domain phrasing (“alla cassa”).

### **EN → JA**
**Source:** Enable two-factor authentication (2FA) in Settings.  
**With Retrieval:** 設定で二要素認証を有効にしてください。  
**Without Retrieval:** 設定で二要素認証 (2FA) を有効にします。  
→ Retrieval yields smoother phrasing and omits redundant annotation.

---

## **Discussion**

Retrieval significantly improves terminology adherence, confirming that even lightweight vector-based retrieval helps LLMs follow domain-specific terms more consistently. Improvements were especially strong for **commerce** and **technical UI** terminology.  

Latency increases were minor (typically ± 0.4 s), making this method practical for production workflows. Scaling from 30 to 50 segments enhanced reliability and produced consistent results across all three target languages.

---

## **Design Decisions and Limitations**

- **Retrieval Size (k = 3)** provides a balance between prompt length and relevance.  
- Current retrieval uses cosine similarity; future work could add **cross-encoder reranking**.  
- Term-adherence scoring is surface-form-based; semantic matching could improve robustness.  
- Cost for the complete experiment remained below **$5 USD**.

---

## **Conclusion**

This project demonstrates that **embedding-based glossary retrieval** significantly improves translation accuracy across multiple LLMs without retraining or fine-tuning. The pipeline is **lightweight**, **modular**, and **easily extensible** to new domains, languages, and model providers.  

---
