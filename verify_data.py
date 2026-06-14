"""
Script di verifica dati — risponde alle 3 domande:
1. SR per difficoltà
2. Attempt distribution
3. JSON Parse Failure Rate (misurato o assente)
"""

import pandas as pd
import glob
import numpy as np

# Carica tutti i CSV no_memory delle cartelle provider
csvs = glob.glob('experiments/results/**/*.csv', recursive=True)
dfs = []
for f in csvs:
    if 'no_memory' in f and any(p in f for p in ['anthropic','openai','groq','llama','mistral']):
        df = pd.read_csv(f)
        dfs.append(df)

data = pd.concat(dfs, ignore_index=True)
data = data[data['no_memory'] == 1]

# Controlla i nomi modello disponibili
print("=== NOMI MODELLO NEI CSV ===")
print(data['model_name'].unique())
print()

models = data['model_name'].unique().tolist()

# ── 1. SR PER DIFFICOLTA ──────────────────────────────────────
print("=== 1. SR PER DIFFICOLTA (valori esatti) ===")
for m in models:
    md = data[data['model_name'] == m]
    for d in ['easy', 'medium', 'hard']:
        sub = md[md['difficulty'] == d]
        if len(sub) == 0:
            continue
        sr      = sub['success'].mean() * 100
        correct = int(sub['success'].sum())
        total   = len(sub)
        print(f"  {m} | {d}: {sr:.4f}% ({correct}/{total})")
print()

# ── 2. ATTEMPT DISTRIBUTION ──────────────────────────────────
print("=== 2. ATTEMPT DISTRIBUTION (valori esatti) ===")
for m in models:
    md  = data[data['model_name'] == m]
    n   = len(md)
    t1  = len(md[(md['success'] == 1) & (md['fix_attempt'] == 1)])
    t2  = len(md[(md['success'] == 1) & (md['fix_attempt'] == 2)])
    t3  = len(md[(md['success'] == 1) & (md['fix_attempt'] == 3)])
    esc = len(md[md['success'] == 0])
    print(f"  {m} (N={n}):")
    print(f"    T1  = {t1/n*100:.2f}% ({t1})")
    print(f"    T2  = {t2/n*100:.2f}% ({t2})")
    print(f"    T3  = {t3/n*100:.2f}% ({t3})")
    print(f"    ESC = {esc/n*100:.2f}% ({esc})")
print()

# ── 3. JSON PARSE FAILURE RATE ───────────────────────────────
print("=== 3. JSON PARSE FAILURE RATE ===")
if 'json_parse_fail' in data.columns:
    for m in models:
        md = data[data['model_name'] == m]
        jf = int(md['json_parse_fail'].sum())
        print(f"  {m}: {jf} failures su {len(md)} run ({jf/len(md)*100:.2f}%)")
else:
    print("  COLONNA ASSENTE — json_parse_fail non presente nei CSV")
    print("  → Rimuovere la metrica dalla tesi o marcarla come 'non rilevata'")