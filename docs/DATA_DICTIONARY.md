# Data dictionary

The units and exact representation will be confirmed against the downloaded `measures_v2.csv` before range validation is implemented.

| Column | Planned role | Description |
|---|---|---|
| `profile_id` | Group only | Identifier for one measurement session |
| `ambient` | Input | Ambient temperature |
| `coolant` | Input | Coolant temperature |
| `motor_speed` | Input | Motor rotational speed |
| `torque` | Input | Motor torque |
| `u_d` | Input | Direct-axis voltage component |
| `u_q` | Input | Quadrature-axis voltage component |
| `i_d` | Input | Direct-axis current component |
| `i_q` | Input | Quadrature-axis current component |
| `pm` | Target | Permanent-magnet rotor temperature |
| `stator_yoke` | Analysis only | Stator-yoke temperature |
| `stator_tooth` | Analysis only | Stator-tooth temperature |
| `stator_winding` | Analysis only | Stator-winding temperature |

Candidate derived features are current magnitude, voltage magnitude, and the difference between coolant and ambient temperature. They will be retained only if group-aware validation or interpretation supports them.
