# ThermalGuard Electric Motor Rotor Temperature Prediction

AI for Engineers Project Submission Report

11 October 2026

Submitted by

Kanha Gupta  1025220005

Nilesh Kumar  1025220011

Aaditya Agarwal  1025220010

Batch 2V11

Submitted to

Dr. Arun Singh Pundir

Thapar Institute of Engineering and Technology

## Abstract

Permanent-magnet synchronous motors can lose efficiency or suffer thermal damage when internal components become too hot. Rotor temperature is difficult to measure directly in a working motor, so this project studies whether machine learning can estimate it from operating signals and nearby temperature sensors. ThermalGuard uses the Electric Motor Temperature dataset recorded on a test bench at Paderborn University. The dataset contains 1,330,816 measurements from 69 operating profiles.

The work compares two sensor configurations and four regression methods. Complete operating profiles are kept together when creating the training, validation, and test sets. This prevents neighbouring measurements from one session appearing on both sides of an evaluation. Validation mean absolute error selects the final model, while 14 profiles remain untouched until the final test. The selected enhanced Histogram Gradient Boosting model achieves a mean absolute error of 5.60°C, a root mean squared error of 7.36°C, and an R² of 0.856 on the final test profiles. It places 54.4 percent of predictions within 5°C of the measured rotor temperature.

Permutation importance and profile-level error analysis make the result easier to interpret. Stator tooth and stator yoke temperatures have the strongest measured predictive influence. Performance still varies across operating profiles because the static model does not explicitly represent thermal history. The repository includes reusable code, automated tests, generated evidence, a saved prediction pipeline, and a Streamlit demonstration application. ThermalGuard is an educational prototype and not a certified protection or motor-control system.

## 1 Problem statement

Electric motors convert electrical energy into mechanical motion, but part of that energy becomes heat. Excess temperature can accelerate insulation ageing, reduce efficiency, alter magnetic properties, and shorten component life. A permanent magnet is located inside the rotor, where direct temperature measurement is inconvenient in many operating systems. A software estimator can use signals that are already available to a motor controller and temperature measurements from easier locations.

The engineering question is:

Can a supervised regression model estimate permanent-magnet rotor temperature from electrical, mechanical, environmental, and stator temperature measurements while remaining reproducible and understandable?

The prediction target is `pm`, measured in degrees Celsius. Each row represents a measurement sampled during an operating profile. The identifier `profile_id` marks a complete session and is used only for data partitioning and diagnostics. It is never given to a model as an input.

## 2 Objectives

The project has six practical objectives:

1. Validate the source dataset and document its structure.
2. Compare a controller-signal configuration with an enhanced configuration that includes stator temperatures.
3. Prevent session leakage by assigning complete profiles to data partitions.
4. Compare simple and nonlinear regression methods using the same evaluation protocol.
5. Explain the selected model through error analysis and permutation importance.
6. Package the trained pipeline in a tested Streamlit application.

Slides and viva preparation are outside the repository scope.

## 3 Dataset

The Electric Motor Temperature dataset was published on Kaggle by Wilhelm Kirchgässner and collaborators [1]. Its measurements were collected by the LEA department at Paderborn University on a permanent-magnet synchronous motor test bench. The project uses `measures_v2.csv`.

| Property | Recorded value |
|---|---:|
| Rows | 1,330,816 |
| Source columns | 13 |
| Operating profiles | 69 |
| Missing required values | 0 |
| Infinite required values | 0 |
| Duplicate rows | 0 |
| Minimum rotor temperature | 20.86°C |
| Maximum rotor temperature | 113.61°C |
| Median profile length | 17,142 rows |

The raw dataset is about 300 MB and is not stored in the Git repository. The data setup guide records its source, expected location, licence, and checksum. Generated metrics, figures, tables, and the trained model artifact are included so an evaluator can inspect the result and run the application without redistributing the source data.

![Figure 1 Dataset overview showing the rotor temperature distribution and measurements per profile](reports/figures/dataset_overview.png)

The profiles differ considerably in length. The target also covers a wide temperature range. Both facts support profile-aware evaluation: a random row split would mix highly related points from the same operating sequence and could produce an optimistic result.

## 4 Data preprocessing and feature engineering

The data loader checks the required schema, numeric types, missing values, infinite values, duplicates, and the availability of multiple profiles. The source data contains no missing or infinite required values, so the workflow does not impute or discard measurements.

Three derived features summarize physically meaningful signal relationships:

- Current magnitude is calculated from the d-axis and q-axis currents.
- Voltage magnitude is calculated from the d-axis and q-axis voltages.
- Coolant and ambient difference measures the temperature difference between the cooling system and surrounding air.

Two feature configurations are compared.

