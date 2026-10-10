# Dataset setup

ThermalGuard uses the Electric Motor Temperature dataset published on Kaggle by Wilhelm Kirchgässner and collaborators. The measurements were collected from a permanent-magnet synchronous motor on a Paderborn University test bench.

Dataset page: <https://www.kaggle.com/datasets/wkirgsn/electric-motor-temperature>

## Expected file

1. Download `measures_v2.csv` from the dataset page.
2. Create `data/raw/` if it does not exist.
3. Place the file at `data/raw/measures_v2.csv`.

The raw file is roughly 300 MB and is excluded from Git. Do not commit Kaggle credentials or API tokens.

The archive used for the documented benchmark had SHA-256 checksum `10E49E6220FA3C8A9D22C8BAB8280FFE2D5E1E3380A6A18BCFC64EA2E8B56B92`.

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

The dataset also contains stator temperature measurements from thermocouples. The enhanced model uses these readings because stator temperatures are easier to instrument than rotor temperature and carry useful information about the motor's thermal state. A controller-signal-only baseline is retained for comparison.

Each row is a measurement sampled at 2 Hz. Separate test sessions are identified by `profile_id`, which ThermalGuard uses to keep entire sessions together during train and test splitting.

## Validation

After adding the file, run:

```powershell
python -m pytest
```

The data loader checks the required schema, numeric types, missing and infinite values, and the availability of multiple measurement profiles before training begins.

## Licence and citation

The Kaggle dataset page lists a CC BY-SA 4.0 licence. Any redistributed sample or derivative must follow that licence. The final report and README will cite the dataset and the associated work on permanent-magnet synchronous motor temperature estimation.
