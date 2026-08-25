# Changelog — fix benchmark harness e dataset sintetico

Data: 2026-07-30
Contesto: bug identificati tramite debug manuale sul benchmark harness
(`experiments/benchmark.py`) e sul dataset sintetico (`experiments/dataset.py`),
Capitolo 5 tesi LM-32. Tutte le modifiche sono state proposte come piano,
confermate esplicitamente, e verificate localmente prima di essere lasciate
sul disco (vedi sezione "Verifica" in fondo).

## 1. Fix isolate

### 1.1 `agent/state.py` — campo `modified_file` mancante da `AgentState`
**Stato**: già risolto in un commit precedente a questa sessione (`0fcdfd8`,
2026-07-30 12:30). Nessuna modifica necessaria.

### 1.2 `agent/agents/test_agent.py` — backslash su Windows in `find_test_file()`
Il primo `return` della funzione già normalizzava il path con
`.replace("\\", "/")`; i due fallback (`match2` e il default
`tests/test_calculator.py`) no. Normalizzati anche questi due, usando
`os.sep` per esplicitare l'intento cross-platform.

### 1.3 `experiments/benchmark.py` — `inject_error()` no-op per `category=="test"`
Implementata l'injection reale: `resolve_test_target_file()` estrae il path
del file di test dai `ci_logs` sintetici (stesso pattern di
`find_test_file()`), poi si applica un find/replace riga per riga (stesso
meccanismo già usato per `config`). Aggiunti tre meccanismi di supporto,
necessari perché alcuni casi non si prestano al find/replace generico:

- `TEST_TARGET_OVERRIDE`: per i casi in cui il `git_diff` descrive
  letteralmente una riga di codice **sorgente** (non del file di test) —
  l'injection viene applicata al modulo `src/*.py` indicato invece che al
  file risolto dai `ci_logs` (es. `test_009` → `src/services.py`).
- `SPECIAL_TEST_INJECTORS`: per i casi in cui il `git_diff` non è un diff di
  righe di codice replay-abile 1:1 (descrive uno spostamento/rimozione di
  file, o ha un numero di righe rimosse/aggiunte non accoppiabile) — un
  piccolo injector dedicato per `test_010`, `test_012`, `test_023`,
  `test_027`, `test_030`, `test_033` (vedi docstring di ciascuno nel codice
  per il razionale specifico).
- `EXCLUDED_TEST_IDS`: 15 id esclusi esplicitamente dall'injection (vedi
  §3).

`inject_error()` ora ritorna `bool`. `run_model()` in `benchmark.py` è stato
aggiornato per intercettare `False` (nessun target valido) e registrare il
caso con `final_status="excluded"` invece di farlo passare per un tentativo
reale — `print_summary()` filtra questi casi dal calcolo del Success Rate
(restano nel CSV/JSON grezzo per trasparenza, con una colonna "Escl." nel
riepilogo a terminale).

### 1.4 `experiments/benchmark.py` — routing errato per `category=="dependency"`
`agent/agents/dependency_agent.py` è risultato **hardcoded** a leggere e
scrivere solo `requirements.txt` (non è stato modificato, come da vincolo
esplicito). Di conseguenza, instradare l'injection su un file diverso
(`package.json`, `ci.yml`) non renderebbe comunque questi casi risolvibili
dal sistema attuale. La fix adottata è quindi l'esclusione esplicita
(`EXCLUDED_DEPENDENCY_IDS`, 10 id — vedi §3) invece di un tentativo di
routing che l'agente non potrebbe comunque sfruttare.

### 1.5 Estensione `ALLOWED_TEST_FILES` / `reset_files()`
Necessaria come conseguenza di 1.3: senza whitelist, `reset_files()` avrebbe
cancellato ogni nuovo file di test ad ogni run. Aggiunto `GROUP1_TEST_FILES`
(29 nomi file) alla whitelist, e `GROUP1_RESTORE_PATHS` (elenco di path
`src/`, `app/`, `tests/` e due file di fixture) ripristinati via
`git checkout HEAD --` in `reset_files()`, stesso meccanismo già usato per
`tests/test_calculator.py` e `ci.yml`. Bonus: anche `tests/test_async.py`
(che prima non veniva mai ripristinato da git, solo protetto dalla
cancellazione) ora viene ripristinato correttamente.

