"""
Dataset sintetico — 150 errori CI per la valutazione sperimentale
Tesi LM-32: Self-Healing CI/CD Pipeline

Struttura: 50 errori per categoria (dependency, test, config)
Difficoltà per categoria: easy ~19, medium ~17, hard ~14
(dep_001-020, test_001-020, conf_001-020 sono il set originale di 60 casi;
 dep_021-050, test_021-050, conf_021-050 sono l'estensione a 150 casi)

Uso:
    from experiments.dataset import DATASET, get_by_category, get_by_difficulty
"""

DATASET = [

    # ══════════════════════════════════════════════════════════
    # CATEGORIA: DEPENDENCY (50 errori)
    # ══════════════════════════════════════════════════════════

    {
        "id": "dep_001",
        "category": "dependency",
        "difficulty": "easy",
        "ci_logs": """
            ##[group]Run pip install -r requirements.txt
            ERROR: Could not find a version that satisfies the requirement numpy==99.99.99 (from versions: 1.3.0, 1.4.1, 1.5.0, 1.6.0, 1.6.1, 1.6.2, 1.7.0, 1.7.1, 1.7.2, 1.8.0, 1.8.1, 1.8.2, 1.9.0, 1.9.1, 1.9.2, 1.9.3, 1.10.0, 1.10.1, 1.10.2, 1.10.4, 1.11.0, 1.11.1, 1.11.2, 1.11.3, 1.12.0, 1.12.1, 1.13.0, 1.13.1, 1.13.3, 1.14.0, 1.14.1, 1.14.2, 1.14.3, 1.14.4, 1.14.5, 1.14.6, 1.15.0, 1.15.1, 1.15.2, 1.15.3, 1.15.4, 1.16.0, 1.16.1, 1.16.2, 1.16.3, 1.16.4, 1.16.5, 1.16.6, 1.17.0, 1.17.1, 1.17.2, 1.17.3, 1.17.4, 1.17.5, 1.18.0, 1.18.1, 1.18.2, 1.18.3, 1.18.4, 1.18.5, 1.19.0, 1.19.1, 1.19.2, 1.19.3, 1.19.4, 1.19.5, 1.20.0, 1.20.1, 1.20.2, 1.20.3, 1.21.0, 1.21.1, 1.21.2, 1.21.3, 1.21.4, 1.21.5, 1.21.6, 1.22.0, 1.22.1, 1.22.2, 1.22.3, 1.22.4, 1.23.0, 1.23.1, 1.23.2, 1.23.3, 1.23.4, 1.23.5, 1.24.0, 1.24.1, 1.24.2, 1.24.3, 1.24.4, 1.25.0, 1.25.1, 1.25.2, 1.26.0, 1.26.1, 1.26.2, 1.26.3, 1.26.4)
            ERROR: No matching distribution found for numpy==99.99.99
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-numpy==1.26.4\n+numpy==99.99.99",
        "ci_job_name": "Install dependencies",
        "expected_fix": "Riportare numpy a una versione valida, es. numpy==1.26.4",
        "notes": "Caso base, versione chiaramente inesistente"
    },

    {
        "id": "dep_002",
        "category": "dependency",
        "difficulty": "easy",
        "ci_logs": """
            ##[group]Run pip install -r requirements.txt
            ERROR: Could not find a version that satisfies the requirement pandas==999.0.0
            ERROR: No matching distribution found for pandas==999.0.0
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-pandas==2.0.3\n+pandas==999.0.0",
        "ci_job_name": "Install dependencies",
        "expected_fix": "Riportare pandas a versione valida, es. pandas==2.0.3",
        "notes": "Stessa struttura dep_001 ma pacchetto diverso"
    },

    {
        "id": "dep_003",
        "category": "dependency",
        "difficulty": "easy",
        "ci_logs": """
            ##[group]Run pip install -r requirements.txt
            ERROR: No matching distribution found for scikit-learn==0.0.1
            Note: scikit-learn 0.0.1 was never released. Latest version is 1.3.2
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-scikit-learn==1.3.0\n+scikit-learn==0.0.1",
        "ci_job_name": "Install dependencies",
        "expected_fix": "Usare scikit-learn==1.3.0 o superiore",
        "notes": "Versione troppo bassa mai rilasciata"
    },

    {
        "id": "dep_004",
        "category": "dependency",
        "difficulty": "easy",
        "ci_logs": """
            ##[group]Run pip install -r requirements.txt
            Collecting requests==2.99.99
            ERROR: Could not find a version that satisfies the requirement requests==2.99.99
            ERROR: No matching distribution found for requests==2.99.99
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-requests==2.31.0\n+requests==2.99.99",
        "ci_job_name": "Install dependencies",
        "expected_fix": "Usare requests==2.31.0",
        "notes": "Errore tipico da copia/incolla versione sbagliata"
    },

    {
        "id": "dep_005",
        "category": "dependency",
        "difficulty": "easy",
        "ci_logs": """
            ##[group]Run pip install -r requirements.txt
            ERROR: No matching distribution found for flask==3.99.0
            Available versions: 0.1, 0.2, ... 2.3.3, 3.0.0, 3.0.1, 3.0.2, 3.0.3
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-flask==3.0.3\n+flask==3.99.0",
        "ci_job_name": "Install dependencies",
        "expected_fix": "Usare flask==3.0.3",
        "notes": "Versione futura non ancora rilasciata"
    },

    {
        "id": "dep_006",
        "category": "dependency",
        "difficulty": "easy",
        "ci_logs": """
            ##[group]Run pip install -r requirements.txt
            ERROR: No matching distribution found for tensorflow==1.0.0 for Python 3.11
            Note: tensorflow 1.x is not compatible with Python 3.11. Use tensorflow>=2.0
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-tensorflow==2.13.0\n+tensorflow==1.0.0",
        "ci_job_name": "Install dependencies",
        "expected_fix": "Usare tensorflow==2.13.0 o superiore",
        "notes": "Incompatibilità versione pacchetto con Python 3.11"
    },

    {
        "id": "dep_007",
        "category": "dependency",
        "difficulty": "easy",
        "ci_logs": """
            ##[group]Run pip install -r requirements.txt
            ERROR: Could not find a version that satisfies the requirement scipy==1.99.0
            ERROR: No matching distribution found for scipy==1.99.0
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-scipy==1.11.3\n+scipy==1.99.0",
        "ci_job_name": "Install dependencies",
        "expected_fix": "Usare scipy==1.11.3",
        "notes": "Versione inesistente libreria scientifica"
    },

    {
        "id": "dep_008",
        "category": "dependency",
        "difficulty": "easy",
        "ci_logs": """
            ##[group]Run pip install -r requirements.txt
            ERROR: Could not find a version that satisfies the requirement matplotlib==10.0.0
            ERROR: No matching distribution found for matplotlib==10.0.0
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-matplotlib==3.8.0\n+matplotlib==10.0.0",
        "ci_job_name": "Install dependencies",
        "expected_fix": "Usare matplotlib==3.8.0",
        "notes": "Major version chiaramente sbagliata"
    },

    {
        "id": "dep_009",
        "category": "dependency",
        "difficulty": "medium",
        "ci_logs": """
            ##[group]Run pip install -r requirements.txt
            ERROR: Cannot install numpy==1.24.0 and pandas==2.0.0 because these package versions have conflicting dependencies.
            The conflict is caused by:
                pandas 2.0.0 depends on numpy>=1.23.2
                scipy 1.9.0 depends on numpy<1.25.0,>=1.18.5
                numpy 1.24.0 is in the range but triggers an internal abi issue
            Could not find a version that satisfies all requirements.
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "+pandas==2.0.0\n+scipy==1.9.0\n-pandas==1.5.3",
        "ci_job_name": "Install dependencies",
        "expected_fix": "Aggiornare scipy a >=1.10.0 o usare pandas==1.5.3 compatibile con scipy 1.9.0",
        "notes": "Conflitto reale tra versioni, richiede ragionamento sulle dipendenze"
    },

    {
        "id": "dep_010",
        "category": "dependency",
        "difficulty": "medium",
        "ci_logs": """
            ##[group]Run pip install -r requirements.txt
            Collecting torch==2.0.0
            Downloading torch-2.0.0-cp311-cp311-manylinux1_x86_64.whl (619.9 MB)
            ERROR: RECORD file has an incorrect length: expected 344, got 199
            Error processing package torch
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-torch==1.13.1\n+torch==2.0.0",
        "ci_job_name": "Install dependencies",
        "expected_fix": "Usare torch==2.1.0 o superiore dove il wheel è corretto, oppure specificare --index-url per PyTorch",
        "notes": "Wheel corrotto per versione specifica — richiede strategia alternativa"
    },

    {
        "id": "dep_011",
        "category": "dependency",
        "difficulty": "medium",
        "ci_logs": """
            ##[group]Run pip install -r requirements.txt
            Collecting my-internal-lib==1.2.3
            ERROR: Could not find a version that satisfies the requirement my-internal-lib==1.2.3
            ERROR: No matching distribution found for my-internal-lib==1.2.3
            Note: my-internal-lib is not available on PyPI. Did you mean to use --extra-index-url?
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "+my-internal-lib==1.2.3",
        "ci_job_name": "Install dependencies",
        "expected_fix": "Rimuovere my-internal-lib da requirements.txt o aggiungere --extra-index-url nel workflow",
        "notes": "Pacchetto interno non su PyPI — richiede comprensione del contesto"
    },

    {
        "id": "dep_012",
        "category": "dependency",
        "difficulty": "medium",
        "ci_logs": """
            ##[group]Run pip install -r requirements.txt
            ERROR: pip's dependency resolver does not currently take into account all the packages that are installed. This behaviour is the source of the following dependency conflicts.
            sqlalchemy 2.0.0 requires typing-extensions>=4.6.0, but you have typing-extensions 4.2.0 which is incompatible.
            pydantic 2.0.0 requires typing-extensions>=4.6.0, but you have typing-extensions 4.2.0 which is incompatible.
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "+sqlalchemy==2.0.0\n+pydantic==2.0.0\n-sqlalchemy==1.4.46",
        "ci_job_name": "Install dependencies",
        "expected_fix": "Aggiornare typing-extensions>=4.6.0 in requirements.txt",
        "notes": "Conflitto dipendenza transitiva — richiede identificare il pacchetto mancante"
    },

    {
        "id": "dep_013",
        "category": "dependency",
        "difficulty": "medium",
        "ci_logs": """
            ##[group]Run pip install -r requirements.txt
            Collecting cryptography==41.0.0
            Downloading cryptography-41.0.0.tar.gz
            error: command '/usr/bin/gcc' failed with exit code 1
            note: This error originates from a subprocess, and is likely not a problem with pip.
            hint: See above for output from the subprocess.
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-cryptography==39.0.2\n+cryptography==41.0.0",
        "ci_job_name": "Install dependencies",
        "expected_fix": "Specificare cryptography==41.0.0 con --only-binary=:all: o usare versione con wheel precompilato",
        "notes": "Build from source fallisce — richiede strategia wheel binario"
    },

    {
        "id": "dep_014",
        "category": "dependency",
        "difficulty": "medium",
        "ci_logs": """
            ##[group]Run pip install -r requirements.txt
            ERROR: Ignored the following versions that require a different python version:
            1.0.0 Requires-Python >=3.10; 2.0.0 Requires-Python >=3.10
            ERROR: Could not find a version of package 'newpackage' that satisfies python_requires >=3.10
            Current python: 3.9.18
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "+newpackage==2.0.0",
        "ci_job_name": "Install dependencies",
        "expected_fix": "Aggiornare python-version a 3.10 nel ci.yml o usare newpackage<1.0.0 compatibile con Python 3.9",
        "notes": "Conflitto Python version — fix può essere nel ci.yml o requirements.txt"
    },

    {
        "id": "dep_015",
        "category": "dependency",
        "difficulty": "medium",
        "ci_logs": """
            ##[group]Run pip install -r requirements.txt
            ERROR: Could not find a version that satisfies the requirement broken-lib==0.0.1 (from versions: none)
            ERROR: No matching distribution found for broken-lib==0.0.1
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "+broken-lib==0.0.1",
        "ci_job_name": "Install dependencies",
        "expected_fix": "Rimuovere broken-lib da requirements.txt — il pacchetto non esiste su PyPI",
        "notes": "Pacchetto completamente inventato — nessuna versione disponibile"
    },

    {
        "id": "dep_016",
        "category": "dependency",
        "difficulty": "hard",
        "ci_logs": """
            ##[group]Run pip install -r requirements.txt
            ERROR: Cannot install -r requirements.txt (line 3) and -r requirements.txt (line 7) because these package versions have conflicting dependencies.
            The conflict is caused by:
                langchain 0.1.0 requires pydantic<3,>=1
                langchain-openai 0.0.5 requires pydantic>=2.0
                langchain-community 0.0.10 requires pydantic<2,>=1
            ERROR: ResolutionImpossible: for help visit https://pip.pypa.io/en/stable/topics/dependency-resolution/
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "+langchain==0.1.0\n+langchain-openai==0.0.5\n+langchain-community==0.0.10",
        "ci_job_name": "Install dependencies",
        "expected_fix": "Allineare le versioni: langchain>=0.2.0, langchain-openai>=0.1.0, langchain-community>=0.2.0 tutte compatibili con pydantic>=2.0",
        "notes": "Conflitto multi-pacchetto complesso — ecosistema LangChain ha storicamente avuto questo problema"
    },

    {
        "id": "dep_017",
        "category": "dependency",
        "difficulty": "hard",
        "ci_logs": """
            ##[group]Run pip install -r requirements.txt
            Collecting numpy (from -r requirements.txt (line 1))
            Downloading numpy-2.0.0-cp311-cp311-manylinux_2_17_x86_64.whl
            Successfully installed numpy-2.0.0
            Collecting pandas==1.5.3 (from -r requirements.txt (line 2))
            ERROR: pandas 1.5.3 requires numpy<1.25,>=1.20.3, but you have numpy 2.0.0 which is incompatible.
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "+numpy==2.0.0\n-numpy>=1.20",
        "ci_job_name": "Install dependencies",
        "expected_fix": "Aggiornare pandas>=2.0.0 compatibile con numpy 2.0 oppure pinnare numpy<1.25",
        "notes": "numpy 2.0 breaking change — rompe molti pacchetti che non hanno ancora aggiornato i vincoli"
    },

    {
        "id": "dep_018",
        "category": "dependency",
        "difficulty": "hard",
        "ci_logs": """
            ##[group]Run pip install -r requirements.txt
            ERROR: pip's legacy dependency resolver does not consider dependency conflicts when selecting packages.
            Attempting to install: grpcio==1.60.0
            grpcio 1.60.0 has requirement protobuf<5.0dev,>=4.21.6
            tensorflow 2.13.0 requires protobuf>=3.20.3,<5.0.0dev
            google-cloud-storage 2.14.0 requires protobuf>=3.20.0
            grpcio-tools 1.60.0 requires grpcio==1.60.0 and protobuf>=4.21.6
            Your environment is inconsistent. protobuf 3.20.3 is installed but grpcio requires >=4.21.6
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "+grpcio==1.60.0\n+grpcio-tools==1.60.0",
        "ci_job_name": "Install dependencies",
        "expected_fix": "Aggiornare protobuf>=4.21.6 e verificare compatibilità con tensorflow e google-cloud-storage",
        "notes": "Conflitto protobuf classico nell'ecosistema Google — richiede conoscenza specifica"
    },

    {
        "id": "dep_019",
        "category": "dependency",
        "difficulty": "hard",
        "ci_logs": """
            ##[group]Run pip install -r requirements.txt
            Collecting spacy==3.7.0
            ERROR: spacy 3.7.0 requires thinc<8.3.0,>=8.2.2, but you have thinc 8.1.0
            ERROR: spacy 3.7.0 requires spacy-legacy<3.1.0,>=3.0.11, but you have spacy-legacy 3.0.10
            ERROR: spacy 3.7.0 requires cymem<2.1.0,>=2.0.2, but you have cymem 2.0.1
            Multiple dependency errors — cannot resolve
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-spacy==3.5.0\n+spacy==3.7.0",
        "ci_job_name": "Install dependencies",
        "expected_fix": "Aggiornare contestualmente: spacy==3.7.0 thinc>=8.2.2 spacy-legacy>=3.0.11 cymem>=2.0.2",
        "notes": "Aggiornamento major con cascade di dipendenze — ecosistema spacy ha dipendenze rigide"
    },

    {
        "id": "dep_020",
        "category": "dependency",
        "difficulty": "hard",
        "ci_logs": """
            ##[group]Run pip install -r requirements.txt
            ERROR: Cannot install celery==5.3.0 and kombu==5.2.0 because these package versions have conflicting dependencies.
            celery 5.3.0 requires kombu>=5.3.0,<6.0
            kombu 5.2.0 is lower than the minimum required by celery 5.3.0
            Additionally: vine 5.0.0 requires kombu>=5.0.0 which is satisfied by 5.2.0, but celery 5.3.0 overrides this constraint
            Error: ResolutionImpossible
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "+celery==5.3.0\n-celery==5.2.7\n+kombu==5.2.0",
        "ci_job_name": "Install dependencies",
        "expected_fix": "Aggiornare kombu>=5.3.0 per soddisfare il vincolo di celery 5.3.0",
        "notes": "Aggiornamento parziale che rompe vincoli — kombu non aggiornato insieme a celery"
    },

    # --- Nuovi casi (dep_021 - dep_050) ---

    {
        "id": "dep_021",
        "category": "dependency",
        "difficulty": "easy",
        "ci_logs": """
            ##[group]Run pip install -r requirements.txt
            Collecting urllib3==2.0.3
            WARNING: The candidate selected for download or install is a yanked version: 'urllib3' candidate (version 2.0.3 at https://pypi.org/simple/urllib3/)
            Reason for being yanked: contains a critical regression in connection pooling
            ERROR: Could not find a version that satisfies the requirement urllib3==2.0.3 that is not yanked
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-urllib3==2.0.2\n+urllib3==2.0.3",
        "ci_job_name": "Install dependencies",
        "expected_fix": "Aggiornare a urllib3==2.0.4 (o altra versione non yanked), poiché 2.0.3 è stata ritirata dagli autori",
        "notes": "Versione yanked su PyPI — diverso da una versione inesistente, richiede riconoscere il warning di yank"
    },

    {
        "id": "dep_022",
        "category": "dependency",
        "difficulty": "easy",
        "ci_logs": """
            ##[group]Run npm ci
            npm ERROR! `npm ci` can only install packages when your package.json and package-lock.json are in sync.
            npm ERROR! Please update your lock file with `npm install` before continuing.
            npm ERROR! Missing: axios@1.6.0 from lock file
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "+    \"axios\": \"^1.6.0\",\n     \"express\": \"^4.18.2\"",
        "ci_job_name": "Install dependencies",
        "expected_fix": "Eseguire npm install in locale per aggiornare package-lock.json e committare il lock file aggiornato",
        "notes": "package.json modificato senza rigenerare package-lock.json — errore comune in progetti Node"
    },

    {
        "id": "dep_023",
        "category": "dependency",
        "difficulty": "easy",
        "ci_logs": """
            ##[group]Run npm install
            npm ERROR! code EBADENGINE
            npm ERROR! engine Unsupported engine
            npm ERROR! Not compatible with your version of node/npm: myapp@1.0.0
            npm ERROR! Required: {"node":">=20.0.0"}
            npm ERROR! Actual: {"npm":"9.8.1","node":"v18.19.0"}
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-  \"engines\": { \"node\": \">=18.0.0\" }\n+  \"engines\": { \"node\": \">=20.0.0\" }",
        "ci_job_name": "Install dependencies",
        "expected_fix": "Aggiornare node-version a '20' nello step actions/setup-node del workflow, oppure abbassare il vincolo engines a >=18.0.0",
        "notes": "Il vincolo engines in package.json non è più soddisfatto dalla versione di Node configurata nel workflow"
    },

    {
        "id": "dep_024",
        "category": "dependency",
        "difficulty": "easy",
        "ci_logs": """
            ##[group]Run pip install -r requirements.txt
            Collecting psycopg2==2.9.9
            Building wheel for psycopg2 (setup.py): finished with status 'error'
            Error: pg_config executable not found.
            libpq-fe.h: No such file or directory
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-psycopg2-binary==2.9.9\n+psycopg2==2.9.9",
        "ci_job_name": "Install dependencies",
        "expected_fix": "Usare psycopg2-binary==2.9.9 invece di psycopg2, oppure installare libpq-dev via apt-get prima della build",
        "notes": "psycopg2 (non-binary) richiede header di sviluppo PostgreSQL assenti sul runner"
    },

    {
        "id": "dep_025",
        "category": "dependency",
        "difficulty": "easy",
        "ci_logs": """
            ##[group]Run pip install -r requirements.txt
            ERROR: Double requirement given: click==8.0.0 (already in click==8.1.7, name='click')
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "  click==8.1.7\n+click==8.0.0",
        "ci_job_name": "Install dependencies",
        "expected_fix": "Rimuovere la riga duplicata click==8.0.0, mantenendo solo click==8.1.7",
        "notes": "Stesso pacchetto pinnato due volte con versioni diverse nello stesso file"
    },

    {
        # NOTA (riscritto il 2026-07-30): caso originale basato su Poetry
        # ("pyproject.toml"/"poetry.lock", ecosistema non presente in questo
        # repo, che usa pip + requirements.txt). Riscritto come equivalente
        # pip-tools mantenendo la stessa lezione concettuale (lockfile non
        # rigenerato dopo una modifica al file sorgente delle dipendenze).
        # Vedi experiments/CHANGELOG_DATASET.md.
        "id": "dep_026",
        "category": "dependency",
        "difficulty": "easy",
        "ci_logs": """
            ##[group]Run pip install -r requirements.txt
            Collecting httpx (from -r requirements.in (line 4))
            ERROR: Could not find a version that satisfies the requirement httpx (from -r requirements.in (line 4))
            Note: requirements.in è stato aggiornato ma requirements.txt (generato con pip-compile) non è stato rigenerato — httpx non è presente nel file effettivamente installato in CI
            ##[endgroup]
            ##[group]Run pytest tests/
            ModuleNotFoundError: No module named 'httpx'
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "+httpx==0.27.0",
        "ci_job_name": "Install dependencies",
        "expected_fix": "Aggiungere httpx==0.27.0 a requirements.txt (rigenerandolo con pip-compile a partire da requirements.in), poiché la dipendenza è stata aggiunta al file sorgente ma mai propagata al file effettivamente installato in CI",
        "notes": "Drift tra requirements.in (sorgente) e requirements.txt (lockfile compilato) — equivalente pip-tools del caso poetry.lock non rigenerato dopo una modifica a pyproject.toml"
    },

    {
        "id": "dep_027",
        "category": "dependency",
        "difficulty": "easy",
        "ci_logs": """
            ##[group]Run npm install
            npm ERROR! code E401
            npm ERROR! 401 Unauthorized - GET https://npm.pkg.github.com/@myorg%2finternal-utils - Unauthorized
            npm ERROR! This is often related to authentication. Run `npm whoami` to verify.
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-      - run: npm install\n-        env:\n-          NODE_AUTH_TOKEN: ${{ secrets.GH_PACKAGES_TOKEN }}\n+      - run: npm install",
        "ci_job_name": "Install dependencies",
        "expected_fix": "Ripristinare la env NODE_AUTH_TOKEN: ${{ secrets.GH_PACKAGES_TOKEN }} nello step npm install per autenticarsi al registry privato",
        "notes": "Token di autenticazione al package registry privato rimosso dallo step"
    },

    {
        "id": "dep_028",
        "category": "dependency",
        "difficulty": "easy",
        "ci_logs": """
            ##[group]Run pytest tests/
            ModuleNotFoundError: No module named 'uvicorn'
            tests/test_server.py:3: in <module>
                from app.server import create_app
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-fastapi[all]==0.104.1\n+fastapi==0.104.1",
        "ci_job_name": "Run Tests",
        "expected_fix": "Ripristinare fastapi[all]==0.104.1 per includere le dipendenze extra come uvicorn, oppure aggiungere uvicorn esplicitamente a requirements.txt",
        "notes": "Extra 'all' rimosso dal pin, sotto-dipendenze necessarie a runtime non installate"
    },

    {
        "id": "dep_029",
        "category": "dependency",
        "difficulty": "easy",
        "ci_logs": """
            ##[group]Run pip install -r requirements.txt
            Collecting grpcio==1.48.0
            ERROR: Could not find a version that satisfies the requirement grpcio==1.48.0 (from versions: 1.54.0, 1.54.2, 1.56.0, 1.59.0, 1.60.0)
            ERROR: No matching distribution found for grpcio==1.48.0
            Note: no manylinux wheel for grpcio==1.48.0 is published for aarch64
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-    runs-on: ubuntu-latest\n+    runs-on: macos-14  # Apple Silicon runner",
        "ci_job_name": "Install dependencies",
        "expected_fix": "Aggiornare grpcio a una versione >=1.54.0 che pubblica wheel per la piattaforma arm64 del runner macos-14",
        "notes": "Cambio del runner a un'architettura arm64 espone la mancanza di wheel precompilati per la versione pinnata"
    },

    {
        # NOTA (riscritto il 2026-07-30): caso originale basato su
        # "npm audit"/package.json (ecosistema Node non presente in questo
        # repo). Riscritto come equivalente pip-audit mantenendo la stessa
        # lezione concettuale (pin vulnerabile segnalato da un audit di
        # sicurezza, l'aggiornamento scelto punta a una versione inesistente).
        # Vedi experiments/CHANGELOG_DATASET.md.
        "id": "dep_030",
        "category": "dependency",
        "difficulty": "easy",
        "ci_logs": """
            ##[group]Run pip install -r requirements.txt
            ERROR: Could not find a version that satisfies the requirement pillow==10.99.0
            ERROR: No matching distribution found for pillow==10.99.0
            Note: pillow==8.3.2 (pin precedente) era stato segnalato da pip-audit per CVE-2021-34552; la versione di aggiornamento scelta non esiste su PyPI
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-pillow==8.3.2\n+pillow==10.99.0",
        "ci_job_name": "Install dependencies",
        "expected_fix": "Aggiornare pillow a una versione realmente pubblicata e priva della vulnerabilità nota, es. pillow==10.3.0, poiché pillow==10.99.0 non esiste su PyPI",
        "notes": "Equivalente pip-audit del caso npm audit: il pin vulnerabile va sostituito, ma la versione di aggiornamento indicata punta a una release inesistente"
    },

    {
        "id": "dep_031",
        "category": "dependency",
        "difficulty": "easy",
        "ci_logs": """
            ##[group]Run yarn install --frozen-lockfile
            error Your lockfile needs to be updated, but yarn was run with '--frozen-lockfile'.
            error Found 1 package that doesn't satisfy your lockfile
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "+    \"lodash\": \"^4.17.21\",",
        "ci_job_name": "Install dependencies",
        "expected_fix": "Eseguire yarn install in locale per rigenerare yarn.lock e committare il file aggiornato",
        "notes": "Dipendenza aggiunta a package.json senza aggiornare yarn.lock, --frozen-lockfile lo rileva in CI"
    },

    {
        "id": "dep_032",
        "category": "dependency",
        "difficulty": "medium",
        "ci_logs": """
            ##[group]Run npm install
            npm ERROR! code ERESOLVE
            npm ERROR! ERESOLVE unable to resolve dependency tree
            npm ERROR! While resolving: my-app@1.0.0
            npm ERROR! Found: react@18.2.0
            npm ERROR! Could not resolve dependency:
            npm ERROR! peer react@"^17.0.0" from react-beautiful-dnd@13.1.1
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "+    \"react-beautiful-dnd\": \"^13.1.1\",",
        "ci_job_name": "Install dependencies",
        "expected_fix": "Sostituire react-beautiful-dnd con una libreria compatibile con react 18 (es. @hello-pangea/dnd), poiché react-beautiful-dnd richiede react ^17",
        "notes": "Conflitto peer dependency npm — libreria non aggiornata per React 18"
    },

    {
        "id": "dep_033",
        "category": "dependency",
        "difficulty": "medium",
        "ci_logs": """
            ##[group]Run pip install -r requirements.txt
            Collecting torch==2.1.0+cu121
            ERROR: Could not find a version that satisfies the requirement torch==2.1.0+cu121 (from versions: 2.1.0, 2.1.0+cpu, 2.1.1, 2.1.1+cpu)
            ERROR: No matching distribution found for torch==2.1.0+cu121
            Note: the CI runner has no GPU and the default PyPI index does not host +cu121 builds
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-torch==2.1.0\n+torch==2.1.0+cu121",
        "ci_job_name": "Install dependencies",
        "expected_fix": "Usare torch==2.1.0 (build CPU standard da PyPI) oppure aggiungere --index-url https://download.pytorch.org/whl/cu121 se serve davvero la build CUDA",
        "notes": "Build CUDA specifica richiede un index url dedicato, non disponibile su PyPI standard"
    },

    {
        "id": "dep_034",
        "category": "dependency",
        "difficulty": "medium",
        "ci_logs": """
            ##[group]Run pip install --require-hashes -r requirements.txt
            ERROR: THESE PACKAGES DO NOT MATCH THE HASHES FROM THE REQUIREMENTS FILE
            click==8.1.7 from https://files.pythonhosted.org/... (from -r requirements.txt (line 12)):
                Expected sha256 a61c...
                     Got        sha256 e1e4...
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-click==8.1.6 --hash=sha256:a61c...\n+click==8.1.7",
        "ci_job_name": "Install dependencies",
        "expected_fix": "Rigenerare requirements.txt con pip-compile per aggiornare anche gli hash associati a click==8.1.7",
        "notes": "Versione del pacchetto aggiornata manualmente senza rigenerare gli hash richiesti da --require-hashes"
    },

    {
        "id": "dep_035",
        "category": "dependency",
        "difficulty": "medium",
        "ci_logs": """
            ##[group]Run conda env create -f environment.yml
            UnsatisfiableError: The following specifications were found to be incompatible with each other:
            Output in format: Requested package -> Available versions

              - python=3.8 -> requires a version of python that is not available
              - scikit-learn=1.4 -> requires python>=3.9
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-  - scikit-learn=1.2\n+  - scikit-learn=1.4",
        "ci_job_name": "Create conda environment",
        "expected_fix": "Aggiornare python a >=3.9 in environment.yml, oppure usare scikit-learn=1.2 compatibile con python=3.8",
        "notes": "Solver conda non riesce a soddisfare simultaneamente python=3.8 e scikit-learn=1.4"
    },

    {
        "id": "dep_036",
        "category": "dependency",
        "difficulty": "medium",
        "ci_logs": """
            ##[group]Run pip install -r requirements.txt
            Collecting acme-internal-utils==0.1.0
              Downloading acme-internal-utils-0.1.0.tar.gz (2.1 kB)
            WARNING: acme-internal-utils 0.1.0 was published to PyPI 3 days ago and does not match the expected internal package hash
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "+acme-internal-utils==0.1.0",
        "ci_job_name": "Install dependencies",
        "expected_fix": "Configurare --index-url sull'indice privato interno con priorità sopra PyPI pubblico, per evitare che pip risolva il nome da un pacchetto pubblico non affidabile (dependency confusion)",
        "notes": "Rischio di dependency confusion: un pacchetto pubblico con lo stesso nome di uno interno viene installato per errore"
    },

    {
        "id": "dep_037",
        "category": "dependency",
        "difficulty": "medium",
        "ci_logs": """
            ##[group]Run pip install -r requirements.txt
            ERROR: Cannot install package: Getting requirements to build wheel did not run successfully.
            BackendUnavailable: Cannot import 'setuptools.build_meta'
            note: This is an issue with the package mentioned above, not pip.
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-requires = [\"setuptools>=65\"]\n+requires = [\"setuptools>=68\"]",
        "ci_job_name": "Install dependencies",
        "expected_fix": "Aggiornare setuptools nell'ambiente CI (pip install --upgrade setuptools) prima di installare i pacchetti che richiedono setuptools>=68 come build backend",
        "notes": "Il build backend richiesto in pyproject.toml non è soddisfatto dalla versione di setuptools preinstallata sul runner"
    },

    {
        "id": "dep_038",
        "category": "dependency",
        "difficulty": "medium",
        "ci_logs": """
            ##[group]Run pip install -r requirements.txt
            Collecting git+https://github.com/myorg/internal-tool.git@v1.2.0
            fatal: could not read Username for 'https://github.com': terminal prompts disabled
            ERROR: Command errored out with exit status 128
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "+git+https://github.com/myorg/internal-tool.git@v1.2.0",
        "ci_job_name": "Install dependencies",
        "expected_fix": "Usare git+https://x-access-token:${{ secrets.GH_PAT }}@github.com/myorg/internal-tool.git@v1.2.0 per autenticarsi al repository privato",
        "notes": "Dipendenza da repository Git privato senza credenziali nell'URL"
    },

    {
        "id": "dep_039",
        "category": "dependency",
        "difficulty": "medium",
        "ci_logs": """
            ##[group]Run pip install -r requirements.txt -r requirements-dev.txt
            ERROR: Cannot install -r requirements-dev.txt (line 4) and -r requirements.txt (line 9) because these package versions have conflicting dependencies.
            The conflict is caused by:
                requirements.txt contains black==23.9.1
                requirements-dev.txt contains black==24.1.0
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "+black==24.1.0",
        "ci_job_name": "Install dependencies",
        "expected_fix": "Allineare la versione di black in requirements-dev.txt a 23.9.1 per essere coerente con requirements.txt (o aggiornare entrambe alla stessa versione)",
        "notes": "Due file di requirements pinnano lo stesso pacchetto a versioni diverse"
    },

    {
        "id": "dep_040",
        "category": "dependency",
        "difficulty": "medium",
        "ci_logs": """
            ##[group]Run npm install
            npm ERROR! code E429
            npm ERROR! 429 Too Many Requests - GET https://registry.npmjs.org/lodash
            npm ERROR! network This is a problem related to network connectivity.
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-      - uses: actions/setup-node@v4\n-        with:\n-          cache: 'npm'\n+      - uses: actions/setup-node@v4",
        "ci_job_name": "Install dependencies",
        "expected_fix": "Ripristinare cache: 'npm' nello step actions/setup-node per ridurre le richieste dirette al registry ed evitare il rate limiting",
        "notes": "Rimozione della cache npm aumenta le richieste dirette al registry pubblico, esponendo al rate limiting"
    },

    {
        "id": "dep_041",
        "category": "dependency",
        "difficulty": "medium",
        "ci_logs": """
            ##[group]Run pip install -r requirements.txt
            Collecting tokenizers==0.15.0
              Building wheel for tokenizers (pyproject.toml): started
              error: can't find Rust compiler
            ERROR: Could not build wheels for tokenizers, which is required to install pyproject.toml-based projects
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-tokenizers==0.13.3\n+tokenizers==0.15.0",
        "ci_job_name": "Install dependencies",
        "expected_fix": "Usare tokenizers==0.15.0 con wheel precompilato disponibile (verificare compatibilità Python) oppure installare il toolchain Rust nel workflow prima del pip install",
        "notes": "Versione senza wheel precompilato per la piattaforma richiede build da sorgente con Rust non disponibile sul runner"
    },

    {
        "id": "dep_042",
        "category": "dependency",
        "difficulty": "hard",
        "ci_logs": """
            ##[group]Run pip install -r requirements.txt
            ERROR: Cannot install -r requirements.txt because these package versions have conflicting dependencies.
            The conflict is caused by:
                package-a 2.0.0 requires shared-lib<3.0,>=2.0
                package-b 1.5.0 requires shared-lib<2.0,>=1.5
            No version of shared-lib satisfies both constraints simultaneously.
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "+package-a==2.0.0\n+package-b==1.5.0",
        "ci_job_name": "Install dependencies",
        "expected_fix": "Aggiornare package-b a una versione compatibile con shared-lib>=2.0 (es. package-b>=2.0.0), poiché non esiste un range di shared-lib che soddisfi entrambi i vincoli attuali",
        "notes": "Diamond dependency: due pacchetti diretti richiedono range incompatibili della stessa dipendenza transitiva"
    },

    {
        "id": "dep_043",
        "category": "dependency",
        "difficulty": "hard",
        "ci_logs": """
            ##[group]Run npm ci
            npm ERROR! code ERESOLVE
            npm ERROR! While resolving: my-app@2.3.0
            npm ERROR! Found: semver@6.3.1
            npm ERROR! Could not resolve dependency:
            npm ERROR! peer semver@"^7.5.4" from some-transitive-dep@3.0.0 (introduced by eslint-config-custom bump)
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-    \"eslint-config-custom\": \"1.2.0\",\n+    \"eslint-config-custom\": \"2.0.0\",",
        "ci_job_name": "Install dependencies",
        "expected_fix": "Aggiungere un campo \"overrides\": { \"semver\": \"^7.5.4\" } in package.json per forzare la versione di semver richiesta dalla dipendenza transitiva aggiornata",
        "notes": "Bump automatico (Dependabot) introduce un vincolo transitivo che richiede l'uso di 'overrides' per essere risolto"
    },

    {
        "id": "dep_044",
        "category": "dependency",
        "difficulty": "hard",
        "ci_logs": """
            ##[group]Run pytest tests/
            ImportError: /lib/x86_64-linux-gnu/libc.so.6: version `GLIBC_2.29' not found (required by /opt/venv/lib/python3.11/site-packages/somepkg/_native.cpython-311-x86_64-linux-gnu.so)
            1 error during collection
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-    runs-on: ubuntu-22.04\n+    runs-on: ubuntu-18.04",
        "ci_job_name": "Run Tests",
        "expected_fix": "Ripristinare runs-on: ubuntu-22.04 (o superiore), poiché il wheel installato per somepkg è compilato contro una versione di glibc non disponibile su ubuntu-18.04",
        "notes": "Incompatibilità ABI a runtime (non a install time) tra il wheel precompilato e la libc del runner più vecchio"
    },

    {
        "id": "dep_045",
        "category": "dependency",
        "difficulty": "hard",
        "ci_logs": """
            ##[group]Run npm install
            npm ERROR! code ELOOP
            npm ERROR! Circular dependency detected in workspace:
            npm ERROR!   packages/core -> packages/utils -> packages/core
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "+    \"@myorg/core\": \"workspace:*\"",
        "ci_job_name": "Install dependencies",
        "expected_fix": "Rimuovere la dipendenza circolare estraendo il codice condiviso in un terzo package workspace indipendente, oppure rimuovere la dipendenza di packages/utils verso packages/core",
        "notes": "Dipendenza circolare tra pacchetti di un monorepo tramite protocollo workspace"
    },

    {
        "id": "dep_046",
        "category": "dependency",
        "difficulty": "hard",
        "ci_logs": """
            ##[group]Run pip install -r requirements.txt
            ERROR: Cannot install django==5.0, django-filter==22.1 and djangorestframework==3.14.0 because these package versions have conflicting dependencies.
            The conflict is caused by:
                django-filter 22.1 requires Django>=3.2,<5.0
                djangorestframework 3.14.0 requires Django>=3.0,<5.0
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-django==4.2.7\n+django==5.0",
        "ci_job_name": "Install dependencies",
        "expected_fix": "Aggiornare contestualmente django-filter>=23.5 e djangorestframework>=3.14.0 (versioni con supporto Django 5.0), oppure rimanere su django==4.2.7",
        "notes": "Aggiornamento major di Django senza aggiornare a cascata i pacchetti dipendenti compatibili"
    },

    {
        "id": "dep_047",
        "category": "dependency",
        "difficulty": "hard",
        "ci_logs": """
            ##[group]Run npm run build
            Uncaught Error: Invalid hook call. Hooks can only be called inside of the body of a function component.
            This could happen for one of the following reasons:
            1. You might have mismatching versions of React and the renderer
            2. You might have more than one copy of React in the same app
            FAIL tests/App.test.jsx
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "+    \"some-ui-lib\": \"3.0.0\",",
        "ci_job_name": "Build and test",
        "expected_fix": "Aggiungere \"overrides\": { \"react\": \"18.2.0\", \"react-dom\": \"18.2.0\" } in package.json per forzare un'unica istanza di react condivisa nell'albero delle dipendenze",
        "notes": "some-ui-lib installa una propria copia di react come dipendenza diretta invece di usare peerDependencies, causando due istanze duplicate a runtime"
    },

    {
        "id": "dep_048",
        "category": "dependency",
        "difficulty": "hard",
        "ci_logs": """
            ##[group]Run pip install -r requirements.txt
            ERROR: Cannot install boto3==1.34.10 and botocore==1.33.0 because these package versions have conflicting dependencies.
            The conflict is caused by:
                boto3 1.34.10 depends on botocore<1.35.0,>=1.34.10
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-botocore==1.34.10\n+botocore==1.33.0",
        "ci_job_name": "Install dependencies",
        "expected_fix": "Allineare botocore==1.34.10 (o rimuovere il pin esplicito e lasciare che boto3 risolva la versione compatibile automaticamente)",
        "notes": "boto3 e botocore devono essere aggiornati in coppia — pin manuale di botocore a versione più vecchia rompe il vincolo"
    },

    {
        "id": "dep_049",
        "category": "dependency",
        "difficulty": "hard",
        "ci_logs": """
            ##[group]Run actions/cache@v4
            Cache restored from key: pip-3.11-9c1a0d3e
            Run pip install -r requirements.txt
            Requirement already satisfied: requests==2.28.0 (from cache) although requirements.txt specifies requests==2.31.0
            FAILED tests/test_api.py::test_new_timeout_param - TypeError: request() got an unexpected keyword argument 'timeout_ms'
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-          key: pip-${{ hashFiles('requirements.txt') }}\n+          key: pip-${{ hashFiles('requirements-base.txt') }}",
        "ci_job_name": "Install dependencies",
        "expected_fix": "Correggere la cache key per usare hashFiles('requirements.txt') (il file realmente modificato), così che un cambiamento nelle dipendenze invalidi correttamente la cache",
        "notes": "La chiave di cache referenzia il file sbagliato: le modifiche a requirements.txt non invalidano la cache, causando l'uso di dipendenze obsolete"
    },

    {
        "id": "dep_050",
        "category": "dependency",
        "difficulty": "hard",
        "ci_logs": """
            ##[group]Run pip install -r requirements.txt
            ERROR: Could not find a version that satisfies the requirement mypackage==2.0.0rc1 (from versions: 1.8.0, 1.9.0, 1.9.1)
            ERROR: No matching distribution found for mypackage==2.0.0rc1
            Note: pre-release versions are not selected by default unless --pre is specified
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-mypackage==1.9.1\n+mypackage==2.0.0rc1",
        "ci_job_name": "Install dependencies",
        "expected_fix": "Usare mypackage==1.9.1 (versione stabile) oppure aggiungere --pre al comando pip install se la release candidate è necessaria intenzionalmente",
        "notes": "Pin a una release candidate (pre-release) che pip ignora di default senza il flag --pre"
    },

    # ══════════════════════════════════════════════════════════
    # CATEGORIA: TEST (50 errori)
    # ══════════════════════════════════════════════════════════

    {
        "id": "test_001",
        "category": "test",
        "difficulty": "easy",
        "ci_logs": """
            ##[group]Run pytest tests/ -v
            FAILED tests/test_calculator.py::test_add_positivi - AssertionError: assert 5 == 99
            short test summary info
            FAILED tests/test_calculator.py::test_add_positivi
            1 failed, 5 passed in 0.42s
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-assert add(2, 3) == 5\n+assert add(2, 3) == 99",
        "ci_job_name": "Run Tests",
        "expected_fix": "Ripristinare assert add(2, 3) == 5",
        "notes": "Assert modificato con valore errato — caso base"
    },

    {
        "id": "test_002",
        "category": "test",
        "difficulty": "easy",
        "ci_logs": """
            ##[group]Run pytest tests/ -v
            FAILED tests/test_calculator.py::test_divide_normale - AssertionError: assert 5.0 == 2.5
            short test summary info
            FAILED tests/test_calculator.py::test_divide_normale
            1 failed, 5 passed in 0.38s
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-assert divide(10, 2) == 5.0\n+assert divide(10, 2) == 2.5",
        "ci_job_name": "Run Tests",
        "expected_fix": "Ripristinare assert divide(10, 2) == 5.0",
        "notes": "Valore atteso sbagliato in operazione aritmetica"
    },

    {
        "id": "test_003",
        "category": "test",
        "difficulty": "easy",
        "ci_logs": """
            ##[group]Run pytest tests/ -v
            FAILED tests/test_calculator.py::test_factorial_normale - AssertionError: assert 120 == 60
            short test summary info
            FAILED tests/test_calculator.py::test_factorial_normale
            1 failed, 5 passed in 0.41s
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-assert factorial(5) == 120\n+assert factorial(5) == 60",
        "ci_job_name": "Run Tests",
        "expected_fix": "Ripristinare assert factorial(5) == 120",
        "notes": "Risultato fattoriale errato nel test"
    },

    {
        "id": "test_004",
        "category": "test",
        "difficulty": "easy",
        "ci_logs": """
            ##[group]Run pytest tests/ -v
            FAILED tests/test_utils.py::test_string_upper - AssertionError: assert 'hello' == 'HELLO'
            AssertionError: assert 'hello' == 'HELLO'
            where 'hello' = to_upper('hello')
            1 failed, 3 passed in 0.29s
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-assert to_upper('hello') == 'HELLO'\n+assert to_upper('hello') == 'hello'",
        "ci_job_name": "Run Tests",
        "expected_fix": "Ripristinare assert to_upper('hello') == 'HELLO'",
        "notes": "Test stringa con attesa lowercase invece di uppercase"
    },

    {
        "id": "test_005",
        "category": "test",
        "difficulty": "easy",
        "ci_logs": """
            ##[group]Run pytest tests/ -v
            FAILED tests/test_api.py::test_status_code - AssertionError: assert 200 == 404
            AssertionError: assert 200 == 404
            where 200 = response.status_code
            1 failed, 4 passed in 0.55s
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-assert response.status_code == 200\n+assert response.status_code == 404",
        "ci_job_name": "Run Tests",
        "expected_fix": "Ripristinare assert response.status_code == 200",
        "notes": "Status code atteso sbagliato"
    },

    {
        "id": "test_006",
        "category": "test",
        "difficulty": "easy",
        "ci_logs": """
            ##[group]Run pytest tests/ -v
            FAILED tests/test_models.py::test_user_creation - AssertionError: assert 'John' == 'john'
            assert 'John' == 'john'
            1 failed, 7 passed in 0.61s
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-assert user.name == 'John'\n+assert user.name == 'john'",
        "ci_job_name": "Run Tests",
        "expected_fix": "Ripristinare assert user.name == 'John' (maiuscola)",
        "notes": "Case sensitivity nel valore atteso"
    },

    {
        "id": "test_007",
        "category": "test",
        "difficulty": "easy",
        "ci_logs": """
            ##[group]Run pytest tests/ -v
            FAILED tests/test_math.py::test_power - AssertionError: assert 8 == 16
            assert 8 == 16
            where 8 = power(2, 3)
            1 failed, 2 passed in 0.22s
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-assert power(2, 3) == 8\n+assert power(2, 4) == 8",
        "ci_job_name": "Run Tests",
        "expected_fix": "Ripristinare assert power(2, 3) == 8",
        "notes": "Esponente sbagliato nel test"
    },

    {
        "id": "test_008",
        "category": "test",
        "difficulty": "easy",
        "ci_logs": """
            ##[group]Run pytest tests/ -v
            FAILED tests/test_list.py::test_list_length - AssertionError: assert 3 == 5
            assert 3 == 5
            where 3 = len([1, 2, 3])
            1 failed, 4 passed in 0.31s
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-assert len([1, 2, 3]) == 3\n+assert len([1, 2, 3]) == 5",
        "ci_job_name": "Run Tests",
        "expected_fix": "Ripristinare assert len([1, 2, 3]) == 3",
        "notes": "Lunghezza lista attesa sbagliata"
    },

    {
        "id": "test_009",
        "category": "test",
        "difficulty": "medium",
        "ci_logs": """
            ##[group]Run pytest tests/ -v
            FAILED tests/test_service.py::test_get_user - AttributeError: 'UserService' object has no attribute 'get_user'
            AttributeError: 'UserService' object has no attribute 'get_user'
            Hint: method was renamed to 'fetch_user' in version 2.0
            1 failed, 6 passed in 0.48s
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-def get_user(self, user_id):\n+def fetch_user(self, user_id):",
        "ci_job_name": "Run Tests",
        "expected_fix": "Aggiornare il test: sostituire service.get_user() con service.fetch_user()",
        "notes": "Rename di metodo nel sorgente non riflesso nel test"
    },

    {
        "id": "test_010",
        "category": "test",
        "difficulty": "medium",
        "ci_logs": """
            ##[group]Run pytest tests/ -v
            FAILED tests/test_api.py::test_create_item - AssertionError: assert {'id': 1, 'name': 'item', 'price': 10.0} == {'id': 1, 'name': 'item'}
            AssertionError: assert ... == ...
            Right dict has extra keys: {'price'}
            1 failed, 8 passed in 0.73s
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "+    'price': 10.0,\n     'id': 1,\n     'name': 'item'",
        "ci_job_name": "Run Tests",
        "expected_fix": "Aggiornare il test per includere il campo 'price' nell'assert atteso",
        "notes": "Nuovo campo aggiunto al modello non incluso nel test"
    },

    {
        "id": "test_011",
        "category": "test",
        "difficulty": "medium",
        "ci_logs": """
            ##[group]Run pytest tests/ -v
            FAILED tests/test_auth.py::test_login - AssertionError: assert True == False
            Expected login to fail with wrong password but it succeeded
            assert response.ok == False
            1 failed, 5 passed in 0.61s
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-    MIN_PASSWORD_LENGTH = 8\n+    MIN_PASSWORD_LENGTH = 4",
        "ci_job_name": "Run Tests",
        "expected_fix": "Aggiornare il test per usare password che fallisce con il nuovo minimo di 4 caratteri, oppure ripristinare MIN_PASSWORD_LENGTH = 8",
        "notes": "Cambio logica business riflessa nel test — ambiguo se fix è nel test o nel sorgente"
    },

    {
        "id": "test_012",
        "category": "test",
        "difficulty": "medium",
        "ci_logs": """
            ##[group]Run pytest tests/ -v
            FAILED tests/test_db.py::test_save_record - TypeError: save() missing 1 required positional argument: 'commit'
            TypeError: save() missing 1 required positional argument: 'commit'
            1 failed, 9 passed in 0.82s
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-def save(self, record):\n+def save(self, record, commit=True):",
        "ci_job_name": "Run Tests",
        "expected_fix": "Il test chiama save(record) — aggiungere commit=True nella chiamata oppure è già default — verificare che il test passi il parametro correttamente",
        "notes": "Nuova firma funzione con parametro obbligatorio aggiunto"
    },

    {
        "id": "test_013",
        "category": "test",
        "difficulty": "medium",
        "ci_logs": """
            ##[group]Run pytest tests/ -v
            FAILED tests/test_mock.py::test_email_send - AssertionError: Expected 'send_email' to have been called once. Called 0 times.
            AssertionError: Expected mock_smtp.send_email to have been called once
            1 failed, 4 passed in 0.44s
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-    smtp.send_email(to, subject, body)\n+    smtp.send_message(to, subject, body)",
        "ci_job_name": "Run Tests",
        "expected_fix": "Aggiornare il mock: mock_smtp.send_message invece di mock_smtp.send_email",
        "notes": "Metodo rinominato nel sorgente, mock non aggiornato"
    },

    {
        "id": "test_014",
        "category": "test",
        "difficulty": "medium",
        "ci_logs": """
            ##[group]Run pytest tests/ -v
            FAILED tests/test_config.py::test_load_config - KeyError: 'database_url'
            KeyError: 'database_url'
            config = load_config()
            assert config['database_url'] == 'sqlite:///test.db'
            1 failed, 3 passed in 0.29s
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-    'database_url': db_url\n+    'db_url': db_url",
        "ci_job_name": "Run Tests",
        "expected_fix": "Aggiornare il test: config['db_url'] invece di config['database_url']",
        "notes": "Chiave dizionario rinominata nel sorgente"
    },

    {
        "id": "test_015",
        "category": "test",
        "difficulty": "medium",
        "ci_logs": """
            ##[group]Run pytest tests/ -v
            FAILED tests/test_validator.py::test_email_validation - AssertionError: assert False == True
            Expected 'user@example' (without TLD) to be invalid but validator accepted it
            1 failed, 6 passed in 0.51s
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-    REQUIRE_TLD = True\n+    REQUIRE_TLD = False",
        "ci_job_name": "Run Tests",
        "expected_fix": "Ripristinare REQUIRE_TLD = True oppure aggiornare il test per accettare il nuovo comportamento",
        "notes": "Cambio di comportamento del validator — fix ambiguo (test o sorgente)"
    },

    {
        "id": "test_016",
        "category": "test",
        "difficulty": "hard",
        "ci_logs": """
            ##[group]Run pytest tests/ -v
            FAILED tests/test_async.py::test_fetch_data - RuntimeError: This event loop is already running
            RuntimeError: This event loop is already running
            async def test_fetch_data():
                result = await fetch_data()
            2 failed, 8 passed in 1.23s
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "+import asyncio\n+loop = asyncio.get_event_loop()\n+loop.run_until_complete(setup())",
        "ci_job_name": "Run Tests",
        "expected_fix": "Rimuovere loop.run_until_complete() dal setup o usare pytest-asyncio con @pytest.mark.asyncio",
        "notes": "Conflitto event loop asyncio — richiede conoscenza pytest-asyncio"
    },

    {
        "id": "test_017",
        "category": "test",
        "difficulty": "hard",
        "ci_logs": """
            ##[group]Run pytest tests/ -v
            FAILED tests/test_integration.py::test_full_pipeline - AssertionError: assert 0 == 1
            Database has 0 records but expected 1
            Note: test_setup fixture is session-scoped and may have been cleaned by another test
            ERROR tests/test_integration.py::test_full_pipeline - sqlite3.OperationalError: no such table: users
            3 failed, 12 passed in 2.41s
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-@pytest.fixture(scope='function')\n+@pytest.fixture(scope='session')\ndef db_setup():",
        "ci_job_name": "Run Tests",
        "expected_fix": "Ripristinare scope='function' per la fixture db_setup o aggiungere autouse e reset esplicito del db",
        "notes": "Scope fixture mal configurato — side effect tra test"
    },

    {
        "id": "test_018",
        "category": "test",
        "difficulty": "hard",
        "ci_logs": """
            ##[group]Run pytest tests/ -v
            FAILED tests/test_cache.py::test_cache_invalidation - AssertionError: assert 'old_value' == 'new_value'
            Cache not invalidated after update
            Time-dependent test: cache TTL is 300s but test uses freeze_time
            ERROR: freeze_time decorator not applied correctly
            2 failed, 5 passed in 0.88s
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-@freeze_time('2024-01-01 12:00:00')\n+@freeze_time('2024-01-01')\ndef test_cache_invalidation():",
        "ci_job_name": "Run Tests",
        "expected_fix": "Ripristinare formato datetime completo: @freeze_time('2024-01-01 12:00:00')",
        "notes": "freeze_time con data senza orario — comportamento diverso per TTL"
    },

    {
        "id": "test_019",
        "category": "test",
        "difficulty": "hard",
        "ci_logs": """
            ##[group]Run pytest tests/ -v
            FAILED tests/test_serializer.py::test_json_serialize - AssertionError: assert '{"date": "2024-01-15"}' == '{"date": "2024-01-15T00:00:00"}'
            JSON serialization format changed
            Expected ISO 8601 with time component
            1 failed, 11 passed in 0.94s
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-    return date.isoformat()\n+    return date.strftime('%Y-%m-%d')",
        "ci_job_name": "Run Tests",
        "expected_fix": "Ripristinare date.isoformat() per mantenere formato ISO 8601 completo, oppure aggiornare tutti i test che si aspettano il formato con orario",
        "notes": "Cambio formato data — impatto a cascata su più test"
    },

    {
        "id": "test_020",
        "category": "test",
        "difficulty": "hard",
        "ci_logs": """
            ##[group]Run pytest tests/ -v
            FAILED tests/test_concurrent.py::test_thread_safety - AssertionError: assert Counter({1: 100}) == Counter({1: 50, 2: 50})
            Race condition detected: counter incremented 100 times instead of 50+50
            Threading issue: lock not acquired correctly
            FAILED tests/test_concurrent.py::test_thread_safety (intermittent)
            2 failed, 14 passed in 3.21s
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-    with self.lock:\n+    # removed lock\n         self.counter += 1",
        "ci_job_name": "Run Tests",
        "expected_fix": "Ripristinare il context manager with self.lock: prima dell'incremento del counter",
        "notes": "Race condition da rimozione lock — test intermittente, difficile da riprodurre"
    },

    # --- Nuovi casi (test_021 - test_050) ---

    {
        "id": "test_021",
        "category": "test",
        "difficulty": "easy",
        "ci_logs": """
            ##[group]Run pytest tests/ -v
            FAILED tests/test_math.py::test_sum_floats - AssertionError: assert 0.30000000000000004 == 0.3
            assert (0.1 + 0.2) == 0.3
            1 failed, 9 passed in 0.33s
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-    assert result == pytest.approx(0.3)\n+    assert result == 0.3",
        "ci_job_name": "Run Tests",
        "expected_fix": "Usare assert result == pytest.approx(0.3) invece del confronto diretto di float",
        "notes": "Errore di precisione floating point classico — richiede pytest.approx"
    },

    {
        "id": "test_022",
        "category": "test",
        "difficulty": "easy",
        "ci_logs": """
            ##[group]Run pytest tests/ -v
            FAILED tests/test_parser.py::test_invalid_input - Failed: DID NOT RAISE <class 'ValueError'>
            parser.py now raises TypeError instead of ValueError for invalid input
            1 failed, 10 passed in 0.40s
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-    raise ValueError(f\"Invalid input: {value}\")\n+    raise TypeError(f\"Invalid input: {value}\")",
        "ci_job_name": "Run Tests",
        "expected_fix": "Aggiornare il test: pytest.raises(TypeError) invece di pytest.raises(ValueError)",
        "notes": "Tipo di eccezione sollevata cambiato nel sorgente, test non aggiornato"
    },

    {
        "id": "test_023",
        "category": "test",
        "difficulty": "easy",
        "ci_logs": """
            ##[group]Run pytest tests/ -v
            ERROR tests/test_payment.py - ModuleNotFoundError: No module named 'app.services.payment'
            tests/test_payment.py:2: in <module>
                from app.services.payment import process_payment
            1 error in 0.12s
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-app/services/payment.py\n+app/billing/payment.py  (file spostato)",
        "ci_job_name": "Run Tests",
        "expected_fix": "Aggiornare l'import nel test: from app.billing.payment import process_payment",
        "notes": "Modulo spostato durante un refactor, import nel test non aggiornato"
    },

    {
        "id": "test_024",
        "category": "test",
        "difficulty": "easy",
        "ci_logs": """
            ##[group]Run pytest tests/ -v
            ERROR tests/test_orders.py::test_create_order - fixture 'db_sesion' not found
            available fixtures: db_session, tmp_path, ...
            1 error in 0.15s
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-def test_create_order(db_session):\n+def test_create_order(db_sesion):",
        "ci_job_name": "Run Tests",
        "expected_fix": "Correggere il typo nel nome della fixture: db_sesion → db_session",
        "notes": "Typo nel nome del parametro fixture — pytest non trova la fixture richiesta"
    },

    {
        "id": "test_025",
        "category": "test",
        "difficulty": "easy",
        "ci_logs": """
            ##[group]Run pytest tests/ -v
            FAILED tests/test_loader.py::test_load_csv - FileNotFoundError: [Errno 2] No such file or directory: '/home/dev/project/data/sample.csv'
            1 failed, 7 passed in 0.28s
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-    path = Path(__file__).parent / 'data' / 'sample.csv'\n+    path = '/home/dev/project/data/sample.csv'",
        "ci_job_name": "Run Tests",
        "expected_fix": "Ripristinare il path relativo Path(__file__).parent / 'data' / 'sample.csv' invece del path assoluto locale",
        "notes": "Path assoluto specifico della macchina dello sviluppatore, inesistente nel runner CI"
    },

    {
        "id": "test_026",
        "category": "test",
        "difficulty": "easy",
        "ci_logs": """
            ##[group]Run pytest tests/ -v
            FAILED tests/test_math.py::test_square[4-15] - AssertionError: assert 16 == 15
            1 failed, 4 passed in 0.30s
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-@pytest.mark.parametrize('n,expected', [(2,4),(3,9),(4,16)])\n+@pytest.mark.parametrize('n,expected', [(2,4),(3,9),(4,15)])",
        "ci_job_name": "Run Tests",
        "expected_fix": "Correggere il valore atteso per n=4: deve essere 16, non 15",
        "notes": "Un solo caso della parametrizzazione ha il valore atteso sbagliato"
    },

    {
        "id": "test_027",
        "category": "test",
        "difficulty": "easy",
        "ci_logs": """
            ##[group]Run pytest tests/ -v
            ERROR tests/test_import.py::test_parse_sample - FileNotFoundError: [Errno 2] No such file or directory: 'tests/fixtures/sample.json'
            1 error in 0.10s
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-tests/fixtures/sample.json  (file rimosso dal commit)",
        "ci_job_name": "Run Tests",
        "expected_fix": "Ripristinare/committare il file tests/fixtures/sample.json richiesto dal test",
        "notes": "File di fixture usato dal test non è stato incluso nel commit"
    },

    {
        "id": "test_028",
        "category": "test",
        "difficulty": "easy",
        "ci_logs": """
            ##[group]Run pytest tests/ -v
            FAILED tests/test_notify.py::test_send_alert - AttributeError: <module 'app.notify'> does not have the attribute 'send_emial'
            1 failed, 5 passed in 0.35s
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-@patch('app.notify.send_email')\n+@patch('app.notify.send_emial')",
        "ci_job_name": "Run Tests",
        "expected_fix": "Correggere il typo nel target del patch: 'app.notify.send_emial' → 'app.notify.send_email'",
        "notes": "Typo nel path del mock patch causa AttributeError invece di un semplice mock silenzioso"
    },

    {
        "id": "test_029",
        "category": "test",
        "difficulty": "easy",
        "ci_logs": """
            ##[group]Run pytest tests/ -v
            FAILED tests/test_registry.py::test_registered_plugins - AssertionError: assert ['b_plugin', 'a_plugin'] == ['a_plugin', 'b_plugin']
            1 failed, 6 passed in 0.22s
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-    assert sorted(registry.keys()) == ['a_plugin', 'b_plugin']\n+    assert list(registry.keys()) == ['a_plugin', 'b_plugin']",
        "ci_job_name": "Run Tests",
        "expected_fix": "Usare sorted(registry.keys()) nel confronto invece di list(), poiché l'ordine di inserimento nel dizionario non è garantito stabile tra le run",
        "notes": "Test assume un ordine di iterazione non garantito su una struttura dizionario/set"
    },

    {
        "id": "test_030",
        "category": "test",
        "difficulty": "easy",
        "ci_logs": """
            ##[group]Run pytest tests/ -v
            FAILED tests/test_legacy.py::test_old_behavior - [XPASS(strict)] bug fixed upstream
            1 failed, 12 passed in 0.51s
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-def normalize(x):\n-    return x  # bug: non normalizza\n+def normalize(x):\n+    return x.strip().lower()",
        "ci_job_name": "Run Tests",
        "expected_fix": "Rimuovere il marker @pytest.mark.xfail(strict=True) da test_old_behavior, dato che il bug è stato risolto e il test ora passa correttamente",
        "notes": "xfail strict fallisce quando il test marcato come 'atteso fallire' passa inaspettatamente (il bug sottostante è stato corretto)"
    },

    {
        "id": "test_031",
        "category": "test",
        "difficulty": "easy",
        "ci_logs": """
            ##[group]Run pytest tests/ -v -W error::DeprecationWarning
            FAILED tests/test_dates.py::test_parse_date - DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal
            1 failed, 14 passed in 0.44s
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-    now = datetime.now(timezone.utc)\n+    now = datetime.utcnow()",
        "ci_job_name": "Run Tests",
        "expected_fix": "Ripristinare datetime.now(timezone.utc) invece di datetime.utcnow(), che è deprecato nelle versioni recenti di Python",
        "notes": "Warning di deprecazione promosso a errore dalla configurazione pytest (-W error), la nuova API deprecata rompe la build"
    },

    {
        "id": "test_032",
        "category": "test",
        "difficulty": "medium",
        "ci_logs": """
            ##[group]Run pytest tests/ -v
            FAILED tests/test_worker.py::test_background_task - AssertionError: assert 'done' == None
            Task had not completed processing when assertion ran
            FAILED tests/test_worker.py::test_background_task (intermittent, passed on retry)
            1 failed, 10 passed in 1.15s
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-    time.sleep(0.5)\n+    time.sleep(0.05)",
        "ci_job_name": "Run Tests",
        "expected_fix": "Ripristinare un'attesa sufficiente (time.sleep(0.5)) oppure sostituire lo sleep fisso con un polling/wait_until sulla condizione di completamento del task",
        "notes": "Timeout ridotto troppo aggressivamente rende il test flaky per race condition sul task in background"
    },

    {
        "id": "test_033",
        "category": "test",
        "difficulty": "medium",
        "ci_logs": """
            ##[group]Run pytest tests/ -v
            FAILED tests/test_settings.py::test_default_config - AssertionError: assert 'debug' == 'production'
            Passes when run alone: pytest tests/test_settings.py::test_default_config
            Fails when run with full suite: shared module-level CONFIG dict mutated by test_settings.py::test_override_config
            2 failed, 20 passed in 1.80s
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-def test_override_config():\n-    config = copy.deepcopy(CONFIG)\n-    config['env'] = 'production'\n+def test_override_config():\n+    CONFIG['env'] = 'production'",
        "ci_job_name": "Run Tests",
        "expected_fix": "Ripristinare la copia difensiva (copy.deepcopy(CONFIG)) in test_override_config invece di mutare direttamente lo stato globale condiviso CONFIG",
        "notes": "Test mutano uno stato globale condiviso senza isolamento — fallisce solo se eseguito insieme ad altri test, non individualmente"
    },

    {
        "id": "test_034",
        "category": "test",
        "difficulty": "medium",
        "ci_logs": """
            ##[group]Run pytest tests/ -v
            FAILED tests/test_weather.py::test_get_forecast - requests.exceptions.ConnectionError: Failed to establish a new connection: Temporary failure in name resolution
            1 failed, 8 passed in 5.02s
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-    @patch('app.weather.requests.get')\n-    def test_get_forecast(self, mock_get):\n+    def test_get_forecast(self):",
        "ci_job_name": "Run Tests",
        "expected_fix": "Ripristinare il mock @patch('app.weather.requests.get') per evitare chiamate di rete reali durante il test, non disponibili nel sandbox CI",
        "notes": "Rimozione del mock espone il test a una dipendenza di rete reale, assente/instabile nell'ambiente CI"
    },

    {
        "id": "test_035",
        "category": "test",
        "difficulty": "medium",
        "ci_logs": """
            ##[group]Run pytest tests/ -v
            FAILED tests/test_sampler.py::test_sample_distribution - AssertionError: assert 0.42 < 0.4
            Test occasionally fails depending on random seed
            1 failed, 6 passed in 0.60s
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-    random.seed(42)\n+    # random.seed(42) rimosso",
        "ci_job_name": "Run Tests",
        "expected_fix": "Ripristinare random.seed(42) all'inizio del test per rendere il campionamento deterministico",
        "notes": "Seed random rimosso — il test diventa non deterministico e fallisce in modo intermittente"
    },

    {
        "id": "test_036",
        "category": "test",
        "difficulty": "medium",
        "ci_logs": """
            ##[group]Run pytest tests/ -n auto
            FAILED tests/test_export.py::test_write_csv - PermissionError: [Errno 13] Permission denied: '/tmp/output.csv'
            Two workers (gw0, gw1) wrote to the same hardcoded temp file concurrently
            2 failed, 30 passed in 4.10s
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-    output_path = tmp_path / 'output.csv'\n+    output_path = '/tmp/output.csv'",
        "ci_job_name": "Run Tests",
        "expected_fix": "Usare la fixture tmp_path di pytest invece di un path fisso '/tmp/output.csv', per garantire un file isolato per ogni worker/test",
        "notes": "Path temporaneo hardcoded condiviso causa collisioni quando i test girano in parallelo con pytest-xdist"
    },

    {
        "id": "test_037",
        "category": "test",
        "difficulty": "medium",
        "ci_logs": """
            ##[group]Run pytest tests/ -v
            FAILED tests/test_report.py::test_render_summary - AssertionError: snapshot mismatch for 'summary_report'
            - Snapshot 'summary_report' does not match
            + Total: $1,234.56
            - Total: 1234.56
            1 failed, 9 passed in 0.70s
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-    return f\"Total: {total}\"\n+    return f\"Total: ${total:,.2f}\"",
        "ci_job_name": "Run Tests",
        "expected_fix": "Rigenerare lo snapshot con pytest --snapshot-update, poiché il nuovo formato di output ($1,234.56) è il comportamento corretto e atteso",
        "notes": "Cambio intenzionale del formato di output richiede l'aggiornamento dello snapshot di riferimento"
    },

    {
        "id": "test_038",
        "category": "test",
        "difficulty": "medium",
        "ci_logs": """
            ##[group]Run pytest tests/ -v
            ERROR tests/test_orders.py::test_order_status - sqlalchemy.exc.OperationalError: (sqlite3.OperationalError) no such column: orders.status
            Hint: a new migration adds this column but was not applied to the test database
            4 errors in 0.95s
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-      - run: alembic upgrade head\n-      - run: pytest tests/\n+      - run: pytest tests/",
        "ci_job_name": "Run Tests",
        "expected_fix": "Ripristinare lo step 'alembic upgrade head' prima di eseguire pytest, per applicare le migrazioni al database di test",
        "notes": "Step di migrazione del database rimosso dal workflow, lo schema di test risulta disallineato dal modello"
    },

    {
        "id": "test_039",
        "category": "test",
        "difficulty": "medium",
        "ci_logs": """
            ##[group]Run pytest tests/ -v --timeout=30
            FAILED tests/test_queue.py::test_consumer_processes_message - Failed: Timeout >30.0s
            Test hung waiting on queue.get() — producer never enqueued a message due to a deadlock on the shared lock
            1 failed, 11 passed in 30.12s
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-    with lock:\n-        queue.put(message)\n-    consumer.process()\n+    with lock:\n+        queue.put(message)\n+        consumer.process()",
        "ci_job_name": "Run Tests",
        "expected_fix": "Spostare consumer.process() fuori dal blocco 'with lock', poiché process() tenta di riacquisire lo stesso lock causando un deadlock",
        "notes": "Deadlock introdotto chiamando una funzione che richiede lo stesso lock già acquisito nel blocco corrente"
    },

    {
        "id": "test_040",
        "category": "test",
        "difficulty": "medium",
        "ci_logs": """
            ##[group]Run pytest tests/ -v
            FAILED tests/test_validation.py::test_error_message - AssertionError: assert 'Invalid value provided' == 'Invalid value'
            Upstream library changed exception wording in v2.1
            1 failed, 13 passed in 0.38s
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-    raise ValidationError('Invalid value')\n+    raise ValidationError('Invalid value provided')",
        "ci_job_name": "Run Tests",
        "expected_fix": "Aggiornare l'assert nel test al nuovo testo del messaggio: 'Invalid value provided'",
        "notes": "Testo del messaggio di eccezione cambiato nel sorgente, test con assert testuale fragile non aggiornato"
    },

    {
        "id": "test_041",
        "category": "test",
        "difficulty": "medium",
        "ci_logs": """
            ##[group]Run pytest tests/ -v
            FAILED tests/test_scheduler.py::test_format_local_time - AssertionError: assert '14:30 UTC' == '16:30 CEST'
            Test assumes the runner's local timezone is Europe/Rome, but GitHub Actions runners default to UTC
            1 failed, 7 passed in 0.42s
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-    assert format_local(dt) == '14:30 UTC'\n+    assert format_local(dt) == '16:30 CEST'",
        "ci_job_name": "Run Tests",
        "expected_fix": "Rendere il test indipendente dal timezone del runner: impostare esplicitamente TZ='Europe/Rome' nell'ambiente di test o confrontare l'orario in UTC",
        "notes": "Test dipende implicitamente dal timezone locale della macchina, diverso tra ambiente di sviluppo e runner CI (UTC)"
    },

    {
        "id": "test_042",
        "category": "test",
        "difficulty": "hard",
        "ci_logs": """
            ##[group]Run pytest tests/ -n 4 -v
            FAILED tests/test_metrics.py::test_increment_counter - AssertionError: assert 97 == 100
            Failure only reproducible under parallel execution (gw2, gw3 share the same Redis counter key)
            FAILED (intermittent, 1/5 runs)
            3 failed, 45 passed in 6.44s
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-    key = f'counter:{uuid.uuid4()}'\n+    key = 'counter:test'",
        "ci_job_name": "Run Tests",
        "expected_fix": "Usare una chiave Redis univoca per test (es. f'counter:{uuid.uuid4()}') invece di una chiave fissa condivisa tra i worker paralleli",
        "notes": "Race condition riproducibile solo con pytest-xdist: worker paralleli condividono una risorsa esterna (Redis) tramite chiave hardcoded"
    },

    {
        "id": "test_043",
        "category": "test",
        "difficulty": "hard",
        "ci_logs": """
            ##[group]Run pytest tests/ -v
            FAILED tests/test_image_processing.py::test_resize[500] - Worker crashed: OOMKilled
            Memory usage grew steadily across parametrized cases: images loaded in fixture are never released between iterations
            2 failed, 48 passed in 45.30s
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-@pytest.fixture\n-def image_cache():\n-    cache = {}\n-    yield cache\n-    cache.clear()\n+@pytest.fixture(scope='session')\n+def image_cache():\n+    cache = {}\n+    yield cache",
        "ci_job_name": "Run Tests",
        "expected_fix": "Ripristinare lo scope della fixture a 'function' (o aggiungere cache.clear() nel teardown) per rilasciare la memoria tra un caso parametrizzato e l'altro",
        "notes": "Fixture con scope 'session' accumula immagini in cache tra le iterazioni parametrizzate, causando un memory leak che porta all'OOM"
    },

    {
        "id": "test_044",
        "category": "test",
        "difficulty": "hard",
        "ci_logs": """
            ##[group]Run pytest tests/ -v
            FAILED tests/test_dedup.py::test_deduplicate_preserves_first - AssertionError: assert ['b','a'] == ['a','b']
            Failure only occurs when PYTHONHASHSEED is randomized (not reproducible with PYTHONHASHSEED=0)
            1 failed, 22 passed in 0.51s
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-    seen = OrderedDict()\n+    seen = {}",
        "ci_job_name": "Run Tests",
        "expected_fix": "Usare dict.fromkeys() o OrderedDict per deduplicare preservando l'ordine di inserimento, invece di una struttura la cui iterazione dipende dall'hash randomizzato",
        "notes": "Comportamento non deterministico legato a PYTHONHASHSEED — il test passa quasi sempre ma fallisce sporadicamente"
    },

    {
        "id": "test_045",
        "category": "test",
        "difficulty": "hard",
        "ci_logs": """
            ##[group]Run pytest tests/ -v
            FAILED tests/test_reports.py::test_final_export - sqlite3.ProgrammingError: Cannot operate on a closed database.
            Failure only on the last test of the session: session-scoped 'db_engine' fixture torn down before function-scoped 'report_writer' fixture that depends on it
            1 failed, 29 passed in 3.02s
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-@pytest.fixture(scope='function')\n-def report_writer(db_engine):\n+@pytest.fixture(scope='module')\n+def report_writer(db_engine):",
        "ci_job_name": "Run Tests",
        "expected_fix": "Ripristinare scope='function' per report_writer, oppure allineare esplicitamente lo scope di db_engine a 'module' per evitare che venga chiuso prima del previsto",
        "notes": "Mismatch di scope tra fixture dipendenti causa un teardown anticipato che si manifesta solo sull'ultimo test della sessione"
    },

    {
        "id": "test_046",
        "category": "test",
        "difficulty": "hard",
        "ci_logs": """
            ##[group]Run pytest tests/ -v
            FAILED tests/test_stats.py::test_variance_calculation - AssertionError: assert 2.9999999999999996 == 3.0
            Passes on x86_64 runners, fails only on macos-14 (Apple Silicon / arm64) due to different floating point rounding in numpy's pairwise summation
            1 failed, 40 passed in 1.10s
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-    assert variance == pytest.approx(3.0)\n+    assert variance == 3.0",
        "ci_job_name": "Run Tests",
        "expected_fix": "Usare pytest.approx(3.0) per il confronto, poiché piccole differenze di arrotondamento floating point tra architetture (x86_64 vs arm64) sono attese e non un bug applicativo",
        "notes": "Differenza di precisione numerica dipendente dall'architettura del runner — comportamento noto e non un errore di calcolo"
    },

    {
        "id": "test_047",
        "category": "test",
        "difficulty": "hard",
        "ci_logs": """
            ##[group]Run pytest tests/ -v --cov=src --cov-fail-under=85
            FAILED tests/test_recommender.py::test_ranking_order - AssertionError: assert ['c','a','b'] == ['a','b','c']
            This test is known to be flaky (fails ~1/20 runs) due to unstable sort on tied scores, but this run also shows coverage dropped to 82%
            Required test coverage of 85% not reached. Total coverage: 82.00%
            2 failed, 60 passed in 8.90s
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-    ranked = sorted(items, key=lambda x: x.score, reverse=True)\n+    ranked = sorted(items, key=lambda x: -x.score)\n-def test_edge_case_empty_input():\n-    assert recommend([]) == []",
        "ci_job_name": "Run Tests",
        "expected_fix": "Rendere l'ordinamento stabile per punteggi pari (aggiungere una key secondaria, es. per id) per eliminare la flakiness, E ripristinare test_edge_case_empty_input rimosso per riportare la coverage sopra l'85%: entrambi i problemi vanno risolti, non solo uno",
        "notes": "Caso ambiguo hard: un test flaky preesistente nasconde una regressione reale di coverage dovuta alla rimozione di un test — richiede distinguere due problemi sovrapposti (famiglia simile a test_011/015/019)"
    },

    {
        "id": "test_048",
        "category": "test",
        "difficulty": "hard",
        "ci_logs": """
            ##[group]Run pytest tests/ -n 4 -v
            ERROR tests/test_upload.py::test_multipart_upload - _pickle.PicklingError: Can't pickle <class 'threading.Lock'> object
            remote process crashed on worker gw1
            1 error, 51 passed in 5.5s
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-@pytest.fixture\n-def upload_client():\n-    return UploadClient()\n+@pytest.fixture(scope='session')\n+def upload_client():\n+    client = UploadClient()\n+    client.lock = threading.Lock()\n+    return client",
        "ci_job_name": "Run Tests",
        "expected_fix": "Evitare di condividere un oggetto con threading.Lock tra worker pytest-xdist: creare il Lock all'interno di ogni test/processo invece che in una fixture session-scoped condivisa",
        "notes": "pytest-xdist esegue i worker come processi separati; oggetti non serializzabili (come i Lock) in fixture condivise causano un crash del worker"
    },

    {
        "id": "test_049",
        "category": "test",
        "difficulty": "hard",
        "ci_logs": """
            ##[group]Run pytest tests/ -v
            FAILED tests/test_logger.py::test_second_call_has_only_its_own_entries - AssertionError: assert ['first','second'] == ['second']
            Entries from a previous test call are leaking into subsequent calls
            1 failed, 16 passed in 0.48s
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-def log_entry(entry, entries=None):\n-    entries = entries if entries is not None else []\n+def log_entry(entry, entries=[]):",
        "ci_job_name": "Run Tests",
        "expected_fix": "Ripristinare entries=None come default e inizializzare entries = entries if entries is not None else [] all'interno della funzione, per evitare la condivisione della lista mutabile di default tra le chiamate",
        "notes": "Classico bug Python: argomento di default mutabile (lista) condiviso e accumulato tra chiamate/test successivi"
    },

    {
        "id": "test_050",
        "category": "test",
        "difficulty": "hard",
        "ci_logs": """
            ##[group]Run pytest tests/ -v
            FAILED tests/test_billing_cycle.py::test_hours_between - AssertionError: assert 23 == 24
            Test run during DST transition (last Sunday of March): one day in the range has only 23 hours in Europe/Rome
            1 failed, 17 passed in 0.39s
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-    assert delta.total_seconds() / 3600 == pytest.approx(24, abs=1)\n+    assert delta.total_seconds() / 3600 == 24",
        "ci_job_name": "Run Tests",
        "expected_fix": "Usare pytest.approx(24, abs=1) (o calcolare in UTC, dove i giorni hanno sempre 24 ore) per tollerare la variazione dovuta al cambio ora legale/solare",
        "notes": "Calcolo di durata in un timezone locale soggetto a DST — il giorno del cambio ora ha 23 o 25 ore, non sempre 24"
    },

    # ══════════════════════════════════════════════════════════
    # CATEGORIA: CONFIG (50 errori)
    # ══════════════════════════════════════════════════════════

    {
        "id": "conf_001",
        "category": "config",
        "difficulty": "easy",
        "ci_logs": """
            ##[group]Set up Python 3.99
            Error: Version 3.99 with arch x64 not found
            The following versions of Python are currently available for use: 3.8.18, 3.9.18, 3.10.13, 3.11.7, 3.12.1
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-          python-version: '3.11'\n+          python-version: '3.99'",
        "ci_job_name": "Set up Python 3.99",
        "expected_fix": "Ripristinare python-version: '3.11'",
        "notes": "Versione Python inesistente — caso base config"
    },

    {
        "id": "conf_002",
        "category": "config",
        "difficulty": "easy",
        "ci_logs": """
            ##[group]Set up Python 3.15
            Error: Version 3.15 with arch x64 not found
            The following versions of Python are currently available: 3.8, 3.9, 3.10, 3.11, 3.12
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-          python-version: '3.12'\n+          python-version: '3.15'",
        "ci_job_name": "Set up Python 3.15",
        "expected_fix": "Usare python-version: '3.12'",
        "notes": "Python 3.15 non ancora rilasciato"
    },

    {
        "id": "conf_003",
        "category": "config",
        "difficulty": "easy",
        "ci_logs": """
            ##[group]Set up Python 2.7
            Error: Version 2.7 with arch x64 not found
            Note: Python 2.7 reached End of Life on January 1, 2020 and is no longer supported in GitHub Actions
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-          python-version: '3.11'\n+          python-version: '2.7'",
        "ci_job_name": "Set up Python 2.7",
        "expected_fix": "Usare python-version: '3.11' o superiore",
        "notes": "Python 2.7 EOL — non supportato in GitHub Actions"
    },

    {
        "id": "conf_004",
        "category": "config",
        "difficulty": "easy",
        "ci_logs": """
            ##[group]Checkout
            Error: Input required and not supplied: token
            at Action.run (/home/runner/work/_actions/actions/checkout@v4/dist/index.js)
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-      - uses: actions/checkout@v4\n+      - uses: actions/checkout@v4\n+        with:\n+          token: ${{ secrets.INVALID_TOKEN }}",
        "ci_job_name": "Checkout",
        "expected_fix": "Rimuovere il campo token o usare ${{ secrets.GITHUB_TOKEN }} che è sempre disponibile",
        "notes": "Secret non esistente nel repository"
    },

    {
        "id": "conf_005",
        "category": "config",
        "difficulty": "easy",
        "ci_logs": """
            ##[group]Run pytest
            Error: Unable to process file command 'add-path' successfully
            /home/runner/work/_temp/_runner_file_commands/add-path_xxx: No such file or directory
            Error: An error occurred trying to execute: set-env
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-      - uses: actions/setup-python@v5\n+      - uses: actions/setup-python@v1",
        "ci_job_name": "Set up Python",
        "expected_fix": "Usare actions/setup-python@v5 (versione aggiornata)",
        "notes": "Azione deprecata — v1 usa comandi workflow deprecati"
    },

    {
        "id": "conf_006",
        "category": "config",
        "difficulty": "easy",
        "ci_logs": """
            ##[group]Run tests
            Error: The `runs-on` value 'ubuntu-18.04' is not valid.
            Valid values are: ubuntu-latest, ubuntu-22.04, ubuntu-20.04, ubuntu-24.04
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-    runs-on: ubuntu-latest\n+    runs-on: ubuntu-18.04",
        "ci_job_name": "Run tests",
        "expected_fix": "Usare runs-on: ubuntu-latest o ubuntu-20.04",
        "notes": "Runner ubuntu-18.04 rimosso da GitHub Actions"
    },

    {
        "id": "conf_007",
        "category": "config",
        "difficulty": "easy",
        "ci_logs": """
            ##[group]Run pip install
            Error: working-directory 'src/backend' does not exist
            The specified working directory does not exist.
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-        working-directory: .\n+        working-directory: src/backend",
        "ci_job_name": "Run pip install",
        "expected_fix": "Ripristinare working-directory: . o creare la directory src/backend",
        "notes": "Directory di lavoro inesistente"
    },

    {
        "id": "conf_008",
        "category": "config",
        "difficulty": "easy",
        "ci_logs": """
            ##[group]Cache dependencies
            Error: Unable to locate executable file: pip. Please verify either the file path exists or the file can be found within a directory specified by the PATH environment variable.
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-      - uses: actions/setup-python@v5\n         with:\n           python-version: '3.11'\n+      # removed setup-python step",
        "ci_job_name": "Install dependencies",
        "expected_fix": "Ripristinare lo step actions/setup-python@v5 prima dell'installazione delle dipendenze",
        "notes": "Step setup-python rimosso — pip non disponibile"
    },

    {
        "id": "conf_009",
        "category": "config",
        "difficulty": "medium",
        "ci_logs": """
            ##[group]Parse workflow file
            Error: .github/workflows/ci.yml (Line: 14, Col: 5): A sequence was not expected
            runs-on: ubuntu-latest
                steps:
                ^ unexpected indentation
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-    runs-on: ubuntu-latest\n-    steps:\n+    runs-on: ubuntu-latest\n+        steps:",
        "ci_job_name": "Parse workflow file",
        "expected_fix": "Correggere l'indentazione di 'steps:' — deve essere a 4 spazi, non 8",
        "notes": "Errore YAML da indentazione — non sempre facile identificare la riga esatta"
    },

    {
        "id": "conf_010",
        "category": "config",
        "difficulty": "medium",
        "ci_logs": """
            ##[group]Run workflow
            Error: The workflow is not valid. .github/workflows/ci.yml (Line: 8, Col: 1): Unexpected value 'on'
            YAMLException: duplicated mapping key at line 8 column 1
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "+on:\n   push:\n     branches: [main]\n+on:\n   pull_request:",
        "ci_job_name": "Run workflow",
        "expected_fix": "Unire i trigger sotto un unico blocco 'on:' con push e pull_request",
        "notes": "Chiave YAML duplicata — aggiunto secondo 'on:' invece di estendere il primo"
    },

    {
        "id": "conf_011",
        "category": "config",
        "difficulty": "medium",
        "ci_logs": """
            ##[group]Upload artifact
            Error: Input required and not supplied: path
            at ArtifactUploader.uploadArtifact
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "+      - uses: actions/upload-artifact@v4\n+        with:\n+          name: test-results",
        "ci_job_name": "Upload artifact",
        "expected_fix": "Aggiungere il campo 'path:' richiesto: path: ./test-results/",
        "notes": "Campo obbligatorio mancante nell'azione"
    },

    {
        "id": "conf_012",
        "category": "config",
        "difficulty": "medium",
        "ci_logs": """
            ##[group]Run tests
            Error: Context access might be invalid: PYTHON_VERSION
            Warning: Unexpected input(s) 'python-versions', valid inputs are ['python-version', 'architecture', 'cache', 'cache-dependency-path', 'token']
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-          python-version: '3.11'\n+          python-versions: '3.11'",
        "ci_job_name": "Set up Python",
        "expected_fix": "Correggere il typo: python-versions → python-version (senza 's')",
        "notes": "Typo nel nome del parametro — errore subdolo"
    },

    {
        "id": "conf_013",
        "category": "config",
        "difficulty": "medium",
        "ci_logs": """
            ##[group]Run pytest
            Error: ##[error]Process completed with exit code 127.
            /bin/bash: pytest: command not found
            ##[endgroup]
            ##[error]Process completed with exit code 127.
        """,
        "git_diff": "-          pip install -r requirements.txt\n+          pip install requests flask",
        "ci_job_name": "Install dependencies",
        "expected_fix": "Ripristinare pip install -r requirements.txt che include pytest",
        "notes": "requirements.txt non installato — pytest mancante"
    },

    {
        "id": "conf_014",
        "category": "config",
        "difficulty": "medium",
        "ci_logs": """
            ##[group]Set environment variable
            Error: Secret DATABASE_URL is not set
            Warning: Skip output because no value was set for DATABASE_URL
            FAILED tests/test_db.py::test_connection - sqlalchemy.exc.ArgumentError: Could not parse rfc1738 URL from string 'None'
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-          DATABASE_URL: ${{ secrets.DATABASE_URL }}\n+          DATABASE_URL: ${{ secrets.DB_URL }}",
        "ci_job_name": "Run Tests",
        "expected_fix": "Correggere il nome del secret: DB_URL → DATABASE_URL (o viceversa, allineare con il secret configurato nel repository)",
        "notes": "Nome secret errato — richiede conoscenza dei secret configurati"
    },

    {
        "id": "conf_015",
        "category": "config",
        "difficulty": "medium",
        "ci_logs": """
            ##[group]Run on schedule
            Warning: The schedule trigger 'cron: 0 * * * *' runs too frequently.
            Error: Workflow runs triggered by a schedule that runs more than once per 5 minutes are not supported.
            The workflow will not run.
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-    - cron: '0 0 * * *'\n+    - cron: '0 * * * *'",
        "ci_job_name": "Scheduled workflow",
        "expected_fix": "Ripristinare cron: '0 0 * * *' (una volta al giorno) invece di ogni ora",
        "notes": "Cron expression troppo frequente — non supportato da GitHub"
    },

    {
        "id": "conf_016",
        "category": "config",
        "difficulty": "hard",
        "ci_logs": """
            ##[group]Run workflow matrix
            Error: Matrix 'python-version' has too many elements: 20. Maximum is 256 total jobs.
            Error: Matrix expansion resulted in 512 jobs, exceeding the maximum of 256.
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "+        python-version: ['3.8','3.9','3.10','3.11','3.12']\n+        os: [ubuntu-latest, windows-latest, macos-latest, ubuntu-20.04]\n+        experimental: [true, false]\n+        arch: [x64, x86]",
        "ci_job_name": "Run workflow matrix",
        "expected_fix": "Ridurre la matrice: rimuovere dimensioni non necessarie o usare 'include' per combinazioni specifiche invece del prodotto cartesiano completo",
        "notes": "Matrix explosion — combinazioni producono troppi job"
    },

    {
        "id": "conf_017",
        "category": "config",
        "difficulty": "hard",
        "ci_logs": """
            ##[group]Deploy to production
            Error: Workflow does not have permission to create deployments.
            Error: Resource not accessible by integration
            HttpError: 403 Forbidden
            at /repos/{owner}/{repo}/deployments
            Note: Required permissions: deployments: write, contents: read
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-permissions:\n-  deployments: write\n-  contents: read\n+permissions:\n+  contents: read",
        "ci_job_name": "Deploy to production",
        "expected_fix": "Ripristinare il permesso deployments: write nel blocco permissions del workflow",
        "notes": "Permesso rimosso dal workflow — richiede comprensione del modello di permessi GitHub Actions"
    },

    {
        "id": "conf_018",
        "category": "config",
        "difficulty": "hard",
        "ci_logs": """
            ##[group]Run tests with coverage
            Error: Error: ENOENT: no such file or directory, open '/home/runner/work/repo/repo/.coverage'
            Coverage.py warning: No data was collected. (no-data-collected)
            ERROR: No coverage data to report
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-          run: pytest tests/ --cov=src --cov-report=xml\n+          run: pytest tests/ -v",
        "ci_job_name": "Run tests with coverage",
        "expected_fix": "Ripristinare --cov=src --cov-report=xml nel comando pytest per generare i dati di coverage",
        "notes": "Flag coverage rimossi — step successivo che legge .coverage fallisce"
    },

    {
        "id": "conf_019",
        "category": "config",
        "difficulty": "hard",
        "ci_logs": """
            ##[group]Build Docker image
            Error: failed to solve: failed to read dockerfile: open Dockerfile: no such file or directory
            Error: buildx failed with: ERROR [internal] load build definition from Dockerfile
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-          context: .\n-          file: ./Dockerfile\n+          context: ./app",
        "ci_job_name": "Build Docker image",
        "expected_fix": "Ripristinare file: ./Dockerfile o specificare file: ./app/Dockerfile se il Dockerfile è stato spostato nella directory app",
        "notes": "Path Dockerfile non aggiornato dopo ristrutturazione del progetto"
    },

    {
        "id": "conf_020",
        "category": "config",
        "difficulty": "hard",
        "ci_logs": """
            ##[group]Publish to PyPI
            Error: HTTPError: 403 Forbidden from https://upload.pypi.org/legacy/
            The credential in the request is not valid for the package.
            Either the credential is invalid or the package name 'mypackage' is not associated with the trusted publisher.
            Error: OpenID Connect token exchange failed: audience mismatch
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-          audience: pypi\n+          audience: testpypi",
        "ci_job_name": "Publish to PyPI",
        "expected_fix": "Ripristinare audience: pypi per il trusted publisher — testpypi è per il registro di test",
        "notes": "Audience OIDC sbagliato — richiede conoscenza trusted publishers PyPI"
    },

    # --- Nuovi casi (conf_021 - conf_050) ---

    {
        "id": "conf_021",
        "category": "config",
        "difficulty": "easy",
        "ci_logs": """
            ##[group]Setup Node.js 21.99
            Error: Unable to find Node version '21.99' for platform linux and architecture x64.
            Available versions: 18.x, 20.x, 21.x (latest patch 21.7.1)
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-          node-version: '20'\n+          node-version: '21.99'",
        "ci_job_name": "Setup Node.js",
        "expected_fix": "Ripristinare node-version: '20' (o una versione patch valida di Node 21, es. '21.7.1')",
        "notes": "Versione Node.js inesistente specificata in actions/setup-node"
    },

    {
        "id": "conf_022",
        "category": "config",
        "difficulty": "easy",
        "ci_logs": """
            ##[group]Run pytest tests/
            FileNotFoundError: [Errno 2] No such file or directory: 'vendor/shared-lib/setup.py'
            Note: 'vendor/shared-lib' is a git submodule and appears empty
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-      - uses: actions/checkout@v4\n-        with:\n-          submodules: true\n+      - uses: actions/checkout@v4",
        "ci_job_name": "Checkout",
        "expected_fix": "Ripristinare submodules: true nello step actions/checkout per inizializzare i submodule git richiesti",
        "notes": "Submodule non inizializzato — la directory risulta vuota e i file richiesti mancano"
    },

    {
        "id": "conf_023",
        "category": "config",
        "difficulty": "easy",
        "ci_logs": """
            ##[group]Run workflow
            Error: Input required and not supplied: environment
            Workflow_dispatch triggered manually without providing the required 'environment' input
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-        environment:\n-          description: 'Target environment'\n-          required: true\n-          default: 'staging'\n+        environment:\n+          description: 'Target environment'\n+          required: true",
        "ci_job_name": "Deploy",
        "expected_fix": "Ripristinare un valore default: 'staging' per l'input 'environment', oppure fornire sempre il valore quando si avvia il workflow manualmente",
        "notes": "Input obbligatorio di workflow_dispatch senza default, dimenticato in un avvio manuale"
    },

    {
        "id": "conf_024",
        "category": "config",
        "difficulty": "easy",
        "ci_logs": """
            ##[group]Waiting for a runner to pick up this job...
            This job is waiting for a runner matching the following labels: self-hosted, gpu, linux
            No runner currently registered with these labels. Job has been queued for 45 minutes.
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-    runs-on: [self-hosted, linux]\n+    runs-on: [self-hosted, gpu, linux]",
        "ci_job_name": "Train model",
        "expected_fix": "Ripristinare runs-on: [self-hosted, linux] oppure registrare un runner con l'etichetta 'gpu' se il job richiede effettivamente una GPU",
        "notes": "Etichetta runner richiesta non corrisponde a nessun runner self-hosted registrato, il job resta bloccato in coda"
    },

    {
        "id": "conf_025",
        "category": "config",
        "difficulty": "easy",
        "ci_logs": """
            ##[group]Run pytest tests/ --durations=10
            Running full test suite (integration tests included)...
            Error: The job running on runner ubuntu-latest has exceeded the maximum execution time of 5 minutes.
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-    timeout-minutes: 20\n+    timeout-minutes: 5",
        "ci_job_name": "Run Tests",
        "expected_fix": "Ripristinare timeout-minutes: 20, poiché la suite di test di integrazione richiede più dei 5 minuti configurati",
        "notes": "Timeout del job impostato troppo basso rispetto al tempo reale necessario alla suite di test"
    },

    {
        "id": "conf_026",
        "category": "config",
        "difficulty": "easy",
        "ci_logs": """
            ##[group]Parse workflow file
            Error: .github/workflows/deploy.yml (Line: 22, Col: 12): Unexpected symbol: '='. Located at position 15 within expression: github.ref = 'refs/heads/main'
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-    if: github.ref == 'refs/heads/main'\n+    if: github.ref = 'refs/heads/main'",
        "ci_job_name": "Deploy",
        "expected_fix": "Correggere l'operatore di confronto: github.ref == 'refs/heads/main' (doppio uguale, non assegnazione)",
        "notes": "Typo sintattico nell'espressione if: singolo '=' invece di '==' non è valido nella expression syntax di GitHub Actions"
    },

    {
        "id": "conf_027",
        "category": "config",
        "difficulty": "easy",
        "ci_logs": """
            ##[group]Parse workflow file
            Error: .github/workflows/ci.yml: Job 'deploy' depends on unknown job 'buld'.
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-    needs: build\n+    needs: buld",
        "ci_job_name": "Deploy",
        "expected_fix": "Correggere il typo: needs: buld → needs: build",
        "notes": "Typo nel nome del job referenziato in 'needs', il job dipendenza non esiste"
    },

    {
        "id": "conf_028",
        "category": "config",
        "difficulty": "easy",
        "ci_logs": """
            ##[group]Set up JDK 17
            Error: No compatible distribution found for 'oracle-jdk'. Supported distributions are: temurin, zulu, adopt, liberica, microsoft, corretto, semeru, oracle
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-          distribution: 'temurin'\n+          distribution: 'oracle-jdk'",
        "ci_job_name": "Set up JDK",
        "expected_fix": "Correggere distribution: 'temurin' (o usare 'oracle', non 'oracle-jdk')",
        "notes": "Nome distribuzione JDK non valido nell'azione actions/setup-java"
    },

    {
        "id": "conf_029",
        "category": "config",
        "difficulty": "easy",
        "ci_logs": """
            ##[group]Run actions/github-script@v7
            Error: Resource not accessible by integration
            HttpError: 403 creating comment on pull request #42
            Note: default GITHUB_TOKEN permissions for this repository are read-only
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-permissions:\n-  pull-requests: write\n-  contents: read\n+permissions:\n+  contents: read",
        "ci_job_name": "Comment on PR",
        "expected_fix": "Ripristinare pull-requests: write nel blocco permissions del workflow per permettere al GITHUB_TOKEN di creare commenti",
        "notes": "Permesso di scrittura sulle PR rimosso dal workflow, il default read-only blocca l'azione"
    },

    {
        "id": "conf_030",
        "category": "config",
        "difficulty": "easy",
        "ci_logs": """
            ##[group]Run ./scripts/build.sh
            D:\\a\\_temp\\xxx.cmd: line 2: syntax error near unexpected token `('
            './scripts/build.sh' is not recognized as an internal or external command
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-      - run: ./scripts/build.sh\n-        shell: bash\n+      - run: ./scripts/build.sh",
        "ci_job_name": "Build",
        "expected_fix": "Ripristinare shell: bash nello step, poiché su runner windows-latest la shell di default non interpreta correttamente uno script bash",
        "notes": "Shell di default sul runner Windows non è bash, uno script .sh richiede shell: bash esplicito"
    },

    {
        "id": "conf_031",
        "category": "config",
        "difficulty": "easy",
        "ci_logs": """
            ##[group]Run pytest tests/
            FAILED tests/test_config.py::test_env_loaded - KeyError: 'API_SECRET'
            load_dotenv() found no .env file (it is in .gitignore and was never committed or set via CI secrets)
            1 failed, 9 passed in 0.30s
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-      - name: Run tests\n-        env:\n-          API_SECRET: ${{ secrets.API_SECRET }}\n-        run: pytest tests/\n+      - name: Run tests\n+        run: pytest tests/",
        "ci_job_name": "Run Tests",
        "expected_fix": "Ripristinare la sezione env: con API_SECRET: ${{ secrets.API_SECRET }} nello step, poiché il file .env locale (in .gitignore) non è disponibile in CI",
        "notes": "Il progetto si basa su un file .env locale non versionato; in CI le variabili vanno iniettate esplicitamente dai secrets"
    },

    {
        "id": "conf_032",
        "category": "config",
        "difficulty": "medium",
        "ci_logs": """
            ##[group]Run actions/cache@v4
            Cache restored from key: pip-3.11-e3b0c44298fc1c149afbf4c8996fb92427ae41e4
            Install dependencies step skipped (cache-hit: true)
            FAILED tests/test_new_feature.py::test_uses_new_api - AttributeError: module 'somepkg' has no attribute 'new_function'
            Note: hashFiles('requirements.text') matched no files, cache key hash is constant regardless of requirements.txt content
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-          key: pip-${{ matrix.python-version }}-${{ hashFiles('requirements.txt') }}\n+          key: pip-${{ matrix.python-version }}-${{ hashFiles('requirements.text') }}",
        "ci_job_name": "Install dependencies",
        "expected_fix": "Correggere il typo nel pattern hashFiles: 'requirements.text' → 'requirements.txt', così la cache key riflette correttamente il contenuto del file",
        "notes": "Typo nell'estensione del file passato a hashFiles rende la cache key costante, la cache non si invalida mai quando le dipendenze cambiano"
    },

    {
        "id": "conf_033",
        "category": "config",
        "difficulty": "medium",
        "ci_logs": """
            ##[group]Run actions/download-artifact@v4
            Error: Multiple artifacts named 'test-results' were found. Since v4, download-artifact no longer merges same-named artifacts from different jobs automatically.
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-      - uses: actions/download-artifact@v3\n+      - uses: actions/download-artifact@v4",
        "ci_job_name": "Aggregate test results",
        "expected_fix": "Aggiornare gli step upload-artifact per usare nomi univoci per matrice (es. name: test-results-${{ matrix.os }}) e usare merge-multiple: true in download-artifact@v4",
        "notes": "Breaking change tra v3 e v4 di download-artifact: il merge automatico di artifact omonimi non è più il comportamento di default"
    },

    {
        "id": "conf_034",
        "category": "config",
        "difficulty": "medium",
        "ci_logs": """
            ##[group]Run deploy job
            The run was canceled because a newer run with the same concurrency group 'deploy' was queued.
            Note: concurrency group does not include the branch name, so deploys from different branches cancel each other
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-concurrency:\n-  group: deploy-${{ github.ref }}\n-  cancel-in-progress: false\n+concurrency:\n+  group: deploy\n+  cancel-in-progress: true",
        "ci_job_name": "Deploy",
        "expected_fix": "Ripristinare group: deploy-${{ github.ref }} e cancel-in-progress: false, per evitare che deploy su branch diversi si cancellino a vicenda",
        "notes": "Gruppo di concorrenza non scoped per branch causa la cancellazione involontaria di deploy in corso su branch diversi"
    },

    {
        "id": "conf_035",
        "category": "config",
        "difficulty": "medium",
        "ci_logs": """
            ##[group]Run reusable workflow ./.github/workflows/publish.yml
            Error: Secret PYPI_API_TOKEN not found in the calling context
            FAILED: twine upload returned non-zero exit status: 403 Forbidden
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-  publish:\n-    uses: ./.github/workflows/publish.yml\n-    secrets: inherit\n+  publish:\n+    uses: ./.github/workflows/publish.yml",
        "ci_job_name": "Publish",
        "expected_fix": "Ripristinare secrets: inherit nella chiamata al reusable workflow per propagare i secret necessari (es. PYPI_API_TOKEN)",
        "notes": "Reusable workflow richiamato senza secrets: inherit non riceve i secret del workflow chiamante"
    },

    {
        "id": "conf_036",
        "category": "config",
        "difficulty": "medium",
        "ci_logs": """
            ##[group]Checking required status checks
            The required status check 'run-tests' has not been reported by any workflow run for this commit.
            Note: the CI job was recently renamed from 'run-tests' to 'test' — branch protection rules still expect the old name
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-  run-tests:\n-    runs-on: ubuntu-latest\n+  test:\n+    runs-on: ubuntu-latest",
        "ci_job_name": "test",
        "expected_fix": "Aggiornare le regole di branch protection per richiedere il nuovo nome del job 'test' invece di 'run-tests' (o rinominare il job mantenendo 'run-tests')",
        "notes": "Rinominare un job senza aggiornare le required status checks nella branch protection blocca il merge delle PR indefinitamente"
    },

    {
        "id": "conf_037",
        "category": "config",
        "difficulty": "medium",
        "ci_logs": """
            ##[group]Waiting for approval
            This job is waiting for required reviewers to approve the deployment to environment 'production'.
            Note: environment protection rule was recently added and no reviewers have been notified/configured for automated nightly deploys
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-    environment: production\n+    environment:\n+      name: production\n+      # required reviewers aggiunti via GitHub UI, non riflessi nel file workflow",
        "ci_job_name": "Deploy to production",
        "expected_fix": "Usare un ambiente separato senza reviewer obbligatori per i deploy automatici notturni (es. 'production-auto'), oppure rimuovere la regola di protezione per i job schedulati",
        "notes": "Regola di protezione ambiente con reviewer obbligatori blocca deploy automatici che non hanno un umano pronto ad approvare"
    },

    {
        "id": "conf_038",
        "category": "config",
        "difficulty": "medium",
        "ci_logs": """
            ##[group]Run test matrix
            Job 'test (3.9)' failed. Canceling all in-progress matrix jobs due to fail-fast: true.
            Job 'test (3.11)' was cancelled before completion — its failure/success status is unknown
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-    strategy:\n-      fail-fast: false\n+    strategy:\n+      fail-fast: true",
        "ci_job_name": "test (3.11)",
        "expected_fix": "Ripristinare fail-fast: false nella strategy della matrice, per permettere a tutte le combinazioni di completare indipendentemente dal fallimento di una singola versione",
        "notes": "fail-fast: true cancella prematuramente le altre combinazioni della matrice, nascondendo informazioni utili sul reale stato delle altre versioni"
    },

    {
        "id": "conf_039",
        "category": "config",
        "difficulty": "medium",
        "ci_logs": """
            ##[group]Run ./.github/actions/setup-env
            Error: Input 'skip-cache' received boolean 'false', but composite actions only support string inputs
            Warning: 'false' (string) was used instead, condition 'if: inputs.skip-cache' always evaluates true
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-          skip-cache: 'false'\n+          skip-cache: false",
        "ci_job_name": "Setup environment",
        "expected_fix": "Passare il valore come stringa: skip-cache: 'false', poiché gli input delle composite action sono sempre stringhe e un booleano non quotato causa una valutazione errata nella condizione",
        "notes": "Gli input di una composite action sono sempre stringhe; passare un booleano non quotato altera la logica condizionale dell'azione"
    },

    {
        "id": "conf_040",
        "category": "config",
        "difficulty": "medium",
        "ci_logs": """
            ##[group]Run some-org/some-action@v1
            Error: some-org/some-action@v1 uses Node 12 which is deprecated and no longer supported by GitHub Actions runners
            Warning: this may be due to the v1 tag being repointed to a newer, incompatible release
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-      - uses: some-org/some-action@8f1a2b3\n+      - uses: some-org/some-action@v1",
        "ci_job_name": "Run some-org/some-action",
        "expected_fix": "Fissare l'azione a uno SHA di commit specifico e verificato (es. @8f1a2b3) invece di un tag mobile come @v1, per evitare che un repointing del tag introduca comportamenti inattesi",
        "notes": "Un tag mobile (@v1) può essere ripuntato dal maintainer a una versione diversa e incompatibile senza preavviso"
    },

    {
        "id": "conf_041",
        "category": "config",
        "difficulty": "medium",
        "ci_logs": """
            ##[group]Run pytest tests/
            FAILED tests/test_model_loading.py::test_load_weights - pickle.UnpicklingError: invalid load key, 'v'.
            Note: model.pkl is tracked via Git LFS and was checked out as a pointer file (133 bytes) instead of the real binary content
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-      - uses: actions/checkout@v4\n-        with:\n-          lfs: true\n+      - uses: actions/checkout@v4",
        "ci_job_name": "Checkout",
        "expected_fix": "Ripristinare lfs: true nello step actions/checkout per scaricare il contenuto reale dei file tracciati da Git LFS",
        "notes": "Senza lfs: true, i file tracciati da Git LFS vengono estratti come pointer testuali invece del contenuto binario reale"
    },

    {
        "id": "conf_042",
        "category": "config",
        "difficulty": "hard",
        "ci_logs": """
            ##[group]Run nested reusable workflow ./.github/workflows/deploy-inner.yml
            Error: Secret AWS_ACCESS_KEY_ID not found in the calling context
            Note: top-level workflow passes secrets: inherit to 'deploy-outer.yml', but 'deploy-outer.yml' calls 'deploy-inner.yml' without re-declaring secrets: inherit
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-  deploy-inner-call:\n-    uses: ./.github/workflows/deploy-inner.yml\n-    secrets: inherit\n+  deploy-inner-call:\n+    uses: ./.github/workflows/deploy-inner.yml",
        "ci_job_name": "deploy-inner-call",
        "expected_fix": "Aggiungere secrets: inherit anche nella chiamata annidata a deploy-inner.yml: l'ereditarietà dei secret non è transitiva attraverso più livelli di reusable workflow",
        "notes": "In una catena di reusable workflow a più livelli, secrets: inherit deve essere dichiarato ad ogni livello di chiamata, non solo al primo"
    },

    {
        "id": "conf_043",
        "category": "config",
        "difficulty": "hard",
        "ci_logs": """
            ##[group]Run test matrix
            Job 'test (ubuntu-latest, 3.11)' was cancelled
            Note: concurrency group 'ci-${{ github.workflow }}' is shared across all matrix jobs instead of being scoped per matrix combination, causing jobs to cancel each other intermittently under load
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-concurrency:\n-  group: ci-${{ github.workflow }}-${{ matrix.os }}-${{ matrix.python-version }}\n+concurrency:\n+  group: ci-${{ github.workflow }}",
        "ci_job_name": "test (ubuntu-latest, 3.11)",
        "expected_fix": "Ripristinare il gruppo di concorrenza scoped per combinazione di matrice (includendo matrix.os e matrix.python-version), non solo per workflow",
        "notes": "Gruppo di concorrenza troppo generico applicato all'interno di un job di matrice causa cancellazioni intermittenti tra combinazioni indipendenti"
    },

    {
        "id": "conf_044",
        "category": "config",
        "difficulty": "hard",
        "ci_logs": """
            ##[group]Run actions/cache@v4
            Cache restored from key: deps-a1b2c3d4 (created on branch 'experimental/broken-upgrade')
            FAILED tests/test_api.py::test_new_endpoint - ImportError: cannot import name 'new_client' from 'sdk'
            Note: cache key does not include branch or ref, main branch picked up a cache written by a feature branch with an unreleased dependency
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-          key: deps-${{ github.ref_name }}-${{ hashFiles('requirements.txt') }}\n+          key: deps-${{ hashFiles('requirements.txt') }}",
        "ci_job_name": "Install dependencies",
        "expected_fix": "Includere github.ref_name (o comunque uno scope di branch) nella cache key, per evitare che branch diversi condividano/inquinino a vicenda la stessa cache",
        "notes": "Cache condivisa senza scoping per branch permette a un branch sperimentale di 'avvelenare' la cache usata dal branch principale"
    },

    {
        "id": "conf_045",
        "category": "config",
        "difficulty": "hard",
        "ci_logs": """
            ##[group]Configure AWS Credentials
            Error: Not authorized to perform sts:AssumeRoleWithWebIdentity
            AdditionalDetails: the role's trust policy condition on token.actions.githubusercontent.com:sub does not match repo:myorg/myrepo:ref:refs/heads/main
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-  deploy:\n-    if: github.ref == 'refs/heads/main'\n+  deploy:\n+    if: startsWith(github.ref, 'refs/heads/release/')",
        "ci_job_name": "Configure AWS Credentials",
        "expected_fix": "Aggiornare la trust policy IAM del ruolo AWS per includere la condition sub che corrisponde a repo:myorg/myrepo:ref:refs/heads/release/*, oppure ripristinare il trigger su refs/heads/main coerente con la policy esistente",
        "notes": "Il trigger del workflow è stato cambiato a un branch pattern diverso senza aggiornare la trust policy OIDC lato AWS, che valida esplicitamente il claim 'sub'"
    },

    {
        "id": "conf_046",
        "category": "config",
        "difficulty": "hard",
        "ci_logs": """
            ##[group]Run pytest tests/
            FAILED tests/test_lock_manager.py::test_acquire_lock - FileExistsError: [Errno 17] File exists: '/tmp/app.lock'
            Note: previous job on this same self-hosted (non-ephemeral) runner crashed and left a stale lock file; ephemeral GitHub-hosted runners would not exhibit this
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-      - name: Clean workspace\n-        run: rm -f /tmp/app.lock\n+      # step di pulizia rimosso",
        "ci_job_name": "Run Tests",
        "expected_fix": "Ripristinare lo step di pulizia che rimuove /tmp/app.lock all'inizio del job, necessario perché il runner self-hosted non è effimero e riusa lo stesso filesystem tra le esecuzioni",
        "notes": "Runner self-hosted persistente conserva stato tra esecuzioni; senza pulizia esplicita un crash precedente lascia file residui che rompono l'esecuzione successiva"
    },

    {
        "id": "conf_047",
        "category": "config",
        "difficulty": "hard",
        "ci_logs": """
            ##[group]Merge pull request #128
            Error: Required status check 'ci/test' is expected but was not found. 2 checks reported: 'test-suite', 'lint'.
            Note: job renamed from 'test' (reported as 'ci/test' via a legacy context) to 'test-suite' in the same PR that also updated the repository ruleset, but the ruleset update did not take effect for in-flight PRs
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-  test:\n-    name: ci/test\n+  test-suite:\n+    name: test-suite",
        "ci_job_name": "test-suite",
        "expected_fix": "Aggiornare il repository ruleset per richiedere 'test-suite' al posto di 'ci/test', oppure mantenere temporaneamente entrambi i nomi finché il ruleset non è allineato, per sbloccare le PR già aperte",
        "notes": "Rinominare contemporaneamente un job e il ruleset di branch protection può disallinearsi per le PR già aperte, bloccando il merge finché non si riallineano manualmente"
    },

    {
        "id": "conf_048",
        "category": "config",
        "difficulty": "hard",
        "ci_logs": """
            ##[group]Run tests on PR
            Error: secrets.DEPLOY_TOKEN is empty
            Warning: this workflow is triggered by 'pull_request_target' (has access to secrets) but checks out the untrusted PR head via actions/checkout with ref: ${{ github.event.pull_request.head.sha }}, so GitHub redacts secrets from the environment as a security measure
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-on: pull_request\n+on: pull_request_target\n       jobs:\n         test:\n           steps:\n-            - uses: actions/checkout@v4\n+            - uses: actions/checkout@v4\n+              with:\n+                ref: ${{ github.event.pull_request.head.sha }}",
        "ci_job_name": "Run tests on PR",
        "expected_fix": "Non eseguire il checkout del codice della PR (head.sha, non fidato) in un workflow pull_request_target con accesso ai secret; separare in due job: uno con pull_request_target solo per operazioni fidate coi secret, uno con pull_request (senza secret) per eseguire il codice della PR",
        "notes": "Caso hard di sicurezza: pull_request_target concede accesso ai secret, eseguire codice non fidato della PR in quel contesto è un rischio di secret-exfiltration, non solo un errore di configurazione da correggere alla leggera"
    },

    {
        "id": "conf_049",
        "category": "config",
        "difficulty": "hard",
        "ci_logs": """
            ##[group]Run actions/cache@v4
            Warning: Cache size of 11.2 GB exceeds the 10 GB repository limit. GitHub has evicted the oldest caches to make space.
            Cache not found for key: build-ubuntu-latest-3.11-4821093 (evicted)
            Run pip install -r requirements.txt (cold install)
            Error: No space left on device
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-          key: build-${{ matrix.os }}-${{ matrix.python-version }}\n+          key: build-${{ matrix.os }}-${{ matrix.python-version }}-${{ github.run_id }}",
        "ci_job_name": "Install dependencies",
        "expected_fix": "Rimuovere github.run_id dalla cache key (crea una cache nuova e mai riusata ad ogni run, saturando il limite di 10GB) e ripulire periodicamente le cache obsolete",
        "notes": "Cache key che include un valore univoco per ogni run (run_id) impedisce il riutilizzo e accumula rapidamente cache ridondanti fino a superare il limite del repository"
    },

    {
        "id": "conf_050",
        "category": "config",
        "difficulty": "hard",
        "ci_logs": """
            ##[group]Run job C
            Error: Job 'C' is skipped because its dependency 'B' did not succeed (B was skipped due to its own if: condition).
            Note: 'needs: [A, B]' without always(), a skipped upstream job counts as not-succeeded and blocks downstream jobs even when the skip was expected
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-  C:\n-    needs: [A, B]\n-    if: always() && needs.A.result == 'success'\n+  C:\n+    needs: [A, B]",
        "ci_job_name": "C",
        "expected_fix": "Ripristinare if: always() && needs.A.result == 'success' nel job C, per non farlo dipendere implicitamente dal successo di B quando B è legittimamente skippato dalla sua condizione",
        "notes": "Senza always(), un job upstream skippato per una condizione attesa blocca comunque i job downstream che dipendono da esso tramite 'needs'"
    },

]


# ══════════════════════════════════════════════════════════════
# FUNZIONI DI UTILITY
# ══════════════════════════════════════════════════════════════

def get_by_category(category: str) -> list:
    """Filtra il dataset per categoria."""
    return [e for e in DATASET if e["category"] == category]


def get_by_difficulty(difficulty: str) -> list:
    """Filtra il dataset per difficoltà."""
    return [e for e in DATASET if e["difficulty"] == difficulty]


def get_stats() -> dict:
    """Statistiche del dataset."""
    categories = {}
    difficulties = {}
    for e in DATASET:
        categories[e["category"]] = categories.get(e["category"], 0) + 1
        difficulties[e["difficulty"]] = difficulties.get(e["difficulty"], 0) + 1
    return {
        "total": len(DATASET),
        "by_category": categories,
        "by_difficulty": difficulties
    }


if __name__ == "__main__":
    stats = get_stats()
    print(f"Dataset: {stats['total']} errori totali")
    print(f"Per categoria: {stats['by_category']}")
    print(f"Per difficoltà: {stats['by_difficulty']}")

    # Verifica IDs unici
    ids = [e["id"] for e in DATASET]
    assert len(ids) == len(set(ids)), "IDs duplicati trovati!"
    print("✅ Tutti gli ID sono unici")