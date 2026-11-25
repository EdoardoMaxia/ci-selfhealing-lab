# Changelog — benchmark harness and synthetic dataset fixes

Date: 2026-07-30
Context: bugs identified through manual debugging of the benchmark harness
(`experiments/benchmark.py`) and of the synthetic dataset (`experiments/dataset.py`)
used in the experimental evaluation. All changes were proposed as a plan,
explicitly confirmed, and verified locally before being kept on disk
(see the "Verification" section at the end).

## 1. Isolated fixes

### 1.1 `agent/state.py` — `modified_file` field missing from `AgentState`
**Status**: already fixed in a commit preceding this session (`0fcdfd8`,
2026-07-30 12:30). No change needed.

### 1.2 `agent/agents/test_agent.py` — backslashes on Windows in `find_test_file()`
The first `return` of the function already normalized the path with
`.replace("\\", "/")`; the two fallbacks (`match2` and the default
`tests/test_calculator.py`) did not. These two were normalized as well, using
`os.sep` to make the cross-platform intent explicit.

### 1.3 `experiments/benchmark.py` — `inject_error()` no-op for `category=="test"`
Implemented the actual injection: `resolve_test_target_file()` extracts the path
of the test file from the synthetic `ci_logs` (same pattern as
`find_test_file()`), then a line-by-line find/replace is applied (same
mechanism already used for `config`). Added three supporting mechanisms,
needed because some cases do not lend themselves to the generic find/replace:

- `TEST_TARGET_OVERRIDE`: for the cases in which the `git_diff` literally
  describes a line of **source** code (not of the test file) —
  the injection is applied to the listed `src/*.py` module instead of the
  file resolved from the `ci_logs` (e.g. `test_009` → `src/services.py`).
- `SPECIAL_TEST_INJECTORS`: for the cases in which the `git_diff` is not a
  1:1 replayable diff of code lines (it describes a file move/removal, or has
  a number of removed/added lines that cannot be paired) — a small dedicated
  injector for `test_010`, `test_012`, `test_023`, `test_027`, `test_030`,
  `test_033` (see the docstring of each one in the code for the specific
  rationale).
- `EXCLUDED_TEST_IDS`: 15 ids explicitly excluded from the injection (see
  §3).

`inject_error()` now returns `bool`. `run_model()` in `benchmark.py` was
updated to catch `False` (no valid target) and record the case with
`final_status="excluded"` instead of passing it off as a real attempt —
`print_summary()` filters these cases out of the Success Rate computation
(they remain in the raw CSV/JSON for transparency, with an "Excl." column in
the terminal summary).

### 1.4 `experiments/benchmark.py` — wrong routing for `category=="dependency"`
`agent/agents/dependency_agent.py` turned out to be **hardcoded** to read and
write only `requirements.txt` (it was not modified, as per an explicit
constraint). As a consequence, routing the injection to a different file
(`package.json`, `ci.yml`) would not make these cases solvable by the current
system anyway. The adopted fix is therefore the explicit exclusion
(`EXCLUDED_DEPENDENCY_IDS`, 10 ids — see §3) instead of a routing attempt that
the agent could not exploit anyway.

### 1.5 Extension of `ALLOWED_TEST_FILES` / `reset_files()`
Needed as a consequence of 1.3: without a whitelist, `reset_files()` would have
deleted every new test file on every run. Added `GROUP1_TEST_FILES`
(29 file names) to the whitelist, and `GROUP1_RESTORE_PATHS` (list of
`src/`, `app/`, `tests/` paths and two fixture files) restored via
`git checkout HEAD --` in `reset_files()`, the same mechanism already used for
`tests/test_calculator.py` and `ci.yml`. Bonus: `tests/test_async.py` as well
(which was previously never restored from git, only protected from
deletion) is now restored correctly.

**Important**: this mechanism requires the files listed in
`GROUP1_RESTORE_PATHS` to be **committed** — `git checkout HEAD -- <path>`
has no effect on untracked files. Until these files are committed,
a real run of `experiments/benchmark.py` would leave the files modified
by the injection/the agent dirty between one case and the next.

## 2. Group 1 — stubs created for the "test" dataset

32 cases (`test_004,005,006,007,008,009,010,011,012,013,014,015,017,019,021,
022,023,024,025,026,027,028,029,030,031,033,035,040,041,045,049,050`) are
now genuinely evaluable: the source module/file exists before the case is
executed, with a "correct" behavior consistent with `expected_fix`, so that
the injection actually breaks it.

