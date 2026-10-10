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
| `stator_yoke` | Input | Stator-yoke temperature measured by thermocouple |
| `stator_tooth` | Input | Stator-tooth temperature measured by thermocouple |
| `stator_winding` | Input | Stator-winding temperature measured by thermocouple |

Derived features are current magnitude, voltage magnitude, and the difference between coolant and ambient temperature. The controller-signal-only feature set is retained as an ablation so the value of the stator sensors can be measured rather than assumed.
