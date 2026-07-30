"""
Script di valutazione sperimentale — Capitolo 5 Tesi LM-32
Self-Healing CI/CD Pipeline — Benchmark Multi-Modello

Esegue il sistema su tutti gli errori del dataset per ogni modello configurato,
misura Success Rate, latenza, distribuzione tentativi e JSON parse failures.
Salva i risultati in CSV pronti per i grafici della tesi.

Uso:
    # Dry-run su Anthropic (solo Router, no CI reale, no memoria)
    python experiments/benchmark.py --provider anthropic --dry-run

    # Run completo su Anthropic (con CI reale, no memoria)
    python experiments/benchmark.py --provider anthropic --no-memory

    # Ablation study con memoria attiva
    python experiments/benchmark.py --provider anthropic

    # Solo una categoria
    python experiments/benchmark.py --provider groq --category dependency --no-memory

    # Modello Ollama specifico
    python experiments/benchmark.py --provider ollama --ollama-model llama3.1:8b --no-memory

    # Test rapido (5 errori per modello)
    python experiments/benchmark.py --provider anthropic --dry-run --limit 5
"""

import os
import sys
import csv
import time
import json
import logging
import argparse
import subprocess
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, str(Path(__file__).parent.parent))

from experiments.dataset import DATASET

# ══════════════════════════════════════════════════════════════
# CONFIGURAZIONE MODELLI
# ══════════════════════════════════════════════════════════════

MODELS = [
    {
        "id":       "anthropic_haiku",
        "provider": "anthropic",
        "name":     "Claude Haiku",
        "type":     "proprietary",
        "timeout":  300,
    },
    {
        "id":       "groq_llama70b",
        "provider": "groq",
        "name":     "Llama 3.3 70B (Groq)",
        "type":     "open-source-cloud",
        "timeout":  300,
    },
    {
        "id":       "ollama_llama8b",
        "provider": "ollama",
        "ollama_model": "llama3.1:8b",
        "name":     "Llama 3.1 8B",
        "type":     "open-source-local",
        "timeout":  900, # <-- prima settato a 600 ma meglio alzare
    },
    {
        "id":       "ollama_mistral7b",
        "provider": "ollama",
        "ollama_model": "mistral:7b",
        "name":     "Mistral 7B",
        "type":     "open-source-local",
        "timeout":  900, # <-- prima settato a 600 ma meglio alzare
    },
    
    {
        "id":       "openai_gpt4o",
        "provider": "openai",
        "name":     "GPT-4o",
        "type":     "proprietary",
        "timeout":  300,
    },
]

# ══════════════════════════════════════════════════════════════
# PATH OUTPUT
# ══════════════════════════════════════════════════════════════

RESULTS_DIR = Path(__file__).parent / "results"
RESULTS_DIR.mkdir(exist_ok=True)

# ══════════════════════════════════════════════════════════════
# LOGGING
# ══════════════════════════════════════════════════════════════

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(RESULTS_DIR / "benchmark.log", encoding="utf-8")
    ]
)
log = logging.getLogger("benchmark")

# ══════════════════════════════════════════════════════════════
# GESTIONE CHROMADB — pulizia e skip
# ══════════════════════════════════════════════════════════════

def clean_chromadb():
    """
    Cancella tutti gli episodi da ChromaDB.
    Da chiamare prima di un benchmark con memoria attiva
    per partire da uno stato pulito.
    """
    try:
        from agent.memory.episodic_store import get_collection
        col   = get_collection()
        count = col.count()
        if count > 0:
            # ChromaDB richiede un filtro where per delete — utilizzo $or su tutti gli outcome
            col.delete(where={
                "$or": [
                    {"outcome": {"$eq": "success"}},
                    {"outcome": {"$eq": "escalated"}},
                    {"outcome": {"$eq": "failed"}},
                ]
            })
            log.info(f"ChromaDB: rimossi {count} episodi")
        else:
            log.info("ChromaDB: già vuoto")
    except Exception as e:
        log.warning(f"Pulizia ChromaDB fallita: {e}")


# ══════════════════════════════════════════════════════════════
# RESET FILE — stato deterministico per ogni test
# ══════════════════════════════════════════════════════════════

ORIGINAL_REQUIREMENTS = "pytest==7.4.0\npytest-cov==4.1.0\n"