**Files created** — source modules (`src/`): `utils.py`, `models.py`,
`services.py`, `auth.py`, `db.py`, `mailer.py`, `config.py`, `validator.py`,
`integration_db.py`, `serializer.py`, `parser.py`, `api.py`, `orders.py`,
`loader.py` (not referenced by the final test, see the note below),
`importer.py`, `registry.py`, `legacy.py`, `settings.py`, `sampler.py`,
`validation.py`, `scheduler.py`, `reports.py`, `logger.py`,
`billing_cycle.py`. `src/calculator.py` extended with `power()`.

**`app/` package** (new, parallel to `src/`): `app/billing/payment.py`,
`app/notify.py` — module names literally dictated by the `expected_fix` of
cases `test_023`/`test_028`.

**Test files created** (`tests/`): 29 files, one or more per module (e.g.
`test_math.py` covers `test_007`+`test_021`+`test_026` in a single file, on
the model already used by `config`/`ci.yml`). Existing `tests/test_api.py` extended
(covers `test_005`+`test_010`). Two fixture files: `tests/data/sample.csv`,
`tests/fixtures/sample.json`.

**Note on `src/loader.py`**: created but no longer referenced — the `git_diff`
of `test_025` describes the path assignment directly in the test
file (not through a helper), so the final stub builds the path
inline in `tests/test_loader.py`. The module remains as an inert stub that
can be removed.

## 3. Cases excluded from the Success Rate (HISTORICAL — superseded, see §7)

### "test" category (15 ids, `EXCLUDED_TEST_IDS` in `benchmark.py`)
`test_016` (actual content of `test_async.py` different from the scenario),
`test_018` (requires `freezegun`), `test_020`/`test_032` (non-deterministic
timing/race), `test_034` (network mock removed → real call),
`test_036`/`test_048` (require `pytest-xdist -n`), `test_037` (requires a
snapshot testing library), `test_038` (requires `alembic`+`sqlalchemy`),
`test_039` (risk of an infinite hang), `test_042` (requires Redis),
`test_043` (requires triggering a real OOM), `test_044` (invalid
premise: a Python 3.7+ dict preserves insertion order regardless of
`PYTHONHASHSEED`), `test_046` (requires a macos-14/arm64 runner),
`test_047` (composite case, coverage gate not present in `ci.yml`).

### "dependency" category (10 ids, `EXCLUDED_DEPENDENCY_IDS` in `benchmark.py`)
`dep_022`, `dep_023`, `dep_027`, `dep_029`, `dep_031`, `dep_032`, `dep_040`,
`dep_043`, `dep_045`, `dep_047` — all npm/yarn/JDK/ci.yml, the real fix cannot
be expressed by writing only `requirements.txt` (the only file that
`dependency_agent.py` can modify).

### Rewritten as Python equivalents (explicitly approved)
- **`dep_026`**: from "poetry lock not regenerated after changing pyproject.toml"
  to "requirements.txt not regenerated with pip-compile after changing
  requirements.in" (same conceptual lesson, `httpx` as the dependency).
  `ci_logs`, `git_diff`, `expected_fix`, `notes` updated; `id`,
  `category`, `difficulty` unchanged.
- **`dep_030`**: from "npm audit reports a vulnerability" to "pip-audit reports
  a vulnerable pin (`pillow`), the indicated upgrade points to a
  non-existent version". Same fields updated.

Both cases are now genuinely injectable/solvable through
`requirements.txt` (verified).

## 4. Final mapping of the 150 cases (HISTORICAL — superseded, see §7)

| Category | Active (counted in SR) | Excluded | Total |
|---|---|---|---|
| dependency | 40 | 10 | 50 |
| test | 35 (3 pre-existing + 32 Group 1) | 15 | 50 |
| config | 50 | 0 | 50 |
| **Total** | **125** | **25** | **150** |

## 5. Verification performed

Temporary script (`_verify_injections.py`, removed after use) that for
each of the 32 Group 1 cases: takes a snapshot of the involved files, calls
`inject_error()`, runs `pytest tests/` and checks for a `returncode != 0`
("red"), restores the snapshot and checks that it goes back to green. Final
result: **32/32 cases verified correctly**. During the verification,
5 real bugs in the initial design of the stubs were found and fixed:

