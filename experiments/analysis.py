"""
Script di analisi e visualizzazione — Capitolo 5 Tesi LM-32
Self-Healing CI/CD Pipeline — Benchmark Multi-Modello

Grafici prodotti:
  1. Bar chart — Success Rate per categoria per modello
  2. Stacked bar — Distribuzione tentativi senza memoria
  3. Heatmap tripla — Router Recall / Precision / F1
  4. Grouped bar — Ablation study memoria
  5. Radar chart — Confronto multi-dimensionale (Router F1)
  6. Bar chart — SR per difficoltà per modello
  7. Stacked bar affiancato — Attempt distribution con vs senza memoria

Uso:
    python experiments/analysis.py
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

# ══════════════════════════════════════════════════════════════
# PATH
# ══════════════════════════════════════════════════════════════

RESULTS_DIR = Path("experiments/results")
FIGURES_DIR = Path("experiments/figures")
FIGURES_DIR.mkdir(exist_ok=True)

# ══════════════════════════════════════════════════════════════
# MAPPA FILE
# ══════════════════════════════════════════════════════════════

FILES = {
    ("Claude Haiku",  "no_memory"): "anthropic/no_memory/benchmark_20260530_180135_dryrun.csv",
    ("Claude Haiku",  "memory"):    "anthropic/memory/run2_plus_openai/benchmark_20260531_182119.csv",
    ("GPT-4o",        "no_memory"): "openai/no_memory/benchmark_20260531_084755_dryrun.csv",
    ("GPT-4o",        "memory"):    "openai/memory/run1/benchmark_20260531_173042.csv",
    ("Llama 3.3 70B", "no_memory"): "groq/no_memory/benchmark_20260531_094026_dryrun.csv",
    ("Llama 3.3 70B", "memory"):    "groq/memory/benchmark_20260601_093236.csv",
    ("Llama 3.1 8B",  "no_memory"): "ollama/llama_3_1_8b/no_memory/benchmark_20260531_104622_dryrun.csv",
    ("Llama 3.1 8B",  "memory"):    "ollama/llama_3_1_8b/memory/benchmark_20260531_190917.csv",
    ("Mistral 7B",    "no_memory"): "ollama/mistral_7b/no_memory/benchmark_20260531_131503_dryrun.csv",
    ("Mistral 7B",    "memory"):    "ollama/mistral_7b/memory/benchmark_20260601_082101.csv",
}

MODEL_ORDER = [
    "Claude Haiku",
    "GPT-4o",
    "Llama 3.3 70B",
    "Llama 3.1 8B",
    "Mistral 7B",
]

COLORS = {
    "Claude Haiku":  "#cc785c",
    "GPT-4o":        "#10a37f",
    "Llama 3.3 70B": "#4f8ef7",
    "Llama 3.1 8B":  "#8b5cf6",
    "Mistral 7B":    "#f59e0b",
}

# ══════════════════════════════════════════════════════════════
# CARICAMENTO
# ══════════════════════════════════════════════════════════════

def load_all_data() -> pd.DataFrame:
    dfs = []
    for (model, condition), rel_path in FILES.items():
        full_path = RESULTS_DIR / rel_path
        if not full_path.exists():
            print(f"⚠️  File non trovato: {full_path}")
            continue
        df = pd.read_csv(full_path)
        df["model_label"] = model
        df["condition"]   = condition
        dfs.append(df)
        print(f"✅ Caricato: {model} / {condition} — {len(df)} righe")
    combined = pd.concat(dfs, ignore_index=True)
    print(f"\nDataset totale: {len(combined)} righe\n")
    return combined


# ══════════════════════════════════════════════════════════════
# STILE
# ══════════════════════════════════════════════════════════════

def set_style():
    plt.rcParams.update({
        "figure.facecolor":  "white",
        "axes.facecolor":    "white",
        "axes.grid":         True,
        "grid.alpha":        0.3,
        "grid.color":        "#cccccc",
        "font.family":       "sans-serif",
        "font.size":         11,
        "axes.titlesize":    13,
        "axes.titleweight":  "bold",
        "axes.labelsize":    11,
        "xtick.labelsize":   10,
        "ytick.labelsize":   10,
        "legend.fontsize":   10,
        "axes.spines.top":   False,
        "axes.spines.right": False,
    })


# ══════════════════════════════════════════════════════════════
# HELPER — F1 macro per categoria
# ══════════════════════════════════════════════════════════════

def compute_f1_macro(md: pd.DataFrame,
                     categories=("dependency", "test", "config")) -> float:
    """F1 macro-averaged sul Router — bilancia precision e recall."""
    f1_scores = []
    for cat in categories:
        tp = len(md[(md["category"] == cat) & (md["router_category"] == cat)])
        fp = len(md[(md["category"] != cat) & (md["router_category"] == cat)])
        fn = len(md[(md["category"] == cat) & (md["router_category"] != cat)])
        p  = tp / (tp + fp) * 100 if (tp + fp) > 0 else 0
        r  = tp / (tp + fn) * 100 if (tp + fn) > 0 else 0
        f1 = 2 * p * r / (p + r) if (p + r) > 0 else 0
        f1_scores.append(f1)
    return float(np.mean(f1_scores))


def _attempt_counts(df: pd.DataFrame, model: str, condition: str):
    """Ritorna (t1%, t2%, t3%, esc%) per un modello e condizione."""
    md = df[(df["condition"] == condition) & (df["model_label"] == model)]
    n  = len(md)
    if n == 0:
        return 0, 0, 0, 0
    t1  = len(md[(md["success"] == 1) & (md["fix_attempt"] == 1)]) / n * 100
    t2  = len(md[(md["success"] == 1) & (md["fix_attempt"] == 2)]) / n * 100
    t3  = len(md[(md["success"] == 1) & (md["fix_attempt"] == 3)]) / n * 100
    esc = len(md[md["success"] == 0]) / n * 100
    return t1, t2, t3, esc


# ══════════════════════════════════════════════════════════════
# FIGURA 1 — SR per categoria
# ══════════════════════════════════════════════════════════════

def plot_sr_by_category(df: pd.DataFrame):
    data       = df[df["condition"] == "no_memory"]
    categories = ["dependency", "test", "config"]
    cat_labels = ["Dependency", "Test", "Config"]
    models     = MODEL_ORDER
    bar_width  = 0.15
    x          = np.arange(len(categories))

    fig, ax = plt.subplots(figsize=(10, 6))
    for i, model in enumerate(models):
        md  = data[data["model_label"] == model]
        srs = [md[md["category"] == c]["success"].mean() * 100
               if len(md[md["category"] == c]) > 0 else 0
               for c in categories]
        offset = (i - len(models) / 2 + 0.5) * bar_width
        bars = ax.bar(x + offset, srs, width=bar_width, label=model,
                      color=COLORS[model], alpha=0.85,
                      edgecolor="white", linewidth=0.5)
        for bar, sr in zip(bars, srs):
            if sr > 0:
                ax.text(bar.get_x() + bar.get_width() / 2,
                        bar.get_height() + 1,
                        f"{sr:.0f}%",
                        ha="center", va="bottom",
                        fontsize=7.5, color="#333333")

    ax.set_xticks(x)
    ax.set_xticklabels(cat_labels, fontsize=11)
    ax.set_ylabel("Success Rate (%)")
    ax.set_title("Success Rate per Categoria — Confronto Multi-Modello\n"
                 "(condizione: senza memoria episodica)")
    ax.set_ylim(0, 115)
    ax.legend(loc="upper right", framealpha=0.9)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.0f}%")) #type: ignore
    plt.tight_layout()
    out = FIGURES_DIR / "fig1_sr_by_category.pdf"
    plt.savefig(out, dpi=300, bbox_inches="tight")
    plt.savefig(str(out).replace(".pdf", ".png"), dpi=200, bbox_inches="tight")
    print(f"Salvato: {out}")
    plt.close()


# ══════════════════════════════════════════════════════════════
# FIGURA 2 — Attempt distribution (senza memoria)
# ══════════════════════════════════════════════════════════════

def plot_attempt_distribution(df: pd.DataFrame):
    models = MODEL_ORDER
    at1, at2, at3, esc = [], [], [], []
    for model in models:
        t1, t2, t3, es = _attempt_counts(df, model, "no_memory")
        at1.append(t1); at2.append(t2); at3.append(t3); esc.append(es)

    x   = np.arange(len(models))
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(x, at1, label="Fix al tentativo 1", color="#10b981", alpha=0.85)
    ax.bar(x, at2, bottom=at1, label="Fix al tentativo 2",
           color="#3b82f6", alpha=0.85)
    ax.bar(x, at3, bottom=np.array(at1) + np.array(at2),
           label="Fix al tentativo 3", color="#8b5cf6", alpha=0.85)
    ax.bar(x, esc, bottom=np.array(at1) + np.array(at2) + np.array(at3),
           label="Escalation", color="#ef4444", alpha=0.75)

    ax.set_xticks(x)
    ax.set_xticklabels(models, rotation=15, ha="right")
    ax.set_ylabel("Percentuale (%)")
    ax.set_title("Distribuzione dei Fix per Tentativo\n"
                 "(condizione: senza memoria episodica)")
    ax.set_ylim(0, 115)
    ax.legend(loc="upper right", framealpha=0.9)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.0f}%")) #type: ignore
    plt.tight_layout()
    out = FIGURES_DIR / "fig2_attempt_distribution.pdf"
    plt.savefig(out, dpi=300, bbox_inches="tight")
    plt.savefig(str(out).replace(".pdf", ".png"), dpi=200, bbox_inches="tight")
    print(f"Salvato: {out}")
    plt.close()


# ══════════════════════════════════════════════════════════════
# FIGURA 3 — Heatmap Router: Recall / Precision / F1
# ══════════════════════════════════════════════════════════════

def plot_router_heatmap(df: pd.DataFrame):
    data       = df[df["condition"] == "no_memory"]
    categories = ["dependency", "test", "config"]
    models     = MODEL_ORDER

    recall_m, precision_m, f1_m = [], [], []
    for model in models:
        md = data[data["model_label"] == model]
        row_r, row_p, row_f = [], [], []
        for cat in categories:
            true_cat  = md[md["category"] == cat]
            recall    = (true_cat["router_correct"].mean() * 100
                         if len(true_cat) > 0 else 0)
            pred_cat  = md[md["router_category"] == cat]
            precision = (len(pred_cat[pred_cat["category"] == cat]) /
                         len(pred_cat) * 100
                         if len(pred_cat) > 0 else 0)
            f1 = (2 * precision * recall / (precision + recall)
                  if (precision + recall) > 0 else 0)
            row_r.append(recall); row_p.append(precision); row_f.append(f1)
        recall_m.append(row_r); precision_m.append(row_p); f1_m.append(row_f)

    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    titles   = ["Recall (%)", "Precision (%)", "F1 Score (%)"]
    matrices = [recall_m, precision_m, f1_m]

    for ax, mat, title in zip(axes, matrices, titles):
        np_mat = np.array(mat)
        im = ax.imshow(np_mat, cmap="RdYlGn", vmin=0, vmax=100, aspect="auto")
        ax.set_xticks(range(len(categories)))
        ax.set_xticklabels(["Dependency", "Test", "Config"], fontsize=10)
        ax.set_yticks(range(len(models)))
        ax.set_yticklabels(models if title == "Recall (%)" else [],
                           fontsize=10)
        for i in range(len(models)):
            for j in range(len(categories)):
                val   = np_mat[i, j]
                color = "white" if val < 50 else "black"
                ax.text(j, i, f"{val:.0f}%", ha="center", va="center",
                        fontsize=10, color=color, fontweight="bold")
        ax.set_title(title, fontsize=12, fontweight="bold", pad=10)
        plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)

    fig.suptitle("Router Classification Performance per Modello e Categoria",
                 fontsize=13, fontweight="bold", y=1.02)
    plt.tight_layout()
    out = FIGURES_DIR / "fig3_router_heatmap.pdf"
    plt.savefig(out, dpi=300, bbox_inches="tight")
    plt.savefig(str(out).replace(".pdf", ".png"), dpi=200, bbox_inches="tight")
    print(f"Salvato: {out}")
    plt.close()


# ══════════════════════════════════════════════════════════════
# FIGURA 4 — Ablation Study Memoria
# ══════════════════════════════════════════════════════════════

def plot_ablation_memory(df: pd.DataFrame):
    models  = MODEL_ORDER
    sr_no, sr_mem = [], []
    for model in models:
        nm = df[(df["model_label"] == model) & (df["condition"] == "no_memory")]
        mm = df[(df["model_label"] == model) & (df["condition"] == "memory")]
        sr_no.append(nm["success"].mean() * 100 if len(nm) > 0 else 0)
        sr_mem.append(mm["success"].mean() * 100 if len(mm) > 0 else 0)

    x, bar_width = np.arange(len(models)), 0.35
    fig, ax = plt.subplots(figsize=(10, 6))
    bars_no  = ax.bar(x - bar_width / 2, sr_no,  bar_width,
                      label="Senza memoria", color="#64748b", alpha=0.85)
    bars_mem = ax.bar(x + bar_width / 2, sr_mem, bar_width,
                      label="Con memoria episodica", color="#10b981", alpha=0.85)

    for i, (no, mem) in enumerate(zip(sr_no, sr_mem)):
        delta = mem - no
        if abs(delta) > 0.5:
            color  = "#10b981" if delta > 0 else "#ef4444"
            symbol = "▲" if delta > 0 else "▼"
            ax.annotate(f"{symbol}{abs(delta):.1f}%",
                        xy=(x[i] + bar_width / 2, max(no, mem) + 6),
                        ha="center", fontsize=9,
                        color=color, fontweight="bold")

    for bar in bars_no:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, h + 0.5,
                f"{h:.2f}%", ha="center", va="bottom", fontsize=8.5)
    for bar in bars_mem:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, h + 0.5,
                f"{h:.2f}%", ha="center", va="bottom", fontsize=8.5)

    ax.set_xticks(x)
    ax.set_xticklabels(models, rotation=15, ha="right")
    ax.set_ylabel("Success Rate (%)")
    ax.set_title("Ablation Study — Impatto della Memoria Episodica RAG\n"
                 "(▲/▼ = delta SR con vs senza memoria)")
    ax.set_ylim(0, 115)
    ax.legend(loc="upper right", framealpha=0.9)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.0f}%")) #type: ignore
    plt.tight_layout()
    out = FIGURES_DIR / "fig4_ablation_memory.pdf"
    plt.savefig(out, dpi=300, bbox_inches="tight")
    plt.savefig(str(out).replace(".pdf", ".png"), dpi=200, bbox_inches="tight")
    print(f"Salvato: {out}")
    plt.close()


# ══════════════════════════════════════════════════════════════
# FIGURA 5 — Radar Chart (Router F1, non Recall)
# ══════════════════════════════════════════════════════════════

def plot_radar_chart(df: pd.DataFrame):
    data   = df[df["condition"] == "no_memory"]
    models = MODEL_ORDER
    dimensions = ["SR Globale", "Router F1", "SR Easy", "SR Hard", "Fix @ T1"]
    N = len(dimensions)

    values_all = []
    for model in models:
        md = data[data["model_label"] == model]
        if len(md) == 0:
            values_all.append([0] * N)
            continue
        sr_global = md["success"].mean() * 100
        router_f1 = compute_f1_macro(md)
        sr_easy   = md[md["difficulty"] == "easy"]["success"].mean() * 100
        sr_hard   = md[md["difficulty"] == "hard"]["success"].mean() * 100
        fix_t1    = (len(md[(md["success"] == 1) & (md["fix_attempt"] == 1)])
                     / len(md) * 100)
        values_all.append([sr_global, router_f1, sr_easy, sr_hard, fix_t1])

    angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
    for model, values in zip(models, values_all):
        v = values + values[:1]
        ax.plot(angles, v, "o-", linewidth=2, label=model,
                color=COLORS[model], markersize=5)
        ax.fill(angles, v, alpha=0.08, color=COLORS[model])

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(dimensions, fontsize=11)
    ax.set_yticks([20, 40, 60, 80, 100])
    ax.set_yticklabels(["20%", "40%", "60%", "80%", "100%"], fontsize=8)
    ax.set_ylim(0, 100)
    ax.set_title("Confronto Multi-Dimensionale — Tutti i Modelli\n"
                 "(condizione: senza memoria episodica)",
                 pad=20, fontsize=13, fontweight="bold")
    ax.legend(loc="upper right", bbox_to_anchor=(1.35, 1.1), framealpha=0.9)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    out = FIGURES_DIR / "fig5_radar_chart.pdf"
    plt.savefig(out, dpi=300, bbox_inches="tight")
    plt.savefig(str(out).replace(".pdf", ".png"), dpi=200, bbox_inches="tight")
    print(f"Salvato: {out}")
    plt.close()


# ══════════════════════════════════════════════════════════════
# FIGURA 6 — SR per difficoltà
# ══════════════════════════════════════════════════════════════

def plot_sr_by_difficulty(df: pd.DataFrame):
    data        = df[df["condition"] == "no_memory"]
    diffs       = ["easy", "medium", "hard"]
    models      = MODEL_ORDER
    colors_diff = ["#10b981", "#f59e0b", "#ef4444"]
    x, bar_width = np.arange(len(models)), 0.25

    fig, ax = plt.subplots(figsize=(11, 6))
    for j, (diff, color) in enumerate(zip(diffs, colors_diff)):
        srs = []
        for model in models:
            md = data[(data["model_label"] == model) &
                      (data["difficulty"] == diff)]
            srs.append(md["success"].mean() * 100 if len(md) > 0 else 0)
        offset = (j - 1) * bar_width
        bars = ax.bar(x + offset, srs, bar_width,
                      label=diff.capitalize(), color=color, alpha=0.85)
        for bar, sr in zip(bars, srs):
            if sr > 0:
                ax.text(bar.get_x() + bar.get_width() / 2,
                        bar.get_height() + 0.8,
                        f"{sr:.2f}%", ha="center", va="bottom", fontsize=8)

    ax.set_xticks(x)
    ax.set_xticklabels(models, rotation=15, ha="right")
    ax.set_ylabel("Success Rate (%)")
    ax.set_title("Success Rate per Difficoltà — Confronto Multi-Modello\n"
                 "(condizione: senza memoria episodica)")
    ax.set_ylim(0, 115)
    ax.legend(title="Difficoltà", loc="upper right", framealpha=0.9)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.0f}%")) #type: ignore
    plt.tight_layout()
    out = FIGURES_DIR / "fig6_sr_by_difficulty.pdf"
    plt.savefig(out, dpi=300, bbox_inches="tight")
    plt.savefig(str(out).replace(".pdf", ".png"), dpi=200, bbox_inches="tight")
    print(f"Salvato: {out}")
    plt.close()


# ══════════════════════════════════════════════════════════════
# FIGURA 7 — Attempt distribution: senza vs con memoria (affiancato)
# Mostra che il T3 si "accende" con la memoria episodica attiva
# ══════════════════════════════════════════════════════════════

def plot_attempt_distribution_memory(df: pd.DataFrame):
    models     = MODEL_ORDER
    conditions = [("no_memory", "Senza memoria episodica"),
                  ("memory",    "Con memoria episodica RAG")]
    colors_bar = ["#10b981", "#3b82f6", "#8b5cf6", "#ef4444"]

    fig, axes = plt.subplots(1, 2, figsize=(16, 6), sharey=True)

    for ax, (cond, cond_label) in zip(axes, conditions):
        at1, at2, at3, esc = [], [], [], []
        for model in models:
            t1, t2, t3, es = _attempt_counts(df, model, cond)
            at1.append(t1); at2.append(t2)
            at3.append(t3); esc.append(es)

        x = np.arange(len(models))
        ax.bar(x, at1, label="Fix al tentativo 1",
               color=colors_bar[0], alpha=0.85)
        ax.bar(x, at2, bottom=at1, label="Fix al tentativo 2",
               color=colors_bar[1], alpha=0.85)
        ax.bar(x, at3, bottom=np.array(at1) + np.array(at2),
               label="Fix al tentativo 3", color=colors_bar[2], alpha=0.85)
        ax.bar(x, esc,
               bottom=np.array(at1) + np.array(at2) + np.array(at3),
               label="Escalation", color=colors_bar[3], alpha=0.75)

        # Annota T3 se > 0 (visibile con memoria)
        for i, (a1, a2, a3) in enumerate(zip(at1, at2, at3)):
            if a3 > 0.1:
                ax.text(i, a1 + a2 + a3 / 2,
                        f"T3\n{a3:.2f}%",
                        ha="center", va="center",
                        fontsize=8, color="white", fontweight="bold")

        ax.set_xticks(x)
        ax.set_xticklabels(models, rotation=15, ha="right")
        ax.set_ylabel("Percentuale (%)" if cond == "no_memory" else "")
        ax.set_title(cond_label, fontsize=12, fontweight="bold")
        ax.set_ylim(0, 115)
        ax.yaxis.set_major_formatter(
            plt.FuncFormatter(lambda v, _: f"{v:.0f}%")) #type: ignore
        ax.legend(loc="upper right", framealpha=0.9, fontsize=9)

    fig.suptitle(
        "Distribuzione dei Fix per Tentativo — Senza vs Con Memoria Episodica\n"
        "(il Fix T3 si attiva con la memoria: gli episodi RAG compensano i casi ambigui)",
        fontsize=12, fontweight="bold")
    plt.tight_layout()
    out = FIGURES_DIR / "fig7_attempt_distribution_memory.pdf"
    plt.savefig(out, dpi=300, bbox_inches="tight")
    plt.savefig(str(out).replace(".pdf", ".png"), dpi=200, bbox_inches="tight")
    print(f"Salvato: {out}")
    plt.close()


# ══════════════════════════════════════════════════════════════
# TABELLA RIEPILOGATIVA — nessun arrotondamento
# ══════════════════════════════════════════════════════════════

def print_summary_table(df: pd.DataFrame):
    """
    Tabella riepilogativa.
    - F1 Macro Router (non Recall)
    - SR difficoltà
    - Attempt distribution
    - JSON parse failure: sempre 0, gestito dal fallback (deciso di non inserie nella tesi in quanto dato non rilevante)
    """
    data   = df[df["condition"] == "no_memory"]
    models = MODEL_ORDER

    print("\n" + "=" * 100)
    print("TABELLA RIEPILOGATIVA — valori esatti (nessun arrotondamento)")
    print("=" * 100)
    print(f"{'Modello':<22} {'SR%':>10} {'Dep%':>10} {'Test%':>10} {'Conf%':>10}"
          f"  {'Easy (n/N %)':>16}  {'Med (n/N %)':>16}  {'Hard (n/N %)':>16}"
          f"  {'F1-R%':>10}  {'AvgLat':>10}")
    print("-" * 100)

    for model in models:
        md = data[data["model_label"] == model]
        if len(md) == 0:
            continue
        # Nessun arrotondamento — 4 decimali
        sr   = md["success"].mean() * 100
        dep  = md[md["category"] == "dependency"]["success"].mean() * 100
        test = md[md["category"] == "test"]["success"].mean() * 100
        conf = md[md["category"] == "config"]["success"].mean() * 100
        lat  = md["latency_sec"].mean()

        # Frazioni esatte
        e = md[md["difficulty"] == "easy"]
        m = md[md["difficulty"] == "medium"]
        h = md[md["difficulty"] == "hard"]
        easy_s = f"{int(e['success'].sum())}/{len(e)} {e['success'].mean()*100:.4f}%"
        med_s  = f"{int(m['success'].sum())}/{len(m)} {m['success'].mean()*100:.4f}%"
        hard_s = f"{int(h['success'].sum())}/{len(h)} {h['success'].mean()*100:.4f}%"

        router_f1 = compute_f1_macro(md)

        print(f"{model:<22}"
              f" {sr:>9.4f}%"
              f" {dep:>9.4f}%"
              f" {test:>9.4f}%"
              f" {conf:>9.4f}%"
              f"  {easy_s:>16}"
              f"  {med_s:>16}"
              f"  {hard_s:>16}"
              f"  {router_f1:>9.4f}%"
              f"  {lat:>9.2f}s")

    print("=" * 100)

    # Ablation
    print("\nABLATION STUDY — Impatto memoria episodica")
    print("=" * 65)
    print(f"{'Modello':<22} {'SR no_mem%':>14} {'SR memory%':>14} {'Delta':>12}")
    print("-" * 65)
    for model in models:
        nm = df[(df["model_label"] == model) & (df["condition"] == "no_memory")]
        mm = df[(df["model_label"] == model) & (df["condition"] == "memory")]
        if len(nm) == 0 or len(mm) == 0:
            continue
        sr_no  = nm["success"].mean() * 100
        sr_mem = mm["success"].mean() * 100
        delta  = sr_mem - sr_no
        sign   = "▲" if delta > 0 else "▼" if delta < 0 else "="
        print(f"{model:<22}"
              f" {sr_no:>13.4f}%"
              f" {sr_mem:>13.4f}%"
              f"  {sign}{abs(delta):>9.4f}%")
    print("=" * 65)

    # Attempt distribution
    print("\nATTEMPT DISTRIBUTION")
    for cond_key, cond_label in [("no_memory", "SENZA memoria"),
                                  ("memory",    "CON memoria")]:
        cdata = df[df["condition"] == cond_key]
        print(f"\n  {cond_label}")
        print("  " + "=" * 82)
        print(f"  {'Modello':<22}"
              f" {'T1 n/N (%)':>16}"
              f" {'T2 n/N (%)':>16}"
              f" {'T3 n/N (%)':>16}"
              f" {'ESC n/N (%)':>16}")
        print("  " + "-" * 82)
        for model in models:
            md = cdata[cdata["model_label"] == model]
            n  = len(md)
            if n == 0:
                continue
            t1  = len(md[(md["success"] == 1) & (md["fix_attempt"] == 1)])
            t2  = len(md[(md["success"] == 1) & (md["fix_attempt"] == 2)])
            t3  = len(md[(md["success"] == 1) & (md["fix_attempt"] == 3)])
            esc = len(md[md["success"] == 0])
            print(f"  {model:<22}"
                  f" {t1}/{n} ({t1/n*100:.4f}%)"
                  f"  {t2}/{n} ({t2/n*100:.4f}%)"
                  f"  {t3}/{n} ({t3/n*100:.4f}%)"
                  f"  {esc}/{n} ({esc/n*100:.4f}%)")
        print("  " + "=" * 82)

    print("\nNOTA T3=0% (no_memory): senza memoria il RAG al T3 è disabilitato.")
    print("  Il contributo del T3 emerge solo con memoria attiva (fig7).")

    # JSON parse failure
    print("\nJSON PARSE FAILURE RATE")
    print("=" * 60)
    if "json_parse_fail" in data.columns:
        for model in models:
            md = data[data["model_label"] == model]
            jf = int(md["json_parse_fail"].sum())
            print(f"  {model}: {jf}/{len(md)} ({jf/len(md)*100:.4f}%)")


# ══════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════

def main():
    set_style()
    print("Caricamento dati...")
    df = load_all_data()

    print("\nGenerazione grafici...")
    plot_sr_by_category(df)               # fig1
    plot_attempt_distribution(df)         # fig2 — senza memoria
    plot_router_heatmap(df)               # fig3
    plot_ablation_memory(df)              # fig4
    plot_radar_chart(df)                  # fig5
    plot_sr_by_difficulty(df)             # fig6
    plot_attempt_distribution_memory(df)  # fig7 — senza vs con memoria

    print_summary_table(df)

    print(f"\n✅ Tutti i grafici salvati in: {FIGURES_DIR}")
    print("   Formato: PDF (per LaTeX) + PNG (per anteprima)")


if __name__ == "__main__":
    main()