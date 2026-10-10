# Workflow diagram

```mermaid
flowchart LR
    A[Acquire dataset] --> B[Check schema and quality]
    B --> C[Explore profiles and target]
    C --> D[Reserve complete test profiles]
    D --> E[Build features inside pipelines]
    E --> F[Compare models with group folds]
    F --> G[Select final model]
    G --> H[Evaluate untouched profiles]
    H --> I[Explain errors and feature influence]
    I --> J[Save pipeline and artifacts]
    J --> K[Run Streamlit demonstrator]
    H --> L[Write submission report]
```

The split happens before preprocessing and model fitting. This order prevents measurements from the same operating session from appearing in both development and final test data.
