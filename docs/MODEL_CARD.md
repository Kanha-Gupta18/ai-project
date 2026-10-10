# ThermalGuard model card

## Intended use

ThermalGuard estimates permanent-magnet rotor temperature from a single row of motor measurements. It is an educational prototype for the AI for Engineers course. The model is intended for demonstrating regression, grouped evaluation, error analysis, and explainability.

It is not a certified thermal protection system. Do not use its output as the sole basis for shutdown, maintenance, or safety decisions.

## Model

- Algorithm: `HistGradientBoostingRegressor`
- Target: permanent-magnet temperature `pm`, in degrees Celsius
- Training data: Electric Motor Temperature dataset
- Development profiles: 55
- Final test profiles: 14
- Random seeds: 42 for the final test split and 43 for the validation split

The model uses eight electrical, mechanical, and environmental measurements, three stator thermocouple readings, and three derived features. `profile_id` is used only for splitting and is never passed to the model.

## Test performance

- MAE: 5.60°C
- RMSE: 7.36°C
- R²: 0.856
- Within ±5°C: 54.4%
- Mean bias: -0.34°C

Performance varies across operating profiles. The worst held-out profile has an MAE of 8.90°C. A low overall bias does not mean individual predictions are unbiased.

## Artifact contract

`models/thermalguard_model.joblib` contains the fitted estimator, ordered feature names, target name, artifact version, and final test metrics. The loader rejects artifacts with an unsupported version or incompatible feature list.

The artifact is generated locally and excluded from Git. Run `python scripts/train_models.py` after adding the dataset to reproduce it.

## Known limitations

- The dataset comes from one test-bench motor, so the results do not establish performance on other motor designs.
- The estimator uses concurrent stator temperatures and does not model the motor's thermal history.
- Errors differ by operating profile, especially during some driving cycles.
- Permutation importance describes predictive dependence, not physical causality.
- Inputs outside the training ranges are not validated yet.
