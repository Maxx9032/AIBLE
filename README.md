# AIBLE — Local Rule-Compliant Rewriter for Word

A Microsoft Word add-in that rewrites selected sentences against rules extracted from a tech-writers' PDF. **Nothing leaves your machine.** 

## Architecture

```
Word doc ── Office.js task pane ──HTTP──> 127.0.0.1:8765 (FastAPI sidecar)
                                                ├── rules.json        (built once from your PDF)
                                                ├── Tesseract         (OCR for image selections)
                                                └── Ollama @ 127.0.0.1:11434  (local LLM)
```

Three pieces:

1. `rule_parser/` — one-time CLI that turns a tech-writers PDF into `rules.json` and a human-readable `rules-memo.md`.
2. `sidecar/` — long-running local FastAPI service that does rule matching, OCR, and LLM calls.
3. `word-addin/` — Office.js task pane: reads selection, calls the sidecar, shows a 3-option dropdown.

## Prerequisites

- **Python 3.10+**
- **Node 18+** (for the Word add-in dev server)
- **Ollama** — install from https://ollama.com and pull a model: `ollama pull llama3.1:8b`
- **Tesseract** (for OCR) — Windows installer: https://github.com/UB-Mannheim/tesseract/wiki. Add the install dir to `PATH`.
- **Microsoft Word** (M365 desktop) for sideloading the add-in.

## Setup

```powershell
# 1. Python deps
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .

# 2. Build rules from your PDF
python -m rule_parser.parse_rules path\to\tech-writers.pdf --out sidecar\

# 3. Start Ollama (in a separate terminal)
ollama serve

# 4. Start the sidecar (in a separate terminal)
python -m sidecar.main

# 5. Sideload the Word add-in (in a separate terminal)
cd word-addin
npm install
npm start
```

## Endpoints (sidecar)

- `GET  /health` — readiness probe.
- `POST /rewrite` — body `{"text": "..."}` → `{"original", "options": [{"text","rule_ids","confidence"}], "explanation"}` (exactly 3 options, ≤60 words each).
- `POST /ocr` — body `{"image_b64": "..."}` → `{"text": "..."}`.

## Data containment

- Sidecar binds **only** to `127.0.0.1:8765`. External connections are refused.
- Input text is never written to disk and never logged (only counts and timings are logged).
- Add-in manifest declares only `https://localhost:*` and `http://127.0.0.1:8765` as allowed hosts.
- Verify: `netstat -an | findstr 8765` should only show `127.0.0.1`.

## Configuration

Environment variables (all optional):

| Var | Default | Purpose |
|---|---|---|
| `AIBLE_OLLAMA_URL` | `http://127.0.0.1:11434` | Ollama endpoint (must be loopback). |
| `AIBLE_OLLAMA_MODEL` | `llama3.1:8b` | Model tag passed to Ollama. |
| `AIBLE_RULES_PATH` | `sidecar/rules.json` | Rules artifact path. |
| `AIBLE_PORT` | `8765` | Sidecar port. |
| `TESSERACT_CMD` | (PATH lookup) | Override Tesseract binary path. |

## Verification

End-to-end smoke test, fully offline:

```powershell
# Health
curl http://127.0.0.1:8765/health

# Rewrite
curl -X POST http://127.0.0.1:8765/rewrite -H "Content-Type: application/json" `
     -d '{"text":"Our team will try to get the report done by EOD if possible."}'
```

Expect three rewrites, each ≤60 words, with `rule_ids` populated.