1. `test_014`: quote/comma mismatch between `git_diff` and `src/config.py`
   — the injection failed silently (no textual match).
2. `test_026`: spacing mismatch in the `parametrize` list between
   `git_diff` and `tests/test_math.py` — same problem.
3. `test_028`: `git_diff` uses the `@patch(...)` decorator syntax, the initial
   stub used the `with patch(...)` context-manager syntax — no
   textual match possible; rewritten with the decorator syntax.
4. `test_033`: `git_diff` with 3 removed lines and 2 added ones — the zip used
   by the generic find/replace paired only the first 2, leaving an
   orphan line (`NameError` instead of the intended behavior). Added a
   dedicated `_inject_test_033`.
5. `test_050`: subtracting two aware `datetime`s with the **same tzinfo
   object** makes Python ignore the offset (documented but
   counterintuitive behavior) — the DST jump was not detected. Fixed by
   explicitly converting to UTC before the subtraction, both in the test and in
   `src/billing_cycle.py`.

A sixth problem (not a bug, but a flakiness risk) was fixed
preemptively: the initial stub of `test_029` used a `set()` to
simulate a "non-guaranteed" iteration order, but with hash randomization
the order happens to match the alphabetical one about 50% of the
time (with 2 elements) — made deterministic by using the insertion order
of a `dict` (`src/registry.py`) instead of the hash-dependent order of a
`set`.

## 6. Next step (HISTORICAL — see §7 for the current state)

The new/modified files have not been committed yet (by policy: commits
are made only on explicit request). For `reset_files()` to work
correctly in a real benchmark run, `git add` +
commit of all the files listed in `GROUP1_RESTORE_PATHS`
(`experiments/benchmark.py`) is needed, in addition to the isolated fix files.

## 7. Replacement of the 25 excluded cases — 150/150 cases now active

Date: 2026-08-25. The 25 cases listed in §3 (15 `test`, 10 `dependency`) were
**replaced** with new scenarios, actually injectable and solvable
by the current system. `EXCLUDED_TEST_IDS`, `EXCLUDED_DEPENDENCY_IDS` and all
the associated exclusion logic (`final_status="excluded"` in
`run_model()`, "Excl." column in `print_summary()`) were **removed**
from `experiments/benchmark.py`. The dataset now has **150/150 active cases**,
0 excluded.

### 7.1 Design constraint discovered

`agent/agents/test_agent.py::test_agent_node` **always and only** writes the
test file resolved by `find_test_file(ci_logs)`, never a `src/` file
(even when the prompt asks it to distinguish "wrong test" from
"wrong source" — the code applies the fix to the test file anyway).
For this reason all 15 new "test" cases are bugs **in the test file itself**
(wrong assert or test data), never in the source — it is the only kind of fix
the agent can actually apply. The pre-existing cases that route
the injection to a `src/` module (`TEST_TARGET_OVERRIDE`, e.g. `test_009`)
work because the real fix is still "update the test to reflect
the legitimate rename/change in the source" — it does not apply to a real bug
in the source, which the agent could not fix.

`agent/agents/dependency_agent.py` always rewrites the whole
`requirements.txt`: every new "dependency" case uses real PyPI packages
(not fictitious names), because the CI runs a real `pip install`.

### 7.2 Dependency — 10 cases replaced (all pure `requirements.txt`)

| id | difficulty | scenario | verified with |
|---|---|---|---|
| dep_022 | easy | typo `flaks==3.0.3` | real `pip install --dry-run` |
| dep_023 | easy | `pyyaml=6.0.1` (single `=`) | same |
| dep_027 | easy | JSON-style line `"requests": "2.31.0"` | same |
| dep_029 | easy | `pywin32==306` (Windows-only) on a Linux runner | injection verified structurally (false negative on the local Windows sandbox, see the note below) |
| dep_031 | easy | truncated marker `requests==2.31.0; python_version` | real `pip install --dry-run` |
| dep_032 | medium | `sphinx==7.2.6` + `docutils==0.22` (sphinx requires `docutils<0.21`) | same |
| dep_040 | medium | self-contradictory range `click<8.0,>=9.0` | same |
| dep_043 | hard | `pandas==2.0.3` + `numpy==2.0.0` (pandas requires `numpy<2`) | same |
| dep_045 | hard | non-existent `-c constraints.txt` | same |
| dep_047 | hard | `streamlit==1.28.0` + `protobuf==5.28.0` (streamlit requires `protobuf<5`) | same |

