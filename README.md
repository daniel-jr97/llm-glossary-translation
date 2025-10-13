# LLM-Only Translation with Glossary Retrieval

This project builds an LLM-only translation pipeline with glossary embedding/retrieval and compares translations **with** vs **without** retrieval.

## What this repo contains
- `src/` retrieval, prompting, and evaluation helpers
- `notebooks/pipeline.ipynb` end-to-end notebook
- `data/glossary.csv` sample glossary (edit/expand)
- `data/samples_en.csv` sample English source segments (edit/expand)

## Quick start
1. Python 3.10+ and VS Code installed
2. Create venv and install libs:
   ```bash
   python -m venv .venv
   # Windows PowerShell (session only):
   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
