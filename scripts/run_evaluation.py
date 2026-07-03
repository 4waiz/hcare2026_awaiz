#!/usr/bin/env python3
"""Recompute evaluation metrics from reviewed_goldset_with_predictions.csv."""
import json
from pathlib import Path
import pandas as pd
labels = ['clean','ambiguity','non_testability','incompleteness']

def metrics(y_true, y_pred):
    n=len(y_true)
    per=[]
    for lab in labels:
        tp=sum((a==lab and b==lab) for a,b in zip(y_true,y_pred))
        fp=sum((a!=lab and b==lab) for a,b in zip(y_true,y_pred))
        fn=sum((a==lab and b!=lab) for a,b in zip(y_true,y_pred))
        prec=tp/(tp+fp) if (tp+fp)>0 else 0
        rec=tp/(tp+fn) if (tp+fn)>0 else 0
        f1=2*prec*rec/(prec+rec) if (prec+rec)>0 else 0
        per.append({'label': lab, 'precision': prec, 'recall': rec, 'f1': f1, 'support': sum(a==lab for a in y_true)})
    return {
        'accuracy': sum(a==b for a,b in zip(y_true,y_pred))/n,
        'macro_precision': sum(p['precision'] for p in per)/len(labels),
        'macro_recall': sum(p['recall'] for p in per)/len(labels),
        'macro_f1': sum(p['f1'] for p in per)/len(labels),
        'per_class': per,
    }

def main():
    path = Path(__file__).resolve().parents[1] / 'supplementary' / 'reviewed_goldset_with_predictions.csv'
    df = pd.read_csv(path)
    y = df['human_primary_label'].tolist()
    results = {}
    for method in ['seed_heuristic','flat_rule_screen','explainable_precedence_screen']:
        results[method] = metrics(y, df[method].tolist())
    print(json.dumps(results, indent=2))

if __name__ == '__main__':
    main()