ALLOWED_TEST_FILES = {"test_calculator.py", "test_async.py"}

def reset_files():
    """
    Ripristina tutti i file modificabili al loro stato corretto
    prima di introdurre l'errore specifico del test case.
    Chiamato automaticamente prima di ogni singolo errore.
    """
    repo_root = Path(".")

    # 1. requirements.txt — versione pulita
    (repo_root / "requirements.txt").write_text(
        ORIGINAL_REQUIREMENTS, encoding="utf-8"
    )

    # 2. test_calculator.py — ripristina da git
    subprocess.run(
        ["git", "checkout", "HEAD", "--", "tests/test_calculator.py"],
        capture_output=True
    )

    # 3. ci.yml — ripristina da git
    subprocess.run(
        ["git", "checkout", "HEAD", "--", ".github/workflows/ci.yml"],
        capture_output=True
    )

    # 4. Rimuovi qualsiasi file di test non autorizzato
    tests_dir = repo_root / "tests"
    if tests_dir.exists():
        for f in tests_dir.glob("*.py"):
            if f.name not in ALLOWED_TEST_FILES:
                f.unlink()
                log.debug(f"Rimosso file di test spurio: {f.name}")

def inject_error(error: dict):
    """
    Introduce l'errore specifico nel file corretto in base alla categoria.
    Chiamato dopo reset_files() per ogni test case.
    """
    repo_root = Path(".")
    category  = error["category"]
    diff      = error.get("git_diff", "")

    if category == "dependency":
        current = (repo_root / "requirements.txt").read_text(encoding="utf-8")
        added   = [l[1:].strip() for l in diff.splitlines() if l.startswith("+")]
        for line in added:
            if line and line not in current:
                current += f"\n{line}"
        (repo_root / "requirements.txt").write_text(current, encoding="utf-8")

    elif category == "config":
        ci_path  = repo_root / ".github/workflows/ci.yml"
        content  = ci_path.read_text(encoding="utf-8")
        removed  = [l[1:].strip() for l in diff.splitlines() if l.startswith("-")]
        added    = [l[1:].strip() for l in diff.splitlines() if l.startswith("+")]
        for old, new in zip(removed, added):
            if old and old in content:
                content = content.replace(old, new, 1)
        ci_path.write_text(content, encoding="utf-8")

    # category == "test": i log sintetici contengono già l'errore,
    # niente modifica su file reale — il Fix Executor correggerà il test.


# ══════════════════════════════════════════════════════════════
# STOP OLLAMA — libera VRAM tra modelli locali
# ══════════════════════════════════════════════════════════════

def stop_ollama_model(model_name: str):
    """Scarica il modello Ollama dalla VRAM e attende la liberazione."""
    try:
        subprocess.run(
            ["ollama", "stop", model_name],
            capture_output=True, timeout=15
        )
        time.sleep(5)
        log.info(f"Ollama: modello {model_name} scaricato dalla VRAM")
    except Exception as e:
        log.warning(f"Ollama stop fallito per {model_name}: {e}")


# ══════════════════════════════════════════════════════════════
# TIMEOUT HANDLER — cross-platform (funziona su Windows)
# ══════════════════════════════════════════════════════════════

def run_with_timeout(func, args=(), timeout=300):
    """
    Esegue func con timeout usando threading.
    Compatibile con Windows dove signal.alarm non è disponibile.
    """
    import threading

    result    = [None]
    exception = [None]

    def target():
        try:
            result[0] = func(*args)
        except Exception as e:
            exception[0] = e #type: ignore

    thread = threading.Thread(target=target, daemon=True)
    thread.start()
    thread.join(timeout=timeout)

    if thread.is_alive():
        raise TimeoutError(f"Timeout dopo {timeout}s")
    if exception[0]:
        raise exception[0]
    return result[0]


# ══════════════════════════════════════════════════════════════
# ESECUZIONE SINGOLO ERRORE
# ══════════════════════════════════════════════════════════════

