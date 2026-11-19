# A2 — rerun of the "test" category with protocol B

Protocol B: only test files may be modified; the 11 cases whose error is injected outside the test file are excluded; the CI must be RED on the full failed state (pre-check) before the agent runs; every fix branch starts from that state; SR = fixed / valid cases (pre-check red).

Files: `benchmark_20261119_114847_anthropic_haiku_nomemory_protob.csv`, `benchmark_20261119_125516_openai_gpt4o_nomemory_protob.csv`, `benchmark_20261119_140155_ollama_qwen38_27b_nomemory_protob.csv`, `benchmark_20261119_151929_ollama_qwen3coder_30b_nomemory_protob.csv`, `benchmark_20261119_165456_ollama_llama8b_nomemory_protob.csv`, `benchmark_20261119_183305_ollama_mistral7b_nomemory_protob.csv`

## 1. Cases and Success Rate

| Model | rows | excluded | inj. failed | pre red | pre green | pre error | valid | fixed | escalated | timeout/error | **SR %** | Router acc. % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Claude Haiku | 50 | 11 | 0 | 39 | 0 | 0 | 39 | 37 | 2 | 0 | **94.9** | 97.4 |
| GPT-4o | 50 | 11 | 0 | 39 | 0 | 0 | 39 | 37 | 2 | 0 | **94.9** | 97.4 |
| Qwen3.8 27B | 50 | 11 | 0 | 39 | 0 | 0 | 39 | 38 | 1 | 0 | **97.4** | 97.4 |
| Qwen3-Coder 30B | 50 | 11 | 0 | 39 | 0 | 0 | 39 | 27 | 12 | 0 | **69.2** | 97.4 |
| Llama 3.1 8B | 50 | 11 | 0 | 39 | 0 | 0 | 39 | 19 | 20 | 0 | **48.7** | 87.2 |
| Mistral 7B | 50 | 11 | 0 | 39 | 0 | 0 | 39 | 18 | 21 | 0 | **46.2** | 82.1 |
| **Pooled** | | | | | | | 234 | 176 | | | **75.2** | |

## 2. Attempt at which the fix succeeded (fixed cases)

| Model | T1 | T2 | T3 | escalated |
|---|---|---|---|---|
| Claude Haiku | 36 | 1 | 0 | 2 |
| GPT-4o | 34 | 3 | 0 | 2 |
| Qwen3.8 27B | 38 | 0 | 0 | 1 |
| Qwen3-Coder 30B | 23 | 3 | 1 | 12 |
| Llama 3.1 8B | 19 | 0 | 0 | 20 |
| Mistral 7B | 17 | 1 | 0 | 21 |

## 3. Fixed cases: CI vs clean source vs assertions

Assertions are compared with the ORIGINAL test (clean baseline before the injection): k/m/r = kept / modified / removed. A fixed case with m>0 or r>0 changed what the test checks.

| Model | fixed | post-CI green | clean source pass | clean source fail | agent file = injected file | all assertions kept | ≥1 modified | ≥1 removed | k/m/r total |
|---|---|---|---|---|---|---|---|---|---|
| Claude Haiku | 37 | 37 | 37 | 0 | 37 | 36 | 1 | 0 | 76/1/0 |
| GPT-4o | 37 | 37 | 37 | 0 | 37 | 34 | 2 | 1 | 74/2/1 |
| Qwen3.8 27B | 38 | 38 | 38 | 0 | 38 | 36 | 2 | 0 | 76/2/0 |
| Qwen3-Coder 30B | 27 | 27 | 27 | 0 | 27 | 23 | 4 | 0 | 44/4/0 |
| Llama 3.1 8B | 19 | 19 | 19 | 0 | 19 | 18 | 1 | 0 | 30/1/0 |
| Mistral 7B | 18 | 18 | 18 | 0 | 18 | 11 | 4 | 3 | 35/4/4 |

Fixed cases to inspect (clean source not passing, or assertions modified/removed):

| Model | Case | clean source | k/m/r |
|---|---|---|---|
| anthropic_haiku | test_007 | pass | 2/1/0 |
| openai_gpt4o | test_005 | pass | 1/1/0 |
| openai_gpt4o | test_033 | pass | 1/1/0 |
| openai_gpt4o | test_047 | pass | 1/0/1 |
| ollama_qwen38_27b | test_007 | pass | 2/1/0 |
| ollama_qwen38_27b | test_032 | pass | 0/1/0 |
| ollama_qwen3coder_30b | test_007 | pass | 2/1/0 |
| ollama_qwen3coder_30b | test_020 | pass | 0/1/0 |
| ollama_qwen3coder_30b | test_029 | pass | 0/1/0 |
| ollama_qwen3coder_30b | test_032 | pass | 0/1/0 |
| ollama_llama8b | test_046 | pass | 0/1/0 |
| ollama_mistral7b | test_005 | pass | 1/1/0 |
| ollama_mistral7b | test_018 | pass | 2/0/1 |
| ollama_mistral7b | test_021 | pass | 1/0/2 |
| ollama_mistral7b | test_033 | pass | 1/0/1 |
| ollama_mistral7b | test_035 | pass | 0/1/0 |
| ollama_mistral7b | test_046 | pass | 0/1/0 |
| ollama_mistral7b | test_050 | pass | 0/1/0 |

## 4. Pre-check anomalies (cases skipped)

