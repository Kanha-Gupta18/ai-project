# Baseline experiment results

These results were produced from all 1,330,816 measurements in `measures_v2.csv`. Complete operating profiles were assigned to either training or testing with `GroupShuffleSplit`, using a fixed random seed of 42. The resulting test set contains profiles that none of the models saw during training.

## Dataset checks

- 1,330,816 rows and 13 source columns
- 69 measurement profiles
- No missing, infinite, or duplicate rows
- Rotor temperature range: 20.86°C to 113.61°C
- Median profile length: 17,142 measurements

## Model comparison

| Feature set | Model | MAE (°C) | RMSE (°C) | R² | Within ±5°C | Fit time |
|---|---|---:|---:|---:|---:|---:|
| Controller signals | Mean baseline | 16.43 | 19.42 | -0.005 | 16.6% | 0.02 s |
| Controller signals | Ridge | 8.63 | 11.17 | 0.668 | 37.6% | 0.34 s |
| Controller signals | Histogram gradient boosting | 9.33 | 11.97 | 0.618 | 36.1% | 7.93 s |
| Controller signals | XGBoost | 9.76 | 12.62 | 0.576 | 35.0% | 18.73 s |
| Enhanced sensors | Mean baseline | 16.43 | 19.42 | -0.005 | 16.6% | 0.01 s |
| Enhanced sensors | **Ridge** | **4.96** | **6.41** | **0.890** | **61.0%** | **0.38 s** |
| Enhanced sensors | Histogram gradient boosting | 5.60 | 7.36 | 0.856 | 54.4% | 6.77 s |
| Enhanced sensors | XGBoost | 5.93 | 7.90 | 0.834 | 53.9% | 20.07 s |

The controller feature set uses ambient and coolant temperature, motor speed, torque, d-q voltage, d-q current, and three derived features. The enhanced set adds stator-yoke, stator-tooth, and stator-winding thermocouple readings.

## Decision

Enhanced Ridge is the selected baseline. It produced the lowest error on unseen operating sessions, trained in under one second, and is easier to explain than either tree ensemble. Adding stator temperatures reduced MAE by 3.66°C compared with the controller-only Ridge model. This sensor ablation gives a concrete engineering justification for using the stator thermocouples.

The selected model still has an RMSE of 6.41°C, so it should be treated as an estimator rather than a safety cutoff. Later evaluation will inspect profile-level errors, residual patterns, and feature contributions before the interface is finalized.

## Reproduce

```powershell
$env:PYTHONPATH = "src"
python scripts/analyze_dataset.py
python scripts/train_models.py
```

Generated figures, metrics, and the serialized model are kept out of Git and can be reproduced using these commands.