**Importante**: questo meccanismo richiede che i file elencati in
`GROUP1_RESTORE_PATHS` siano **committati** — `git checkout HEAD -- <path>`
non ha effetto su file untracked. Finché questi file non vengono committati,
un run reale di `experiments/benchmark.py` lascerebbe i file modificati
dall'injection/dall'agente sporchi tra un caso e l'altro.

## 2. Gruppo 1 — stub creati per il dataset "test"

32 casi (`test_004,005,006,007,008,009,010,011,012,013,014,015,017,019,021,
022,023,024,025,026,027,028,029,030,031,033,035,040,041,045,049,050`) sono
ora genuinamente valutabili: modulo/file sorgente esiste prima dell'esecuzione
del caso, con comportamento "corretto" coerente con `expected_fix`, cosicché
l'injection lo rompa realmente.

**File creati** — moduli sorgente (`src/`): `utils.py`, `models.py`,
`services.py`, `auth.py`, `db.py`, `mailer.py`, `config.py`, `validator.py`,
`integration_db.py`, `serializer.py`, `parser.py`, `api.py`, `orders.py`,
`loader.py` (non referenziato dal test finale, vedi nota sotto),
`importer.py`, `registry.py`, `legacy.py`, `settings.py`, `sampler.py`,
`validation.py`, `scheduler.py`, `reports.py`, `logger.py`,
`billing_cycle.py`. `src/calculator.py` esteso con `power()`.

**Package `app/`** (nuovo, parallelo a `src/`): `app/billing/payment.py`,
`app/notify.py` — nomi di modulo dettati letteralmente da `expected_fix` dei
casi `test_023`/`test_028`.

**File di test creati** (`tests/`): 29 file, uno o più per modulo (es.
`test_math.py` copre `test_007`+`test_021`+`test_026` in un solo file, sul
modello già usato da `config`/`ci.yml`). `tests/test_api.py` esistente esteso
(copre `test_005`+`test_010`). Due file di fixture: `tests/data/sample.csv`,
`tests/fixtures/sample.json`.

**Nota su `src/loader.py`**: creato ma non più referenziato — il `git_diff`
di `test_025` descrive l'assegnazione del path direttamente nel file di
test (non tramite un helper), quindi lo stub finale costruisce il path
inline in `tests/test_loader.py`. Il modulo resta come stub inerte,
rimovibile.

## 3. Casi esclusi dal Success Rate (STORICO — superato, vedi §7)

### Categoria "test" (15 id, `EXCLUDED_TEST_IDS` in `benchmark.py`)
`test_016` (contenuto reale di `test_async.py` diverso dallo scenario),
`test_018` (richiede `freezegun`), `test_020`/`test_032` (timing/race
non deterministici), `test_034` (mock di rete rimosso → chiamata reale),
`test_036`/`test_048` (richiedono `pytest-xdist -n`), `test_037` (richiede
libreria di snapshot testing), `test_038` (richiede `alembic`+`sqlalchemy`),
`test_039` (rischio di hang infinito), `test_042` (richiede Redis),
`test_043` (richiede innescare un OOM reale), `test_044` (premessa non
valida: dict Python 3.7+ preserva l'ordine di inserimento a prescindere da
`PYTHONHASHSEED`), `test_046` (richiede runner macos-14/arm64),
`test_047` (caso composito, coverage gate non presente in `ci.yml`).

### Categoria "dependency" (10 id, `EXCLUDED_DEPENDENCY_IDS` in `benchmark.py`)
`dep_022`, `dep_023`, `dep_027`, `dep_029`, `dep_031`, `dep_032`, `dep_040`,
`dep_043`, `dep_045`, `dep_047` — tutti npm/yarn/JDK/ci.yml, fix reale non
esprimibile scrivendo solo `requirements.txt` (unico file che
`dependency_agent.py` può modificare).

### Riscritti come equivalenti Python (approvato esplicitamente)
- **`dep_026`**: da "poetry lock non rigenerato dopo modifica pyproject.toml"
  a "requirements.txt non rigenerato con pip-compile dopo modifica di
  requirements.in" (stessa lezione concettuale, `httpx` come dipendenza).
  `ci_logs`, `git_diff`, `expected_fix`, `notes` aggiornati; `id`,
  `category`, `difficulty` invariati.
- **`dep_030`**: da "npm audit segnala vulnerabilità" a "pip-audit segnala
  un pin vulnerabile (`pillow`), l'aggiornamento indicato punta a una
  versione inesistente". Stessi campi aggiornati.