| Feature configuration | Inputs |
|---|---|
| Controller signals | Ambient temperature, coolant temperature, motor speed, torque, d-q voltage, d-q current, current magnitude, voltage magnitude, and coolant minus ambient temperature |
| Enhanced sensors | Every controller feature plus stator yoke, stator tooth, and stator winding temperatures |

The controller configuration represents a lower-sensor scenario. The enhanced configuration asks whether nearby thermal measurements materially improve rotor temperature estimation.

![Figure 2 Spearman correlations for a reproducible 100000 row sample](reports/figures/correlation_heatmap.png)

Correlation is used only as an exploratory summary. It does not establish causation, and nonlinear models can use relationships that a pairwise correlation does not capture.

## 5 Experimental design

### 5.1 Profile-aware partitions

The 69 operating profiles are divided into 44 training profiles, 11 validation profiles, and 14 final test profiles. The split uses fixed random seeds so it can be reproduced. No profile appears in more than one partition.

The training profiles fit each candidate. Validation mean absolute error selects the feature configuration and model. After selection, the chosen pipeline is refitted on the combined 55-profile development set and evaluated once on the 14 untouched test profiles.

### 5.2 Models

Four methods provide a bounded and defensible comparison:

- Mean baseline predicts the training target mean and establishes a minimum reference.
- Ridge regression provides a regularized linear benchmark with scaled features and target.
- Histogram Gradient Boosting models nonlinear relationships and interactions in tabular data [2].
- XGBoost supplies a second strong tree-boosting comparison [3].

The purpose is not to try every available algorithm. The selected set shows whether a nonlinear model adds useful accuracy beyond simple baselines and whether that result is consistent across two boosting implementations.

### 5.3 Measures

Mean absolute error is the primary selection measure because it reports an average error in degrees Celsius. Root mean squared error places more weight on large mistakes. R² compares the model with a mean prediction. The percentage within 5°C gives an intuitive tolerance measure, while mean bias shows whether predictions tend to run high or low.

## 6 Project workflow and architecture

![Figure 3 ThermalGuard training evaluation and inference workflow](reports/figures/workflow_diagram.png)

Reusable package modules handle validation, splitting, feature creation, modeling, diagnostics, artifact persistence, and application input checking. The analysis and training scripts import these modules. The Streamlit interface loads the same serialized pipeline evaluated in the experiment, so inference does not reproduce preprocessing independently.

The main safeguards are:

- `profile_id` is a grouping field and never a model input.
- Training and evaluation profiles do not overlap.
- Validation data selects the model before the final test is examined.
- The saved artifact stores the fitted estimator, feature order, input ranges, target, version, and final metrics.
- The application validates the artifact and input contract before prediction.

## 7 Model comparison

| Feature set | Model | MAE °C | RMSE °C | R² | Within 5°C |
|---|---|---:|---:|---:|---:|
| Controller signals | Mean baseline | 15.68 | 19.19 | -0.013 | 19.9% |
| Controller signals | Ridge | 10.46 | 13.03 | 0.533 | 28.7% |
| Controller signals | Histogram Gradient Boosting | 7.75 | 9.95 | 0.727 | 39.7% |
| Controller signals | XGBoost | 8.11 | 10.57 | 0.692 | 39.5% |
| Enhanced sensors | Mean baseline | 15.68 | 19.19 | -0.013 | 19.9% |
| Enhanced sensors | Ridge | 5.85 | 7.10 | 0.861 | 46.6% |
| Enhanced sensors | Histogram Gradient Boosting | 4.61 | 6.11 | 0.897 | 65.0% |
| Enhanced sensors | XGBoost | 4.81 | 6.42 | 0.887 | 65.2% |

Adding stator temperatures improves every learned model. The selected enhanced Histogram Gradient Boosting model reduces validation MAE by about 40 percent compared with the controller-only version of the same method. XGBoost places a slightly larger share of validation predictions within 5°C, but its MAE and RMSE are worse. The predeclared primary measure therefore selects Histogram Gradient Boosting.

## 8 Final evaluation

The selected pipeline is refitted on the combined training and validation profiles, then evaluated once on the final test profiles.

| Measure | Final test result |
|---|---:|
| Mean absolute error | 5.60°C |
| Root mean squared error | 7.36°C |
| R² | 0.856 |
| Predictions within 5°C | 54.4% |
| Mean bias | -0.34°C |

The final test result is less favorable than the validation result. This difference is expected when held-out operating profiles contain conditions that differ from the profiles used for model selection. Reporting both values gives a more honest view than choosing a model directly on the test set.

![Figure 4 Actual predicted and residual diagnostics for the final model](reports/figures/final_model_diagnostics.png)

