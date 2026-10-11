# Workflow diagram

```mermaid
flowchart LR
    A[Acquire dataset] --> B[Check schema and quality]
    B --> C[Explore profiles and target]
    C --> D[Reserve validation and test profiles]
    D --> E[Build features]
    E --> F[Compare models on validation profiles]
    F --> G[Refit selected model on development profiles]
    G --> H[Evaluate untouched test profiles]
    H --> I[Explain errors and feature influence]
    I --> J[Save pipeline and artifacts]
    J --> K[Run Streamlit demonstrator]
    H --> L[Prepare notebook and presentation evidence]
```

The split happens before preprocessing and model fitting. This order prevents measurements from the same operating session from appearing in both development and final test data.
