# AIBLE on macOS — Build & Install Guide

This guide covers two audiences:

- **Builder** (you, on a Mac): turn the source into a distributable package.
- **End user** (your colleague): install and run that package.

> **Why a Mac is required to build:** the sidecar is frozen into a native
> binary with PyInstaller, which **cannot cross-compile**. The Windows package
> (`dist/AIBLE-Setup.zip`) will not run on macOS. You must run the build step
> below **on a Mac** to produce a Mac binary. Everything needed is in
> `packaging-mac/`.

---

## Part A — Build the package (on a Mac)

### Prerequisites
- macOS 12+ (Apple Silicon or Intel).
- **Python 3.10+**: `python3 --version` (install via [python.org](https://www.python.org/downloads/) or `brew install python`).
- **Xcode Command Line Tools**: `xcode-select --install` (for `hdiutil`, `codesign`).
- The project folder (copy it to the Mac, or `git clone`).

### One command
```bash
cd /path/to/AIBLE
bash packaging-mac/build_installer_mac.sh
```

This will:
1. Create a venv and install deps + PyInstaller.
2. Build `sidecar/rules.json` if missing (from `style-guide.pdf`, or an empty set — the curated seed rules still apply).
3. Freeze the sidecar to `dist/AIBLE-Sidecar/` (no Python needed by users).
4. Stage the payload and produce:
   - `dist/AIBLE-Setup-mac.zip`
   - `dist/AIBLE-Setup-mac.dmg`

Hand either artifact to colleagues. The `.dmg` is the nicer experience.

### (Recommended) Sign & notarize
Unsigned builds trigger Gatekeeper warnings. With an Apple Developer ID:
```bash
codesign --deep --force --options runtime \
  --sign "Developer ID Application: NAME (TEAMID)" \
  dist/AIBLE-Sidecar/AIBLE-Sidecar
# rebuild the dmg after signing, then:
xcrun notarytool submit dist/AIBLE-Setup-mac.dmg \
  --apple-id <id> --team-id <TEAMID> --password <app-specific-pw> --wait
xcrun stapler staple dist/AIBLE-Setup-mac.dmg
```
Without this, users just right-click → **Open** once (see below).

---

## Part B — Install (end user, on a Mac)

1. Open `AIBLE-Setup-mac.dmg` (or unzip `AIBLE-Setup-mac.zip`).
2. Double-click **`install.command`**.
   - If macOS blocks it: **right-click → Open → Open**.
   - Or in Terminal: `chmod +x install.command && ./install.command`
3. Launch **AIBLE** from `~/Applications` (or Launchpad).
4. Pick **Open Demo** — the recommended path. Your browser opens the app.

The installer copies to `~/Applications/AIBLE`, creates `~/Applications/AIBLE.app`,
and clears the Gatekeeper quarantine flag on the copied files. **No admin rights needed.**

### Gatekeeper ("unidentified developer")
If the app or scripts are blocked:
- Right-click → **Open** → **Open**, or
- `xattr -dr com.apple.quarantine ~/Applications/AIBLE`

### Optional: AI rephrase
The core style check is instant and needs **no model**. The optional
"AI rephrase" button uses a local model via Ollama:
```bash
./install.command --with-ai
```
Installs Ollama (via Homebrew if present) and pulls a ~2 GB model. On Apple
Silicon this runs on the GPU and is much faster than the CPU latency seen on
typical Windows laptops.

---

## What runs where (privacy)

```
Browser ──► 127.0.0.1:8765  (AIBLE sidecar — frozen binary)
                 ├── deterministic rule engine (instant, no model)
                 └── optional: 127.0.0.1:11434 (Ollama) for AI rephrase
```
The sidecar binds to loopback only. No document text leaves the Mac. Feedback
is stored locally in `AIBLE-Sidecar/data`.

---

## Word add-in (same limitation as Windows)

Word for Mac honors the same admin-managed Microsoft 365 policy that blocks
manual add-in sideloading. The packaged launcher's **Word add-in** option
explains this and reveals the bundled `manifest.xml`. To enable it, your IT
admin must publish that manifest via **Microsoft 365 admin center → Settings →
Integrated apps → Upload custom apps** (Centralized Deployment). No installer
can bypass tenant policy. Until then, use the browser demo.

---

## No-build fallback (run from source)

If you can't build a binary, run the sidecar directly (needs Python on the Mac):
```bash
cd /path/to/AIBLE
python3 -m venv .venv && source .venv/bin/activate
pip install -e .
python -m sidecar.main        # then open http://127.0.0.1:8765/
```
See `RUN_MAC.md` for the full from-source workflow.

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| `bad interpreter: /bin/bash^M` | Script has Windows line endings: `perl -i -pe 's/\r$//' *.command *.sh` |
| `"AIBLE-Sidecar" cannot be opened` | `xattr -dr com.apple.quarantine ~/Applications/AIBLE` |
| `install.command` won't run on double-click | Right-click → Open, or `chmod +x install.command` |
| Demo page unreachable | The sidecar didn't start — check `/tmp/aible-sidecar.log` |
| AI rephrase fails | Ensure Ollama is running: `ollama serve`, model pulled: `ollama pull llama3.2:3b` |
| PyInstaller build fails on `pymupdf` | Use Python 3.12: `brew install python@3.12 && python3.12 -m venv .venv` |
| `hdiutil`/`codesign` not found | `xcode-select --install` |
