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
import fnmatch
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


# File di test creati per il Gruppo 1 (vedi experiments/CHANGELOG_DATASET.md).
# Senza questa whitelist reset_files() li cancellerebbe ad ogni run, dato che
# rimuove qualsiasi tests/*.py non elencato qui.
GROUP1_TEST_FILES = {
    "test_utils.py", "test_api.py", "test_models.py", "test_math.py",
    "test_list.py", "test_service.py", "test_auth.py", "test_db.py",
    "test_mock.py", "test_config.py", "test_validator.py",
    "test_integration.py", "test_serializer.py", "test_parser.py",
    "test_payment.py", "test_orders.py", "test_loader.py", "test_import.py",
    "test_notify.py", "test_registry.py", "test_legacy.py", "test_dates.py",
    "test_settings.py", "test_sampler.py", "test_validation.py",
    "test_scheduler.py", "test_reports.py", "test_logger.py",
    "test_billing_cycle.py",
}

ALLOWED_TEST_FILES = {"test_calculator.py", "test_async.py"} | GROUP1_TEST_FILES

# Percorsi (relativi alla repo root) di tutti i file sorgente/app/test/fixture
# creati per il Gruppo 1 che vanno ripristinati da git ad ogni reset_files()
# (possono essere modificati sia dall'injection sia da un fix dell'agente).
GROUP1_RESTORE_PATHS = [
    # src/
    "src/calculator.py", "src/utils.py", "src/models.py", "src/services.py",
    "src/auth.py", "src/db.py", "src/mailer.py", "src/config.py",
    "src/validator.py", "src/integration_db.py", "src/serializer.py",
    "src/parser.py", "src/api.py", "src/orders.py", "src/loader.py",
    "src/importer.py", "src/registry.py", "src/legacy.py", "src/settings.py",
    "src/sampler.py", "src/validation.py", "src/scheduler.py",
    "src/reports.py", "src/logger.py", "src/billing_cycle.py",
    # app/
    "app/__init__.py", "app/billing/__init__.py", "app/billing/payment.py",
    "app/notify.py",
    # tests/ (contenuto, non solo esistenza — vedi GROUP1_TEST_FILES per la whitelist)
    "tests/test_async.py",
    *[f"tests/{name}" for name in GROUP1_TEST_FILES],
    # fixture dati
    "tests/data/sample.csv", "tests/fixtures/sample.json",
]


# ══════════════════════════════════════════════════════════════
# CASI ESCLUSI DAL BENCHMARK — limiti strutturali del dataset
# Vedi experiments/CHANGELOG_DATASET.md per il razionale caso-per-caso.
# ══════════════════════════════════════════════════════════════

# Categoria "test": casi del dataset sintetico che referenziano moduli
# applicativi mai esistiti nel repo e troppo complessi per uno stub minimale
# ("Gruppo 2" dell'analisi), o con premesse tecnicamente non riproducibili.
EXCLUDED_TEST_IDS = {
    "test_016",  # file esiste (test_async.py) ma con contenuto reale diverso dallo scenario descritto
    "test_018",  # richiede freezegun, non presente in requirements.txt di produzione
    "test_020",  # race condition non deterministica — rischio di flakiness nel benchmark stesso
    "test_032",  # timing-based (time.sleep) — stesso rischio di flakiness
    "test_034",  # rimuove un mock di rete: senza mock la CI farebbe una chiamata reale, esito non deterministico
    "test_036",  # richiede pytest-xdist -n auto, non presente in ci.yml
    "test_037",  # expected_fix richiede una libreria di snapshot testing non installata
    "test_038",  # richiede alembic + sqlalchemy, dipendenze pesanti non presenti
    "test_039",  # deadlock reale con Lock non rientrante — rischio di hang infinito del job CI
    "test_042",  # richiede un servizio Redis reale
    "test_043",  # richiede innescare un OOM reale — inaffidabile/pericoloso in CI condivisa
    "test_044",  # premessa non valida: dict Python 3.7+ preserva l'ordine di inserimento a prescindere da PYTHONHASHSEED
    "test_046",  # richiede un runner macos-14/arm64, la CI attuale è solo ubuntu-latest
    "test_047",  # caso composito (flaky sort + coverage gate all'85%, non presente in ci.yml)
    "test_048",  # richiede pytest-xdist -n, oggetti non picklabili tra worker
}

