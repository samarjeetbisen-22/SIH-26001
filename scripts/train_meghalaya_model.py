"""
Meghalaya XGBoost Landslide Susceptibility Model
Train on 6-factor balanced dataset with 5-Fold Stratified CV and Holdout Evaluation.
Outputs:
- models/meghalaya/meghalaya_xgboost.pkl
- data/processed/results/meghalaya/meghalaya_model_report.json
- data/processed/results/meghalaya/meghalaya_model_performance.png
"""

import os
import sys
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import xgboost as xgb
from sklearn.model_selection import StratifiedKFold, train_test_split
from sklearn.metrics import (accuracy_score, f1_score, roc_auc_score,
                             confusion_matrix, classification_report,
                             precision_score, recall_score)
import joblib
import warnings
warnings.filterwarnings('ignore')

TRAIN_CSV   = "data/processed/training/meghalaya/meghalaya_training.csv"
MODEL_DIR   = "models/meghalaya"
RESULTS_DIR = "data/processed/results/meghalaya"
RANDOM_SEED = 42

os.makedirs(MODEL_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

FEATURES = ['elevation', 'slope', 'aspect', 'curvature', 'twi', 'lithology']

print("=" * 60)
print("Meghalaya XGBoost Susceptibility Model")
print("=" * 60)

df = pd.read_csv(TRAIN_CSV)
df = df.dropna(subset=FEATURES + ['target'])
print(f"Total samples: {len(df):,}")
print(f"  Positive: {int(df['target'].sum()):,}")
print(f"  Negative: {int((df['target'] == 0).sum()):,}")

X = df[FEATURES].values
y = df['target'].values

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=RANDOM_SEED
)
print(f"Train samples: {len(X_train):,} | Test samples: {len(X_test):,}")

params = dict(
    n_estimators=150,
    max_depth=6,
    learning_rate=0.08,
    subsample=0.8,
    colsample_bytree=0.8,
    min_child_weight=3,
    reg_alpha=0.1,
    reg_lambda=1.0,
    eval_metric='logloss',
    random_state=RANDOM_SEED,
    n_jobs=-1,
)

print("\nRunning 5-Fold Stratified Cross Validation ...")
skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_SEED)
cv_acc, cv_f1, cv_auc = [], [], []

for fold, (tr_idx, val_idx) in enumerate(skf.split(X_train, y_train)):
    xtr, xval = X_train[tr_idx], X_train[val_idx]
    ytr, yval = y_train[tr_idx], y_train[val_idx]
    m = xgb.XGBClassifier(**params)
    m.fit(xtr, ytr, eval_set=[(xval, yval)], verbose=False)
    preds = m.predict(xval)
    probs = m.predict_proba(xval)[:, 1]
    acc = accuracy_score(yval, preds)
    f1  = f1_score(yval, preds)
    auc = roc_auc_score(yval, probs)
    cv_acc.append(acc); cv_f1.append(f1); cv_auc.append(auc)
    print(f"  Fold {fold+1}: Acc={acc:.4f} F1={f1:.4f} AUC={auc:.4f}")

print(f"Mean CV: Acc={np.mean(cv_acc):.4f} F1={np.mean(cv_f1):.4f} AUC={np.mean(cv_auc):.4f}")

print("\nTraining final model on full train split ...")
final_model = xgb.XGBClassifier(**params)
final_model.fit(X_train, y_train, eval_set=[(X_test, y_test)], verbose=False)

test_preds = final_model.predict(X_test)
test_probs = final_model.predict_proba(X_test)[:, 1]

test_acc  = accuracy_score(y_test, test_preds)
test_prec = precision_score(y_test, test_preds)
test_rec  = recall_score(y_test, test_preds)
test_f1   = f1_score(y_test, test_preds)
test_auc  = roc_auc_score(y_test, test_probs)
cm        = confusion_matrix(y_test, test_preds)

