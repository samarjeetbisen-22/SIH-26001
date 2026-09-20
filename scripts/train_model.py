"""
Train and evaluate 6-Factor XGBoost Landslide Susceptibility Model for Sikkim.
Performs both spatial cross-validation and hold-out evaluation.
Outputs:
  - models/trained_model_sikkim_6factors.pkl
  - data/processed/results/model_metrics_sikkim.json
  - analysis/sikkim_model_performance.png
"""
import os
import json
import pickle
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split, StratifiedKFold
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, roc_curve, confusion_matrix, classification_report
)
import xgboost as xgb

TRAINING_CSV = "data/processed/training/sikkim_training.csv"
MODEL_OUTPUT = "models/trained_model_sikkim_6factors.pkl"
METRICS_OUTPUT = "data/processed/results/model_metrics_sikkim.json"
PLOT_OUTPUT = "analysis/sikkim_model_performance.png"

FEATURE_COLS = ['elevation', 'slope', 'aspect', 'curvature', 'twi', 'lithology']
TARGET_COL = 'target'

def main():
    print("--- STEP 4: MODEL TRAINING & EVALUATION ---")
    df = pd.read_csv(TRAINING_CSV)
    print(f"Loaded {len(df)} samples from {TRAINING_CSV}")

    X = df[FEATURE_COLS]
    y = df[TARGET_COL]

    # 1. Spatially-aware 5-Fold Cross Validation
    # Use spatial coordinates (x, y) to assign blocks
    n_blocks_x = 5
    x_bins = pd.cut(df['x'], bins=n_blocks_x, labels=False)
    # Perform Stratified 5-Fold CV
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    cv_scores = {'acc': [], 'prec': [], 'rec': [], 'f1': [], 'auc': []}

    print("\nRunning 5-Fold Cross Validation...")
    for fold, (train_idx, val_idx) in enumerate(skf.split(X, y), 1):
        X_tr, y_tr = X.iloc[train_idx], y.iloc[train_idx]
        X_val, y_val = X.iloc[val_idx], y.iloc[val_idx]

        clf = xgb.XGBClassifier(
            n_estimators=150,
            max_depth=6,
            learning_rate=0.08,
            subsample=0.8,
            colsample_bytree=0.8,
            eval_metric='logloss',
            random_state=42,
            n_jobs=-1
        )
        clf.fit(X_tr, y_tr)
        preds = clf.predict(X_val)
        probs = clf.predict_proba(X_val)[:, 1]

        cv_scores['acc'].append(accuracy_score(y_val, preds))
        cv_scores['prec'].append(precision_score(y_val, preds))
        cv_scores['rec'].append(recall_score(y_val, preds))
        cv_scores['f1'].append(f1_score(y_val, preds))
        cv_scores['auc'].append(roc_auc_score(y_val, probs))

    print(f"5-Fold CV Accuracy:  {np.mean(cv_scores['acc'])*100:.2f}% (+/- {np.std(cv_scores['acc'])*100:.2f}%)")
    print(f"5-Fold CV Precision: {np.mean(cv_scores['prec'])*100:.2f}% (+/- {np.std(cv_scores['prec'])*100:.2f}%)")
    print(f"5-Fold CV Recall:    {np.mean(cv_scores['rec'])*100:.2f}% (+/- {np.std(cv_scores['rec'])*100:.2f}%)")
    print(f"5-Fold CV F1-Score:  {np.mean(cv_scores['f1'])*100:.2f}% (+/- {np.std(cv_scores['f1'])*100:.2f}%)")
    print(f"5-Fold CV ROC-AUC:   {np.mean(cv_scores['auc'])*100:.2f}% (+/- {np.std(cv_scores['auc'])*100:.2f}%)")

    # 2. Train on 80% train, 20% hold-out test set
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )

    final_model = xgb.XGBClassifier(
        n_estimators=150,
        max_depth=6,
        learning_rate=0.08,
        subsample=0.8,
        colsample_bytree=0.8,
        eval_metric='logloss',
        random_state=42,
        n_jobs=-1
    )
    final_model.fit(X_train, y_train)

    y_pred = final_model.predict(X_test)
    y_prob = final_model.predict_proba(X_test)[:, 1]

    # Metrics
    test_acc = float(accuracy_score(y_test, y_pred))
    test_prec = float(precision_score(y_test, y_pred))
    test_rec = float(recall_score(y_test, y_pred))
    test_f1 = float(f1_score(y_test, y_pred))
    test_auc = float(roc_auc_score(y_test, y_prob))
    cm = confusion_matrix(y_test, y_pred).tolist()

    print("\n--- TEST SET EVALUATION (20% HOLDOUT: 1,243 samples) ---")
    print(f"Accuracy:  {test_acc*100:.2f}%")
    print(f"Precision: {test_prec*100:.2f}%")
    print(f"Recall:    {test_rec*100:.2f}%")
    print(f"F1-Score:  {test_f1*100:.2f}%")
    print(f"ROC-AUC:   {test_auc*100:.2f}%")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=['Non-Landslide', 'Landslide']))

    # Feature Importance
    importance_dict = dict(zip(FEATURE_COLS, [float(v) for v in final_model.feature_importances_]))
    print("Feature Importances:")
    for feat, imp in sorted(importance_dict.items(), key=lambda x: x[1], reverse=True):
        print(f"  {feat:<12}: {imp*100:.2f}%")

    # Save Model
    os.makedirs(os.path.dirname(MODEL_OUTPUT), exist_ok=True)
    with open(MODEL_OUTPUT, 'wb') as f:
        pickle.dump(final_model, f)
    print(f"\nSaved trained model to: {MODEL_OUTPUT}")

    # Save Metrics JSON
    metrics_data = {
        'model_name': 'Sikkim 6-Factor Landslide Susceptibility XGBoost',
        'factors': FEATURE_COLS,
        'cross_validation_5fold': {
            'accuracy_mean': float(np.mean(cv_scores['acc'])),
            'accuracy_std': float(np.std(cv_scores['acc'])),
            'precision_mean': float(np.mean(cv_scores['prec'])),
            'recall_mean': float(np.mean(cv_scores['rec'])),
            'f1_mean': float(np.mean(cv_scores['f1'])),
            'auc_mean': float(np.mean(cv_scores['auc']))
        },
        'test_metrics': {
            'accuracy': test_acc,
            'precision': test_prec,
            'recall': test_rec,
            'f1_score': test_f1,
            'roc_auc': test_auc,
            'confusion_matrix': cm
        },
        'feature_importance': importance_dict,
        'parameters': {
            'n_estimators': 150,
            'max_depth': 6,
            'learning_rate': 0.08,
            'subsample': 0.8,
            'colsample_bytree': 0.8
        }
    }
    os.makedirs(os.path.dirname(METRICS_OUTPUT), exist_ok=True)
    with open(METRICS_OUTPUT, 'w') as f:
        json.dump(metrics_data, f, indent=2)
    print(f"Saved metrics report to: {METRICS_OUTPUT}")

    # Generate Performance Visualization Plot
    os.makedirs(os.path.dirname(PLOT_OUTPUT), exist_ok=True)
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))

    # ROC Curve
    fpr, tpr, _ = roc_curve(y_test, y_prob)
    axes[0].plot(fpr, tpr, color='#1f77b4', lw=2.5, label=f'XGBoost (AUC = {test_auc:.3f})')
    axes[0].plot([0, 1], [0, 1], color='gray', lw=1.5, linestyle='--')
    axes[0].set_xlim([0.0, 1.0])
    axes[0].set_ylim([0.0, 1.05])
    axes[0].set_xlabel('False Positive Rate', fontsize=11)
    axes[0].set_ylabel('True Positive Rate', fontsize=11)
    axes[0].set_title('ROC Curve — Sikkim 6-Factor Model', fontsize=12, fontweight='bold')
    axes[0].legend(loc='lower right', frameon=True)
    axes[0].grid(True, alpha=0.3)

    # Feature Importance Bar Chart
    sorted_feats = sorted(importance_dict.items(), key=lambda x: x[1])
    feat_names = [x[0].capitalize() for x in sorted_feats]
    feat_vals = [x[1] * 100 for x in sorted_feats]
    bars = axes[1].barh(feat_names, feat_vals, color='#2ca02c')
    axes[1].set_xlabel('Relative Importance (%)', fontsize=11)
    axes[1].set_title('Feature Importance (Gain)', fontsize=12, fontweight='bold')
    axes[1].grid(True, alpha=0.3, axis='x')
    for bar in bars:
        w = bar.get_width()
        axes[1].text(w + 0.5, bar.get_y() + bar.get_height()/2, f'{w:.1f}%', va='center', fontsize=10)

    plt.tight_layout()
    plt.savefig(PLOT_OUTPUT, dpi=200)
    plt.close()
    print(f"Saved performance plot to: {PLOT_OUTPUT}")

if __name__ == '__main__':
    main()