def run_single_error(error: dict, dry_run: bool, no_memory: bool) -> dict:
    """
    Esegue il sistema su un singolo errore del dataset.
    Ritorna un dizionario con tutte le metriche del run.
    """
    # Import lazy per evitare problemi di reload
    from agent.graph import app

    state = {
        "ci_logs":          error["ci_logs"],
        "ci_job_name":      error["ci_job_name"],
        "ci_conclusion":    "failure",
        "commit_sha":       f"{error['id']}_benchmark",
        "repo_name":        os.getenv("GITHUB_REPO", ""),
        "git_diff":         error.get("git_diff", ""),
        "repo_path":        ".",
        "attempt_number":   1,
        "attempts_history": [],
        # dry_run: salta CI reale → ci_fixed=True da subito
        "ci_fixed":         True if dry_run else None,
        # no_memory / dry_run: salta salvataggio ChromaDB
        "skip_memory":      no_memory or dry_run,
    }

    start_time = time.time()
    result     = app.invoke(state) #type: ignore
    elapsed    = round(time.time() - start_time, 2)

    # ── Estrai metriche ──
    history      = result.get("attempts_history", [])
    final_status = result.get("final_status", "unknown")
    router_cat   = result.get("error_category", "unknown")
    router_conf  = result.get("error_confidence", 0.0) or 0.0
    router_reason= result.get("router_reasoning", "") or ""

    # Routing corretto rispetto al ground truth del dataset
    router_correct = 1 if router_cat == error["category"] else 0

    # Tentativo al quale è stato fixato (1, 2 o 3) — None se escalated
    fix_attempt = len(history) if final_status == "fixed" and history else None

    # JSON parse failure: fallback attivato nel router
    json_parse_fail = 1 if (
        router_cat == "unknown" and
        router_conf == 0.0 and
        "Parsing fallito" in router_reason
    ) else 0


    # Cerca nel reasoning o nella history se la memoria è stata usata
    memory_hits = 0
    for h in history:
        if h.get("memory_used"):  # campo da aggiungere negli agenti
            memory_hits += 1

    return {
        "error_id":           error["id"],
        "category":           error["category"],
        "difficulty":         error["difficulty"],
        "final_status":       final_status,
        "success":            1 if final_status == "fixed" else 0,
        "router_category":    router_cat,
        "router_correct":     router_correct,
        "router_confidence":  round(router_conf, 3),
        "router_reasoning":   router_reason[:200],
        "attempts_count":     len(history),
        "fix_attempt":        fix_attempt,
        "json_parse_fail":    json_parse_fail,
        "latency_sec":        elapsed,
        "memory_hits":   memory_hits,   # quante volte RAG ha trovato episodi
        "memory_active": 0 if no_memory else 1,  # condizione sperimentale
    }


# ══════════════════════════════════════════════════════════════
# ESECUZIONE MODELLO COMPLETO
# ══════════════════════════════════════════════════════════════

def run_model(model: dict, errors: list, dry_run: bool, no_memory: bool) -> list:
    """
    Esegue tutti gli errori su un modello specifico.
    Gestisce reset file, timeout, pause e liberazione VRAM.
    """
    # Configura provider per questo modello
    os.environ["LLM_PROVIDER"] = model["provider"]
    if model["provider"] == "ollama":
        os.environ["OLLAMA_MODEL"] = model.get("ollama_model", "llama3.1:8b")

    results = []
    total   = len(errors)
    timeout = model["timeout"]

    log.info(f"\n{'='*60}")
    log.info(f"MODELLO: {model['name']} ({model['id']})")
    log.info(f"Errori: {total} | Timeout: {timeout}s | "
             f"dry-run: {dry_run} | no-memory: {no_memory}")
    log.info(f"{'='*60}")

    for i, error in enumerate(errors):
        log.info(
            f"\n[{i+1}/{total}] {error['id']} "
            f"({error['category']} / {error['difficulty']})"
        )

        # ── Reset file prima di ogni test ──
        reset_files()

        # ── Inject errore nel file (solo se non dry-run) ──
        if not dry_run:
            try:
                inject_error(error)
            except Exception as e:
                log.warning(f"inject_error fallito: {e} — uso log sintetici")

        # ── Riga di risultato di default (per timeout o errori) ──
        row = {
            "model_id":           model["id"],
            "model_name":         model["name"],
            "model_type":         model["type"],
            "dry_run":            1 if dry_run else 0,
            "no_memory":          1 if no_memory else 0,
            "error_id":           error["id"],
            "category":           error["category"],
            "difficulty":         error["difficulty"],
            "final_status":       "timeout",
            "success":            0,
            "router_category":    "",
            "router_correct":     0,
            "router_confidence":  0.0,
            "router_reasoning":   "",
            "attempts_count":     0,
            "fix_attempt":        None,
            "json_parse_fail":    0,
            "latency_sec":        float(timeout),
            "error_msg":          "",
        }

        try:
            run_result = run_with_timeout(
                run_single_error,
                args=(error, dry_run, no_memory),
                timeout=timeout
            )
            # Merge
            row.update(run_result) #type: ignore
            row["error_msg"] = ""

            status_icon = "✅" if row["success"] else "❌"
            log.info(
                f"  {status_icon} {row['final_status']} | "
                f"router: {row['router_category']} "
                f"({row['router_confidence']:.0%}) | "
                f"attempts: {row['attempts_count']} | "
                f"{row['latency_sec']}s"
            )

        except TimeoutError:
            row["error_msg"] = "TIMEOUT"
            log.warning(f"  ⏰ TIMEOUT dopo {timeout}s")

        except Exception as e:
            row["final_status"] = "error"
            row["error_msg"]    = str(e)[:300]
            log.error(f"  💥 ERRORE: {e}")

        results.append(row)

        # ── Pausa tra errori ──
        pause = 1 if model["provider"] in ("anthropic", "groq") else 2
        time.sleep(pause)

    # ── Libera VRAM dopo modello locale ──
    if model["provider"] == "ollama":
        stop_ollama_model(model.get("ollama_model", ""))
        time.sleep(8)  # pausa generosa tra modelli locali

    return results


