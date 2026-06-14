"""
Dataset sintetico — 60 errori CI per la valutazione sperimentale
Tesi LM-32: Self-Healing CI/CD Pipeline

Struttura: 20 errori per categoria (dependency, test, config)
Difficoltà: easy (8), medium (7), hard (5) per categoria

Uso:
    from experiments.dataset import DATASET, get_by_category, get_by_difficulty
"""

DATASET = [

    # ══════════════════════════════════════════════════════════
    # CATEGORIA: DEPENDENCY (20 errori)
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

    # ══════════════════════════════════════════════════════════
    # CATEGORIA: TEST (20 errori)
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

    # ══════════════════════════════════════════════════════════
    # CATEGORIA: CONFIG (20 errori)
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