Entrambi i casi risultano ora genuinamente iniettabili/risolvibili tramite
`requirements.txt` (verificato).

## 4. Mappatura finale dei 150 casi (STORICO — superato, vedi §7)

| Categoria | Attivi (contano nel SR) | Esclusi | Totale |
|---|---|---|---|
| dependency | 40 | 10 | 50 |
| test | 35 (3 preesistenti + 32 Gruppo 1) | 15 | 50 |
| config | 50 | 0 | 50 |
| **Totale** | **125** | **25** | **150** |

## 5. Verifica eseguita

Script temporaneo (`_verify_injections.py`, rimosso dopo l'uso) che per
ognuno dei 32 casi Gruppo 1: fa uno snapshot dei file coinvolti, chiama
`inject_error()`, esegue `pytest tests/` e verifica un `returncode != 0`
("rosso"), ripristina lo snapshot e verifica che torni verde. Risultato
finale: **32/32 casi verificati correttamente**. Durante la verifica sono
stati scoperti e corretti 5 bug reali nel design iniziale degli stub:

1. `test_014`: mismatch di virgolette/virgola tra `git_diff` e `src/config.py`
   — l'injection falliva silenziosamente (nessun match testuale).
2. `test_026`: mismatch di spaziatura nella lista `parametrize` tra
   `git_diff` e `tests/test_math.py` — stesso problema.
3. `test_028`: `git_diff` usa la sintassi decoratore `@patch(...)`, lo stub
   iniziale usava la sintassi context-manager `with patch(...)` — nessun
   match testuale possibile; riscritto con la sintassi decoratore.
4. `test_033`: `git_diff` con 3 righe rimosse e 2 aggiunte — lo zip use
   dal find/replace generico accoppiava solo le prime 2, lasciando una riga
   orfana (`NameError` invece del comportamento voluto). Aggiunto
   `_inject_test_033` dedicato.
5. `test_050`: sottrarre due `datetime` aware con lo **stesso oggetto
   tzinfo** fa sì che Python ignori l'offset (comportamento documentato ma
   controintuitivo) — il salto DST non veniva rilevato. Corretto convertendo
   esplicitamente a UTC prima della sottrazione, sia nel test sia in
   `src/billing_cycle.py`.

Un sesto problema (non un bug, ma un rischio di flakiness) è stato corretto
preventivamente: lo stub iniziale di `test_029` usava un `set()` per
simulare un ordine di iterazione "non garantito", ma con hash randomization
l'ordine coincide casualmente con quello alfabetico circa il 50% delle
volte (con 2 elementi) — reso deterministico usando l'ordine di inserimento
di un `dict` (`src/registry.py`) invece dell'ordine hash-dipendente di un
`set`.

## 6. Prossimo passo (STORICO — vedi §7 per lo stato attuale)

I file nuovi/modificati non sono ancora stati committati (per policy: si
committa solo su richiesta esplicita). Perché `reset_files()` funzioni
correttamente in un run reale del benchmark, è necessario `git add` +
commit di tutti i file elencati in `GROUP1_RESTORE_PATHS`
(`experiments/benchmark.py`), oltre ai file di fix isolati.

## 7. Sostituzione dei 25 casi esclusi — 150/150 casi ora attivi

Data: 2026-08-25. I 25 casi elencati in §3 (15 `test`, 10 `dependency`) sono
stati **sostituiti** con scenari nuovi, realmente iniettabili e risolvibili
dal sistema attuale. `EXCLUDED_TEST_IDS`, `EXCLUDED_DEPENDENCY_IDS` e tutta
la logica di esclusione associata (`final_status="excluded"` in
`run_model()`, colonna "Escl." in `print_summary()`) sono state **rimosse**
da `experiments/benchmark.py`. Il dataset ora conta **150/150 casi attivi**,
0 esclusi.

### 7.1 Vincolo di design scoperto

`agent/agents/test_agent.py::test_agent_node` scrive **sempre e solo** il
file di test risolto da `find_test_file(ci_logs)`, mai un file `src/`
(anche quando il prompt gli chiede di distinguere "test sbagliato" da
"sorgente sbagliato" — il codice applica comunque il fix al file di test).
Per questo tutti i 15 nuovi casi "test" sono bug **nel file di test stesso**
(assert o dato di test errato), mai nel sorgente — è l'unico tipo di fix che
l'agente può realmente applicare. I casi preesistenti che instradano
l'injection su un modulo `src/` (`TEST_TARGET_OVERRIDE`, es. `test_009`)
funzionano perché il fix reale è comunque "aggiorna il test per riflettere
il rename/cambiamento legittimo nel sorgente" — non si applica a un bug reale
nel sorgente, che l'agente non potrebbe correggere.

