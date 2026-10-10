# Model artifact

Run the training workflow to create:

```text
models/thermalguard_model.joblib
```

The artifact contains the selected estimator, ordered feature contract, observed input ranges, median interface defaults, target name, artifact version, and final test metrics. The model file is generated locally and excluded from Git.

The Streamlit application validates the artifact before prediction. An incompatible version, missing feature contract, or missing input summary stops the application with an error instead of producing a prediction.
