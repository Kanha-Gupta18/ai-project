# Verification record

Date: 11 October 2026

## Purpose

This record documents the clean-environment and portability checks completed for Section 7 of the implementation plan.

## Environment

- Operating system: Windows
- Python: 3.14.3
- Environment: project-local `.venv`
- scikit-learn: 1.8.0
- Streamlit: 1.54.0
- Additional Python versions installed: none

The isolated environment was created from the Python installation already present on the machine. The package and development dependencies were installed from `pyproject.toml`.

## Checks and results

| Check | Result |
|---|---|
| Import local `thermalguard` package | Pass |
| Import scikit-learn, Streamlit, and XGBoost | Pass |
| Initial repository test run | 18 passed in the existing environment |
| Initial isolated test run | 17 passed, 1 failed because the moved repository left a stale relative app path |
| Corrected Streamlit smoke test | 1 passed |
| Focused artifact and feature tests in `.venv` | 2 passed |
| Final complete test suite in `.venv` | 18 passed in 10.52 seconds |
| Dependency integrity check | Pass |
| Dataset analysis regeneration | Pass |
| Complete model training and evaluation | Pass |
| Rebuilt artifact prediction | Pass, 59.52°C for median inputs |
| Metric comparison with the previous run | Exact match for selected model and all final test metrics |
| Lint on all Section 7 code changes | Pass |
| Final full-project lint | Pass |
| Git whitespace validation | Pass |

## Issue found and corrected

`tests/test_streamlit_app.py` opened `app.py` with a relative path. Streamlit resolves that path from the test caller, and cached bytecode still referred to the repository's previous location after the folder was moved.

The test now derives the repository root from `Path(__file__).resolve()` and passes an absolute path to Streamlit. The artifact existence check uses the same repository root. This makes the smoke test independent of the current working directory and the folder's previous location.

The review also removed one unused import and corrected two import-order findings reported by Ruff. These edits do not change model behavior.

A later clean install initially resolved scikit-learn 1.9.1 and Streamlit 1.65.0 because the dependency limits were too broad. The Streamlit smoke test stalled in that environment. The project now constrains scikit-learn to the tested 1.8 release series and Streamlit to the tested 1.54 release series. After installing those versions, dependency checks, all 18 tests, and the full lint suite passed.

The analysis and training scripts were then run against all 1,330,816 rows. They selected `enhanced__hist_gradient_boosting` again and reproduced every final test metric exactly. The rebuilt artifact also passed the application and direct prediction checks.

## Reproduction commands

```powershell
.venv\Scripts\python.exe -m pytest
.venv\Scripts\python.exe -m ruff check .
$env:PYTHONPATH = "src"
.venv\Scripts\python.exe scripts/analyze_dataset.py
.venv\Scripts\python.exe scripts/train_models.py
.venv\Scripts\python.exe -m streamlit run app.py
```

The rebuilt metrics, tables, figures, and model artifact are the reference outputs for the notebook and presentation.
