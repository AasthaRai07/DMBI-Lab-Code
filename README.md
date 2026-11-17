# Android Malware Detection Using App Permission Patterns

Data mining and business intelligence project (DMBI CA2, with Experiment 10 as the base workflow). It classifies Android apps as benign or malware from the permissions they request, so a security team can review the most suspicious apps first.

---

## Business Problem

Android apps request permissions such as access to contacts, SMS or the internet. Malicious apps often request unusual combinations of these, but many legitimate apps request sensitive permissions too. Permissions are available for every app cheaply, so a classifier built on them can act as a first screen before slower code analysis.

The key business measure is **recall** on malware: a missed malware app is never reviewed, so recall matters more than a small rise in false alarms.

---

## Dataset

**NATICUSdroid (Android Permissions)**, UCI Machine Learning Repository, dataset ID 722, CC BY 4.0.

- 29,332 apps, 86 binary permission features (1 = requested, 0 = not requested)
- Target column `Result`: 0 = benign, 1 = malware
- No missing values

The dataset is not included in this repo. Download it from https://archive.ics.uci.edu/dataset/722 and save it as `naticusdroid.csv`.

---

## Data Preparation

- **Duplicates removed before splitting:** 21,841 rows (74.5%) are exact duplicates. Removing them before the split prevents the same app from appearing in both training and test data.
- **Class balance after cleaning:** 4,867 benign and 2,624 malware apps (7,491 rows).
- **No scaling:** tree-based models do not need it.
- **Split:** stratified 70/30 train-test split with seed 42 (5,243 training, 2,248 test).

---

## Models

- **Decision Tree** (Gini criterion): readable if-then rules that explain each flag.
- **Random Forest** (100 trees): better accuracy and recall, with feature importances.

---

## Results (test set, 2,248 apps)

| Model | Accuracy | Precision | Recall | F1-score | ROC-AUC | Missed malware | False alarms |
|---|---:|---:|---:|---:|---:|---:|---:|
| Decision Tree | 0.882 | 0.821 | 0.846 | 0.834 | 0.879 | 121 of 787 | 145 of 1,461 |
| Random Forest | **0.928** | **0.888** | **0.910** | **0.899** | **0.977** | **71 of 787** | **90 of 1,461** |

The majority-class baseline (always predicting benign) reaches 65.0% accuracy.

---

## Key Findings

- The Random Forest is better on every measure. It catches 716 of 787 malware apps.
- The strongest signals are `READ_PHONE_STATE`, `c2dm.permission.RECEIVE`, `INSTALL_SHORTCUT`, `READ_EXTERNAL_STORAGE` and `BILLING`.
- These are statistical associations in this dataset, not proof that a permission causes malicious behaviour.
- Business use: sort incoming apps by Random Forest score, review the highest-risk apps first, and use the Decision Tree rules to explain each flag.

---

## Outputs

The `outputs/` folder holds the figures and metrics from the CA2 run:

- `fig1_class_distribution_report.png`: class counts before and after removing duplicates
- `terminal_output_report.png`: printed output of the pipeline run
- `fig2_confusion_matrices_report.png`: confusion matrices for both models
- `fig3_metrics_by_model_report.png`: accuracy, precision, recall and F1 by model
- `fig4_roc_curves_report.png`: ROC curves on the test set
- `fig5_feature_importance_report.png`: top 15 Random Forest permissions
- `metrics.json`: all numeric results

The `_report` suffix marks figures taken from the CA2 report. Running the pipeline writes its own figures to `outputs/`.

---

## How to Run

### 1. Run Pipeline
```bash
pip install -r requirements.txt
python3 src/ca2_pipeline.py naticusdroid.csv
```

### 2. Launch Interactive Web Dashboard
```bash
python app.py
```
Open **http://localhost:5000** in your browser to view the interactive performance dashboard, visualizations gallery, decision tree rules, and live permission-risk scanner (or open `dashboard.html` directly).

The Experiment 10 steps are in `experiments/exp10/exp10_android_malware.py`. Run it from the folder that contains `naticusdroid.csv`.

---

## Repository Structure

```
├── README.md
├── requirements.txt
├── src/
│   └── ca2_pipeline.py          # CA2 pipeline: load, clean, train, evaluate, plot
├── experiments/
│   └── exp10/
│       └── exp10_android_malware.py   # Experiment 10 steps 1-8
└── outputs/                     # figures and metrics from the CA2 run
```

---

## Limitations

- Permissions alone cannot show that an app is malicious. Legitimate messaging, navigation and banking apps often request sensitive permissions.
- The data covers apps released between 2010 and 2019, so newer malware may behave differently.
- Duplicates and conflicting permission patterns add label noise.
- Results come from a single split. Repeated cross-validation is the next step.