`agent/agents/dependency_agent.py` riscrive sempre l'intero
`requirements.txt`: ogni nuovo caso "dependency" usa pacchetti PyPI reali
(non nomi fittizi), perché la CI esegue un vero `pip install`.

### 7.2 Dependency — 10 casi sostituiti (tutti puro `requirements.txt`)

| id | difficulty | scenario | verificato con |
|---|---|---|---|
| dep_022 | easy | typo `flaks==3.0.3` | `pip install --dry-run` reale |
| dep_023 | easy | `pyyaml=6.0.1` (singolo `=`) | idem |
| dep_027 | easy | riga in stile JSON `"requests": "2.31.0"` | idem |
| dep_029 | easy | `pywin32==306` (Windows-only) su runner Linux | injection verificata strutturalmente (falso negativo su sandbox Windows locale, vedi nota sotto) |
| dep_031 | easy | marker troncato `requests==2.31.0; python_version` | `pip install --dry-run` reale |
| dep_032 | medium | `sphinx==7.2.6` + `docutils==0.22` (sphinx richiede `docutils<0.21`) | idem |
| dep_040 | medium | range auto-contraddittorio `click<8.0,>=9.0` | idem |
| dep_043 | hard | `pandas==2.0.3` + `numpy==2.0.0` (pandas richiede `numpy<2`) | idem |
| dep_045 | hard | `-c constraints.txt` inesistente | idem |
| dep_047 | hard | `streamlit==1.28.0` + `protobuf==5.28.0` (streamlit richiede `protobuf<5`) | idem |