# ══════════════════════════════════════════════════════════════
# SALVATAGGIO RISULTATI
# ══════════════════════════════════════════════════════════════

def save_results(all_results: list, run_id: str):
    """Salva i risultati in CSV e JSON. Chiamato dopo ogni modello."""
    if not all_results:
        log.warning("Nessun risultato da salvare")
        return None

    csv_path  = RESULTS_DIR / f"benchmark_{run_id}.csv"
    json_path = RESULTS_DIR / f"benchmark_{run_id}.json"

    fieldnames = list(all_results[0].keys())
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_results)

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)

    log.info(f"Salvati {len(all_results)} risultati → {csv_path.name}")
    return csv_path


# ══════════════════════════════════════════════════════════════
# RIEPILOGO A TERMINALE
# ══════════════════════════════════════════════════════════════

def print_summary(all_results: list):
    """Stampa tabelle riassuntive a terminale al termine del benchmark."""
    if not all_results:
        return

    # Raggruppa per modello
    by_model = {}
    for r in all_results:
        mid = r["model_id"]
        if mid not in by_model:
            by_model[mid] = []
        by_model[mid].append(r)

    print("\n" + "="*72)
    print("RIEPILOGO BENCHMARK — SUCCESS RATE GLOBALE")
    print("="*72)
    print(f"{'Modello':<30} {'SR%':>6} {'Router%':>8} {'AvgLat':>8} {'JSONfail':>9} {'N':>4}")
    print("-"*72)

    for mid, rows in by_model.items():
        n          = len(rows)
        sr         = sum(r["success"] for r in rows) / n * 100
        ra         = sum(r["router_correct"] for r in rows) / n * 100
        lat        = sum(r["latency_sec"] for r in rows) / n
        jf         = sum(r["json_parse_fail"] for r in rows)
        name       = rows[0]["model_name"]
        print(f"{name:<30} {sr:>5.1f}% {ra:>7.1f}% {lat:>7.1f}s {jf:>9} {n:>4}")

    print("\nSUCCESS RATE PER CATEGORIA")
    print("="*72)
    cats = ["dependency", "test", "config"]
    print(f"{'Modello':<30}" + "".join(f" {c[:6]:>9}" for c in cats))
    print("-"*60)

    for mid, rows in by_model.items():
        name = rows[0]["model_name"]
        line = f"{name:<30}"
        for cat in cats:
            sub = [r for r in rows if r["category"] == cat]
            sr  = sum(r["success"] for r in sub) / len(sub) * 100 if sub else -1
            line += f" {sr:>8.1f}%" if sr >= 0 else f" {'N/A':>9}"
        print(line)

    print("\nSUCCESS RATE PER DIFFICOLTÀ")
    print("="*72)
    diffs = ["easy", "medium", "hard"]
    print(f"{'Modello':<30}" + "".join(f" {d[:6]:>9}" for d in diffs))
    print("-"*60)

    for mid, rows in by_model.items():
        name = rows[0]["model_name"]
        line = f"{name:<30}"
        for diff in diffs:
            sub = [r for r in rows if r["difficulty"] == diff]
            sr  = sum(r["success"] for r in sub) / len(sub) * 100 if sub else -1
            line += f" {sr:>8.1f}%" if sr >= 0 else f" {'N/A':>9}"
        print(line)

    print("="*72)