print(f"\nHoldout Test Evaluation:")
print(f"  Accuracy:  {test_acc:.4f} ({test_acc*100:.2f}%)")
print(f"  Precision: {test_prec:.4f}")
print(f"  Recall:    {test_rec:.4f}")
print(f"  F1-Score:  {test_f1:.4f}")
print(f"  ROC-AUC:   {test_auc:.4f}")
print(f"\nConfusion Matrix:\n{cm}")

fi = final_model.feature_importances_
fi_df = pd.DataFrame({'Feature': FEATURES, 'Importance': fi}).sort_values('Importance', ascending=False)
print("\nFeature Importance:")
for _, row in fi_df.iterrows():
    print(f"  {row['Feature']:12s}: {row['Importance']*100:.2f}%")

model_path = os.path.join(MODEL_DIR, "meghalaya_xgboost.pkl")
joblib.dump(final_model, model_path)
print(f"\nModel saved: {model_path}")

report = {
    "state": "Meghalaya",
    "n_train": len(X_train),
    "n_test": len(X_test),
    "n_positive": int(df['target'].sum()),
    "n_negative": int((df['target'] == 0).sum()),
    "cv_accuracy_mean": float(np.mean(cv_acc)),
    "cv_f1_mean": float(np.mean(cv_f1)),
    "cv_roc_auc_mean": float(np.mean(cv_auc)),
    "test_accuracy": float(test_acc),
    "test_precision": float(test_prec),
    "test_recall": float(test_rec),
    "test_f1": float(test_f1),
    "test_roc_auc": float(test_auc),
    "confusion_matrix": cm.tolist(),
    "feature_importance": fi_df.set_index('Feature')['Importance'].to_dict(),
    "hyperparameters": params,
    "utm_crs": "EPSG:32646"
}
report_path = os.path.join(RESULTS_DIR, "meghalaya_model_report.json")
with open(report_path, "w") as f:
    json.dump(report, f, indent=2)
print(f"Report saved: {report_path}")

# Performance plot
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
colors = plt.cm.Blues_r(np.linspace(0.2, 0.8, len(FEATURES)))
axes[0].barh(fi_df['Feature'], fi_df['Importance'] * 100, color=colors)
axes[0].set_xlabel("Importance (%)")
axes[0].set_title("Feature Importance — Meghalaya XGBoost")
axes[0].invert_yaxis()
for i, (_, row) in enumerate(fi_df.iterrows()):
    axes[0].text(row['Importance'] * 100 + 0.2, i, f"{row['Importance']*100:.1f}%", va='center', fontsize=9)

metrics_labels = ['Accuracy', 'F1-Score', 'ROC-AUC']
cv_vals = [np.mean(cv_acc)*100, np.mean(cv_f1)*100, np.mean(cv_auc)*100]
te_vals = [test_acc*100, test_f1*100, test_auc*100]
x = np.arange(len(metrics_labels))
w = 0.35
axes[1].bar(x - w/2, cv_vals, w, label='5-Fold CV', color='steelblue', alpha=0.85)
axes[1].bar(x + w/2, te_vals, w, label='Holdout Test', color='darkorange', alpha=0.85)
axes[1].set_xticks(x)
axes[1].set_xticklabels(metrics_labels)
axes[1].set_ylim(0, 105)
axes[1].set_ylabel("Score (%)")
axes[1].set_title("Model Performance — Meghalaya XGBoost")
axes[1].legend()
for i, (cv, te) in enumerate(zip(cv_vals, te_vals)):
    axes[1].text(i - w/2, cv + 0.5, f"{cv:.1f}", ha='center', fontsize=8)
    axes[1].text(i + w/2, te + 0.5, f"{te:.1f}", ha='center', fontsize=8)

plt.tight_layout()
plot_path = os.path.join(RESULTS_DIR, "meghalaya_model_performance.png")
plt.savefig(plot_path, dpi=150, bbox_inches='tight')
plt.close()
print(f"Performance plot saved: {plot_path}")
print("Training and evaluation complete.")