# Categoria "dependency": casi npm/yarn/JDK/ci.yml il cui fix reale non tocca
# requirements.txt. agent/agents/dependency_agent.py è hardcoded a leggere e
# scrivere solo requirements.txt: instradare l'injection su un altro file non
# li renderebbe comunque risolvibili dal sistema attuale, quindi si escludono
# esplicitamente invece di iniettare un errore che l'agente non potrà mai fixare.
EXCLUDED_DEPENDENCY_IDS = {
    "dep_022", "dep_023", "dep_027", "dep_029",
    "dep_031", "dep_032", "dep_040", "dep_043",
    "dep_045", "dep_047",
}


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

    # 4. File sorgente/fixture del Gruppo 1 — ripristina da git (possono essere
    #    stati modificati dall'injection o da un fix applicato dall'agente)
    if GROUP1_RESTORE_PATHS:
        subprocess.run(
            ["git", "checkout", "HEAD", "--", *GROUP1_RESTORE_PATHS],
            capture_output=True
        )

    # 5. Rimuovi qualsiasi file di test non autorizzato
    tests_dir = repo_root / "tests"
    if tests_dir.exists():
        for f in tests_dir.rglob("*.py"):
            if f.name not in ALLOWED_TEST_FILES:
                f.unlink()
                log.debug(f"Rimosso file di test spurio: {f.name}")


def resolve_test_target_file(error: dict, repo_root: Path):
    """
    Determina il file di test reale da modificare per un caso 'test',
    leggendo il path dai ci_logs sintetici (stesso pattern usato da
    agent.agents.test_agent.find_test_file).
    Ritorna None se nei log non compare un path riconoscibile.
    """
    import re
    match = re.search(r'(?:FAILED|ERROR)\s+(tests/[\w./]+\.py)', error.get("ci_logs", ""))
    if not match:
        return None
    return repo_root / match.group(1)


def _inject_test_generic(target: "Path", diff: str) -> bool:
    """Injection generica: find/replace riga per riga (stesso pattern di 'config')."""
    if not target.exists():
        return False
    content = target.read_text(encoding="utf-8")
    removed = [l[1:].strip() for l in diff.splitlines() if l.startswith("-")]
    added   = [l[1:].strip() for l in diff.splitlines() if l.startswith("+")]
    changed = False
    for old, new in zip(removed, added):
        if old and old in content:
            content = content.replace(old, new, 1)
            changed = True
    if changed:
        target.write_text(content, encoding="utf-8")
    return changed


def _inject_test_023(repo_root: Path) -> bool:
    """
    test_023: il git_diff del caso descrive uno spostamento di file
    (app/services/payment.py -> app/billing/payment.py), non un diff di
    righe di codice — il find/replace generico non si applica. La baseline
    di tests/test_payment.py importa già dal path corretto (app.billing.payment,
    coerente con expected_fix); l'injection riscrive l'import sul path vecchio
    per riprodurre il ModuleNotFoundError descritto nel caso.
    """
    target = repo_root / "tests/test_payment.py"
    if not target.exists():
        return False
    content = target.read_text(encoding="utf-8")
    new_content = content.replace(
        "from app.billing.payment import", "from app.services.payment import"
    )
    if new_content == content:
        return False
    target.write_text(new_content, encoding="utf-8")
    return True


def _inject_test_027(repo_root: Path) -> bool:
    """
    test_027: il git_diff descrive la rimozione di un file di fixture dal
    commit, non un diff di righe — l'injection cancella il file di fixture
    per riprodurre il FileNotFoundError descritto nel caso.
    """
    fixture = repo_root / "tests/fixtures/sample.json"
    if not fixture.exists():
        return False
    fixture.unlink()
    return True