Note on `dep_029`: being the only platform-related case, `pip install
--dry-run` on this Windows development sandbox does not fail (pywin32 has
a wheel for win_amd64) — an expected local false negative. On the real CI runner
(`ubuntu-latest`, see `.github/workflows/ci.yml`) it always fails, as
described in the `ci_logs`. The local verification was limited to checking that
the injection actually writes `pywin32==306` into `requirements.txt`.

All the version constraints mentioned above (e.g. `sphinx 7.2.6 depends on
docutils<0.21`, `pandas 2.0.3 depends on numpy<2`, `streamlit 1.28.0 depends
on protobuf<5`) were **verified with a real `pip install --dry-run`
against PyPI**, both for the "broken" state (exit code ≠ 0) and for the proposed
fix (exit code 0) — they are not made-up constraints.

### 7.3 Test — 15 cases replaced (deterministic bug in the test file)

Each case has a new `src/` module + `tests/` file (full list in
`GROUP1_RESTORE_PATHS`/`REPLACEMENT_TEST_FILES` in `benchmark.py`), uses only
the standard library + `pytest`/`pytest-cov` (no external dependency not
present in the production `requirements.txt`), and is 100% deterministic
(no `time.sleep`, no real threading, no real network).

| id | difficulty | new src/ | replaces |
|---|---|---|---|
| test_016 | hard | `fetcher.py` | pytest-asyncio → stdlib `asyncio` only, dedicated injector `_inject_test_016` |
| test_018 | hard | `cache.py` | freezegun → injectable fake clock |
| test_020 | hard | `counter.py` | real race condition → deterministic sequential simulation |
| test_032 | medium | `worker.py` | timing/sleep → truncated task queue |
| test_034 | medium | `weather.py` | network mock removed → injectable fetch with a deterministically failing default |
| test_036 | medium | `exporter.py` | pytest-xdist → path collision with exclusive write (`O_EXCL`) |
| test_037 | medium | `summary.py` | snapshot testing library → direct comparison with assert |
| test_038 | medium | `orders.py` (extended) | alembic/sqlalchemy → field default changed in a plain Python model |
| test_039 | medium | `pipeline.py` | real deadlock → producer/consumer inversion (immediate `IndexError`) |
| test_042 | hard | `metrics.py` | Redis → in-memory store with colliding namespaces |
| test_043 | hard | `image_cache.py` | real OOM → deterministic count of accumulated entries |
| test_044 | hard | `dedup.py` | wrong premise about `PYTHONHASHSEED` → assert with wrong alphabetical order (also corrects the original's wrong technical claim) |
| test_046 | hard | `stats.py` | dependency on the macos-14/arm64 arch → same problem (exact float comparison) reproducible on any platform |
| test_047 | hard | `recommender.py` | unstable sort + unconfigured coverage gate → composite case in the test file, dedicated injector `_inject_test_047` |
| test_048 | hard | `upload.py` | pytest-xdist + non-picklable object → state mistakenly shared between two instances, single process |

`tests/test_orders.py`/`src/orders.py` (already used by the pre-existing case
`test_024`) were **extended**, not replaced: added a new
test function (`test_order_status`) and a new field with a default
(`status="pending"`) in `create_order`, without touching `test_create_order`.
`tests/test_async.py` already existed (with content unrelated to the scenario,
see §3) and was rewritten from scratch.

### 7.4 Changes to `experiments/benchmark.py`

- Removed `EXCLUDED_TEST_IDS`, `EXCLUDED_DEPENDENCY_IDS` and every reference to them.
- `GROUP1_TEST_FILES` unchanged; added a new set `REPLACEMENT_TEST_FILES`
  (13 names) merged into `ALLOWED_TEST_FILES`.
- `GROUP1_RESTORE_PATHS` extended with the 14 new `src/*.py` and (via
  `REPLACEMENT_TEST_FILES`) the 13 new `tests/*.py`.
- `SPECIAL_TEST_INJECTORS` extended with `_inject_test_016` (multi-line block,
  nested asyncio wrapper) and `_inject_test_047` (replacement of the whole
  file content, composite case). No pre-existing key touched.
- `TEST_TARGET_OVERRIDE` unchanged — none of the 15 new cases requires it.

### 7.5 Verification performed

Temporary script (`_verify_replacements.py`, removed after use), same
scheme as Group 1 (snapshot → `inject_error()` → check red →
restore → check green), with two differences:

- The new `src/`/`tests/` files are still **untracked** in git in this
  session, so `reset_files()` (which uses `git checkout HEAD --`) cannot
  restore them — the script took a manual in-memory snapshot/restore
  to work around the problem. **The same constraint already documented in
  §"Next step" applies: without committing these files, a real benchmark run
  would leave the files dirty between one case and the next.**
- For the 10 `dependency` cases, "red"/"green" was verified with a
  real `pip install --dry-run -r requirements.txt` (not just with the absence
  of exceptions), to confirm that the PyPI conflicts/errors mentioned in the
  `ci_logs` are real.

Final result: **25/25 cases verified correctly** (red
on injection, green after restore/fix).

### 7.6 Final mapping of the 150 cases (updated)

| Category | Active (counted in SR) | Excluded | Total |
|---|---|---|---|
| dependency | 50 | 0 | 50 |
| test | 50 | 0 | 50 |
| config | 50 | 0 | 50 |
| **Total** | **150** | **0** | **150** |

### 7.7 Next step

As for Group 1: the new files (14 `src/*.py`, 13 `tests/*.py`) and the
modified ones (`src/orders.py`, `tests/test_orders.py`, `tests/test_async.py`,
`experiments/dataset.py`, `experiments/benchmark.py`) have not been
committed yet (by policy: commits are made only on explicit request). For
`reset_files()` to work correctly in a real benchmark run,
`git add` + commit of all these files is needed.

## 8. MSR 2027 revision F1 — corrected benchmark: 79 cases kept, 71 excluded

Date: 2026-11-25. Context: the failing-state verification of 20 Nov 2026
(`--verify-dep-config`) found that only 73/150 injected states made the CI fail.
Rule adopted for the corrected benchmark: **a case stays only if its error is the
same as in the submission** (same `git_diff`, `ci_logs` and `expected_fix`, at most
a different version number) **and the CI actually turns red**. Every other case is
excluded, with a one-line reason, in `experiments/excluded_cases.json`
(11 test, 15 dependency, 45 config). Kept: 39 test, 35 dependency, 5 config.

### 8.1 Harness
- `inject_error()` returns `False` when the target file is unchanged (dependency
  and config too). Callers skip such a case: the agent is never run on a state
  identical to the clean baseline (the 46 null config injections were silent).
- `setup_case()`: clean baseline, then the case context, then the injection.
- Every mode of `experiments/benchmark.py` skips the cases in `excluded_cases.json`.
- `--failing-state`: protocol B (pre-check red on the full failing state, fix
  branches from it) for every category.
- `--verify-dep-config`: non-injectable cases are not pushed; cases with context
  also push "clean state + context" (must be green).

### 8.2 Config — only cases whose error is unchanged
- `conf_001`, `conf_003`: `git_diff` aligned to `ci.yml` (double quotes). The
  first occurrence of `python-version: "3.11"` is the setup-python step of job A.
- `conf_002`: Python 3.15 has been released (3.15.2 in the setup-python manifest),
  so the injected version is now 3.17 (absent from the manifest), in `git_diff`,
  `ci_logs`, `ci_job_name` and `notes`; the "-" line and `expected_fix` use 3.11,
  the version actually in `ci.yml`.
- Kept unchanged: `conf_006` (the run never starts: runner label retired),
  `conf_013`.

### 8.3 Dependency — pre-existing context (D1)
New optional field `context_requirements`: pins quoted in the case's `ci_logs`
that are a pre-existing state of the repository for that case, written before
the injection (never in the `git_diff`, never on GitHub `main`). Kept only where,
on Python 3.11 with pip, clean state + context installs and the suite passes,
and clean state + context + injection makes `pip install` fail with the resolver:
`dep_012` (typing-extensions==4.2.0), `dep_018` (protobuf==3.20.3),
`dep_025` (click==8.1.7), `dep_048` (boto3==1.34.10).
Tried and excluded: `dep_017`, `dep_046` (still install: PyPI metadata lacks the
upper bound quoted in the log), `dep_019` (cymem==2.0.1 does not exist on PyPI),
`dep_039` (depends on requirements-dev.txt).

### 8.4 Clean reference per case
`experiments/reference_states.json` (`--export-references`): for each kept
dependency/config case, the clean file its specialist repairs
(requirements.txt + context, or ci.yml at HEAD).