# ══════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="Benchmark multi-modello — Self-Healing CI Tesi LM-32"
    )
    parser.add_argument(
        "--provider",
        choices=["anthropic", "groq", "ollama", "openai", "all"],
        default="all",
        help="Provider LLM (default: all)"
    )
    parser.add_argument(
        "--ollama-model",
        dest="ollama_model",
        choices=["llama3.1:8b", "mistral:7b", "all"],
        default="all",
        help="Modello Ollama specifico (usare con --provider ollama)"
    )
    parser.add_argument(
        "--category",
        choices=["dependency", "test", "config", "all"],
        default="all",
        help="Categoria errori (default: all)"
    )
    parser.add_argument(
        "--difficulty",
        choices=["easy", "medium", "hard", "all"],
        default="all",
        help="Difficoltà errori (default: all)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Solo Router, nessuna CI reale. Implica --no-memory."
    )
    parser.add_argument(
        "--no-memory",
        action="store_true",
        help="Disabilita salvataggio in ChromaDB. "
             "Usare per benchmark comparativo (condizioni identiche tra modelli)."
    )
    parser.add_argument(
        "--clean-memory",
        action="store_true",
        help="Cancella ChromaDB prima di iniziare il benchmark."
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limita a N errori per modello (test rapido)"
    )
    args = parser.parse_args()

    # dry-run implica no-memory
    if args.dry_run:
        args.no_memory = True

    # ── Pulizia ChromaDB se richiesta ──
    if args.clean_memory:
        log.info("Pulizia ChromaDB richiesta...")
        clean_chromadb()


    # ── Filtra dataset ──
    errors = DATASET
    if args.category != "all":
        errors = [e for e in errors if e["category"] == args.category]
    if args.difficulty != "all":
        errors = [e for e in errors if e["difficulty"] == args.difficulty]
    if args.limit:
        errors = errors[:args.limit]

    log.info(f"Dataset: {len(errors)} errori selezionati")

    # ── Filtra modelli ──
    models = MODELS
    if args.provider != "all":
        models = [m for m in models if m["provider"] == args.provider]
    if args.provider == "ollama" and args.ollama_model != "all":
        models = [m for m in models if m.get("ollama_model") == args.ollama_model]

    if not models:
        log.error("Nessun modello selezionato — controlla --provider e --ollama-model")
        sys.exit(1)

    log.info(f"Modelli: {[m['name'] for m in models]}")
    log.info(
        f"Modalità: {'dry-run' if args.dry_run else 'full'} | "
        f"memoria: {'OFF' if args.no_memory else 'ON'}"
    )

    # ── Run ID per i file di output ──
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    if args.dry_run:
        run_id += "_dryrun"
    elif args.no_memory:
        run_id += "_nomemory"

    all_results = []

    for model in models:
        log.info(f"\n▶ Avvio: {model['name']}")
        try:
            model_results = run_model(
                model, errors,
                dry_run=args.dry_run,
                no_memory=args.no_memory
            )
            all_results.extend(model_results)

            # Salvataggio intermedio dopo ogni modello
            save_results(all_results, run_id)
            log.info(f"✓ {model['name']} completato — risultati salvati")

            time.sleep(3)

        except KeyboardInterrupt:
            log.warning("Benchmark interrotto dall'utente (Ctrl+C)")
            break
        except Exception as e:
            log.error(f"Errore critico su {model['name']}: {e}")
            continue

    # ── Salvataggio finale e riepilogo ──
    csv_path = save_results(all_results, run_id)
    print_summary(all_results)

    print(f"\n✅ Benchmark completato — {len(all_results)} run totali")
    if csv_path:
        print(f"📄 CSV: {csv_path}")
    print(f"📁 Risultati: {RESULTS_DIR}")


if __name__ == "__main__":
    main()