def _inject_test_010(repo_root: Path) -> bool:
    """
    test_010: il git_diff mostra solo una riga aggiunta (nessuna riga
    rimossa in coppia) — il find/replace generico basato su zip(removed,
    added) non produce nulla. La baseline di tests/test_api.py è già nello
    stato corretto (assert include 'price'); l'injection rimuove la chiave
    'price' dall'assert per riprodurre il disallineamento col dict reale
    restituito da create_item (che la include sempre).
    """
    target = repo_root / "tests/test_api.py"
    if not target.exists():
        return False
    content = target.read_text(encoding="utf-8")
    new_content = content.replace(
        '{"id": 1, "name": "item", "price": 10.0}',
        '{"id": 1, "name": "item"}',
    )
    if new_content == content:
        return False
    target.write_text(new_content, encoding="utf-8")
    return True


def _inject_test_012(repo_root: Path) -> bool:
    """
    test_012: il diff originale mostra l'aggiunta di 'commit=True' (un
    parametro CON default), che non romperebbe mai una chiamata save(record)
    esistente — non riproduce l'errore "missing required argument" descritto
    nei ci_logs. Injection custom: rende 'commit' posizionale obbligatorio
    (senza default), coerente con l'errore realmente osservato.
    """
    target = repo_root / "src/db.py"
    if not target.exists():
        return False
    content = target.read_text(encoding="utf-8")
    new_content = content.replace(
        "def save(self, record, commit=True):",
        "def save(self, record, commit):",
    )
    if new_content == content:
        return False
    target.write_text(new_content, encoding="utf-8")
    return True


def _inject_test_030(repo_root: Path) -> bool:
    """
    test_030: il git_diff descrive il fix storico gia' applicato a
    src/legacy.py (fuori dal nostro controllo, e' gia' nello stato corretto
    nella baseline) — non c'e' nulla da reiniettare li'. Il vero elemento
    rotto e' un marker @pytest.mark.xfail(strict=True) rimasto sul test
    dopo che il bug e' stato risolto: l'injection lo riaggiunge, causando un
    XPASS(strict) che pytest tratta come fallimento.
    """
    target = repo_root / "tests/test_legacy.py"
    if not target.exists():
        return False
    content = target.read_text(encoding="utf-8")
    new_content = content.replace(
        "def test_old_behavior():",
        "@pytest.mark.xfail(strict=True)\ndef test_old_behavior():",
    )
    if new_content == content:
        return False
    target.write_text(new_content, encoding="utf-8")
    return True


def _inject_test_033(repo_root: Path) -> bool:
    """
    test_033: il git_diff ha 3 righe rimosse e 2 aggiunte — lo zip(removed,
    added) del find/replace generico accoppia solo le prime 2 e lascia
    orfana la terza riga rimossa (mutazione diretta di CONFIG accanto alla
    variabile locale 'config' ormai indefinita: rompe comunque il test, ma
    con un NameError invece del comportamento voluto). Injection custom:
    sostituisce l'intero corpo del test con la mutazione diretta dello stato
    globale condiviso CONFIG, riproducendo esattamente lo scenario descritto.
    """
    target = repo_root / "tests/test_settings.py"
    if not target.exists():
        return False
    content = target.read_text(encoding="utf-8")
    new_content = content.replace(
        "    config = copy.deepcopy(CONFIG)\n"
        "    config['env'] = 'production'\n"
        "    assert config['env'] == 'production'",
        "    CONFIG['env'] = 'production'\n"
        "    assert CONFIG['env'] == 'production'",
    )
    if new_content == content:
        return False
    target.write_text(new_content, encoding="utf-8")
    return True


SPECIAL_TEST_INJECTORS = {
    "test_010": _inject_test_010,
    "test_012": _inject_test_012,
    "test_023": _inject_test_023,
    "test_027": _inject_test_027,
    "test_030": _inject_test_030,
    "test_033": _inject_test_033,
}

# Casi in cui il git_diff descrive letteralmente una riga di codice SORGENTE
# (non del file di test) — l'injection generica va applicata al modulo src/
# indicato qui invece che al file risolto da resolve_test_target_file().
# Tutti questi seguono la convenzione standard "-"=stato corretto,
# "+"=stato introdotto dal fix a monte non riflesso nel test (vedi notes
# di ciascun caso in experiments/dataset.py).
TEST_TARGET_OVERRIDE = {
    "test_009": "src/services.py",
    "test_011": "src/auth.py",
    "test_013": "src/mailer.py",
    "test_014": "src/config.py",
    "test_015": "src/validator.py",
    "test_019": "src/serializer.py",
    "test_022": "src/parser.py",
    "test_040": "src/validation.py",
    "test_049": "src/logger.py",
}


