# NLP Red-Teaming Prototype

# NOTE: Run these commands from the project root (folder that contains attacks/, models/, runner/, eval/, ui/, data/).

# -----------------------
# 1 Create & activate venv
# -----------------------
# PowerShell (Windows - recommended):
python -m venv .venv
# If PowerShell blocks scripts one-time (run as current user):
# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
.\.venv\Scripts\Activate.ps1

# macOS / Linux (bash):
# python -m venv .venv
# source .venv/bin/activate

# -----------------------
# 2 Install dependencies
# -----------------------
pip install -r requirements.txt

# -----------------------
# 3 Generate attacks (use -m to preserve package imports)
# -----------------------
python -m attacks.generator
# This writes data/sample_attack_cases.json

# -----------------------
# 4 Run runner (mock model) — produces data/results.jsonl
# -----------------------
python -m runner.cli --model=mock --attacks-file=data/sample_attack_cases.json --workers=4

# If debugging, run single worker:
# python -m runner.cli --model=mock --attacks-file=data/sample_attack_cases.json --workers=1

# -----------------------
# 5 Score results — produces data/score_report.json
# -----------------------
python -m eval.scorer --results=data/results.jsonl --out=data/score_report.json

# -----------------------
# 6 Start UI (open in a new terminal/tab so Streamlit stays live)
# -----------------------
# Activate venv in that shell if not already active:
# Windows (PowerShell)
.\.venv\Scripts\Activate.ps1
streamlit run ui/app.py
# Open the Local URL shown (usually http://localhost:8501)

# -----------------------
# 7 One-shot (generator → runner → scorer)
# -----------------------
python -m attacks.generator
python -m runner.cli --model=mock --attacks-file=data/sample_attack_cases.json --workers=4
python -m eval.scorer --results=data/results.jsonl --out=data/score_report.json

# -----------------------
# 8 Run tests
# -----------------------
# From project root (venv active)
python -m pytest -q
# If pytest has import errors, set PYTHONPATH for the invocation (PowerShell):
$env:PYTHONPATH = (Get-Location).Path
python -m pytest -q

# -----------------------
# 9 Quick inspection commands (PowerShell)
# -----------------------
# Tail results (last 40 lines)
Get-Content data\results.jsonl -Tail 40

# Pretty-print score report
Get-Content data\score_report.json | Out-String | ConvertFrom-Json

# Open files in VSCode (if installed)
code data\results.jsonl data\score_report.json data\sample_attack_cases.json

# -----------------------
# 10 Common troubleshooting notes (copy as-needed)
# -----------------------
# - If you see ModuleNotFoundError when running python attacks/generator.py etc:
#   Use the -m form from project root: python -m attacks.generator
# - If .venv activation blocked: run Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force (PowerShell)
# - If Streamlit throws StreamlitDuplicateElementId: pull latest ui/app.py (uses unique keys) and restart Streamlit.
# - If Streamlit lacks experimental_rerun: UI will show instructions to refresh browser manually.
# - Files produced by pipeline:
#     data/results.jsonl        # newline-delimited JSON per model call
#     data/score_report.json    # scored results (JSON array)
#     data/model_calls.log      # append-only model call log
# -------------------------------------------------------------------------------
# End of quick start block — run steps in order (use separate terminal for Streamlit UI).
