# Running AIBLE on macOS

Same project as the Windows version — only the shell, install commands, and a few paths differ. Architecture, endpoints, and containment guarantees are identical.

## Prerequisites

```bash
# Homebrew (skip if installed): https://brew.sh
brew install python@3.12 node tesseract
brew install ollama
brew services start ollama   # runs as a background service on 127.0.0.1:11434
ollama pull llama3.1:8b      # ~5 GB, one time
```

## One-time project setup

```bash
cd /path/to/AIBLE

# Python deps
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e .

# Build rules artifact from your tech-writers PDF
python -m rule_parser.parse_rules path/to/style-guide.pdf --out sidecar/

# Word add-in deps (only if you'll use the Word add-in)
cd word-addin && npm install && cd ..
```

## Run the web demo (recommended)

```bash
source .venv/bin/activate     # if not already active
python -m sidecar.main        # leave this terminal open
# In a second terminal:
open http://127.0.0.1:8765/
```

Stop the sidecar with `Ctrl+C`. Use `Insert sample` → `Analyze` in the browser to see the whole-doc spell-check view.

## Run the Word add-in (only if Word for Mac is licensed and unmanaged)

```bash
# In a separate terminal, with the sidecar already running:
cd word-addin
npm start                     # sideloads + launches Word for Mac
npm stop                      # to clean up
```

If your Mac is admin-managed by IT, expect the same Office add-in policy block as Windows — Word for Mac honors tenant-wide M365 add-in policies. The web demo is the unblocked path.

## Daily start / stop

```bash
# Start
brew services start ollama
source /path/to/AIBLE/.venv/bin/activate
python -m sidecar.main &
open http://127.0.0.1:8765/

# Stop
pkill -f "sidecar.main"
brew services stop ollama     # optional, frees memory
```

## Diagnostics

```bash
# Bindings (everything should be 127.0.0.1 / ::1):
lsof -i -P -n | grep -E ':(8765|11434|3000) '

# Health
curl http://127.0.0.1:8765/health

# Smoke-test rewrite
curl -X POST http://127.0.0.1:8765/rewrite \
     -H "Content-Type: application/json" \
     -d '{"text":"We will utilize the disk to facilitate file storage."}'

# Admin endpoints (token in sidecar/.admin-token)
TOK=$(cat sidecar/.admin-token)
curl -H "Authorization: Bearer $TOK" http://127.0.0.1:8765/feedback
curl -X POST -H "Authorization: Bearer $TOK" http://127.0.0.1:8765/admin/learn
```

## Differences from the Windows guide

| Concern | Windows | macOS |
|---|---|---|
| venv activate | `.\.venv\Scripts\Activate.ps1` | `source .venv/bin/activate` |
| Open browser | `Start-Process http://...` | `open http://...` |
| Open file | `Invoke-Item file.docx` | `open file.docx` |
| Kill process | `taskkill /F /IM ...` | `pkill -f ...` |
| Tesseract install | Windows installer + PATH edit | `brew install tesseract` |
| Ollama service | Installed via .exe, runs at login | `brew services start ollama` |
| Path separator | `\` | `/` |

## Common issues

- **`pip install -e .` fails on a build wheel for `pymupdf`** — try Python 3.12 specifically (`python3.12 -m venv .venv`); 3.13/3.14 wheels lag on release.
- **`ollama pull` fails with `pull model manifest: file does not exist`** — the tag is `llama3.1:8b`, not `llama3.1:8b-instruct`.
- **Sidecar won't start with `RuntimeError: refuses non-loopback URL`** — unset any `AIBLE_OLLAMA_URL` env var that points off-machine.
- **Tesseract not found at runtime** — `brew install tesseract`, or set `TESSERACT_CMD=$(which tesseract)` before starting the sidecar.
- **Mixed-content errors in the demo** — only relevant if you reverse-proxy the demo behind HTTPS; same-origin loopback HTTP is fine.
