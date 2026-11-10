# DMBI Lab: Android Malware Detection with Data Mining

Code for Experiment No. 10 and CA2 (Data Mining and Business Intelligence).

| Folder | What it is |
|---|---|
| `exp10_android_malware/` | Experiment 10 code (Steps 1-8 from the report) |
| `ca2_android_malware/` | CA2 mini project: full pipeline that writes figures and `metrics.json` |

CA1 is a written report with no code, so nothing is stored for it here.

## Setup

```bash
pip install pandas numpy scikit-learn matplotlib
```

Download NATICUSdroid (UCI dataset ID 722) and save it as `naticusdroid.csv` in the folder you run from. It has 86 binary permission columns plus `Result` (0 = benign, 1 = malware).

## Run

```bash
python3 ca2_android_malware/ca2_pipeline.py naticusdroid.csv
python3 exp10_android_malware/exp10_android_malware.py
```

## Notes

- Duplicates are removed before the train/test split to avoid leakage.
- Both models use `random_state=42` and the same stratified 70/30 split.
- Expected test results (from the report): Decision Tree accuracy 0.882, Random Forest accuracy 0.928, Random Forest recall 0.910.
