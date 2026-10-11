# ThermalGuard master project plan

## Project summary

ThermalGuard is an explainable machine learning project for predicting the permanent-magnet rotor temperature of an electric motor. It uses operating signals and thermal sensor readings from the Electric Motor Temperature dataset. The finished project includes the complete regression workflow, reproducible evaluation, a saved prediction pipeline, a Streamlit demonstration application, technical documentation, automated tests, and a submission report.

Slides and viva preparation are outside this repository because another team member is responsible for them.

## Problem statement

Electric motors can lose efficiency or suffer damage when internal components operate above safe temperatures. Direct rotor temperature measurement is not always practical in a deployed system. This project studies whether supervised regression can estimate rotor temperature from measurements that are easier to collect during operation.

The prediction target is `pm`, the permanent-magnet rotor temperature in degrees Celsius. The project compares a controller-signal feature set with an enhanced feature set that also includes stator temperature sensors.

## Objectives

1. Validate and preprocess the source dataset in a reproducible way.
2. Explore the data and document the main operating and thermal patterns.
3. Prevent leakage by separating complete measurement profiles between data partitions.
4. Compare a baseline, a linear model, and nonlinear tree-based models.
5. Select the model using validation data and report one final evaluation on untouched test profiles.
6. Explain model behavior through residual analysis, profile-level errors, and permutation importance.
7. Package the selected pipeline for consistent inference.
8. Provide a simple interface that accepts motor measurements and returns a temperature estimate.
9. Document the method, results, limitations, and reproduction steps in the repository and submission report.

## Scope

### Included

- Dataset validation and preprocessing
- Exploratory data analysis
- Derived electrical and thermal features
- Group-aware train, validation, and test partitions
- Regression model comparison
- Hyperparameter selection on validation profiles
- Final test evaluation
- Error analysis and model explanation
- Saved model artifact
- Streamlit application
- Automated tests
- README, architecture notes, model card, and submission report

### Excluded

- Presentation slides
- Viva preparation
- Hardware deployment
- Real-time motor control
- Safety certification
- Claims that the model can replace a physical protection system

## Dataset and prediction contract

The source file is `data/raw/measures_v2.csv`.

- Rows: 1,330,816
- Source columns: 13
- Measurement profiles: 69
- Target: `pm`
- Grouping field: `profile_id`
- Missing, infinite, and duplicate required rows found during validation: none
- Observed target range: 20.86°C to 113.61°C

`profile_id` identifies a measurement session. It is used only for splitting and diagnostics and is never provided to a model as an input.

## Delivery sections and status

| Section | Work | Status | Evidence |
|---|---|---|---|
| 1 | Repository structure, scope, and data contract | Complete | Package layout, README, and project documentation |
| 2 | Data loading, validation, and preprocessing | Complete | Reusable data functions and dataset analysis outputs |
| 3 | Exploratory analysis | Complete | Dataset summary, generated figures, and documented observations |
| 4 | Model training and comparison | Complete | Baseline, Ridge, Histogram Gradient Boosting, and XGBoost validation results |
| 5 | Final evaluation and explanation | Complete | Test metrics, profile errors, residual diagnostics, and permutation importance |
| 6 | Prediction artifact and Streamlit application | Complete | Serialized pipeline, input contract, application, and tests |
| 7 | Clean-environment verification | Complete | Python 3.14 isolated install, focused tests, lint, and application smoke check verified on 11 October 2026 |
| 8 | Submission report | Complete | Executed notebook, report source, formatted Word report, and repository indexes verified on 11 October 2026 |

The numbered sections are reviewed one at a time. Work moves to the next section after the current section has been demonstrated and approved.

## Rubric coverage

| Rubric area | Project evidence |
|---|---|
| Problem understanding and objective clarity | Defined engineering problem, target, users, assumptions, and safety boundary |
| Data collection and preprocessing | Dataset provenance, schema checks, derived features, and profile-aware splitting |
| Model development and implementation | Four model families, two feature sets, reusable pipelines, and saved artifact |
| Performance evaluation and interpretation | MAE, RMSE, R², tolerance accuracy, bias, profile analysis, and feature importance |
| Innovation and creativity | Comparison of controller-only and enhanced sensing, group-aware validation, engineering error analysis, and deployable demonstration |

## Final results currently recorded

The enhanced Histogram Gradient Boosting model was selected using validation MAE. After selection, it was refitted on the combined training and validation profiles and evaluated once on 14 untouched test profiles.

| Metric | Final test result |
|---|---:|
| MAE | 5.60°C |
| RMSE | 7.36°C |
| R² | 0.856 |
| Predictions within ±5°C | 54.4% |
| Mean bias | -0.34°C |

## Completion criteria

The project is ready for submission when all of the following are true:

- A fresh environment can install the documented dependencies without installing another Python version solely to match a version number.
- The automated tests pass.
- The dataset analysis and training commands reproduce the recorded output files.
- The Streamlit application starts and predicts using the saved artifact.
- The report uses the generated results and does not contain unsupported figures.
- The README describes setup, reproduction, application use, limitations, and repository structure.
- The working tree and remote repository contain the intended final files.

## Main risks and controls

| Risk | Control |
|---|---|
| Measurements from one session leak across partitions | Split complete `profile_id` groups, not individual rows |
| Final test data influences model choice | Select with validation MAE and evaluate the test set once |
| Preprocessing differs between training and inference | Serialize and load the complete fitted pipeline |
| High average accuracy hides weak driving cycles | Report per-profile errors, bias, and worst profiles |
| Feature importance is interpreted as causation | Describe permutation importance as predictive influence only |
| Users treat the demonstration as a safety system | State that it is a course project and not a certified controller |

## Remaining handoff

All eight implementation sections are complete. The repository now contains the working model, application, generated evidence, executed notebook, and final submission report. No slide or viva work is planned in this repository.
