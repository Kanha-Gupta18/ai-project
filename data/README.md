# Dataset setup

ThermalGuard uses the Electric Motor Temperature dataset published on Kaggle by Wilhelm Kirchgässner and collaborators. The measurements were collected from a permanent-magnet synchronous motor on a Paderborn University test bench.

Dataset page: <https://www.kaggle.com/datasets/wkirgsn/electric-motor-temperature>

## Expected file

1. Download `measures_v2.csv` from the dataset page.
2. Create `data/raw/` if it does not exist.
3. Place the file at `data/raw/measures_v2.csv`.

The raw file is roughly 300 MB and is excluded from Git. Do not commit Kaggle credentials or API tokens.

## Expected columns

The first implementation will validate these columns:

- `profile_id`
- `ambient`
- `coolant`
- `motor_speed`
- `torque`
- `u_d`
- `u_q`
- `i_d`
- `i_q`
- `pm`

The dataset also contains stator temperature measurements. They will be examined during analysis but will not be used as predictors in the main rotor-temperature model unless the project plan is revised with a clear engineering reason.

## Licence and citation

The Kaggle dataset page lists a CC BY-SA 4.0 licence. Any redistributed sample or derivative must follow that licence. The final report and README will cite the dataset and the associated work on permanent-magnet synchronous motor temperature estimation.