The predictions follow the overall temperature trend, but the residual plot contains profile-specific bands rather than a uniform cloud. The average bias is small, yet individual profiles can have larger systematic errors.

## 9 Error analysis and explanation

Profile 45 has the largest mean absolute error at 8.90°C. Profile 11 has a positive bias of 5.42°C and a negative R², showing that the model is not equally reliable for every driving cycle. Aggregate metrics must therefore be read with the profile table rather than treated as a guarantee for each session.

Permutation importance is calculated on a fixed 20,000-row sample from the final test set. Each feature is shuffled while the others stay unchanged, and the resulting increase in mean absolute error is measured.

| Feature | MAE increase after permutation |
|---|---:|
| Stator tooth temperature | 13.25°C |
| Stator yoke temperature | 7.22°C |
| Stator winding temperature | 2.30°C |
| Coolant and ambient difference | 1.93°C |
| Ambient temperature | 1.46°C |

The ranking supports the enhanced sensor result because stator temperatures provide useful information about the thermal condition of the motor. It is not a causal ranking. Correlated temperature sensors can share or redistribute importance, and a feature may be predictive because it responds to the same operating history as the target.

## 10 Application and reproducibility

The Streamlit application accepts 11 raw measurements, checks them against the artifact contract and observed training ranges, creates the derived features, and displays the rotor temperature estimate. It does not load the full dataset or train a model during prediction.

The repository includes:

- reusable source modules;
- analysis and training scripts;
- 18 automated tests;
- the verified model artifact;
- generated metrics, tables, and figures;
- an executed project notebook;
- architecture, data, model, and verification documentation; and
- the Streamlit application.

The final verification used Python 3.14.3, scikit-learn 1.8.0, and Streamlit 1.54.0. Dependency integrity, all 18 tests, the full lint suite, dataset analysis, complete model training, artifact inference, application smoke testing, and the live Streamlit health endpoint passed. A complete rerun selected the same model and reproduced every final test metric exactly.

## 11 Limitations and responsible use

ThermalGuard has several limits that matter in an engineering review.

First, it treats each row as a static observation. Motor temperature evolves over time, so lagged signals or a sequence model may represent thermal history better. Second, performance varies across held-out profiles even when the average result is good. Third, the enhanced model depends on stator thermocouples that may not be present in every installation. Fourth, the training ranges come from one test-bench dataset and do not cover every motor design, environment, sensor calibration, or fault condition.

The model should not control a motor, set a shutdown threshold, or replace certified thermal protection. Before any operational use, it would need validation on the target motor, uncertainty and out-of-distribution handling, sensor-failure tests, timing tests, monitoring, and a safety review.

## 12 Conclusion

The experiment shows that rotor temperature can be estimated from the available motor measurements with useful accuracy on unseen operating profiles. The enhanced sensor configuration is substantially better than controller signals alone, and Histogram Gradient Boosting gives the lowest validation MAE. On the untouched final test set, the model reaches 5.60°C MAE and R² of 0.856.

The main engineering lesson is that evaluation design matters as much as model choice. Keeping complete profiles separate produces a more credible estimate of performance than a random row split. Error analysis also shows why one aggregate score is insufficient. ThermalGuard is complete as a reproducible course project and demonstration application, while its documented limits prevent the result from being mistaken for a production safety system.

## References

[1] W. Kirchgässner and contributors. Electric Motor Temperature dataset. Kaggle. Test bench measurements collected by the LEA department at Paderborn University. https://www.kaggle.com/dsv/2161054

[2] scikit-learn developers. HistGradientBoostingRegressor documentation. https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.HistGradientBoostingRegressor.html

[3] T. Chen and C. Guestrin. XGBoost A Scalable Tree Boosting System. Proceedings of the 22nd ACM SIGKDD International Conference on Knowledge Discovery and Data Mining, 2016, pages 785 to 794. https://doi.org/10.1145/2939672.2939785

## Appendix A Reproduction commands

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
python -m pytest
$env:PYTHONPATH = "src"
python scripts/analyze_dataset.py
python scripts/train_models.py
python -m streamlit run app.py
```

## Appendix B Repository structure

| Path | Purpose |
|---|---|
| `src/thermalguard` | Reusable data, feature, model, evaluation, artifact, and application logic |
| `scripts` | Reproducible dataset analysis and training entry points |
| `tests` | Automated unit and application checks |
| `models` | Verified serialized prediction artifact |
| `reports/metrics` | Dataset and experiment metrics |
| `reports/tables` | Profile errors and permutation importance |
| `reports/figures` | Exploratory and diagnostic figures |
| `notebooks` | Executed project walkthrough |
| `docs` | Plans, architecture, data dictionary, model card, and verification record |

