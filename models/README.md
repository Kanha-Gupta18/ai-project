# Model artifact

The repository includes the verified prediction artifact:

```text
models/thermalguard_model.joblib
```

The artifact contains the selected estimator, ordered feature contract, observed input ranges, median interface defaults, target name, artifact version, and final test metrics. Running the training workflow rebuilds this file from the source dataset.

The Streamlit application validates the artifact before prediction. An incompatible version, missing feature contract, or missing input summary stops the application with an error instead of producing a prediction.
