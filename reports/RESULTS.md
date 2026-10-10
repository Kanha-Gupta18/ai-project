# Experiment results

## Evaluation design

All partitions are separated by `profile_id`, so one operating session cannot appear in more than one partition. The 69 profiles are divided into 44 training profiles, 11 validation profiles, and 14 final test profiles.

The training set fits each candidate. Validation MAE selects the model and feature set. The selected model is then refitted on the combined 55-profile development set and evaluated once on the untouched test profiles.

## Dataset checks

- 1,330,816 rows and 13 source columns
- 69 measurement profiles
- No missing, infinite, or duplicate rows
- Rotor temperature range: 20.86°C to 113.61°C
- Median profile length: 17,142 measurements

## Validation comparison

| Feature set | Model | MAE (°C) | RMSE (°C) | R² | Within ±5°C |
|---|---|---:|---:|---:|---:|
| Controller signals | Mean baseline | 15.68 | 19.19 | -0.013 | 19.9% |
| Controller signals | Ridge | 10.46 | 13.03 | 0.533 | 28.7% |
| Controller signals | Histogram gradient boosting | 7.75 | 9.95 | 0.727 | 39.7% |
| Controller signals | XGBoost | 8.11 | 10.57 | 0.692 | 39.5% |
| Enhanced sensors | Mean baseline | 15.68 | 19.19 | -0.013 | 19.9% |
| Enhanced sensors | Ridge | 5.85 | 7.10 | 0.861 | 46.6% |
| Enhanced sensors | **Histogram gradient boosting** | **4.61** | **6.11** | **0.897** | **65.0%** |
| Enhanced sensors | XGBoost | 4.81 | 6.42 | 0.887 | 65.2% |

The controller set contains ambient and coolant temperatures, speed, torque, d-q voltage, d-q current, and three derived features. The enhanced set adds the stator-yoke, stator-tooth, and stator-winding thermocouple readings.

## Final test results

| Metric | Result |
|---|---:|
| MAE | 5.60°C |
| RMSE | 7.36°C |
| R² | 0.856 |
| Predictions within ±5°C | 54.4% |
| Mean bias | -0.34°C |

These final figures are less favorable than the validation figures, which is expected when operating conditions differ between profiles. Profile 45 has the largest MAE at 8.90°C. Profile 11 has a positive bias of 5.42°C and a negative R², which shows that performance is not consistent across every driving cycle.

## Feature influence

Permutation importance measures the increase in MAE after shuffling one feature in a 20,000-row test sample. Stator-tooth temperature has the largest measured effect, followed by stator-yoke and stator-winding temperature. This supports the enhanced sensor set, but correlated thermal sensors can share or redistribute importance, so the ranking is not a causal claim.

| Feature | MAE increase after permutation |
|---|---:|
| Stator tooth temperature | 13.25°C |
| Stator yoke temperature | 7.22°C |
| Stator winding temperature | 2.30°C |
| Coolant and ambient difference | 1.93°C |
| Ambient temperature | 1.46°C |

## Interpretation and limits

The residual plot contains profile-specific bands rather than a uniform cloud. The static model does not explicitly represent thermal history, even though rotor temperature changes gradually over time. It is suitable for a course demonstration and comparative experiment, but it should not control a motor or replace a certified protection system.

## Reproduce

```powershell
$env:PYTHONPATH = "src"
python scripts/analyze_dataset.py
python scripts/train_models.py
```

The commands regenerate the metrics, per-profile table, permutation importance table, diagnostic figure, and serialized model artifact.