Nota `dep_029`: essendo l'unico caso legato alla piattaforma, `pip install
--dry-run` su questo sandbox di sviluppo Windows non fallisce (pywin32 ha
wheel per win_amd64) — falso negativo locale atteso. Sul runner CI reale
(`ubuntu-latest`, vedi `.github/workflows/ci.yml`) fallisce sempre, come
descritto nei `ci_logs`. La verifica locale si è limitata a controllare che
l'injection scriva davvero `pywin32==306` in `requirements.txt`.

Tutti i vincoli di versione citati sopra (es. `sphinx 7.2.6 depends on
docutils<0.21`, `pandas 2.0.3 depends on numpy<2`, `streamlit 1.28.0 depends
on protobuf<5`) sono stati **verificati con `pip install --dry-run` reale
contro PyPI**, sia per lo stato "rotto" (exit code ≠ 0) sia per il fix
proposto (exit code 0) — non sono vincoli inventati.

### 7.3 Test — 15 casi sostituiti (bug deterministico nel file di test)

Ogni caso ha un nuovo modulo `src/` + file `tests/` (elenco completo in
`GROUP1_RESTORE_PATHS`/`REPLACEMENT_TEST_FILES` in `benchmark.py`), usa solo
la standard library + `pytest`/`pytest-cov` (nessuna dipendenza esterna non
presente in `requirements.txt` di produzione), ed è deterministico al 100%
(nessun `time.sleep`, nessun threading reale, nessuna rete reale).

| id | difficulty | src/ nuovo | sostituisce |
|---|---|---|---|
| test_016 | hard | `fetcher.py` | pytest-asyncio → solo `asyncio` stdlib, injector dedicato `_inject_test_016` |
| test_018 | hard | `cache.py` | freezegun → clock fittizio iniettabile |
| test_020 | hard | `counter.py` | race condition reale → simulazione sequenziale deterministica |
| test_032 | medium | `worker.py` | timing/sleep → coda di task troncata |
| test_034 | medium | `weather.py` | mock di rete rimosso → fetch iniettabile con default deterministicamente fallimentare |
| test_036 | medium | `exporter.py` | pytest-xdist → collisione di path con scrittura esclusiva (`O_EXCL`) |
| test_037 | medium | `summary.py` | libreria di snapshot testing → confronto diretto con assert |
| test_038 | medium | `orders.py` (esteso) | alembic/sqlalchemy → default di campo cambiato in un modello Python semplice |
| test_039 | medium | `pipeline.py` | deadlock reale → inversione producer/consumer (`IndexError` immediato) |
| test_042 | hard | `metrics.py` | Redis → store in-memory con namespace collidenti |
| test_043 | hard | `image_cache.py` | OOM reale → conteggio deterministico di entry accumulate |
| test_044 | hard | `dedup.py` | premessa errata su `PYTHONHASHSEED` → assert con ordine alfabetico errato (corregge anche il fatto tecnico sbagliato dell'originale) |
| test_046 | hard | `stats.py` | dipendenza da arch macos-14/arm64 → stesso problema (confronto float esatto) riproducibile su qualunque piattaforma |
| test_047 | hard | `recommender.py` | sort instabile + coverage gate non configurato → caso composito nel file di test, injector dedicato `_inject_test_047` |
| test_048 | hard | `upload.py` | pytest-xdist + oggetto non picklabile → stato condiviso per errore tra due istanze, singolo processo |

`tests/test_orders.py`/`src/orders.py` (già usati dal caso preesistente
`test_024`) sono stati **estesi**, non sostituiti: aggiunta una nuova
funzione di test (`test_order_status`) e un nuovo campo con default
(`status="pending"`) in `create_order`, senza toccare `test_create_order`.
`tests/test_async.py` esisteva già (con contenuto scollegato dallo scenario,
vedi §3) ed è stato riscritto da zero.

### 7.4 Modifiche a `experiments/benchmark.py`

- Rimossi `EXCLUDED_TEST_IDS`, `EXCLUDED_DEPENDENCY_IDS` e ogni riferimento.
- `GROUP1_TEST_FILES` invariato; aggiunto un nuovo set `REPLACEMENT_TEST_FILES`
  (13 nomi) unito ad `ALLOWED_TEST_FILES`.
- `GROUP1_RESTORE_PATHS` esteso con i 14 nuovi `src/*.py` e (via
  `REPLACEMENT_TEST_FILES`) i 13 nuovi `tests/*.py`.
- `SPECIAL_TEST_INJECTORS` esteso con `_inject_test_016` (blocco multi-riga,
  wrapper asyncio nested) e `_inject_test_047` (sostituzione dell'intero
  contenuto del file, caso composito). Nessuna chiave preesistente toccata.
- `TEST_TARGET_OVERRIDE` invariato — nessuno dei 15 nuovi casi lo richiede.

### 7.5 Verifica eseguita

Script temporaneo (`_verify_replacements.py`, rimosso dopo l'uso), stesso
schema del Gruppo 1 (snapshot → `inject_error()` → verifica rosso →
ripristino → verifica verde), con due differenze:

- I nuovi file `src/`/`tests/` sono ancora **untracked** in git in questa
  sessione, quindi `reset_files()` (che usa `git checkout HEAD --`) non può
  ripristinarli — lo script ha fatto uno snapshot/restore manuale in memoria
  per bypassare il problema. **Vale lo stesso vincolo già documentato in
  §"Prossimo passo": senza commit di questi file, un run reale del benchmark
  lascerebbe i file sporchi tra un caso e l'altro.**
- Per i 10 casi `dependency`, il "rosso"/"verde" è stato verificato con un
  vero `pip install --dry-run -r requirements.txt` (non solo con l'assenza
  di eccezioni), per confermare che i conflitti/errori PyPI citati nei
  `ci_logs` sono reali.

Risultato finale: **25/25 casi verificati correttamente** (rosso
sull'injection, verde dopo il ripristino/fix).

### 7.6 Mappatura finale dei 150 casi (aggiornata)

| Categoria | Attivi (contano nel SR) | Esclusi | Totale |
|---|---|---|---|
| dependency | 50 | 0 | 50 |
| test | 50 | 0 | 50 |
| config | 50 | 0 | 50 |
| **Totale** | **150** | **0** | **150** |

### 7.7 Prossimo passo

Come già per il Gruppo 1: i file nuovi (14 `src/*.py`, 13 `tests/*.py`) e
modificati (`src/orders.py`, `tests/test_orders.py`, `tests/test_async.py`,
`experiments/dataset.py`, `experiments/benchmark.py`) non sono ancora stati
committati (per policy: si committa solo su richiesta esplicita). Perché
`reset_files()` funzioni correttamente in un run reale del benchmark, è
necessario `git add` + commit di tutti questi file.
