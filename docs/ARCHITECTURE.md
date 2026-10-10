# Architecture

ThermalGuard separates reusable project code from the analysis notebook and the Streamlit interface. The notebook will call functions from the package instead of keeping the only working implementation inside notebook cells.

```mermaid
flowchart TD
    A[data/raw/measures_v2.csv] --> B[Data validation]
    B --> C[Profile-aware train, validation, and test split]
    C --> D[Feature and model pipeline]
    D --> E[Validation comparison]
    E --> F[Model selection and development refit]
    F --> G[Untouched test evaluation]
    G --> H[Saved pipeline]
    G --> I[Generated metrics, tables, and figures]
    H --> J[Streamlit application]
    I --> K[Submission report]
```

## Package responsibilities

- `data.py` will load, validate, and split the dataset.
- `features.py` will define the approved raw and derived features.
- `modeling.py` builds model candidates, features, and regression metrics.
- `evaluation.py` calculates residual, profile, and permutation diagnostics.
- `artifact.py` saves, validates, and runs the inference artifact.
- `config.py` will hold shared paths, column names, and the random seed.

Modules will be introduced with the feature that needs them. Empty placeholder modules are not part of the initial repository.

## Main safeguards

- `profile_id` is a grouping field, not a model input.
- Complete profiles are reserved for the test set.
- Preprocessing is fitted using training data only during selection.
- Validation profiles select the model. The final test set is not used for selection.
- The application loads the same serialized pipeline used during evaluation.
