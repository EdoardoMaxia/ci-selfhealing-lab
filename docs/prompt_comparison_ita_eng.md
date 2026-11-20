# Confronto prompt italiani → inglesi

## Commit di traduzione: `366b417` (12 novembre 2026)
## Analisi: 20 novembre 2026 — su `msr-revision` @ `ab49660`

Domanda del professore: il calo di Mistral 7B dopo la traduzione IT→EN dipende da un'istruzione cambiata oppure dalla sensibilità del modello alla lingua? Questo documento confronta riga per riga tutti i testi tradotti che arrivano ai modelli (system prompt, user message, testi dei tentativi, history, episodi di memoria) e documenta anche le stringhe tradotte che non arrivano ai modelli.

### Sommario

- File modificati dal commit: **26** (21 in `agent/`, 5 script fuori da `agent/`).
- File che contengono testo inviato ai modelli: **5** (`router.py`, `dependency_agent.py`, `test_agent.py`, `config_agent.py`, `episodic_store.py`).
- Stringhe tradotte in questi 5 file: **59**, di cui **28** arrivano al modello e 31 no (docstring, log, messaggi d'errore).
- Righe di prompt confrontate (non vuote): **144** — 98 tradotte ed equivalenti ✅, 45 identiche (segnaposto, delimitatori di codice, chiavi JSON), 1 ⚠️.
- Istruzioni aggiunte: **0**.
- Istruzioni rimosse: **0**.
- Istruzioni modificate (non solo tradotte): **1**, nel Router: il campo libero `reasoning` del JSON passa da "spiegazione breve in italiano" a "short explanation in English". **Nessuna** nel Dependency Agent e nel Config Agent.
- Indentazione e spazi finali identici in tutte le 144 coppie di righe.
- Struttura del codice identica prima e dopo il commit (AST con le stringhe mascherate) in 25 file su 26; l'eccezione è `agent/tests/test_memory.py` (rinomina di una variabile locale in uno script di test).
- Modifiche ai prompt dopo la traduzione: **nessuna** (§7).

### Metodo

1. Per ogni file toccato dal commit, il sorgente prima (`366b417^`) e dopo (`366b417`) è stato analizzato con `ast`: sostituendo ogni stringa con un segnaposto, i due alberi sintattici risultano identici. Quindi il commit cambia solo testi, e le stringhe si possono appaiare 1:1 per posizione.
2. Le f-string sono riportate per intero, con le espressioni tra graffe; il testo nelle tabelle è quello esatto del codice (spazi iniziali rimossi solo per leggibilità, ma verificati identici).
3. Per ogni stringa è stato seguito il flusso dei dati nel codice per stabilire se arriva al modello (es. `fix_applied` della history entra nel prompt del tentativo 2 come `{prev}`; il `fix_applied` dello stato no).
4. Ogni riga che arriva al modello è stata valutata a mano: ✅ = traduzione equivalente, = identica, ⚠️ = istruzione cambiata.

---

### 1. Router Agent (`agent/agents/router.py`)

Stringhe cambiate nel commit: 6, di cui 2 arrivano al modello. Struttura del codice (AST con stringhe mascherate) identica: sì.

#### 1.1 System prompt

**System prompt (`ROUTER_SYSTEM_PROMPT`)** — riga 43

| # | Italiano | English | Equivalente? | Nota |
|---|---|---|:---:|---|
| 1 | `Sei un esperto di CI/CD e DevOps. Il tuo compito è classificare` | `You are a CI/CD and DevOps expert. Your task is to classify` | ✅ |  |
| 2 | `il tipo di errore di una pipeline CI analizzando i log.` | `the type of error of a CI pipeline by analyzing its logs.` | ✅ |  |
| 3 | `Categorie disponibili:` | `Available categories:` | ✅ |  |
| 4 | `- DEPENDENCY: errori su librerie, pip install fallito, ModuleNotFoundError,` | `- DEPENDENCY: library errors, failed pip install, ModuleNotFoundError,` | ✅ |  |
| 5 | `versioni incompatibili, ImportError, package not found` | `incompatible versions, ImportError, package not found` | ✅ |  |
| 6 | `- TEST: test falliti, AssertionError, fixture rotte, mock issues,` | `- TEST: failed tests, AssertionError, broken fixtures, mock issues,` | ✅ |  |
| 7 | `pytest failures, coverage insufficiente` | `pytest failures, insufficient coverage` | ✅ |  |
| 8 | `- CONFIG: errori YAML, variabili d'ambiente mancanti, Docker issues,` | `- CONFIG: YAML errors, missing environment variables, Docker issues,` | ✅ |  |
| 9 | `secrets non configurati, errori di sintassi nel file CI` | `unconfigured secrets, syntax errors in the CI file` | ✅ |  |
| 10 | `- UNKNOWN: non riconducibile alle categorie precedenti` | `- UNKNOWN: not attributable to the previous categories` | ✅ |  |
| 11 | `Rispondi ESCLUSIVAMENTE con un JSON valido, senza testo aggiuntivo:` | `Respond EXCLUSIVELY with a valid JSON, without additional text:` | ✅ |  |
| 12 | `{` | `{` | = identica |  |
| 13 | `"category": "DEPENDENCY\|TEST\|CONFIG\|UNKNOWN",` | `"category": "DEPENDENCY\|TEST\|CONFIG\|UNKNOWN",` | = identica |  |
| 14 | `"confidence": 0.0-1.0,` | `"confidence": 0.0-1.0,` | = identica |  |
| 15 | `"reasoning": "spiegazione breve in italiano di max 2 righe"` | `"reasoning": "short explanation in English, max 2 lines"` | ⚠️ | Unica istruzione non solo tradotta: cambia la lingua richiesta per il campo libero `reasoning` (IT→EN). Non tocca `category` né `confidence`; `router_reasoning` non viene passato agli agenti specialisti (compare solo nel corpo della PR). |
| 16 | `}` | `}` | = identica |  |

#### 1.2 User message template

**User message (`user_message` in `router_node`)** — riga 73

| # | Italiano | English | Equivalente? | Nota |
|---|---|---|:---:|---|
| 1 | `Analizza questo errore CI e classificalo.` | `Analyze this CI error and classify it.` | ✅ |  |
| 2 | `**Job fallito:** {state['ci_job_name']}` | `**Failed job:** {state['ci_job_name']}` | ✅ |  |
| 3 | `**Conclusione:** {state['ci_conclusion']}` | `**Conclusion:** {state['ci_conclusion']}` | ✅ |  |
| 4 | `**Commit SHA:** {state['commit_sha'][:8]}` | `**Commit SHA:** {state['commit_sha'][:8]}` | = identica |  |
| 5 | `**Log CI (ultimi 100 righe):**` | `**CI log (last 100 lines):**` | ✅ | Imprecisa in entrambe le versioni: il codice passa gli ultimi 3000 caratteri. |
| 6 | `` ``` `` | `` ``` `` | = identica |  |
| 7 | `{state['ci_logs'][-3000:]}` | `{state['ci_logs'][-3000:]}` | = identica |  |
| 8 | `` ``` `` | `` ``` `` | = identica |  |
| 9 | `**Git diff del commit:**` | `**Git diff of the commit:**` | ✅ |  |
| 10 | `` ``` `` | `` ``` `` | = identica |  |
| 11 | `{state.get('git_diff', 'Non disponibile')[:1500]}` | `{state.get('git_diff', 'Not available')[:1500]}` | ✅ | Valore di default mai usato nel benchmark (`git_diff` è sempre presente). |
| 12 | `` ``` `` | `` ``` `` | = identica |  |
| 13 | `Classifica l'errore rispondendo SOLO con il JSON richiesto.` | `Classify the error by responding ONLY with the requested JSON.` | ✅ |  |

#### 1.3 Altre stringhe tradotte (non arrivano al modello)

| Riga | Tipo | Italiano | English |
|---|---|---|---|
| 13 | docstring | `Rimuove i blocchi di reasoning <think>...</think> che alcuni modelli ⏎ (es. Qwen3.8, Qwen3-Coder via Ollama) anteponte alla risposta vera e ⏎ propria. Va chiamata PRIMA di qualunque parsing (JSON o contenuto file).` | `Removes the <think>...</think> reasoning blocks that some models ⏎ (e.g. Qwen3.8, Qwen3-Coder via Ollama) prepend to the actual answer. ⏎ Must be called BEFORE any parsing (JSON or file content).` |
| 39 | eccezione | `Provider non supportato: {LLM_PROVIDER}` | `Unsupported provider: {LLM_PROVIDER}` |
| 66 | docstring | `Nodo Router: classifica il tipo di errore CI usando LLM. ⏎ Riceve lo State e restituisce gli aggiornamenti da applicare.` | `Router node: classifies the type of CI error using an LLM. ⏎ Receives the State and returns the updates to apply.` |
| 115 | fallback di `router_reasoning` (letto da `benchmark.py`, tradotto nello stesso commit) | `Parsing fallito` | `Parsing failed` |

Commenti nel codice tradotti: 8 (irrilevanti per il modello).

### 2. Dependency Agent (`agent/agents/dependency_agent.py`)

Stringhe cambiate nel commit: 17, di cui 8 arrivano al modello. Struttura del codice (AST con stringhe mascherate) identica: sì.

#### 2.1 System prompt

**System prompt (`DEPENDENCY_SYSTEM_PROMPT`)** — riga 21

| # | Italiano | English | Equivalente? | Nota |
|---|---|---|:---:|---|
| 1 | `Sei un esperto di gestione delle dipendenze Python.` | `You are an expert in Python dependency management.` | ✅ |  |
| 2 | `Il tuo compito è analizzare un errore di dipendenza in una CI pipeline` | `Your task is to analyze a dependency error in a CI pipeline` | ✅ |  |
| 3 | `e generare il contenuto CORRETTO e COMPLETO del file requirements.txt.` | `and generate the CORRECT and COMPLETE content of the requirements.txt file.` | ✅ |  |
| 4 | `Regole:` | `Rules:` | ✅ |  |
| 5 | `1. Analizza i log per capire QUALE dipendenza ha causato il fallimento` | `1. Analyze the logs to understand WHICH dependency caused the failure` | ✅ |  |
| 6 | `2. Usa il contenuto attuale del requirements.txt come base` | `2. Use the current content of requirements.txt as the base` | ✅ |  |
| 7 | `3. Genera il file requirements.txt corretto e completo` | `3. Generate the correct and complete requirements.txt file` | ✅ |  |
| 8 | `4. Rispondi SOLO con il contenuto del file, senza spiegazioni né markdown` | `4. Respond ONLY with the file content, without explanations or markdown` | ✅ |  |
| 9 | `Strategie per tentativo:` | `Strategies per attempt:` | ✅ |  |
| 10 | `- Tentativo 1: pin della versione corretta (es. numpy==1.24.0)` | `- Attempt 1: pin the correct version (e.g. numpy==1.24.0)` | ✅ |  |
| 11 | `- Tentativo 2: aggiorna il gruppo di dipendenze correlate` | `- Attempt 2: update the group of related dependencies` | ✅ |  |
| 12 | `- Tentativo 3: usa fix simili dal contesto storico fornito` | `- Attempt 3: use similar fixes from the provided historical context` | ✅ |  |

#### 2.2 User message template

**User message (`user_message`)** — riga 119

| # | Italiano | English | Equivalente? | Nota |
|---|---|---|:---:|---|
| 1 | `**Strategia per questo tentativo:** {attempt_context}` | `**Strategy for this attempt:** {attempt_context}` | ✅ |  |
| 2 | `**Log CI con l'errore:**` | `**CI log with the error:**` | ✅ |  |
| 3 | `` ``` `` | `` ``` `` | = identica |  |
| 4 | `{state['ci_logs'][-2000:]}` | `{state['ci_logs'][-2000:]}` | = identica |  |
| 5 | `` ``` `` | `` ``` `` | = identica |  |
| 6 | `**requirements.txt attuale:**` | `**Current requirements.txt:**` | ✅ |  |
| 7 | `` ``` `` | `` ``` `` | = identica |  |
| 8 | `{current_requirements}` | `{current_requirements}` | = identica |  |
| 9 | `` ``` `` | `` ``` `` | = identica |  |
| 10 | `**Git diff del commit che ha causato il fallimento:**` | `**Git diff of the commit that caused the failure:**` | ✅ |  |
| 11 | `` ``` `` | `` ``` `` | = identica |  |
| 12 | `{state.get('git_diff', 'Non disponibile')}` | `{state.get('git_diff', 'Not available')}` | ✅ | Valore di default mai usato nel benchmark (`git_diff` è sempre presente). |
| 13 | `` ``` `` | `` ``` `` | = identica |  |
| 14 | `Genera il contenuto COMPLETO e CORRETTO del nuovo requirements.txt.` | `Generate the COMPLETE and CORRECT content of the new requirements.txt.` | ✅ |  |
| 15 | `Rispondi SOLO con il contenuto del file, senza backtick né spiegazioni.` | `Respond ONLY with the file content, without backticks or explanations.` | ✅ |  |

#### 2.3 Testi dei tentativi, history ed episodi

**`attempt_context`, tentativo 1** — riga 91

| # | Italiano | English | Equivalente? | Nota |
|---|---|---|:---:|---|
| 1 | `Applica un fix CONSERVATIVO: pinna solo la versione della dipendenza rotta.` | `Apply a CONSERVATIVE fix: pin only the version of the broken dependency.` | ✅ |  |

**`prev` di default al tentativo 2 (solo se la history è vuota)** — riga 93

| # | Italiano | English | Equivalente? | Nota |
|---|---|---|:---:|---|
| 1 | `nessuno` | `none` | ✅ |  |

**`attempt_context`, tentativo 2** — riga 94

| # | Italiano | English | Equivalente? | Nota |
|---|---|---|:---:|---|
| 1 | `Il tentativo precedente ha fallito: {prev}` | `The previous attempt failed: {prev}` | ✅ |  |
| 2 | `Applica un fix PIU AMPIO: aggiorna tutte le dipendenze correlate al problema.` | `Apply a BROADER fix: update all the dependencies related to the problem.` | ✅ |  |

**`attempt_context`, tentativo 3** — riga 107

| # | Italiano | English | Equivalente? | Nota |
|---|---|---|:---:|---|
| 1 | `I tentativi precedenti hanno fallito:` | `The previous attempts failed:` | ✅ |  |
| 2 | `{prev_list}` | `{prev_list}` | = identica |  |
| 3 | `{memory_context}` | `{memory_context}` | = identica |  |
| 4 | `Usa le informazioni dalla memoria per proporre un fix diverso dai precedenti.` | `Use the information from memory to propose a fix different from the previous ones.` | ✅ |  |

**`fix_applied` nella history → `{prev}` (T2), `{prev_list}` (T3), episodi di memoria** — riga 171

| # | Italiano | English | Equivalente? | Nota |
|---|---|---|:---:|---|
| 1 | `requirements.txt aggiornato (tentativo {attempt})` | `requirements.txt updated (attempt {attempt})` | ✅ |  |

**output di `compute_diff` senza modifiche → `fix_diff` → episodi di memoria (T3, solo run con memoria)** — riga 69

| # | Italiano | English | Equivalente? | Nota |
|---|---|---|:---:|---|
| 1 | `(nessuna modifica rilevata)` | `(no changes detected)` | ✅ |  |

#### 2.4 Altre stringhe tradotte (non arrivano al modello)

| Riga | Tipo | Italiano | English |
|---|---|---|---|
| 40 | docstring | `Legge il requirements.txt dal repo locale.` | `Reads requirements.txt from the local repo.` |
| 49 | docstring | `Scrive il nuovo requirements.txt sul disco.` | `Writes the new requirements.txt to disk.` |
| 52 | print/log | `✍️  requirements.txt aggiornato in {req_path}` | `✍️  requirements.txt updated in {req_path}` |
| 57 | docstring | `Diff riga per riga, preserva l'ordine.` | `Line-by-line diff, preserves ordering.` |
| 73 | docstring | `Nodo Dependency Agent: genera e applica un fix al requirements.txt.` | `Dependency Agent node: generates and applies a fix to requirements.txt.` |
| 82 | print/log | `📦 Dependency Agent — Tentativo {attempt}/3` | `📦 Dependency Agent — Attempt {attempt}/3` |
| 115 | print/log | `🧠 Memoria: trovati {len(similar)} episodi simili` | `🧠 Memory: found {len(similar)} similar episodes` |
| 161 | print/log | `Modifiche: ⏎ {diff}` | `Changes: ⏎ {diff}` |
| 178 | `fix_applied` dello stato (non usato nei prompt) | `Dependency fix tentativo {attempt}: {diff[:100]}` | `Dependency fix attempt {attempt}: {diff[:100]}` |

Commenti nel codice tradotti: 12 (irrilevanti per il modello).

### 3. Test Agent (`agent/agents/test_agent.py`)

Stringhe cambiate nel commit: 14, di cui 8 arrivano al modello. Struttura del codice (AST con stringhe mascherate) identica: sì.

#### 3.1 System prompt

**System prompt (`TEST_SYSTEM_PROMPT`)** — riga 16

| # | Italiano | English | Equivalente? | Nota |
|---|---|---|:---:|---|
| 1 | `Sei un esperto di testing Python con pytest.` | `You are an expert in Python testing with pytest.` | ✅ |  |
| 2 | `Il tuo compito è analizzare un test fallito e proporre il fix corretto.` | `Your task is to analyze a failed test and propose the correct fix.` | ✅ |  |
| 3 | `REGOLA CRITICA: devi distinguere due scenari:` | `CRITICAL RULE: you must distinguish between two scenarios:` | ✅ |  |
| 4 | `1. Il TEST è sbagliato (assert con valore errato, mock non aggiornato) → fix il test` | `1. The TEST is wrong (assert with wrong value, outdated mock) → fix the test` | ✅ |  |
| 5 | `2. Il CODICE SORGENTE è sbagliato → fix il codice sorgente` | `2. The SOURCE CODE is wrong → fix the source code` | ✅ |  |
| 6 | `In entrambi i casi, rispondi con il contenuto COMPLETO e CORRETTO del file` | `In both cases, respond with the COMPLETE and CORRECT content of the file` | ✅ |  |
| 7 | `da modificare. Rispondi SOLO con il contenuto del file, senza markdown né spiegazioni.` | `to modify. Respond ONLY with the file content, without markdown or explanations.` | ✅ |  |
| 8 | `Strategie per tentativo:` | `Strategies per attempt:` | ✅ |  |
| 9 | `- Tentativo 1: fix minimale — cambia solo la riga che causa il fallimento` | `- Attempt 1: minimal fix — change only the line causing the failure` | ✅ |  |
| 10 | `- Tentativo 2: fix contestuale — aggiorna anche i test correlati o il setup` | `- Attempt 2: contextual fix — also update related tests or the setup` | ✅ |  |
| 11 | `- Tentativo 3: approccio diverso dai precedenti — considera di riscrivere il test` | `- Attempt 3: approach different from the previous ones — consider rewriting the test` | ✅ |  |

#### 3.2 User message template

**User message (`user_message`)** — riga 116

| # | Italiano | English | Equivalente? | Nota |
|---|---|---|:---:|---|
| 1 | `**Strategia:** {attempt_context}` | `**Strategy:** {attempt_context}` | ✅ |  |
| 2 | `**Log CI (errore pytest):**` | `**CI log (pytest error):**` | ✅ |  |
| 3 | `` ``` `` | `` ``` `` | = identica |  |
| 4 | `{state['ci_logs'][-2000:]}` | `{state['ci_logs'][-2000:]}` | = identica |  |
| 5 | `` ``` `` | `` ``` `` | = identica |  |
| 6 | `**Contenuto attuale del file di test ({test_file}):**` | `**Current content of the test file ({test_file}):**` | ✅ |  |
| 7 | `` ```python `` | `` ```python `` | = identica |  |
| 8 | `{test_code}` | `{test_code}` | = identica |  |
| 9 | `` ``` `` | `` ``` `` | = identica |  |
| 10 | `**Codice sorgente (per contesto):**` | `**Source code (for context):**` | ✅ |  |
| 11 | `` ```python `` | `` ```python `` | = identica |  |
| 12 | `{src_code}` | `{src_code}` | = identica |  |
| 13 | `` ``` `` | `` ``` `` | = identica |  |
| 14 | `**Git diff del commit:**` | `**Git diff of the commit:**` | ✅ |  |
| 15 | `` ``` `` | `` ``` `` | = identica |  |
| 16 | `{state.get('git_diff', 'N/A')}` | `{state.get('git_diff', 'N/A')}` | = identica |  |
| 17 | `` ``` `` | `` ``` `` | = identica |  |
| 18 | `Genera il contenuto COMPLETO e CORRETTO del file di test.` | `Generate the COMPLETE and CORRECT content of the test file.` | ✅ |  |
| 19 | `Rispondi SOLO con il codice Python, senza backtick né spiegazioni.` | `Respond ONLY with the Python code, without backticks or explanations.` | ✅ |  |

#### 3.3 Testi dei tentativi, history ed episodi

**`attempt_context`, tentativo 1** — riga 91

| # | Italiano | English | Equivalente? | Nota |
|---|---|---|:---:|---|
| 1 | `Fix MINIMALE: correggi solo la riga che causa il fallimento.` | `MINIMAL fix: correct only the line causing the failure.` | ✅ |  |

**`prev` di default al tentativo 2 (solo se la history è vuota)** — riga 93

| # | Italiano | English | Equivalente? | Nota |
|---|---|---|:---:|---|
| 1 | `nessuno` | `none` | ✅ |  |

**`attempt_context`, tentativo 2** — riga 94

| # | Italiano | English | Equivalente? | Nota |
|---|---|---|:---:|---|
| 1 | `Il tentativo precedente ({prev}) ha fallito. Fix PIÙ AMPIO: aggiorna anche i test correlati.` | `The previous attempt ({prev}) failed. BROADER fix: also update the related tests.` | ✅ |  |

**`attempt_context`, tentativo 3** — riga 106

| # | Italiano | English | Equivalente? | Nota |
|---|---|---|:---:|---|
| 1 | `I tentativi precedenti hanno fallito:` | `The previous attempts failed:` | ✅ |  |
| 2 | `{prev_list}` | `{prev_list}` | = identica |  |
| 3 | `{memory_context}` | `{memory_context}` | = identica |  |
| 4 | `Usa le informazioni dalla memoria per proporre un fix diverso dai precedenti.` | `Use the information from memory to propose a fix different from the previous ones.` | ✅ |  |

**`fix_applied` nella history → `{prev}` (T2), `{prev_list}` (T3), episodi di memoria** — riga 167

| # | Italiano | English | Equivalente? | Nota |
|---|---|---|:---:|---|
| 1 | `test file aggiornato (tentativo {attempt})` | `test file updated (attempt {attempt})` | ✅ |  |

**output di `compute_diff` senza modifiche → `fix_diff` → episodi di memoria (T3, solo run con memoria)** — riga 52

| # | Italiano | English | Equivalente? | Nota |
|---|---|---|:---:|---|
| 1 | `(nessuna modifica)` | `(no changes)` | ✅ |  |

#### 3.4 Altre stringhe tradotte (non arrivano al modello)

| Riga | Tipo | Italiano | English |
|---|---|---|---|
| 41 | print/log | `✍️  File aggiornato: {path}` | `✍️  File updated: {path}` |
| 56 | docstring | `Estrae il path del file di test dai log pytest. ⏎ Es: 'FAILED tests/test_calculator.py::test_add' → 'tests/test_calculator.py'` | `Extracts the test file path from the pytest logs. ⏎ E.g.: 'FAILED tests/test_calculator.py::test_add' → 'tests/test_calculator.py'` |
| 77 | print/log | `🧪 Test Agent — Tentativo {attempt}/3` | `🧪 Test Agent — Attempt {attempt}/3` |
| 114 | print/log | `🧠 Memoria: trovati {len(similar)} episodi simili` | `🧠 Memory: found {len(similar)} similar episodes` |
| 159 | print/log | `Modifiche: ⏎ {diff}` | `Changes: ⏎ {diff}` |
| 175 | `fix_applied` dello stato (non usato nei prompt) | `Test fix tentativo {attempt}: {diff[:80]}` | `Test fix attempt {attempt}: {diff[:80]}` |

Commenti nel codice tradotti: 8 (irrilevanti per il modello).

### 4. Config Agent (`agent/agents/config_agent.py`)

Stringhe cambiate nel commit: 13, di cui 8 arrivano al modello. Struttura del codice (AST con stringhe mascherate) identica: sì.

#### 4.1 System prompt

**System prompt (`CONFIG_SYSTEM_PROMPT`)** — riga 14

| # | Italiano | English | Equivalente? | Nota |
|---|---|---|:---:|---|
| 1 | `Sei un esperto di GitHub Actions e CI/CD pipelines.` | `You are an expert in GitHub Actions and CI/CD pipelines.` | ✅ |  |
| 2 | `Il tuo compito è analizzare un errore nel file .github/workflows/ci.yml` | `Your task is to analyze an error in the .github/workflows/ci.yml file` | ✅ |  |
| 3 | `e generare il contenuto CORRETTO e COMPLETO del file.` | `and generate the CORRECT and COMPLETE content of the file.` | ✅ |  |
| 4 | `Conoscenze chiave:` | `Key knowledge:` | ✅ |  |
| 5 | `- Versioni Python valide per actions/setup-python: 3.8, 3.9, 3.10, 3.11, 3.12` | `- Valid Python versions for actions/setup-python: 3.8, 3.9, 3.10, 3.11, 3.12` | ✅ |  |
| 6 | `- Versioni actions raccomandate: actions/checkout@v4, actions/setup-python@v5` | `- Recommended action versions: actions/checkout@v4, actions/setup-python@v5` | ✅ |  |
| 7 | `- Il file YAML deve avere indentazione a 2 spazi, mai tab` | `- The YAML file must use 2-space indentation, never tabs` | ✅ |  |
| 8 | `- I job devono avere almeno: runs-on, steps con checkout e setup` | `- Jobs must have at least: runs-on, steps with checkout and setup` | ✅ |  |
| 9 | `Rispondi SOLO con il contenuto YAML del file, senza backtick né spiegazioni.` | `Respond ONLY with the YAML content of the file, without backticks or explanations.` | ✅ |  |
| 10 | `Strategie per tentativo:` | `Strategies per attempt:` | ✅ |  |
| 11 | `- Tentativo 1: fix minimale — correggi solo la riga problematica` | `- Attempt 1: minimal fix — correct only the problematic line` | ✅ |  |
| 12 | `- Tentativo 2: fix strutturale — rivedi l'intera sezione con l'errore` | `- Attempt 2: structural fix — review the whole section containing the error` | ✅ |  |
| 13 | `- Tentativo 3: riscrivi il job completo con configurazione standard` | `- Attempt 3: rewrite the complete job with a standard configuration` | ✅ |  |

#### 4.2 User message template

**User message (`user_message`)** — riga 93

| # | Italiano | English | Equivalente? | Nota |
|---|---|---|:---:|---|
| 1 | `**Strategia:** {attempt_context}` | `**Strategy:** {attempt_context}` | ✅ |  |
| 2 | `**Log CI (errore):**` | `**CI log (error):**` | ✅ |  |
| 3 | `` ``` `` | `` ``` `` | = identica |  |
| 4 | `{state['ci_logs'][-2000:]}` | `{state['ci_logs'][-2000:]}` | = identica |  |
| 5 | `` ``` `` | `` ``` `` | = identica |  |
| 6 | `**Contenuto attuale di .github/workflows/ci.yml:**` | `**Current content of .github/workflows/ci.yml:**` | ✅ |  |
| 7 | `` ```yaml `` | `` ```yaml `` | = identica |  |
| 8 | `{current_yaml}` | `{current_yaml}` | = identica |  |
| 9 | `` ``` `` | `` ``` `` | = identica |  |
| 10 | `**Git diff del commit:**` | `**Git diff of the commit:**` | ✅ |  |
| 11 | `` ``` `` | `` ``` `` | = identica |  |
| 12 | `{state.get('git_diff', 'N/A')}` | `{state.get('git_diff', 'N/A')}` | = identica |  |
| 13 | `` ``` `` | `` ``` `` | = identica |  |
| 14 | `Genera il contenuto COMPLETO e CORRETTO del file ci.yml.` | `Generate the COMPLETE and CORRECT content of the ci.yml file.` | ✅ |  |
| 15 | `Rispondi SOLO con il YAML, senza backtick né spiegazioni.` | `Respond ONLY with the YAML, without backticks or explanations.` | ✅ |  |

#### 4.3 Testi dei tentativi, history ed episodi

**`attempt_context`, tentativo 1** — riga 68

| # | Italiano | English | Equivalente? | Nota |
|---|---|---|:---:|---|
| 1 | `Fix MINIMALE: correggi solo la riga che causa il fallimento.` | `MINIMAL fix: correct only the line causing the failure.` | ✅ |  |

**`prev` di default al tentativo 2 (solo se la history è vuota)** — riga 70

| # | Italiano | English | Equivalente? | Nota |
|---|---|---|:---:|---|
| 1 | `nessuno` | `none` | ✅ |  |

**`attempt_context`, tentativo 2** — riga 71

| # | Italiano | English | Equivalente? | Nota |
|---|---|---|:---:|---|
| 1 | `Tentativo precedente ({prev}) fallito. Rivedi l'intera sezione.` | `Previous attempt ({prev}) failed. Review the whole section.` | ✅ |  |

**`attempt_context`, tentativo 3** — riga 83

| # | Italiano | English | Equivalente? | Nota |
|---|---|---|:---:|---|
| 1 | `I tentativi precedenti hanno fallito:` | `The previous attempts failed:` | ✅ |  |
| 2 | `{prev_list}` | `{prev_list}` | = identica |  |
| 3 | `{memory_context}` | `{memory_context}` | = identica |  |
| 4 | `Usa le informazioni dalla memoria per proporre un fix diverso dai precedenti.` | `Use the information from memory to propose a fix different from the previous ones.` | ✅ |  |

**`fix_applied` nella history → `{prev}` (T2), `{prev_list}` (T3), episodi di memoria** — riga 138

| # | Italiano | English | Equivalente? | Nota |
|---|---|---|:---:|---|
| 1 | `ci.yml aggiornato (tentativo {attempt})` | `ci.yml updated (attempt {attempt})` | ✅ |  |

**output di `compute_diff` senza modifiche → `fix_diff` → episodi di memoria (T3, solo run con memoria)** — riga 53

| # | Italiano | English | Equivalente? | Nota |
|---|---|---|:---:|---|
| 1 | `(nessuna modifica)` | `(no changes)` | ✅ |  |

#### 4.4 Altre stringhe tradotte (non arrivano al modello)

| Riga | Tipo | Italiano | English |
|---|---|---|---|
| 42 | print/log | `✍️  ci.yml aggiornato` | `✍️  ci.yml updated` |
| 62 | print/log | `⚙️  Config Agent — Tentativo {attempt}/3` | `⚙️  Config Agent — Attempt {attempt}/3` |
| 91 | print/log | `🧠 Memoria: trovati {len(similar)} episodi simili` | `🧠 Memory: found {len(similar)} similar episodes` |
| 131 | print/log | `Modifiche: ⏎ {diff}` | `Changes: ⏎ {diff}` |
| 146 | `fix_applied` dello stato (non usato nei prompt) | `Config fix tentativo {attempt}: {diff[:80]}` | `Config fix attempt {attempt}: {diff[:80]}` |

Commenti nel codice tradotti: 3 (irrilevanti per il modello).

### 5. Episodic Store (`agent/memory/episodic_store.py`)

Stringhe cambiate nel commit: 9, di cui 2 arrivano al modello. Struttura del codice (AST con stringhe mascherate) identica: sì.

Le altre parti del testo degli episodi (`{i}. [similarity: …] {ep['fix_applied']}` e `Diff: …`) erano già in inglese anche nella versione italiana e non cambiano.

#### 5.1 Testi dei tentativi, history ed episodi

**`format_episodes_for_prompt` senza episodi → `{memory_context}` al tentativo 3 (sempre presente nei run no-memory, store vuoto)** — riga 144

| # | Italiano | English | Equivalente? | Nota |
|---|---|---|:---:|---|
| 1 | `Nessun episodio simile trovato in memoria.` | `No similar episode found in memory.` | ✅ |  |

**`format_episodes_for_prompt`, intestazione degli episodi recuperati (T3, run con memoria)** — riga 146

| # | Italiano | English | Equivalente? | Nota |
|---|---|---|:---:|---|
| 1 | `Fix simili dal passato (ordinati per similarità):` | `Similar past fixes (sorted by similarity):` | ✅ |  |

#### 5.2 Altre stringhe tradotte (non arrivano al modello)

| Riga | Tipo | Italiano | English |
|---|---|---|---|
| 14 | docstring | `Restituisce la collection ChromaDB, creandola se non esiste. ⏎ Usa l'embedding function di default (sentence-transformers locale) ⏎ oppure OpenAI se la key è disponibile.` | `Returns the ChromaDB collection, creating it if it does not exist. ⏎ Uses the default embedding function (local sentence-transformers) ⏎ or OpenAI if the key is available.` |
| 42 | docstring | `Salva un episodio in ChromaDB dopo il completamento di un ciclo. ⏎ outcome: "success" \| "failed" \| "escalated" ⏎ Ritorna l'ID dell'episodio salvato.` | `Saves an episode in ChromaDB after a cycle completes. ⏎ outcome: "success" \| "failed" \| "escalated" ⏎ Returns the ID of the saved episode.` |
| 83 | print/log | `💾 Episodio salvato in memoria (outcome: {outcome}, id: {episode_id[:8]})` | `💾 Episode saved to memory (outcome: {outcome}, id: {episode_id[:8]})` |
| 94 | docstring | `Recupera gli episodi più simili all'errore corrente. ⏎ only_successful=True filtra solo i fix che hanno funzionato. ⏎ Ritorna lista di dict con fix_applied, fix_diff, similarity score.` | `Retrieves the episodes most similar to the current error. ⏎ only_successful=True keeps only the fixes that worked. ⏎ Returns a list of dicts with fix_applied, fix_diff, similarity score.` |
| 119 | print/log | `⚠️ Errore retrieval: {e}` | `⚠️ Retrieval error: {e}` |
| 139 | docstring | `Formatta gli episodi recuperati in testo leggibile dall'LLM. ⏎ Usato come context nel prompt del tentativo 3.` | `Formats the retrieved episodes as text readable by the LLM. ⏎ Used as context in the attempt-3 prompt.` |
| 156 | docstring | `Statistiche sulla memoria — utile per i grafici della tesi.` | `Memory statistics — useful for the paper figures.` |

Commenti nel codice tradotti: 7 (irrilevanti per il modello).


---

### 6. Conclusione

- [x] Tutte le traduzioni sono equivalenti: **Sì**, con un'eccezione nel Router (lingua del campo `reasoning`), che non riguarda gli agenti specialisti.
- [x] Nessuna istruzione aggiunta: **Sì**.
- [x] Nessuna istruzione rimossa: **Sì**.
- [x] Nessuna istruzione modificata semanticamente nel Dependency Agent e nel Config Agent: **Sì**. In tutto il sistema: 1 (Router, `reasoning`).

**Verdetto.** Il calo di Mistral 7B tra il run di settembre e il rerun di novembre (no-memory: dependency 26/50 → 13/50, config 21/50 → 5/50, complessivo 42.00% → 25.33%; fonte: `stato_attuale_msr2027.md`) **non è attribuibile a un'istruzione cambiata nella traduzione**. I prompt del Dependency Agent e del Config Agent sono traduzioni riga per riga, senza istruzioni aggiunte, rimosse o modificate, e il codice che li costruisce e ne ripulisce l'output è identico. Anche le istruzioni di formato sono le stesse nelle due lingue ("senza backtick né spiegazioni" / "without backticks or explanations").

**Evidenza che si tratti di sensibilità del modello alla lingua del prompt**
- A/B controllato del Dependency Agent (`experiments/ab_dependency_agent.py`): stesso modello `mistral-4k`, stessi 50 casi dependency × 5 ripetizioni, cambia solo la lingua del prompt. Output con formato valido al tentativo 1: 11/250 (4.4%) con il prompt inglese, 101/250 (40.4%) con quello italiano; output con backtick 213 contro 85, pur con la stessa istruzione di non usarli.
- Run di controllo con i prompt italiani sopra la logica attuale (branch `italian-prompts`, dataset e repo inglesi): Mistral 38.67% (IT) contro 25.33% (EN), McNemar p = 0.0045. Valori riportati dall'autore; il CSV è sul DGX e non è stato riletto in questa analisi.
- Per il Config Agent non esiste un A/B dedicato: l'effetto della lingua è dedotto per analogia (stesse istruzioni, stessi input salvo 2 casi, §8). Se il run di controllo ha i dati per categoria, conviene riportarli.

**Fattori residui, non esclusi da questa analisi.** Tra settembre e novembre cambiano anche: il modello Ollama (`mistral-4k` riscaricato; il digest di settembre non è noto), le versioni delle librerie, 5 input del dataset per dependency/config (§8) e la variabilità tra run. Il run di controllo in italiano (38.67%) recupera la maggior parte della distanza da settembre (42.00%); i circa 3 punti restanti sono compatibili con questi fattori.

---

### 7. Modifiche post-traduzione (e prima, rispetto a settembre)

- **Dopo la traduzione**: `git diff 366b417..HEAD -- agent/agents/ agent/memory/episodic_store.py` è **vuoto**. I commit successivi toccano `agent/state.py`, `agent/pipeline/fix_executor.py` e `agent/github/client.py` (protocollo B per la categoria test, `ab49660`), che non contengono testo inviato ai modelli.
- **Tra il codice di settembre e la traduzione** (`68a3924`, 26 ago → `366b417^`): nei file degli agenti e in `episodic_store.py` cambiano solo il retrieval della memoria al tentativo 3 (esclusione dello stesso `case_id`, categoria `"test"` invece di `"config"` nel Test Agent). Nessun testo dei prompt. Il commit `41254b7` con le modifiche locali del DGX non tocca gli agenti.

### 8. Altri input al modello cambiati nella stessa finestra (fuori dal commit `366b417`)

Il commit `f26cac7` (12 nov) ha tradotto il dataset e il repository di prova (`src/`, `app/`, `tests/`). Non sono prompt, ma sono input che arrivano ai modelli. `requirements.txt` e `.github/workflows/ci.yml`, cioè i file che leggono Dependency Agent e Config Agent, non sono stati toccati.

| Categoria | `ci_logs` cambiati | `git_diff` cambiati |
|---|---|---|
| dependency (50) | 3 | 0 |
| config (50) | 0 | 2 |
| test (50) | 14 | 4 |

Le 5 modifiche di dependency/config, per intero:

| Caso | Campo | Italiano | English |
|---|---|---|---|
| dep_026 | `ci_logs` | `Note: requirements.in è stato aggiornato ma requirements.txt (generato con pip-compile) non è stato rigenerato — httpx non è presente nel file effettivamente installato in CI` | `Note: requirements.in was updated but requirements.txt (generated with pip-compile) was not regenerated — httpx is not present in the file actually installed in CI` |
| dep_029 | `ci_logs` | `Note: pywin32 pubblica distribuzioni solo per Windows (win32/win_amd64) — nessuna disponibile per Linux` | `Note: pywin32 publishes distributions only for Windows (win32/win_amd64) — none available for Linux` |
| dep_030 | `ci_logs` | `Note: pillow==8.3.2 (pin precedente) era stato segnalato da pip-audit per CVE-2021-34552; la versione di aggiornamento scelta non esiste su PyPI` | `Note: pillow==8.3.2 (previous pin) had been flagged by pip-audit for CVE-2021-34552; the chosen upgrade version does not exist on PyPI` |
| conf_037 | `git_diff` | `+      # required reviewers aggiunti via GitHub UI, non riflessi nel file workflow` | `+      # required reviewers added via the GitHub UI, not reflected in the workflow file` |
| conf_046 | `git_diff` | `+      # step di pulizia rimosso` | `+      # cleanup step removed` |

Nella categoria test cambiano anche i nomi delle funzioni di test e alcune righe esplicative nei log (es. `test_add_positivi` → `test_add_positive`), coerenti con la traduzione dei file di test che il Test Agent legge.

### 9. Verifica incrociata (stringhe italiane residue)

- `grep -rn "[àèéìòù]" agent/agents/ agent/memory/episodic_store.py` → nessun risultato.
- `grep -rni "tentativo\|errore\|dipendenz\|configura\|rispondi\|analizza\|genera\|correggi" agent/agents/` → solo falsi positivi inglesi (`generate`, `configuration`).
- Lo stesso controllo su tutto `agent/`, test compresi, con parole solo italiane (`tentativo`, `nessun`, `rispondi`, `strategia`, `aggiornat`, `fallit`, ...) → nessun risultato.

### 10. Altri file toccati dal commit

Nessuno di questi file contiene testo inviato ai modelli.

| File | Stringhe tradotte | Commenti tradotti | Struttura identica | Testo inviato al modello |
|---|---|---|---|---|
| `agent/github/client.py` | 27 | 19 | sì | no |
| `agent/graph.py` | 8 | 12 | sì | no |
| `agent/pipeline/context_builder.py` | 3 | 6 | sì | no |
| `agent/pipeline/fix_executor.py` | 12 | 9 | sì | no |
| `agent/pipeline/trigger.py` | 14 | 14 | sì | no |
| `agent/state.py` | 0 | 20 | sì | no |
| `agent/tests/test_benchmark_inject_error.py` | 4 | 0 | sì | no |
| `agent/tests/test_config_agent.py` | 2 | 0 | sì | no |
| `agent/tests/test_dependency_agent.py` | 10 | 4 | sì | no |
| `agent/tests/test_end_to_end.py` | 3 | 1 | sì | no |
| `agent/tests/test_find_test_file_paths.py` | 4 | 3 | sì | no |
| `agent/tests/test_fix_executor_modified_file.py` | 2 | 2 | sì | no |
| `agent/tests/test_memory.py` | 7 | 6 | no (rinomina della variabile locale `distanti` → `distant`) | no |
| `agent/tests/test_router.py` | 10 | 8 | sì | no |
| `agent/tests/test_strip_think_blocks.py` | 5 | 0 | sì | no |
| `agent/tests/test_test_agent.py` | 3 | 0 | sì | no |
| `check_models.py` | 0 | — | sì | no |
| `experiments/analysis.py` | 56 | — | sì | no |
| `experiments/benchmark.py` | 72 | — | sì | no |
| `explore_logs.py` | 4 | — | sì | no |
| `verify_data.py` | 7 | — | sì | no |

Nota su `experiments/benchmark.py`: la metrica `json_parse_fail` cerca la stringa di fallback del Router. È stata tradotta nello stesso commit in entrambi i punti (`"Parsing fallito"` → `"Parsing failed"`), quindi la metrica resta coerente.