def inject_error(error: dict) -> bool:
    """
    Introduce l'errore specifico nel file corretto in base alla categoria.
    Chiamato dopo reset_files() per ogni test case.

    Ritorna True se l'injection è stata applicata con successo, False se il
    caso va escluso dal conteggio del Success Rate (nessun file target valido,
    o caso esplicitamente fuori scope — vedi EXCLUDED_TEST_IDS,
    EXCLUDED_DEPENDENCY_IDS e experiments/CHANGELOG_DATASET.md).
    """
    repo_root = Path(".")
    category  = error["category"]
    diff      = error.get("git_diff", "")
    error_id  = error["id"]

    if category == "dependency":
        if error_id in EXCLUDED_DEPENDENCY_IDS:
            log.info(f"{error_id}: escluso — il fix reale non tocca requirements.txt "
                     f"(dependency_agent non potrebbe applicarlo comunque)")
            return False
        current = (repo_root / "requirements.txt").read_text(encoding="utf-8")
        added   = [l[1:].strip() for l in diff.splitlines() if l.startswith("+")]
        for line in added:
            if line and line not in current:
                current += f"\n{line}"
        (repo_root / "requirements.txt").write_text(current, encoding="utf-8")
        return True

    elif category == "config":
        ci_path  = repo_root / ".github/workflows/ci.yml"
        content  = ci_path.read_text(encoding="utf-8")
        removed  = [l[1:].strip() for l in diff.splitlines() if l.startswith("-")]
        added    = [l[1:].strip() for l in diff.splitlines() if l.startswith("+")]
        for old, new in zip(removed, added):
            if old and old in content:
                content = content.replace(old, new, 1)
        ci_path.write_text(content, encoding="utf-8")
        return True

    elif category == "test":
        if error_id in EXCLUDED_TEST_IDS:
            log.info(f"{error_id}: escluso — vedi experiments/CHANGELOG_DATASET.md")
            return False
        special = SPECIAL_TEST_INJECTORS.get(error_id)
        if special:
            return special(repo_root)
        override = TEST_TARGET_OVERRIDE.get(error_id)
        target = (repo_root / override) if override else resolve_test_target_file(error, repo_root)
        if target is None or not target.exists():
            log.warning(f"{error_id}: file target non trovato ({target}) — escluso dal Success Rate")
            return False
        return _inject_test_generic(target, diff)

    return False


# ══════════════════════════════════════════════════════════════
# PULIZIA BRANCH REMOTI — rimuove i branch "fix/ai-*" residui
# ══════════════════════════════════════════════════════════════

def cleanup_fix_branches(repo_name: str = "") -> int:
    """
    Cancella dal repository remoto tutti i branch che matchano il pattern
    "fix/ai-*", creati da fix_executor_node ad ogni tentativo di fix
    (vedi agent/pipeline/fix_executor.py::build_branch_name). Senza pulizia
    si accumulano ad ogni run del benchmark.

    Usa l'istanza GitHub gia' configurata nel progetto (PyGitHub +
    GITHUB_TOKEN dal .env, vedi agent/github/client.py::get_repo).

    Non solleva eccezioni: un fallimento nella pulizia non deve interrompere
    il benchmark. Ritorna il numero di branch effettivamente rimossi.
    """
    from agent.github.client import get_repo

    repo_name = repo_name or os.getenv("GITHUB_REPO", "")
    if not repo_name:
        log.warning("cleanup_fix_branches: GITHUB_REPO non configurato — skip")
        return 0

    try:
        repo = get_repo(repo_name)
        targets = [b for b in repo.get_branches() if fnmatch.fnmatch(b.name, "fix/ai-*")]
    except Exception as e:
        log.warning(f"cleanup_fix_branches: impossibile leggere i branch remoti: {e}")
        return 0

    if not targets:
        log.info("cleanup_fix_branches: nessun branch 'fix/ai-*' da rimuovere")
        return 0

    removed = 0
    for branch in targets:
        try:
            repo.get_git_ref(f"heads/{branch.name}").delete()
            removed += 1
        except Exception as e:
            log.warning(f"cleanup_fix_branches: impossibile rimuovere {branch.name}: {e}")
        time.sleep(0.5)  # rate limiting sull'API GitHub

    log.info(f"cleanup_fix_branches: rimossi {removed}/{len(targets)} branch 'fix/ai-*'")
    return removed


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

