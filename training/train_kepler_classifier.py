"""Train the Kepler planet-vs-false-positive classifier used by the app.

    pip install -r training/requirements.txt
    python training/train_kepler_classifier.py

This is the team's final setup from the hackathon notebook (training/notebooks/nasakepler.py),
rerun on the real KOI values instead of the standardized copy:

  * label   CONFIRMED or CANDIDATE -> 1 (planet-like signal), FALSE POSITIVE -> 0
  * features the 11 "core" transit and stellar parameters; no koi_score and no
             false-positive flags, because those are the vetting outcome itself
  * CV      GroupKFold(5) grouped by star (kepid), so planets of one star never sit on
             both sides of a split
  * model   LightGBM, class_weight='balanced', early stopping on AUC

Outputs
  models/kepler_lgbm.json   compact tree dump read by backend/classifier.py (pure Python,
                            so the browser demo needs no LightGBM)
  models/kepler_metrics.json cross-validated metrics, confusion matrix, importances, medians
  data/kepler_ai.csv        out-of-fold probability for every KOI: each object is scored by
                            a model that never saw its star
"""
from __future__ import annotations

import json
import warnings
from pathlib import Path

import lightgbm as lgb
import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.metrics import average_precision_score, confusion_matrix, roc_auc_score
from sklearn.model_selection import GroupKFold

warnings.filterwarnings('ignore', category=lgb.basic.LGBMDeprecationWarning) if hasattr(lgb.basic, 'LGBMDeprecationWarning') else None
warnings.filterwarnings('ignore', message='.*eval_set.*deprecated')

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / 'data' / 'raw'

FEATURES = [
    'koi_period', 'koi_duration', 'koi_depth', 'koi_model_snr', 'koi_num_transits',
    'koi_teq', 'koi_prad', 'koi_sma', 'koi_steff', 'koi_srad', 'koi_smass',
]
PARAMS = dict(learning_rate=0.05, subsample=0.8, subsample_freq=1, colsample_bytree=0.8,
              max_depth=-1, class_weight='balanced', random_state=42, verbose=-1)


def load() -> pd.DataFrame:
    vals = pd.read_csv(RAW / 'kepler_koi_values_2020.csv', comment='#', low_memory=False)
    labels = pd.read_csv(RAW / 'kepler_koi_2025_labels.csv')
    assert (vals['kepoi_name'].values == labels['kepoi_name'].values).all()
    df = vals.drop(columns=['koi_disposition']).join(labels['koi_disposition'])
    df['label'] = df['koi_disposition'].map({'CONFIRMED': 1, 'CANDIDATE': 1, 'FALSE POSITIVE': 0})
    return df.dropna(subset=['label']).drop_duplicates('kepoi_name').reset_index(drop=True)


def compact(booster: lgb.Booster) -> dict:
    """Flatten each tree into parallel arrays: easy and fast to walk in plain Python."""
    trees = []
    for t in booster.dump_model()['tree_info']:
        feat, thr, left, right, dleft, value = [], [], [], [], [], []

        def walk(node):
            i = len(feat)
            feat.append(-1); thr.append(0.0); left.append(-1); right.append(-1)
            dleft.append(True); value.append(0.0)
            if 'leaf_value' in node:
                value[i] = node['leaf_value']
                return i
            assert node['decision_type'] == '<='
            feat[i] = node['split_feature']
            thr[i] = node['threshold']
            dleft[i] = node['default_left']
            left[i] = walk(node['left_child'])
            right[i] = walk(node['right_child'])
            return i

        walk(t['tree_structure'])
        trees.append({'f': feat, 't': thr, 'l': left, 'r': right, 'd': dleft, 'v': value})
    return {'objective': 'binary', 'features': FEATURES, 'trees': trees}


def main() -> None:
    df = load()
    X = df[FEATURES].apply(pd.to_numeric, errors='coerce')
    y = df['label'].astype(int)
    groups = df['kepid']

    oof = np.zeros(len(df))
    aucs, aps, iters = [], [], []
    for fold, (tr, va) in enumerate(GroupKFold(n_splits=5).split(X, y, groups), 1):
        imp = SimpleImputer(strategy='median').fit(X.iloc[tr])
        m = lgb.LGBMClassifier(n_estimators=10000, **PARAMS)
        m.fit(imp.transform(X.iloc[tr]), y.iloc[tr],
              eval_set=[(imp.transform(X.iloc[va]), y.iloc[va])], eval_metric='auc',
              callbacks=[lgb.early_stopping(50, verbose=False)])
        p = m.predict_proba(imp.transform(X.iloc[va]), num_iteration=m.best_iteration_)[:, 1]
        oof[va] = p
        aucs.append(roc_auc_score(y.iloc[va], p)); aps.append(average_precision_score(y.iloc[va], p))
        iters.append(m.best_iteration_)
        print(f'fold {fold}: AUC={aucs[-1]:.4f}  AP={aps[-1]:.4f}  trees={m.best_iteration_}')

    imp = SimpleImputer(strategy='median').fit(X)
    n_trees = int(np.median(iters))
    final = lgb.LGBMClassifier(n_estimators=n_trees, **PARAMS).fit(imp.transform(X), y)

    out = ROOT / 'models'
    out.mkdir(exist_ok=True)
    model = compact(final.booster_)
    (out / 'kepler_lgbm.json').write_text(json.dumps(model, separators=(',', ':')))

    pred = (oof >= 0.5).astype(int)
    gain = final.booster_.feature_importance(importance_type='gain')
    metrics = {
        'label': 'planet-like signal (CONFIRMED or CANDIDATE) vs FALSE POSITIVE',
        'cv': 'GroupKFold(5) by star (kepid)',
        'n_objects': int(len(df)),
        'n_positive': int(y.sum()),
        'auc_mean': float(np.mean(aucs)), 'auc_std': float(np.std(aucs)),
        'ap_mean': float(np.mean(aps)), 'ap_std': float(np.std(aps)),
        'accuracy_at_0_5': float((pred == y).mean()),
        'confusion_matrix': confusion_matrix(y, pred, labels=[0, 1]).tolist(),
        'n_trees': n_trees,
        'importance_gain': dict(zip(FEATURES, (gain / gain.sum()).round(4).tolist())),
        'medians': dict(zip(FEATURES, imp.statistics_.round(6).tolist())),
    }
    (out / 'kepler_metrics.json').write_text(json.dumps(metrics, indent=2))

    koi = 'KOI-' + df['kepoi_name'].str[1:].str.lstrip('0')
    pd.DataFrame({'catalog_id': koi, 'ai_planet_prob': oof.round(4)}).to_csv(ROOT / 'data' / 'kepler_ai.csv', index=False)

    # The pure-Python evaluator must agree with LightGBM exactly.
    import sys
    sys.path.insert(0, str(ROOT))
    from backend.classifier import KeplerClassifier
    clf = KeplerClassifier(out / 'kepler_lgbm.json', out / 'kepler_metrics.json')
    sample = X.sample(300, random_state=0)
    ours = np.array([clf.predict(r.to_dict()) for _, r in sample.iterrows()])
    ref = final.predict_proba(imp.transform(sample))[:, 1]
    assert np.allclose(ours, ref, atol=1e-6), float(np.abs(ours - ref).max())

    print(f"\nAUC {metrics['auc_mean']:.4f} ± {metrics['auc_std']:.4f}   AP {metrics['ap_mean']:.4f}   "
          f"acc@0.5 {metrics['accuracy_at_0_5']:.3f}   trees {n_trees}   json {(out / 'kepler_lgbm.json').stat().st_size // 1024} KB")


if __name__ == '__main__':
    main()
