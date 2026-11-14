"""
Synthetic dataset — 150 CI errors for the experimental evaluation
Self-Healing CI/CD Pipeline

Structure: 50 errors per category (dependency, test, config)
Difficulty per category: easy ~19, medium ~17, hard ~14
(dep_001-020, test_001-020, conf_001-020 are the original set of 60 cases;
 dep_021-050, test_021-050, conf_021-050 are the extension to 150 cases)

Usage:
    from experiments.dataset import DATASET, get_by_category, get_by_difficulty
"""

DATASET = [

    # ══════════════════════════════════════════════════════════
    # CATEGORY: DEPENDENCY (50 errors)
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
        "expected_fix": "Restore numpy to a valid version, e.g. numpy==1.26.4",
        "notes": "Base case, clearly non-existent version"
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
        "expected_fix": "Restore pandas to a valid version, e.g. pandas==2.0.3",
        "notes": "Same structure as dep_001 but a different package"
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
        "expected_fix": "Use scikit-learn==1.3.0 or higher",
        "notes": "Too-low version that was never released"
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
        "expected_fix": "Use requests==2.31.0",
        "notes": "Typical copy/paste error with the wrong version"
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
        "expected_fix": "Use flask==3.0.3",
        "notes": "Future version not yet released"
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
        "expected_fix": "Use tensorflow==2.13.0 or higher",
        "notes": "Package version incompatible with Python 3.11"
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
        "expected_fix": "Use scipy==1.11.3",
        "notes": "Non-existent version of a scientific library"
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
        "expected_fix": "Use matplotlib==3.8.0",
        "notes": "Clearly wrong major version"
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
        "expected_fix": "Upgrade scipy to >=1.10.0 or use pandas==1.5.3, compatible with scipy 1.9.0",
        "notes": "Real conflict between versions, requires reasoning about the dependencies"
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
        "expected_fix": "Use torch==2.1.0 or higher where the wheel is correct, or specify --index-url for PyTorch",
        "notes": "Corrupted wheel for a specific version — requires an alternative strategy"
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
        "expected_fix": "Remove my-internal-lib from requirements.txt or add --extra-index-url in the workflow",
        "notes": "Internal package not on PyPI — requires understanding the context"
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
        "expected_fix": "Upgrade typing-extensions>=4.6.0 in requirements.txt",
        "notes": "Transitive dependency conflict — requires identifying the missing package"
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
        "expected_fix": "Specify cryptography==41.0.0 with --only-binary=:all: or use a version with a prebuilt wheel",
        "notes": "Build from source fails — requires a binary wheel strategy"
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
        "expected_fix": "Update python-version to 3.10 in ci.yml or use newpackage<1.0.0, compatible with Python 3.9",
        "notes": "Python version conflict — the fix can be in ci.yml or requirements.txt"
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
        "expected_fix": "Remove broken-lib from requirements.txt — the package does not exist on PyPI",
        "notes": "Completely made-up package — no version available"
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
        "expected_fix": "Align the versions: langchain>=0.2.0, langchain-openai>=0.1.0, langchain-community>=0.2.0, all compatible with pydantic>=2.0",
        "notes": "Complex multi-package conflict — the LangChain ecosystem has historically had this problem"
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
        "expected_fix": "Upgrade pandas>=2.0.0, compatible with numpy 2.0, or pin numpy<1.25",
        "notes": "numpy 2.0 breaking change — breaks many packages that have not yet updated their constraints"
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
        "expected_fix": "Upgrade protobuf>=4.21.6 and verify compatibility with tensorflow and google-cloud-storage",
        "notes": "Classic protobuf conflict in the Google ecosystem — requires specific knowledge"
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
        "expected_fix": "Upgrade together: spacy==3.7.0 thinc>=8.2.2 spacy-legacy>=3.0.11 cymem>=2.0.2",
        "notes": "Major upgrade with a dependency cascade — the spacy ecosystem has strict dependencies"
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
        "expected_fix": "Upgrade kombu>=5.3.0 to satisfy the constraint of celery 5.3.0",
        "notes": "Partial upgrade that breaks constraints — kombu not upgraded together with celery"
    },

    # --- New cases (dep_021 - dep_050) ---

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
        "expected_fix": "Upgrade to urllib3==2.0.4 (or another non-yanked version), since 2.0.3 was withdrawn by its authors",
        "notes": "Yanked version on PyPI — different from a non-existent version, requires recognizing the yank warning"
    },

    {
        # NOTE (rewritten): original case based on npm/package-lock.json,
        # an ecosystem not present in this repo (pip + requirements.txt).
        # Rewritten as a typo in the package name — see CHANGELOG_DATASET.md.
        "id": "dep_022",
        "category": "dependency",
        "difficulty": "easy",
        "ci_logs": """
            ##[group]Run pip install -r requirements.txt
            Collecting flaks==3.0.3
            ERROR: Could not find a version that satisfies the requirement flaks==3.0.3 (from versions: none)
            ERROR: No matching distribution found for flaks==3.0.3
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-flask==3.0.3\n+flaks==3.0.3",
        "ci_job_name": "Install dependencies",
        "expected_fix": "Fix the typo in the package name: flaks==3.0.3 -> flask==3.0.3",
        "notes": "Typo in the package name (not in the version) — pip finds no distribution because 'flaks' does not exist on PyPI"
    },

    {
        # NOTE (rewritten): original case based on package.json "engines"/Node,
        # an ecosystem not present in this repo. Rewritten as an invalid version
        # operator in requirements.txt — see CHANGELOG_DATASET.md.
        "id": "dep_023",
        "category": "dependency",
        "difficulty": "easy",
        "ci_logs": """
            ##[group]Run pip install -r requirements.txt
            ERROR: Invalid requirement: 'pyyaml=6.0.1': Expected end or semicolon (after name and no valid version specifier)
                pyyaml=6.0.1
                       ~^
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-pyyaml==6.0.1\n+pyyaml=6.0.1",
        "ci_job_name": "Install dependencies",
        "expected_fix": "Fix the version operator from a single '=' to '==': pyyaml==6.0.1",
        "notes": "Syntax error in requirements.txt: pip requires '==' for exact pinning (PEP 508), a single '=' is not a valid version operator"
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
        "expected_fix": "Use psycopg2-binary==2.9.9 instead of psycopg2, or install libpq-dev via apt-get before the build",
        "notes": "psycopg2 (non-binary) requires PostgreSQL development headers that are missing on the runner"
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
        "expected_fix": "Remove the duplicate line click==8.0.0, keeping only click==8.1.7",
        "notes": "Same package pinned twice with different versions in the same file"
    },

    {
        # NOTE (rewritten on 2026-07-30): original case based on Poetry
        # ("pyproject.toml"/"poetry.lock", an ecosystem not present in this
        # repo, which uses pip + requirements.txt). Rewritten as the pip-tools
        # equivalent keeping the same conceptual lesson (lockfile not
        # regenerated after a change to the dependency source file).
        # See experiments/CHANGELOG_DATASET.md.
        "id": "dep_026",
        "category": "dependency",
        "difficulty": "easy",
        "ci_logs": """
            ##[group]Run pip install -r requirements.txt
            Collecting httpx (from -r requirements.in (line 4))
            ERROR: Could not find a version that satisfies the requirement httpx (from -r requirements.in (line 4))
            Note: requirements.in was updated but requirements.txt (generated with pip-compile) was not regenerated — httpx is not present in the file actually installed in CI
            ##[endgroup]
            ##[group]Run pytest tests/
            ModuleNotFoundError: No module named 'httpx'
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "+httpx==0.27.0",
        "ci_job_name": "Install dependencies",
        "expected_fix": "Add httpx==0.27.0 to requirements.txt (regenerating it with pip-compile from requirements.in), since the dependency was added to the source file but never propagated to the file actually installed in CI",
        "notes": "Drift between requirements.in (source) and requirements.txt (compiled lockfile) — pip-tools equivalent of the case of a poetry.lock not regenerated after a change to pyproject.toml"
    },

    {
        # NOTE (rewritten): original case based on an authenticated private npm
        # registry, an ecosystem not present in this repo. Rewritten as a
        # JSON-style line mistakenly copied into requirements.txt —
        # verified with a real "pip install --dry-run" — see
        # CHANGELOG_DATASET.md.
        "id": "dep_027",
        "category": "dependency",
        "difficulty": "easy",
        "ci_logs": """
            ##[group]Run pip install -r requirements.txt
            ERROR: Invalid requirement: '"requests": "2.31.0"': Expected package name at the start of dependency specifier
                "requests": "2.31.0"
                ^
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-requests==2.31.0\n+\"requests\": \"2.31.0\"",
        "ci_job_name": "Install dependencies",
        "expected_fix": "Replace the JSON-style line with the correct requirements.txt syntax: requests==2.31.0",
        "notes": "Line mistakenly copied from a JSON-style file (e.g. package.json) — not valid in a requirements.txt (PEP 508 format, not JSON)"
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
        "expected_fix": "Restore fastapi[all]==0.104.1 to include the extra dependencies such as uvicorn, or add uvicorn explicitly to requirements.txt",
        "notes": "'all' extra removed from the pin, sub-dependencies needed at runtime are not installed"
    },

    {
        # NOTE (rewritten): original case required changing "runs-on" in
        # ci.yml (out of scope for dependency_agent, which only writes
        # requirements.txt). Rewritten as a Windows-only package installed
        # without an environment marker on a Linux runner — see CHANGELOG_DATASET.md.
        "id": "dep_029",
        "category": "dependency",
        "difficulty": "easy",
        "ci_logs": """
            ##[group]Run pip install -r requirements.txt
            Collecting pywin32==306
            ERROR: Could not find a version that satisfies the requirement pywin32==306 (from versions: none)
            ERROR: No matching distribution found for pywin32==306
            Note: pywin32 publishes distributions only for Windows (win32/win_amd64) — none available for Linux
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "+pywin32==306",
        "ci_job_name": "Install dependencies",
        "expected_fix": "Remove pywin32==306 from requirements.txt (or add it with the environment marker ; sys_platform == 'win32'), since the CI runner is Linux and pywin32 does not publish distributions for this platform",
        "notes": "Windows-only dependency added without an environment marker, installed unconditionally even on the Linux ubuntu-latest runner"
    },

    {
        # NOTE (rewritten on 2026-07-30): original case based on
        # "npm audit"/package.json (a Node ecosystem not present in this
        # repo). Rewritten as the pip-audit equivalent keeping the same
        # conceptual lesson (vulnerable pin flagged by a security audit,
        # the chosen upgrade points to a non-existent version).
        # See experiments/CHANGELOG_DATASET.md.
        "id": "dep_030",
        "category": "dependency",
        "difficulty": "easy",
        "ci_logs": """
            ##[group]Run pip install -r requirements.txt
            ERROR: Could not find a version that satisfies the requirement pillow==10.99.0
            ERROR: No matching distribution found for pillow==10.99.0
            Note: pillow==8.3.2 (previous pin) had been flagged by pip-audit for CVE-2021-34552; the chosen upgrade version does not exist on PyPI
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-pillow==8.3.2\n+pillow==10.99.0",
        "ci_job_name": "Install dependencies",
        "expected_fix": "Upgrade pillow to an actually published version free of the known vulnerability, e.g. pillow==10.3.0, since pillow==10.99.0 does not exist on PyPI",
        "notes": "pip-audit equivalent of the npm audit case: the vulnerable pin must be replaced, but the indicated upgrade version points to a non-existent release"
    },

    {
        # NOTE (rewritten): original case based on yarn.lock, an ecosystem
        # not present in this repo. Rewritten as an orphan semicolon
        # left over after removing an environment marker — see
        # CHANGELOG_DATASET.md.
        "id": "dep_031",
        "category": "dependency",
        "difficulty": "easy",
        "ci_logs": """
            ##[group]Run pip install -r requirements.txt
            pip._vendor.packaging.markers.InvalidMarker: Expected marker operator, one of <=, <, !=, ==, >=, >, ~=, ===, in, not in
                python_version
                              ^
            ERROR: Invalid requirement: 'requests==2.31.0; python_version'
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-requests==2.31.0; python_version >= '3.8'\n+requests==2.31.0; python_version",
        "ci_job_name": "Install dependencies",
        "expected_fix": "Restore the full environment marker expression: requests==2.31.0; python_version >= '3.8' (or remove the marker entirely: requests==2.31.0)",
        "notes": "The environment marker was truncated during an edit, leaving only 'python_version' with no operator or value — invalid according to PEP 508 (verified with a real pip install --dry-run, which produces exactly this InvalidMarker)"
    },

    {
        # NOTE (rewritten): original case based on an npm peer dependency
        # conflict (ERESOLVE), an ecosystem not present in this repo.
        # Rewritten as a real pip equivalent — verified with a
        # real "pip install --dry-run" (sphinx 7.2.6 explicitly declares
        # docutils<0.21 in its own metadata) — see
        # CHANGELOG_DATASET.md.
        "id": "dep_032",
        "category": "dependency",
        "difficulty": "medium",
        "ci_logs": """
            ##[group]Run pip install -r requirements.txt
            ERROR: Cannot install -r requirements.txt (line 3) and docutils==0.22 because these package versions have conflicting dependencies.
            The conflict is caused by:
                The user requested docutils==0.22
                sphinx 7.2.6 depends on docutils<0.21 and >=0.18.1
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "+sphinx==7.2.6\n-docutils==0.20.1\n+docutils==0.22",
        "ci_job_name": "Install dependencies",
        "expected_fix": "Align docutils to a version compatible with sphinx==7.2.6 (e.g. docutils==0.20.1, which satisfies >=0.18.1 and <0.21)",
        "notes": "sphinx 7.2.6 explicitly declares in its own metadata an upper bound on docutils (<0.21) — Python equivalent of the npm ERESOLVE peer-dependency conflict"
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
        "expected_fix": "Use torch==2.1.0 (standard CPU build from PyPI) or add --index-url https://download.pytorch.org/whl/cu121 if the CUDA build is really needed",
        "notes": "A specific CUDA build requires a dedicated index url, not available on the standard PyPI"
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
        "expected_fix": "Regenerate requirements.txt with pip-compile to also update the hashes associated with click==8.1.7",
        "notes": "Package version updated manually without regenerating the hashes required by --require-hashes"
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
        "expected_fix": "Upgrade python to >=3.9 in environment.yml, or use scikit-learn=1.2, compatible with python=3.8",
        "notes": "The conda solver cannot satisfy python=3.8 and scikit-learn=1.4 simultaneously"
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
        "expected_fix": "Configure --index-url on the internal private index with priority over the public PyPI, to prevent pip from resolving the name from an untrusted public package (dependency confusion)",
        "notes": "Dependency confusion risk: a public package with the same name as an internal one is installed by mistake"
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
        "expected_fix": "Upgrade setuptools in the CI environment (pip install --upgrade setuptools) before installing the packages that require setuptools>=68 as build backend",
        "notes": "The build backend required in pyproject.toml is not satisfied by the setuptools version preinstalled on the runner"
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
        "expected_fix": "Use git+https://x-access-token:${{ secrets.GH_PAT }}@github.com/myorg/internal-tool.git@v1.2.0 to authenticate to the private repository",
        "notes": "Dependency on a private Git repository without credentials in the URL"
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
        "expected_fix": "Align the black version in requirements-dev.txt to 23.9.1 to be consistent with requirements.txt (or update both to the same version)",
        "notes": "Two requirements files pin the same package to different versions"
    },

    {
        # NOTE (rewritten): original case required modifying ci.yml
        # (cache of the actions/setup-node step), out of scope for
        # dependency_agent. Rewritten as a self-contradictory version
        # range in requirements.txt — see CHANGELOG_DATASET.md.
        "id": "dep_040",
        "category": "dependency",
        "difficulty": "medium",
        "ci_logs": """
            ##[group]Run pip install -r requirements.txt
            Collecting click<8.0,>=9.0
            ERROR: Could not find a version that satisfies the requirement click<8.0,>=9.0 (from versions: 6.6, 6.7, 7.0, 7.1.2, 8.0.0, 8.0.1, 8.0.2, 8.0.3, 8.0.4, 8.1.0, 8.1.3, 8.1.7)
            ERROR: No matching distribution found for click<8.0,>=9.0
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-click==8.1.7\n+click<8.0,>=9.0",
        "ci_job_name": "Install dependencies",
        "expected_fix": "Fix the contradictory version range (>=9.0 and <8.0 cannot both be true): use click==8.1.7",
        "notes": "Self-contradictory version range (no version can satisfy both >=9.0 and <8.0) — likely a typo in the order of the operators"
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
        "expected_fix": "Use tokenizers==0.15.0 with an available prebuilt wheel (check Python compatibility) or install the Rust toolchain in the workflow before pip install",
        "notes": "A version without a prebuilt wheel for the platform requires a source build with Rust, which is not available on the runner"
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
        "expected_fix": "Upgrade package-b to a version compatible with shared-lib>=2.0 (e.g. package-b>=2.0.0), since no shared-lib range satisfies both current constraints",
        "notes": "Diamond dependency: two direct packages require incompatible ranges of the same transitive dependency"
    },

    {
        # NOTE (rewritten): original case required the npm
        # "overrides" mechanism (package.json), not present in this ecosystem.
        # Rewritten as a real pandas/numpy conflict that requires
        # upgrading the "indirect" dependency (pandas), not only the one
        # bumped directly (numpy) — see CHANGELOG_DATASET.md.
        "id": "dep_043",
        "category": "dependency",
        "difficulty": "hard",
        "ci_logs": """
            ##[group]Run pip install -r requirements.txt
            Collecting pandas==2.0.3
            Collecting numpy==2.0.0
            ERROR: Cannot install numpy==2.0.0 and pandas==2.0.3 because these package versions have conflicting dependencies.
            The conflict is caused by:
                pandas 2.0.3 depends on numpy>=1.20.3 and <2
                The user requested numpy==2.0.0
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "+pandas==2.0.3\n+numpy==2.0.0",
        "ci_job_name": "Install dependencies",
        "expected_fix": "Upgrade pandas to a version with NumPy 2.0 support (e.g. pandas==2.2.2 or higher), or pin numpy<2.0 (e.g. numpy==1.26.4) to stay compatible with pandas==2.0.3 — simply pinning numpy==2.0.0 is not enough, because pandas 2.0.3 explicitly declares numpy<2 among its dependencies",
        "notes": "An isolated bump of numpy to a major version (2.0) breaks the constraint declared by pandas 2.0.3, which predates NumPy 2.0 support — requires cascading the upgrade to pandas as well, not just removing the numpy pin. Python equivalent of the 'Dependabot bump requires a transitive override' case"
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
        "expected_fix": "Restore runs-on: ubuntu-22.04 (or higher), since the wheel installed for somepkg is compiled against a glibc version not available on ubuntu-18.04",
        "notes": "Runtime (not install-time) ABI incompatibility between the prebuilt wheel and the libc of the older runner"
    },

    {
        # NOTE (rewritten): original case based on an npm monorepo
        # workspace, an ecosystem not present in this repo. Rewritten as a
        # reference to a non-existent constraints file (-c), a real but
        # little-known pip mechanism — see CHANGELOG_DATASET.md.
        "id": "dep_045",
        "category": "dependency",
        "difficulty": "hard",
        "ci_logs": """
            ##[group]Run pip install -r requirements.txt
            ERROR: Could not open requirements file: [Errno 2] No such file or directory: 'constraints.txt'
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "+-c constraints.txt",
        "ci_job_name": "Install dependencies",
        "expected_fix": "Remove the '-c constraints.txt' line from requirements.txt, since the referenced constraints file does not exist in the repository (or, if the constraint was intentional, inline its pins directly into requirements.txt itself)",
        "notes": "Reference to a non-existent constraints file (-c) — pip supports recursive inclusion of requirements/constraints files with -r/-c, but fails with an unintuitive error if the referenced file is missing"
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
        "expected_fix": "Upgrade together django-filter>=23.5 and djangorestframework>=3.14.0 (versions with Django 5.0 support), or stay on django==4.2.7",
        "notes": "Major Django upgrade without cascading the upgrade to the compatible dependent packages"
    },

    {
        # NOTE (rewritten): original case based on a runtime React
        # duplication (npm/JS), an ecosystem not present in this repo.
        # Rewritten as a real Python equivalent, verified with a
        # real "pip install --dry-run" (streamlit 1.28.0 explicitly declares
        # protobuf<5 in its own metadata) — see
        # CHANGELOG_DATASET.md.
        "id": "dep_047",
        "category": "dependency",
        "difficulty": "hard",
        "ci_logs": """
            ##[group]Run pip install -r requirements.txt
            Collecting streamlit==1.28.0
            Collecting protobuf==5.28.0
            ERROR: Cannot install -r requirements.txt (line 3) and protobuf==5.28.0 because these package versions have conflicting dependencies.
            The conflict is caused by:
                The user requested protobuf==5.28.0
                streamlit 1.28.0 depends on protobuf<5 and >=3.20
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "+streamlit==1.28.0\n+protobuf==5.28.0",
        "ci_job_name": "Install dependencies",
        "expected_fix": "Pin protobuf to a version compatible with streamlit==1.28.0 (e.g. protobuf==4.25.3, which satisfies >=3.20 and <5), since streamlit explicitly declares protobuf<5 — the direct pin protobuf==5.28.0 is not compatible, a 4.x version must be chosen",
        "notes": "streamlit 1.28.0 explicitly declares in its own metadata an upper bound on protobuf (<5) — an isolated bump of protobuf to a major version breaks this constraint, requires identifying and pinning the correct indirect dependency (removing the pin is not enough) — Python equivalent of the 'React duplication caused by an outdated UI library' case"
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
        "expected_fix": "Align botocore==1.34.10 (or remove the explicit pin and let boto3 resolve the compatible version automatically)",
        "notes": "boto3 and botocore must be upgraded together — manually pinning botocore to an older version breaks the constraint"
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
        "expected_fix": "Fix the cache key to use hashFiles('requirements.txt') (the file actually modified), so that a change in the dependencies correctly invalidates the cache",
        "notes": "The cache key references the wrong file: changes to requirements.txt do not invalidate the cache, causing outdated dependencies to be used"
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
        "expected_fix": "Use mypackage==1.9.1 (stable version) or add --pre to the pip install command if the release candidate is intentionally needed",
        "notes": "Pin to a release candidate (pre-release) that pip ignores by default without the --pre flag"
    },

    # ══════════════════════════════════════════════════════════
    # CATEGORY: TEST (50 errors)
    # ══════════════════════════════════════════════════════════

    {
        "id": "test_001",
        "category": "test",
        "difficulty": "easy",
        "ci_logs": """
            ##[group]Run pytest tests/ -v
            FAILED tests/test_calculator.py::test_add_positive - AssertionError: assert 5 == 99
            short test summary info
            FAILED tests/test_calculator.py::test_add_positive
            1 failed, 5 passed in 0.42s
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-assert add(2, 3) == 5\n+assert add(2, 3) == 99",
        "ci_job_name": "Run Tests",
        "expected_fix": "Restore assert add(2, 3) == 5",
        "notes": "Assert modified with a wrong value — base case"
    },

    {
        "id": "test_002",
        "category": "test",
        "difficulty": "easy",
        "ci_logs": """
            ##[group]Run pytest tests/ -v
            FAILED tests/test_calculator.py::test_divide_normal - AssertionError: assert 5.0 == 2.5
            short test summary info
            FAILED tests/test_calculator.py::test_divide_normal
            1 failed, 5 passed in 0.38s
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-assert divide(10, 2) == 5.0\n+assert divide(10, 2) == 2.5",
        "ci_job_name": "Run Tests",
        "expected_fix": "Restore assert divide(10, 2) == 5.0",
        "notes": "Wrong expected value in an arithmetic operation"
    },

    {
        "id": "test_003",
        "category": "test",
        "difficulty": "easy",
        "ci_logs": """
            ##[group]Run pytest tests/ -v
            FAILED tests/test_calculator.py::test_factorial_normal - AssertionError: assert 120 == 60
            short test summary info
            FAILED tests/test_calculator.py::test_factorial_normal
            1 failed, 5 passed in 0.41s
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-assert factorial(5) == 120\n+assert factorial(5) == 60",
        "ci_job_name": "Run Tests",
        "expected_fix": "Restore assert factorial(5) == 120",
        "notes": "Wrong factorial result in the test"
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
        "expected_fix": "Restore assert to_upper('hello') == 'HELLO'",
        "notes": "String test expecting lowercase instead of uppercase"
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
        "expected_fix": "Restore assert response.status_code == 200",
        "notes": "Wrong expected status code"
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
        "expected_fix": "Restore assert user.name == 'John' (capitalized)",
        "notes": "Case sensitivity in the expected value"
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
        "expected_fix": "Restore assert power(2, 3) == 8",
        "notes": "Wrong exponent in the test"
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
        "expected_fix": "Restore assert len([1, 2, 3]) == 3",
        "notes": "Wrong expected list length"
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
        "expected_fix": "Update the test: replace service.get_user() with service.fetch_user()",
        "notes": "Method rename in the source not reflected in the test"
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
        "expected_fix": "Update the test to include the 'price' field in the expected assert",
        "notes": "New field added to the model not included in the test"
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
        "expected_fix": "Update the test to use a password that fails with the new minimum of 4 characters, or restore MIN_PASSWORD_LENGTH = 8",
        "notes": "Business logic change reflected in the test — ambiguous whether the fix is in the test or in the source"
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
        "expected_fix": "The test calls save(record) — add commit=True in the call or it is already the default — verify that the test passes the parameter correctly",
        "notes": "New function signature with an added required parameter"
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
        "expected_fix": "Update the mock: mock_smtp.send_message instead of mock_smtp.send_email",
        "notes": "Method renamed in the source, mock not updated"
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
        "expected_fix": "Update the test: config['db_url'] instead of config['database_url']",
        "notes": "Dictionary key renamed in the source"
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
        "expected_fix": "Restore REQUIRE_TLD = True or update the test to accept the new behavior",
        "notes": "Validator behavior change — ambiguous fix (test or source)"
    },

    {
        # NOTE (rewritten): the previous actual content of test_async.py
        # required pytest-asyncio (a plugin not present in the production
        # requirements.txt). Rewritten using only stdlib asyncio — see
        # CHANGELOG_DATASET.md. Injection handled by _inject_test_016 in
        # benchmark.py (multi-line block, not a 1:1 find/replace).
        "id": "test_016",
        "category": "test",
        "difficulty": "hard",
        "ci_logs": """
            ##[group]Run pytest tests/ -v
            FAILED tests/test_async.py::test_fetch_data - RuntimeError: This event loop is already running
            RuntimeError: This event loop is already running
            loop.run_until_complete() was called from inside a loop already started by asyncio.run()
            1 failed, 59 passed in 0.41s
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-    result = asyncio.run(fetch_data())\n+    async def runner():\n+        loop = asyncio.get_event_loop()\n+        return loop.run_until_complete(fetch_data())\n+\n+    result = asyncio.run(runner())",
        "ci_job_name": "Run Tests",
        "expected_fix": "Remove the runner()/loop.run_until_complete() wrapper and restore the direct call result = asyncio.run(fetch_data()), since calling run_until_complete() on an already running loop (inside asyncio.run) always raises RuntimeError",
        "notes": "Replaces the previous actual content of test_async.py (which required pytest-asyncio) with a case based only on stdlib asyncio — nesting loop.run_until_complete() inside a loop already started by asyncio.run() is a real and deterministic error, not timing-dependent"
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
        "expected_fix": "Restore scope='function' for the db_setup fixture or add autouse and an explicit db reset",
        "notes": "Misconfigured fixture scope — side effect between tests"
    },

    {
        # NOTE (rewritten): original case required freezegun (not present
        # in the production requirements.txt). Rewritten with a fake clock
        # explicitly injected into TTLCache — same lesson (time-based
        # expiration), fully deterministic — see
        # CHANGELOG_DATASET.md.
        "id": "test_018",
        "category": "test",
        "difficulty": "hard",
        "ci_logs": """
            ##[group]Run pytest tests/ -v
            FAILED tests/test_cache.py::test_cache_invalidation - AssertionError: assert 'old_value' is None
            The expected value was None (expired), but the entry is not yet considered expired by the test's fake clock
            1 failed, 59 passed in 0.03s
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-    fake_time[0] = 301\n+    fake_time[0] = 250",
        "ci_job_name": "Run Tests",
        "expected_fix": "Set fake_time[0] to a value >= ttl_seconds (e.g. 301, beyond the 300s TTL) so that cache.get() considers the entry expired and returns None",
        "notes": "Replaces freezegun (not present in requirements.txt) with a fake clock explicitly injected into TTLCache — same lesson (time-based expiration) but fully deterministic, without depending on real timestamps"
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
        "expected_fix": "Restore date.isoformat() to keep the full ISO 8601 format, or update all the tests that expect the format with time",
        "notes": "Date format change — cascading impact on multiple tests"
    },

    {
        # NOTE (rewritten): original case based on a real multi-thread
        # race condition (non-deterministic, risk of flakiness in the
        # benchmark itself). Rewritten as a deterministic sequential
        # simulation of two "workers" — see CHANGELOG_DATASET.md.
        "id": "test_020",
        "category": "test",
        "difficulty": "hard",
        "ci_logs": """
            ##[group]Run pytest tests/ -v
            FAILED tests/test_concurrent.py::test_thread_safety - AssertionError: assert 100 == 80
            The work of worker B (worker_b) was not included in the batch passed to run_workers
            1 failed, 59 passed in 0.02s
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-    total = run_workers(counter, worker_a + worker_b)\n+    total = run_workers(counter, worker_a + worker_a)",
        "ci_job_name": "Run Tests",
        "expected_fix": "Restore worker_a + worker_b (not worker_a + worker_a) in the call to run_workers(), so that the work of both workers is actually counted",
        "notes": "Replaces the original scenario based on a real multi-thread race condition (non-deterministic, risk of flakiness in the benchmark) with a deterministic data composition bug that reproduces the same symptom (wrong final count of the shared counter)"
    },

    # --- New cases (test_021 - test_050) ---

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
        "expected_fix": "Use assert result == pytest.approx(0.3) instead of the direct float comparison",
        "notes": "Classic floating point precision error — requires pytest.approx"
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
        "expected_fix": "Update the test: pytest.raises(TypeError) instead of pytest.raises(ValueError)",
        "notes": "Type of the raised exception changed in the source, test not updated"
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
        "expected_fix": "Update the import in the test: from app.billing.payment import process_payment",
        "notes": "Module moved during a refactor, import in the test not updated"
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
        "expected_fix": "Fix the typo in the fixture name: db_sesion → db_session",
        "notes": "Typo in the fixture parameter name — pytest cannot find the requested fixture"
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
        "expected_fix": "Restore the relative path Path(__file__).parent / 'data' / 'sample.csv' instead of the local absolute path",
        "notes": "Absolute path specific to the developer's machine, non-existent on the CI runner"
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
        "expected_fix": "Fix the expected value for n=4: it must be 16, not 15",
        "notes": "Only one case of the parametrization has the wrong expected value"
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
        "git_diff": "-tests/fixtures/sample.json  (file removed from the commit)",
        "ci_job_name": "Run Tests",
        "expected_fix": "Restore/commit the tests/fixtures/sample.json file required by the test",
        "notes": "Fixture file used by the test was not included in the commit"
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
        "expected_fix": "Fix the typo in the patch target: 'app.notify.send_emial' → 'app.notify.send_email'",
        "notes": "Typo in the mock patch path causes an AttributeError instead of a simple silent mock"
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
        "expected_fix": "Use sorted(registry.keys()) in the comparison instead of list(), since the insertion order in the dictionary is not guaranteed to be stable across runs",
        "notes": "Test assumes a non-guaranteed iteration order on a dictionary/set structure"
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
        "git_diff": "-def normalize(x):\n-    return x  # bug: does not normalize\n+def normalize(x):\n+    return x.strip().lower()",
        "ci_job_name": "Run Tests",
        "expected_fix": "Remove the @pytest.mark.xfail(strict=True) marker from test_old_behavior, since the bug was fixed and the test now passes correctly",
        "notes": "Strict xfail fails when the test marked as 'expected to fail' unexpectedly passes (the underlying bug was fixed)"
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
        "expected_fix": "Restore datetime.now(timezone.utc) instead of datetime.utcnow(), which is deprecated in recent Python versions",
        "notes": "Deprecation warning promoted to error by the pytest configuration (-W error), the new deprecated API breaks the build"
    },

    {
        # NOTE (rewritten): original case based on time.sleep/timing (risk
        # of flakiness). Rewritten as a truncated task queue, deterministic
        # — see CHANGELOG_DATASET.md.
        "id": "test_032",
        "category": "test",
        "difficulty": "medium",
        "ci_logs": """
            ##[group]Run pytest tests/ -v
            FAILED tests/test_worker.py::test_background_task - AssertionError: assert 'pending' == 'done'
            1 failed, 59 passed in 0.02s
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-    tasks = [make_task(\"pending\"), make_task(\"done\")]\n+    tasks = [make_task(\"pending\")]",
        "ci_job_name": "Run Tests",
        "expected_fix": "Restore the full list of tasks (including make_task(\"done\")) in the test, so that process_queue processes the whole queue before checking the final state",
        "notes": "A task was removed from the queue in the test, so process_queue stops at the last available state ('pending') instead of reaching 'done' — replaces the original scenario based on non-deterministic timing/sleep with a 100% deterministic truncated test data case"
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
        "expected_fix": "Restore the defensive copy (copy.deepcopy(CONFIG)) in test_override_config instead of directly mutating the shared global state CONFIG",
        "notes": "Tests mutate a shared global state without isolation — fails only when run together with other tests, not individually"
    },

    {
        # NOTE (rewritten): original case removed a unittest.mock mock,
        # exposing the test to a real network ConnectionError (non
        # deterministic in CI). Rewritten with a fetch injectable via
        # dependency injection: the real default deterministically
        # fails, no real network I/O involved — see
        # CHANGELOG_DATASET.md.
        "id": "test_034",
        "category": "test",
        "difficulty": "medium",
        "ci_logs": """
            ##[group]Run pytest tests/ -v
            FAILED tests/test_weather.py::test_get_forecast - RuntimeError: network not available in this environment
            1 failed, 59 passed in 0.02s
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-    result = get_forecast(\"Rome\", fetch=fake_fetch)\n+    result = get_forecast(\"Rome\")",
        "ci_job_name": "Run Tests",
        "expected_fix": "Restore the fetch=fake_fetch parameter in the call to get_forecast(), to prevent the test from using the real fetch (which in the test environment always raises RuntimeError, since no network connection is available)",
        "notes": "Removal of the fake fetch injection: the test ends up using the real implementation, which is deterministically unavailable (no real network call is made, unlike the original scenario based on a removed unittest.mock mock and a non-deterministic network ConnectionError)"
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
        "git_diff": "-    random.seed(42)\n+    # random.seed(42) removed",
        "ci_job_name": "Run Tests",
        "expected_fix": "Restore random.seed(42) at the beginning of the test to make the sampling deterministic",
        "notes": "Random seed removed — the test becomes non-deterministic and fails intermittently"
    },

    {
        # NOTE (rewritten): original case required pytest-xdist -n auto
        # (not present in requirements.txt). Rewritten as a path collision
        # in a single process/single test, deterministic — see
        # CHANGELOG_DATASET.md.
        "id": "test_036",
        "category": "test",
        "difficulty": "medium",
        "ci_logs": """
            ##[group]Run pytest tests/ -v
            FAILED tests/test_export.py::test_write_csv - FileExistsError: [Errno 17] File exists: 'output.csv'
            Two writes used the same hardcoded path instead of two isolated files
            1 failed, 59 passed in 0.02s
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-    write_csv(str(tmp_path / \"output2.csv\"), [[\"b\", \"2\"]])\n+    write_csv(str(tmp_path / \"output.csv\"), [[\"b\", \"2\"]])",
        "ci_job_name": "Run Tests",
        "expected_fix": "Use a distinct path (e.g. tmp_path / 'output2.csv') for the second write, instead of reusing the same path 'output.csv' already created by the first call to write_csv",
        "notes": "write_csv opens the file in exclusive write mode (os.O_EXCL): reusing the same path for two distinct writes always causes a deterministic FileExistsError — replaces the original scenario based on a race condition between parallel pytest-xdist workers (not available in this environment) while keeping the same lesson (isolated output paths)"
    },

    {
        # NOTE (rewritten): original case required a snapshot testing
        # library that is not installed. Rewritten with a direct comparison
        # via assert, same lesson — see CHANGELOG_DATASET.md.
        "id": "test_037",
        "category": "test",
        "difficulty": "medium",
        "ci_logs": """
            ##[group]Run pytest tests/ -v
            FAILED tests/test_report.py::test_render_summary - AssertionError: assert 'Total: $1,234.56' == 'Total: 1234.56'
            1 failed, 59 passed in 0.02s
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-    assert result == \"Total: $1,234.56\"\n+    assert result == \"Total: 1234.56\"",
        "ci_job_name": "Run Tests",
        "expected_fix": "Update the expected assert to the new format 'Total: $1,234.56' (with currency symbol and thousands separator), consistent with the actual output of render_summary()",
        "notes": "Replaces the original scenario based on a snapshot testing library that is not available with a direct comparison via assert (same lesson: the expected assert in the test was not updated after an intentional format change)"
    },

    {
        # NOTE (rewritten): original case required alembic + sqlalchemy
        # (heavy dependencies not present). Rewritten as a field default
        # changed in a plain Python model (src/orders.py), same
        # lesson (schema changed, test not updated) — see
        # CHANGELOG_DATASET.md.
        "id": "test_038",
        "category": "test",
        "difficulty": "medium",
        "ci_logs": """
            ##[group]Run pytest tests/ -v
            FAILED tests/test_orders.py::test_order_status - AssertionError: assert 'pending' == 'new'
            1 failed, 59 passed in 0.02s
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-    assert order[\"status\"] == \"pending\"\n+    assert order[\"status\"] == \"new\"",
        "ci_job_name": "Run Tests",
        "expected_fix": "Update the assert to the current default value of the status field ('pending'), introduced by create_order after the field was added to the model",
        "notes": "Replaces the original scenario based on a missing Alembic migration (dependency not present in this repo) with an equivalent deterministic case: the default value of the 'status' field changed in the model but the assert in the test was not updated"
    },

    {
        # NOTE (rewritten): original case based on a real deadlock with a
        # non-reentrant Lock (risk of an infinite hang of the CI job).
        # Rewritten as an inversion of the producer/consumer order, immediate
        # and deterministic failure — see CHANGELOG_DATASET.md.
        "id": "test_039",
        "category": "test",
        "difficulty": "medium",
        "ci_logs": """
            ##[group]Run pytest tests/ -v
            FAILED tests/test_queue.py::test_consumer_processes_message - IndexError: pop from empty list
            run_pipeline() received an empty queue instead of the queue populated by producer()
            1 failed, 59 passed in 0.02s
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-    result = run_pipeline(queue, consumer)\n+    result = run_pipeline([], consumer)",
        "ci_job_name": "Run Tests",
        "expected_fix": "Restore result = run_pipeline(queue, consumer) (the queue populated by producer()), instead of passing an empty list",
        "notes": "Replaces the original scenario based on a real deadlock (risk of an infinite hang of the CI job) with an inversion of the order of operations that produces an immediate and deterministic failure (IndexError), keeping the same lesson (critical order of operations in a producer/consumer pipeline)"
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
        "expected_fix": "Update the assert in the test to the new message text: 'Invalid value provided'",
        "notes": "Exception message text changed in the source, test with a fragile textual assert not updated"
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
        "expected_fix": "Make the test independent of the runner timezone: explicitly set TZ='Europe/Rome' in the test environment or compare the time in UTC",
        "notes": "Test implicitly depends on the local timezone of the machine, which differs between the development environment and the CI runner (UTC)"
    },

    {
        # NOTE (rewritten): original case required a real Redis
        # service. Rewritten with an equivalent in-memory store, same
        # lesson (counter key mistakenly shared), deterministic
        # and single-process — see CHANGELOG_DATASET.md.
        "id": "test_042",
        "category": "test",
        "difficulty": "hard",
        "ci_logs": """
            ##[group]Run pytest tests/ -v
            FAILED tests/test_metrics.py::test_increment_counter - AssertionError: assert 101 == 61
            key_a and key_b point to the same counter store key: the increments of both "workers" add up on the same entry
            1 failed, 59 passed in 0.02s
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-    key_b = make_key(\"service-b\")\n+    key_b = make_key(\"service-a\")",
        "ci_job_name": "Run Tests",
        "expected_fix": "Use distinct namespaces for key_a and key_b (e.g. make_key('service-b') for key_b), so that the two counters do not share the same entry in the store",
        "notes": "Replaces Redis (external service not available in this environment) with an equivalent in-memory store — same lesson (counter key mistakenly shared between two logical 'workers'/namespaces), fully deterministic and single-process"
    },

    {
        # NOTE (rewritten): original case required triggering a real OOM
        # (unreliable/dangerous in a shared CI). Rewritten with a
        # deterministic count of the entries accumulated in the cache, same
        # lesson — see CHANGELOG_DATASET.md.
        "id": "test_043",
        "category": "test",
        "difficulty": "hard",
        "ci_logs": """
            ##[group]Run pytest tests/ -v
            FAILED tests/test_image_processing.py::test_resize_iterations - AssertionError: assert 3 == 0
            The cache is not emptied between one iteration and the next: the images accumulate instead of being released
            1 failed, 59 passed in 0.02s
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-        cache.clear()\n+        pass  # clear() removed by mistake",
        "ci_job_name": "Run Tests",
        "expected_fix": "Restore cache.clear() after every cache.load() in the loop, so that the cache is emptied between one parametrized iteration and the next instead of accumulating entries indefinitely",
        "notes": "Replaces the real OOM of the original case (risky/unreliable to trigger in a shared CI) with a deterministic count of the entries accumulated in the cache — same lesson (resources not released between iterations), verifiable with a simple assert without consuming real memory"
    },

    {
        # NOTE (rewritten): the premise of the original is factually wrong
        # (a Python 3.7+ dict always preserves insertion order,
        # PYTHONHASHSEED is irrelevant). Rewritten with an assert in the test that
        # wrongly expects alphabetical order — see
        # CHANGELOG_DATASET.md.
        "id": "test_044",
        "category": "test",
        "difficulty": "hard",
        "ci_logs": """
            ##[group]Run pytest tests/ -v
            FAILED tests/test_dedup.py::test_deduplicate_preserves_first - AssertionError: assert ['b', 'a', 'c'] == ['a', 'b', 'c']
            1 failed, 59 passed in 0.02s
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-    assert result == [\"b\", \"a\", \"c\"]\n+    assert result == [\"a\", \"b\", \"c\"]",
        "ci_job_name": "Run Tests",
        "expected_fix": "Restore the expected assert to the order of first appearance (['b', 'a', 'c']), consistent with the implementation of deduplicate_preserves_first based on dict.fromkeys(), which preserves insertion order in Python 3.7+ regardless of PYTHONHASHSEED",
        "notes": "Corrects the factually wrong premise of the original case (a Python 3.7+ dict always preserves insertion order, PYTHONHASHSEED is irrelevant) with an assert in the test that wrongly expected alphabetical order instead of order of first appearance — deterministic bug, no dependency on hash randomization"
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
        "expected_fix": "Restore scope='function' for report_writer, or explicitly align the scope of db_engine to 'module' to prevent it from being closed earlier than expected",
        "notes": "Scope mismatch between dependent fixtures causes an early teardown that only shows up on the last test of the session"
    },

    {
        # NOTE (rewritten): original case required a macos-14/arm64 runner
        # (the current CI is ubuntu-latest only). Rewritten with the exact
        # same underlying problem (exact float comparison), reproducible
        # deterministically on any standard IEEE 754 platform —
        # see CHANGELOG_DATASET.md.
        "id": "test_046",
        "category": "test",
        "difficulty": "hard",
        "ci_logs": """
            ##[group]Run pytest tests/ -v
            FAILED tests/test_stats.py::test_variance_calculation - AssertionError: assert 0.006666666666666668 == 0.006666666666666667
            Floating point comparison with exact equality: small rounding errors in IEEE 754 arithmetic make the comparison unstable
            1 failed, 59 passed in 0.02s
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-    assert result == pytest.approx(0.006666666666666667)\n+    assert result == 0.006666666666666667",
        "ci_job_name": "Run Tests",
        "expected_fix": "Restore pytest.approx(0.006666666666666667) for the comparison, since an exact equality comparison between floats is fragile due to floating point rounding errors",
        "notes": "Replaces the original scenario tied to the runner architecture (x86_64 vs arm64, not deterministically reproducible on a fixed ubuntu-latest runner) with the exact same underlying problem (exact float comparison), which shows up deterministically on any standard IEEE 754 platform"
    },

    {
        # NOTE (rewritten): original case combined an unstable sort with an
        # 85% coverage gate not configured in this ci.yml. Rewritten
        # as a composite case fully confined to the test file (assert
        # with wrong tie-break + removed function) — injection handled by
        # _inject_test_047 in benchmark.py (replacement of the whole file, not
        # a 1:1 find/replace) — see CHANGELOG_DATASET.md.
        "id": "test_047",
        "category": "test",
        "difficulty": "hard",
        "ci_logs": """
            ##[group]Run pytest tests/ -v
            FAILED tests/test_recommender.py::test_ranking_order - AssertionError: assert ['a', 'b', 'c'] == ['c', 'a', 'b']
            tests/test_recommender.py::test_edge_case_empty_input not found — the function appears to have been removed from the file
            1 failed, 58 passed in 0.02s
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-    assert recommend(items) == [\"a\", \"b\", \"c\"]\n+    assert recommend(items) == [\"c\", \"a\", \"b\"]\n-\n-\n-def test_edge_case_empty_input():\n-    assert recommend([]) == []",
        "ci_job_name": "Run Tests",
        "expected_fix": "Fix the assert of test_ranking_order to the correct expected value (['a', 'b', 'c'], tie-break order by ascending 'id' on equal scores) AND restore the test_edge_case_empty_input function removed from the file: both problems must be solved, not just one",
        "notes": "Composite case (two independent problems in the same test file): an assert with a wrong expected value and a test function removed entirely — replaces the original combination of an unstable sort + coverage gate (not configured in this ci.yml) with two defects fully confined to the test file, both deterministic"
    },

    {
        # NOTE (rewritten): original case required pytest-xdist -n
        # (non-picklable objects between workers). Rewritten with the same
        # underlying lesson (state mistakenly shared between two "clients" that
        # should be independent), reproduced in a single process in a
        # deterministic way — see CHANGELOG_DATASET.md.
        "id": "test_048",
        "category": "test",
        "difficulty": "hard",
        "ci_logs": """
            ##[group]Run pytest tests/ -v
            FAILED tests/test_upload.py::test_multipart_upload - AssertionError: assert ['part1.bin', 'part2.bin'] == ['part1.bin']
            client_a and client_b point to the same UploadClient instance instead of two independent instances
            1 failed, 59 passed in 0.02s
            ##[endgroup]
            ##[error]Process completed with exit code 1.
        """,
        "git_diff": "-    client_b = UploadClient()\n+    client_b = client_a",
        "ci_job_name": "Run Tests",
        "expected_fix": "Restore client_b = UploadClient() (a new independent instance) instead of reassigning client_b to the same object as client_a",
        "notes": "Replaces pytest-xdist (not present in requirements.txt) and the threading.Lock pickling error with the same underlying lesson (state mistakenly shared between two 'clients' that should be independent), reproduced in a single process in a fully deterministic way"
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
        "expected_fix": "Restore entries=None as the default and initialize entries = entries if entries is not None else [] inside the function, to avoid sharing the mutable default list between calls",
        "notes": "Classic Python bug: mutable default argument (list) shared and accumulated across subsequent calls/tests"
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
        "expected_fix": "Use pytest.approx(24, abs=1) (or compute in UTC, where days always have 24 hours) to tolerate the variation due to the daylight saving time change",
        "notes": "Duration computed in a local timezone subject to DST — the day of the clock change has 23 or 25 hours, not always 24"
    },

    # ══════════════════════════════════════════════════════════
    # CATEGORY: CONFIG (50 errors)
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
        "expected_fix": "Restore python-version: '3.11'",
        "notes": "Non-existent Python version — base config case"
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
        "expected_fix": "Use python-version: '3.12'",
        "notes": "Python 3.15 not yet released"
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
        "expected_fix": "Use python-version: '3.11' or higher",
        "notes": "Python 2.7 EOL — not supported in GitHub Actions"
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
        "expected_fix": "Remove the token field or use ${{ secrets.GITHUB_TOKEN }}, which is always available",
        "notes": "Secret that does not exist in the repository"
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
        "expected_fix": "Use actions/setup-python@v5 (updated version)",
        "notes": "Deprecated action — v1 uses deprecated workflow commands"
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
        "expected_fix": "Use runs-on: ubuntu-latest or ubuntu-20.04",
        "notes": "ubuntu-18.04 runner removed from GitHub Actions"
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
        "expected_fix": "Restore working-directory: . or create the src/backend directory",
        "notes": "Non-existent working directory"
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
        "expected_fix": "Restore the actions/setup-python@v5 step before installing the dependencies",
        "notes": "setup-python step removed — pip not available"
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
        "expected_fix": "Fix the indentation of 'steps:' — it must be 4 spaces, not 8",
        "notes": "YAML indentation error — not always easy to identify the exact line"
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
        "expected_fix": "Merge the triggers under a single 'on:' block with push and pull_request",
        "notes": "Duplicate YAML key — a second 'on:' was added instead of extending the first one"
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
        "expected_fix": "Add the required 'path:' field: path: ./test-results/",
        "notes": "Required field missing in the action"
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
        "expected_fix": "Fix the typo: python-versions → python-version (without the 's')",
        "notes": "Typo in the parameter name — subtle error"
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
        "expected_fix": "Restore pip install -r requirements.txt, which includes pytest",
        "notes": "requirements.txt not installed — pytest missing"
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
        "expected_fix": "Fix the secret name: DB_URL → DATABASE_URL (or vice versa, align with the secret configured in the repository)",
        "notes": "Wrong secret name — requires knowledge of the configured secrets"
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
        "expected_fix": "Restore cron: '0 0 * * *' (once a day) instead of every hour",
        "notes": "Cron expression too frequent — not supported by GitHub"
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
        "expected_fix": "Reduce the matrix: remove unnecessary dimensions or use 'include' for specific combinations instead of the full Cartesian product",
        "notes": "Matrix explosion — combinations produce too many jobs"
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
        "expected_fix": "Restore the deployments: write permission in the permissions block of the workflow",
        "notes": "Permission removed from the workflow — requires understanding the GitHub Actions permission model"
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
        "expected_fix": "Restore --cov=src --cov-report=xml in the pytest command to generate the coverage data",
        "notes": "Coverage flags removed — the subsequent step that reads .coverage fails"
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
        "expected_fix": "Restore file: ./Dockerfile or specify file: ./app/Dockerfile if the Dockerfile was moved to the app directory",
        "notes": "Dockerfile path not updated after restructuring the project"
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
        "expected_fix": "Restore audience: pypi for the trusted publisher — testpypi is for the test registry",
        "notes": "Wrong OIDC audience — requires knowledge of PyPI trusted publishers"
    },

    # --- New cases (conf_021 - conf_050) ---

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
        "expected_fix": "Restore node-version: '20' (or a valid patch version of Node 21, e.g. '21.7.1')",
        "notes": "Non-existent Node.js version specified in actions/setup-node"
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
        "expected_fix": "Restore submodules: true in the actions/checkout step to initialize the required git submodules",
        "notes": "Submodule not initialized — the directory is empty and the required files are missing"
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
        "expected_fix": "Restore a default: 'staging' value for the 'environment' input, or always provide the value when starting the workflow manually",
        "notes": "Required workflow_dispatch input without a default, forgotten in a manual run"
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
        "expected_fix": "Restore runs-on: [self-hosted, linux] or register a runner with the 'gpu' label if the job actually requires a GPU",
        "notes": "The requested runner label does not match any registered self-hosted runner, the job stays stuck in the queue"
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
        "expected_fix": "Restore timeout-minutes: 20, since the integration test suite requires more than the configured 5 minutes",
        "notes": "Job timeout set too low compared to the actual time needed by the test suite"
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
        "expected_fix": "Fix the comparison operator: github.ref == 'refs/heads/main' (double equals, not assignment)",
        "notes": "Syntax typo in the if expression: a single '=' instead of '==' is not valid in the GitHub Actions expression syntax"
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
        "expected_fix": "Fix the typo: needs: buld → needs: build",
        "notes": "Typo in the name of the job referenced in 'needs', the dependency job does not exist"
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
        "expected_fix": "Fix distribution: 'temurin' (or use 'oracle', not 'oracle-jdk')",
        "notes": "Invalid JDK distribution name in the actions/setup-java action"
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
        "expected_fix": "Restore pull-requests: write in the permissions block of the workflow to allow the GITHUB_TOKEN to create comments",
        "notes": "PR write permission removed from the workflow, the read-only default blocks the action"
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
        "expected_fix": "Restore shell: bash in the step, since on the windows-latest runner the default shell does not correctly interpret a bash script",
        "notes": "The default shell on the Windows runner is not bash, a .sh script requires an explicit shell: bash"
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
        "expected_fix": "Restore the env: section with API_SECRET: ${{ secrets.API_SECRET }} in the step, since the local .env file (in .gitignore) is not available in CI",
        "notes": "The project relies on a local, unversioned .env file; in CI the variables must be injected explicitly from the secrets"
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
        "expected_fix": "Fix the typo in the hashFiles pattern: 'requirements.text' → 'requirements.txt', so that the cache key correctly reflects the file content",
        "notes": "Typo in the file extension passed to hashFiles makes the cache key constant, the cache is never invalidated when the dependencies change"
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
        "expected_fix": "Update the upload-artifact steps to use unique names per matrix (e.g. name: test-results-${{ matrix.os }}) and use merge-multiple: true in download-artifact@v4",
        "notes": "Breaking change between v3 and v4 of download-artifact: automatic merging of same-named artifacts is no longer the default behavior"
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
        "expected_fix": "Restore group: deploy-${{ github.ref }} and cancel-in-progress: false, to prevent deploys on different branches from cancelling each other",
        "notes": "Concurrency group not scoped per branch causes the unintended cancellation of in-progress deploys on different branches"
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
        "expected_fix": "Restore secrets: inherit in the call to the reusable workflow to propagate the required secrets (e.g. PYPI_API_TOKEN)",
        "notes": "Reusable workflow called without secrets: inherit does not receive the secrets of the calling workflow"
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
        "expected_fix": "Update the branch protection rules to require the new job name 'test' instead of 'run-tests' (or rename the job keeping 'run-tests')",
        "notes": "Renaming a job without updating the required status checks in the branch protection blocks the merge of PRs indefinitely"
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
        "git_diff": "-    environment: production\n+    environment:\n+      name: production\n+      # required reviewers added via the GitHub UI, not reflected in the workflow file",
        "ci_job_name": "Deploy to production",
        "expected_fix": "Use a separate environment without required reviewers for the nightly automatic deploys (e.g. 'production-auto'), or remove the protection rule for scheduled jobs",
        "notes": "Environment protection rule with required reviewers blocks automatic deploys that have no human ready to approve"
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
        "expected_fix": "Restore fail-fast: false in the matrix strategy, to allow all combinations to complete regardless of the failure of a single version",
        "notes": "fail-fast: true prematurely cancels the other matrix combinations, hiding useful information about the actual state of the other versions"
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
        "expected_fix": "Pass the value as a string: skip-cache: 'false', since composite action inputs are always strings and an unquoted boolean causes a wrong evaluation in the condition",
        "notes": "The inputs of a composite action are always strings; passing an unquoted boolean alters the conditional logic of the action"
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
        "expected_fix": "Pin the action to a specific, verified commit SHA (e.g. @8f1a2b3) instead of a mutable tag such as @v1, to prevent a tag repointing from introducing unexpected behavior",
        "notes": "A mutable tag (@v1) can be repointed by the maintainer to a different and incompatible version without notice"
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
        "expected_fix": "Restore lfs: true in the actions/checkout step to download the actual content of the files tracked by Git LFS",
        "notes": "Without lfs: true, the files tracked by Git LFS are checked out as text pointers instead of the actual binary content"
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
        "expected_fix": "Also add secrets: inherit in the nested call to deploy-inner.yml: secret inheritance is not transitive across multiple levels of reusable workflows",
        "notes": "In a multi-level chain of reusable workflows, secrets: inherit must be declared at every call level, not only at the first one"
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
        "expected_fix": "Restore the concurrency group scoped per matrix combination (including matrix.os and matrix.python-version), not only per workflow",
        "notes": "Overly generic concurrency group applied inside a matrix job causes intermittent cancellations between independent combinations"
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
        "expected_fix": "Include github.ref_name (or at least a branch scope) in the cache key, to prevent different branches from sharing/polluting the same cache",
        "notes": "Cache shared without per-branch scoping allows an experimental branch to 'poison' the cache used by the main branch"
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
        "expected_fix": "Update the IAM trust policy of the AWS role to include the sub condition matching repo:myorg/myrepo:ref:refs/heads/release/*, or restore the trigger on refs/heads/main consistent with the existing policy",
        "notes": "The workflow trigger was changed to a different branch pattern without updating the OIDC trust policy on the AWS side, which explicitly validates the 'sub' claim"
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
        "git_diff": "-      - name: Clean workspace\n-        run: rm -f /tmp/app.lock\n+      # cleanup step removed",
        "ci_job_name": "Run Tests",
        "expected_fix": "Restore the cleanup step that removes /tmp/app.lock at the beginning of the job, needed because the self-hosted runner is not ephemeral and reuses the same filesystem across runs",
        "notes": "A persistent self-hosted runner keeps state across runs; without explicit cleanup, a previous crash leaves leftover files that break the next run"
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
        "expected_fix": "Update the repository ruleset to require 'test-suite' instead of 'ci/test', or temporarily keep both names until the ruleset is aligned, to unblock already open PRs",
        "notes": "Renaming a job and the branch protection ruleset at the same time can get out of sync for already open PRs, blocking the merge until they are realigned manually"
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
        "expected_fix": "Do not check out the PR code (head.sha, untrusted) in a pull_request_target workflow with access to secrets; split into two jobs: one with pull_request_target only for trusted operations with secrets, one with pull_request (without secrets) to run the PR code",
        "notes": "Hard security case: pull_request_target grants access to secrets, running untrusted PR code in that context is a secret-exfiltration risk, not just a configuration error to be fixed lightly"
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
        "expected_fix": "Remove github.run_id from the cache key (it creates a new, never reused cache on every run, saturating the 10GB limit) and periodically clean up obsolete caches",
        "notes": "A cache key that includes a unique value for every run (run_id) prevents reuse and quickly accumulates redundant caches until the repository limit is exceeded"
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
        "expected_fix": "Restore if: always() && needs.A.result == 'success' in job C, so that it does not implicitly depend on the success of B when B is legitimately skipped by its condition",
        "notes": "Without always(), an upstream job skipped by an expected condition still blocks the downstream jobs that depend on it through 'needs'"
    },

]


# ══════════════════════════════════════════════════════════════
# UTILITY FUNCTIONS
# ══════════════════════════════════════════════════════════════

def get_by_category(category: str) -> list:
    """Filters the dataset by category."""
    return [e for e in DATASET if e["category"] == category]


def get_by_difficulty(difficulty: str) -> list:
    """Filters the dataset by difficulty."""
    return [e for e in DATASET if e["difficulty"] == difficulty]


def get_stats() -> dict:
    """Dataset statistics."""
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
    print(f"Dataset: {stats['total']} total errors")
    print(f"By category: {stats['by_category']}")
    print(f"By difficulty: {stats['by_difficulty']}")

    # Check that IDs are unique
    ids = [e["id"] for e in DATASET]
    assert len(ids) == len(set(ids)), "Duplicate IDs found!"
    print("✅ All IDs are unique")