def run_model(model: dict, errors: list, dry_run: bool, no_memory: bool,
              keep_branches: bool = False) -> list:
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
        injected = True
        if not dry_run:
            try:
                injected = inject_error(error)
            except Exception as e:
                log.warning(f"inject_error fallito: {e} — uso log sintetici")
                injected = True  # comportamento storico: procede coi soli log sintetici

        # ── Caso escluso: nessun target valido per l'injection reale.
        #    Non viene eseguito il sistema — il caso non entra nel Success Rate. ──
        if not dry_run and not injected:
            log.info(f"  ⏭️  {error['id']} escluso dal Success Rate (injection non applicabile)")
            results.append({
                "model_id":           model["id"],
                "model_name":         model["name"],
                "model_type":         model["type"],
                "dry_run":            0,
                "no_memory":          1 if no_memory else 0,
                "error_id":           error["id"],
                "category":           error["category"],
                "difficulty":         error["difficulty"],
                "final_status":       "excluded",
                "success":            0,
                "router_category":    "",
                "router_correct":     0,
                "router_confidence":  0.0,
                "router_reasoning":   "",
                "attempts_count":     0,
                "fix_attempt":        None,
                "json_parse_fail":    0,
                "latency_sec":        0.0,
                "error_msg":          "excluded_no_valid_injection_target",
            })
            time.sleep(1 if model["provider"] in ("anthropic", "groq") else 2)
            continue

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

    # ── Pulizia incrementale branch "fix/ai-*" creati da questo modello ──
    if not keep_branches:
        cleanup_fix_branches()

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

    # Raggruppa per modello — i casi "excluded" (injection non applicabile,
    # vedi EXCLUDED_TEST_IDS/EXCLUDED_DEPENDENCY_IDS) non entrano nel calcolo
    # del Success Rate: restano nel CSV/JSON per trasparenza, ma qui sono filtrati.
    by_model = {}
    excluded_count = {}
    for r in all_results:
        mid = r["model_id"]
        if r.get("final_status") == "excluded":
            excluded_count[mid] = excluded_count.get(mid, 0) + 1
            continue
        if mid not in by_model:
            by_model[mid] = []
        by_model[mid].append(r)

    print("\n" + "="*72)
    print("RIEPILOGO BENCHMARK — SUCCESS RATE GLOBALE")
    print("(casi esclusi non conteggiati — vedi colonna 'Escl.')")
    print("="*72)
    print(f"{'Modello':<30} {'SR%':>6} {'Router%':>8} {'AvgLat':>8} {'JSONfail':>9} {'N':>4} {'Escl.':>6}")
    print("-"*72)

    for mid, rows in by_model.items():
        n          = len(rows)
        sr         = sum(r["success"] for r in rows) / n * 100
        ra         = sum(r["router_correct"] for r in rows) / n * 100
        lat        = sum(r["latency_sec"] for r in rows) / n
        jf         = sum(r["json_parse_fail"] for r in rows)
        escl       = excluded_count.get(mid, 0)
        name       = rows[0]["model_name"]
        print(f"{name:<30} {sr:>5.1f}% {ra:>7.1f}% {lat:>7.1f}s {jf:>9} {n:>4} {escl:>6}")

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
    parser.add_argument(
        "--keep-branches",
        action="store_true",
        help="Disabilita la pulizia automatica dei branch 'fix/ai-*' su GitHub "
             "(utile per debug)."
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

    # ── Pulizia branch "fix/ai-*" residui da run precedenti ──
    if not args.keep_branches:
        log.info("Pulizia branch 'fix/ai-*' residui da run precedenti...")
        cleanup_fix_branches()
    else:
        log.info("--keep-branches attivo: salto la pulizia dei branch 'fix/ai-*'")

    all_results = []

    for model in models:
        log.info(f"\n▶ Avvio: {model['name']}")
        try:
            model_results = run_model(
                model, errors,
                dry_run=args.dry_run,
                no_memory=args.no_memory,
                keep_branches=args.keep_branches
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