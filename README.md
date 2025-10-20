# NLP Red-Teaming Prototype

A comprehensive tool for red-teaming NLP models with automated attack generation, execution, scoring, and visualization.

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Setup](#setup)
- [Usage](#usage)
- [Quick Start Pipeline](#quick-start-pipeline)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)

## Overview

This project provides a complete pipeline for testing NLP models against various adversarial attacks:

1. **Attack Generation** - Generate diverse attack test cases
2. **Runner** - Execute attacks against target models
3. **Scorer** - Evaluate and score results
4. **UI** - Visualize results through an interactive Streamlit dashboard

## Prerequisites

- Python 3.7+
- pip (Python package installer)

## Setup

### 1. Create Virtual Environment

**Windows (PowerShell - recommended):**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

> **Note:** If PowerShell blocks script execution, run this one-time command:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
> ```

**macOS / Linux:**

```bash
python -m venv .venv
source .venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

## Usage

> **Important:** Run all commands from the project root directory (the folder containing `attacks/`, `models/`, `runner/`, `eval/`, `ui/`, `data/`).

### Step 1: Generate Attack Cases

```bash
python -m attacks.generator
```

This creates `data/sample_attack_cases.json` with generated test cases.

### Step 2: Run Attacks Against Model

```bash
python -m runner.cli --model=mock --attacks-file=data/sample_attack_cases.json --workers=4
```

This produces `data/results.jsonl` with model responses.

**For debugging (single worker):**

```bash
python -m runner.cli --model=mock --attacks-file=data/sample_attack_cases.json --workers=1
```

### Step 3: Score Results

```bash
python -m eval.scorer --results=data/results.jsonl --out=data/score_report.json
```

This generates `data/score_report.json` with scored results.

### Step 4: Launch UI Dashboard

Open a new terminal/tab and run:

```bash
# Activate virtual environment first
.\.venv\Scripts\Activate.ps1  # Windows
# source .venv/bin/activate    # macOS/Linux

# Start Streamlit
streamlit run ui/app.py
```

The UI will be available at `http://localhost:8501`.

## Quick Start Pipeline

Run the complete pipeline in one go:

```bash
python -m attacks.generator
python -m runner.cli --model=mock --attacks-file=data/sample_attack_cases.json --workers=4
python -m eval.scorer --results=data/results.jsonl --out=data/score_report.json
```

Then launch the UI in a separate terminal to view results.

## Testing

Run the test suite from the project root:

```bash
python -m pytest -q
```

**If you encounter import errors:**

```powershell
# PowerShell
$env:PYTHONPATH = (Get-Location).Path
python -m pytest -q
```

```bash
# macOS/Linux
export PYTHONPATH=$(pwd)
python -m pytest -q
```

## Troubleshooting

### Common Issues

**ModuleNotFoundError when running scripts:**
- Always use the `-m` module form from project root
- Example: `python -m attacks.generator` instead of `python attacks/generator.py`

**Virtual environment activation blocked (Windows):**
- Run: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force`

**StreamlitDuplicateElementId error:**
- Pull the latest `ui/app.py` (uses unique keys) and restart Streamlit

**Missing experimental_rerun in Streamlit:**
- The UI will display instructions to manually refresh the browser

### Output Files

The pipeline generates these files in the `data/` directory:

| File | Description |
|------|-------------|
| `results.jsonl` | Newline-delimited JSON with model responses |
| `score_report.json` | Scored results in JSON array format |
| `model_calls.log` | Append-only log of all model calls |
| `sample_attack_cases.json` | Generated attack test cases |

### Useful Commands (PowerShell)

**View last 40 lines of results:**

```powershell
Get-Content data\results.jsonl -Tail 40
```

**Pretty-print score report:**

```powershell
Get-Content data\score_report.json | Out-String | ConvertFrom-Json
```

**Open files in VS Code:**

```powershell
code data\results.jsonl data\score_report.json data\sample_attack_cases.json
```

## Project Structure

```
RedTeam/
├── attacks/        # Attack generation logic
├── models/         # Model implementations
├── runner/         # Attack execution engine
├── eval/           # Scoring and evaluation
├── ui/             # Streamlit dashboard
├── data/           # Generated data and results
└── tests/          # Test suite
```