None: the CI was red on the failed state for every valid case.

## 5. Per case (F<n> = fixed at attempt n, esc = escalated, — = not valid)

| Case | anthropic_haiku | openai_gpt4o | ollama_qwen38_27b | ollama_qwen3coder_30b | ollama_llama8b | ollama_mistral7b |
|---|---|---|---|---|---|---|
| test_001 | F1 | F1 | F1 | esc | esc | F1 |
| test_002 | F1 | F1 | F1 | esc | esc | esc |
| test_003 | F1 | F1 | F1 | F1 | esc | F2 |
| test_004 | F1 | F1 | F1 | F1 | esc | esc |
| test_005 | F1 | F1 | F1 | F3 | F1 | F1 |
| test_006 | F1 | F1 | F1 | F2 | F1 | F1 |
| test_007 | F1 | F1 | F1 | F2 | F1 | F1 |
| test_008 | F1 | F1 | F1 | F1 | F1 | F1 |
| test_009 | excl | excl | excl | excl | excl | excl |
| test_010 | F1 | F1 | F1 | F1 | esc | esc |
| test_011 | excl | excl | excl | excl | excl | excl |
| test_012 | excl | excl | excl | excl | excl | excl |
| test_013 | excl | excl | excl | excl | excl | excl |
| test_014 | excl | excl | excl | excl | excl | excl |
| test_015 | excl | excl | excl | excl | excl | excl |
| test_016 | F1 | F1 | F1 | F1 | esc | esc |
| test_017 | F1 | esc | F1 | esc | esc | esc |
| test_018 | F1 | F1 | F1 | F1 | F1 | F1 |
| test_019 | excl | excl | excl | excl | excl | excl |
| test_020 | esc | F2 | F1 | F1 | esc | esc |
| test_021 | F1 | F1 | F1 | F1 | F1 | F1 |
| test_022 | excl | excl | excl | excl | excl | excl |
| test_023 | esc | esc | esc | esc | esc | esc |
| test_024 | F1 | F1 | F1 | esc | F1 | F1 |
| test_025 | F1 | F1 | F1 | F1 | esc | esc |
| test_026 | F1 | F1 | F1 | F1 | F1 | esc |
| test_027 | excl | excl | excl | excl | excl | excl |
| test_028 | F1 | F1 | F1 | F1 | F1 | esc |
| test_029 | F1 | F1 | F1 | F1 | F1 | F1 |
| test_030 | F1 | F1 | F1 | esc | esc | F1 |
| test_031 | F1 | F1 | F1 | F1 | esc | esc |
| test_032 | F1 | F1 | F1 | F1 | esc | esc |
| test_033 | F1 | F1 | F1 | esc | F1 | F1 |
| test_034 | F1 | F1 | F1 | esc | esc | esc |
| test_035 | F2 | F2 | F1 | esc | esc | F1 |
| test_036 | F1 | F1 | F1 | F1 | esc | esc |
| test_037 | F1 | F1 | F1 | F2 | F1 | esc |
| test_038 | F1 | F1 | F1 | esc | esc | F1 |
| test_039 | F1 | F1 | F1 | F1 | F1 | esc |
| test_040 | excl | excl | excl | excl | excl | excl |
| test_041 | F1 | F1 | F1 | F1 | F1 | esc |
| test_042 | F1 | F2 | F1 | esc | esc | esc |
| test_043 | F1 | F1 | F1 | F1 | F1 | F1 |
| test_044 | F1 | F1 | F1 | F1 | F1 | esc |
| test_045 | F1 | F1 | F1 | F1 | esc | esc |
| test_046 | F1 | F1 | F1 | F1 | F1 | F1 |
| test_047 | F1 | F1 | F1 | esc | esc | esc |
| test_048 | F1 | F1 | F1 | F1 | F1 | F1 |
| test_049 | excl | excl | excl | excl | excl | excl |
| test_050 | F1 | F1 | F1 | F1 | F1 | F1 |

## 6. The 11 excluded cases under the old protocol (`--verify-excluded`)

File: `verify_excluded_20261119_113819.csv`. *test file only* = what the old Fix Executor committed (branch from clean main + test file); *full failed state* = injected file included.

| Case | error injected in | test file only | full failed state | bug confirmed | runs (only / full) |
|---|---|---|---|---|---|
| test_009 | `src/services.py` | green | red | yes | 44507547523 / 44507561223 |
| test_011 | `src/auth.py` | green | red | yes | 44507719275 / 44507734661 |
| test_012 | `src/db.py` | green | red | yes | 44507852366 / 44507868127 |
| test_013 | `src/mailer.py` | green | red | yes | 44508020750 / 44508040112 |
| test_014 | `src/config.py` | green | red | yes | 44508150420 / 44508167006 |
| test_015 | `src/validator.py` | green | red | yes | 44508278175 / 44508294124 |
| test_019 | `src/serializer.py` | green | red | yes | 44508448693 / 44508465013 |
| test_022 | `src/parser.py` | green | red | yes | 44508582159 / 44508597351 |
| test_027 | `tests/fixtures/sample.json` | green | red | yes | 44508712930 / 44508724849 |
| test_040 | `src/validation.py` | green | red | yes | 44508837024 / 44508852973 |
| test_049 | `src/logger.py` | green | red | yes | 44508964654 / 44508981368 |

Bug confirmed on 11/11 cases.
